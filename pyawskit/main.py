import multiprocessing
import subprocess
import sys
import os

from sultan import Sultan


import boto3
import tqdm

from pylogconf.core import setup
from pytconf import register_main, config_arg_parse_and_launch, register_endpoint

import pyawskit.common
import pyawskit.roles
from pyawskit.aws import ProcessData, request_spot_instances, tag_resources, poll_instances_till_done, wait_for_ssh, \
    attach_disks
from pyawskit.common import update_etc_hosts, update_ssh_config, update_file, do_hush_login, wait_net_service
from pyawskit.configs import ConfigFilter, ConfigName, ConfigAwsCodeartifactNpm, ConfigAwsCodeartifactPip
from pyawskit.configs import ConfigRoleDuplicate, ConfigRole

from pyawskit.static import APP_NAME, VERSION_STR, DESCRIPTION
from pyawskit.utils import object_exists, compress_one_file, print_exception
import pyawskit.inet

import pyawskit.aws_codeartifact_npm_env_config_code
import pyawskit.aws_codeartifact_pip_env_config_code
import pyawskit.aws_ecr_login_code


@register_endpoint(
    description="configure npm for codeartifact",
    configs=[
        ConfigAwsCodeartifactNpm,
    ],
)
def aws_codeartifact_npm_env_config() -> None:
    pyawskit.aws_codeartifact_npm_env_config_code.run()


@register_endpoint(
    description="configure pip for codeartifact",
    configs=[
        ConfigAwsCodeartifactPip,
    ],
)
def aws_codeartifact_pip_env_config() -> None:
    pyawskit.aws_codeartifact_pip_env_config_code.run()


@register_endpoint(
    description="docker login to aws ecr",
)
def aws_ecr_login() -> None:
    pyawskit.aws_ecr_login_code.run()


@register_endpoint(
    description="Compress an S3 folder",
)
def compress_s3_folder() -> None:
    """
    This script accepts three parameters: bucket, in-folder, out-folder
    It reads every file in in-folder, gzip it, and then writes it with the suffix ".gz"
    to the out folder.

    The credentials for this are NOT stored in this script
    but rather are in ~/.aws/credentials.
    """
    bucket_name = "bucket_name"
    folder_in = "flipkart/"
    folder_out = "flipkart_gz"
    do_progress = False
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    gen = bucket.objects.filter(Prefix=folder_in)
    if do_progress:
        gen = tqdm.tqdm(gen)
    jobs = []
    for object_summary in gen:
        print(f"doing [{object_summary.key}]")
        full_name = object_summary.key
        basename = os.path.basename(full_name)
        compressed_basename = basename + ".gz"
        full_compressed_name = os.path.join(folder_out, compressed_basename)
        if object_exists(s3, bucket_name, full_compressed_name):
            print("object exists, skipping")
            continue
        jobs.append([basename, full_name, compressed_basename, full_compressed_name, bucket_name])
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        pool.map_async(compress_one_file, jobs, error_callback=print_exception)
        pool.join()


@register_endpoint(
    description="Copy important files to a machine like key files and such",
)
def copy_to_machine() -> None:
    """
    TODO:
    - do not copy ~/.aws/shell (it is big)
    """
    folders_to_copy = [
        "~/.aws",
        "~/.ssh",
        "~/.s3cfg",
        "~/.gitconfig",
        "~/.passwd-s3fs",
    ]

    assert len(sys.argv) == 2
    machine_name = sys.argv[1]
    args = [
        "scp",
        "-r",
    ]
    args.extend(map(os.path.expanduser, folders_to_copy))
    args.append(f"{machine_name}:~")
    # subprocess.check_call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.check_call(args)


@register_endpoint(
    description="Generate /etc/hosts file for you. Must be run as root",
    configs=[
        ConfigFilter,
    ],
)
def generate_etc_hosts() -> None:
    """
    This script will update ~/.aws/config file with the names of your machines.
    Notice that you must hold all of your .pem files in ~/.aws/keys
    """
    file_etc_hosts = "/etc/hosts"
    if not os.geteuid() == 0 and not os.access(file_etc_hosts, os.W_OK):
        sys.exit(f"script must be run as root or {file_etc_hosts} must be writable")
    update_etc_hosts(all_hosts=not ConfigFilter.filter)


@register_endpoint(
    description="Generate ~/ssh/config or ~/.ssh/config.d/99_dynamic.conf file for you",
    configs=[
        ConfigFilter,
    ],
)
def generate_ssh_config() -> None:
    """
    This script will update ~/.aws/config file with the names of your machines.
    Notice that you must hold all of your .pem files in ~/.aws/keys
    """
    update_ssh_config(not ConfigFilter.filter)


@register_endpoint(
    description="Generate ~/.hosts for you",
    configs=[
        ConfigFilter,
    ],
)
def generate_tilde_hosts() -> None:
    """
    This script will update ~/.hosts file with the names of your machines.
    You must use something like libnss_homehosts to use this file for each app.
    """
    update_file(filename="~/.hosts", pattern="{ip} {host}\n", do_all=not ConfigFilter.filter)


@register_endpoint(
    description="Launch a machine on AWS via a json configuration",
    configs=[
        ConfigName,
    ],
)
def launch_machine() -> None:
    """
    This script launches a new machine via boto3 with configuration from
    ~/.pyawskit/launch_config.json

    If you want to know how to edit this file look at:
    http://boto3.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.request_spot_instances

    References:
    - http://boto3.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.run_instances
    - http://boto3.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.request_spot_instances
    - https://stackoverflow.com/questions/35721557/boto3-spot-instance-creation
    - https://github.com/abdul/ec2-spot-instance-launcher
    - https://peteris.rocks/blog/script-to-launch-amazon-ec2-spot-instances/

    This is the real script where most of this one is from:
    - https://gist.github.com/aloysius-lim/b77f6d62a595ae329e41
    """
    pd = ProcessData(name=ConfigName.name)

    client = boto3.client("ec2", region_name=pd.p_region)
    ec2 = boto3.resource("ec2", region_name=pd.p_region)

    r_request_spot_instances = request_spot_instances(client, pd)
    request_ids = [r["SpotInstanceRequestId"] for r in r_request_spot_instances["SpotInstanceRequests"]]
    tag_resources(client, request_ids, pd.p_launch_config[pd.p_name]["spot_request_tags"])
    # other way of waiting...
    # wait_using_waiter(client, pd, request_ids)
    instances = poll_instances_till_done(ec2, pd, request_ids)
    instance_ids = [i.id for i in instances]
    tag_resources(client, instance_ids, pd.p_launch_config[pd.p_name]["instance_tags"])
    wait_for_ssh(instances)

    # TODO: we just need to add the instances we created
    update_ssh_config(all_hosts=False)

    attach_disks(ec2, instance_ids, pd.p_launch_config[pd.p_name]["disks_to_attach"])


@register_endpoint(
    description="Prepares your account on a new AWS machine",
)
def prep_account():
    """
    These are the types of things it does:
    - copy ~/.aws ~/.ssh ~/.s3cfg ~/.gitconfig ~/.passwd-s3fs to it
    - set quiet login using:
        $ touch ~/.hushlogin
    - configure vim to do correct python editing and save editing positions.
    - install fancy prompt on it.
    - put the git repositories you want on it.
    """
    do_hush_login()


@register_endpoint(
    description="Prepare a machine for work",
)
def prep_machine(name: str) -> None:
    """
    A python version of the bash script here:
    https://gist.github.com/joemiller/6049831

    - sudo purge-old-kernels --keep 1 # to remove old kernels
    - install a list of packages on the system:
    - format and mount all disks
        use mdadm
    - set the hostname in /etc/hosts beside
        127.0.0.1 localhost [hostname]
        to avoid problems resolving the host name.
        $ touch ~/.hushlogin
    - configure vim to do correct python editing and save editing positions.
    - install fancy prompt on it.
    - put the git repositories you want on it.
    :param name:
    :return:
    """
    with Sultan.load(sudo=False, hostname=name) as sultan:
        sultan.sudo("apt update -y")
        sultan.sudo("apt dist-upgrade -y")
        sultan.sudo("reboot")
    wait_net_service(server=name, port=22)
    with Sultan.load(sudo=False, hostname=name) as sultan:
        sultan.run("touch ~/.hushlogin")


@register_endpoint(
    description="Shows all the disks you have on an AWS machine",
)
def show_disks() -> None:
    print(pyawskit.common.get_disks())


@register_endpoint(
    description="Duplicate a role",
    configs=[
        ConfigRoleDuplicate,
    ],
)
def role_duplicate() -> None:
    pyawskit.roles.role_duplicate()


@register_endpoint(
    description="Delete a role",
    configs=[
        ConfigRole,
    ],
)
def role_delete() -> None:
    pyawskit.roles.role_delete()


@register_endpoint(
    description="Get a role",
    configs=[
        ConfigRole,
    ],
)
def role_get() -> None:
    pyawskit.roles.role_get()


@register_endpoint(
    description="Check if you have an internet connection",
    configs=[
    ],
)
def inet_check() -> None:
    if pyawskit.inet.check():
        print("The Internet is connected.")
    else:
        print("The Internet is not connected.")


@register_endpoint(
    description="Get your public IP address",
    configs=[
    ],
)
def inet_my_ip() -> None:
    print(pyawskit.inet.my_ip())


@register_main(
    main_description=DESCRIPTION,
    app_name=APP_NAME,
    version=VERSION_STR,
)
def main():
    setup()
    config_arg_parse_and_launch()


if __name__ == "__main__":
    main()
