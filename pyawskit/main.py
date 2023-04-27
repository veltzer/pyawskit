import logging
import multiprocessing
import subprocess
import sys
import os

from sultan import Sultan


import boto3
import tqdm

import pymount.mgr
from pylogconf.core import setup
from pytconf import register_main, config_arg_parse_and_launch, register_endpoint

import pyawskit.common
from pyawskit.aws import ProcessData, request_spot_instances, tag_resources, poll_instances_till_done, wait_for_ssh, \
    attach_disks
from pyawskit.common import update_etc_hosts, update_ssh_config, update_file, do_hush_login, wait_net_service, \
    get_disks, erase_partition_table, reread_partition_table, format_device, mount_disk
from pyawskit.configs import ConfigFilter, ConfigName, ConfigWork, ConfigAwsCodeartifactNpm, ConfigAwsCodeartifactPip

from pyawskit.static import APP_NAME, VERSION_STR, DESCRIPTION
from pyawskit.utils import object_exists, compress_one_file, print_exception

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
    description="docker login to aws acr",
)
def aws_ecr_login() -> None:
    pyawskit.aws_ecr_login_code.run()


@register_endpoint(
    description="Compress an S3 folder",
)
def compress_s3_folder() -> None:
    """
    This script accepts three parameters: bucket, in-folder, out-folder
    It reads every file in in-folder, gzip it, and then writes it with the suffix '.gz'
    to the out folder.

    The credentials for this are NOT stored in this script
    but rather are in ~/.aws/credentials.
    """
    bucket_name = 'bucket_name'
    folder_in = 'flipkart/'
    folder_out = 'flipkart_gz'
    do_progress = False
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    gen = bucket.objects.filter(Prefix=folder_in)
    if do_progress:
        gen = tqdm.tqdm(gen)
    jobs = []
    for object_summary in gen:
        print(f"doing [{object_summary.key}]")
        full_name = object_summary.key
        basename = os.path.basename(full_name)
        compressed_basename = basename + '.gz'
        full_compressed_name = os.path.join(folder_out, compressed_basename)
        if object_exists(s3, bucket_name, full_compressed_name):
            print('object exists, skipping')
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

    client = boto3.client('ec2', region_name=pd.p_region)
    ec2 = boto3.resource('ec2', region_name=pd.p_region)

    r_request_spot_instances = request_spot_instances(client, pd)
    request_ids = [r['SpotInstanceRequestId'] for r in r_request_spot_instances['SpotInstanceRequests']]
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


def mount_dists() -> None:
    """
    This script mounts all the local disks as individuals

    TODO:
    - make this run in parallel on multiple cores and enable the user to choose (via
    command line option) whether to run this multi-core or not.
    """
    pyawskit.common.check_root()
    # TODO: ask the user for yes/no confirmation since we are brutally
    # erasing all of the local disks...
    disks = pyawskit.common.get_disks()
    for disk in disks:
        folder = f"/mnt/{disk}"
        pyawskit.common.erase_partition_table(disk=disk)
        pyawskit.common.format_device(disk=disk)
        pyawskit.common.mount_disk(disk=disk, folder=folder)


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
    print(get_disks())


def unify_disks() -> None:
    """
    unify disks of a machine in raid 0

    This script is derived from the following bash script:
    https://gist.github.com/joemiller/6049831

    NOTES:
    - python has no support for 'mount' and 'umount' system
    calls. the result is that we use the command line tools
    to do mounting and un mounting.
    References:
    - http://stackoverflow.com/questions/1667257/how-do-i-mount-a-filesystem-using-python

    References:
    - http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/raid-config.html
    - http://www.tecmint.com/create-raid0-in-linux/
    - http://dev.bizo.com/2012/07/mdadm-device-or-resource-busy.html

    TODO:
    - make this script work in parallel. But for the dd(1) and mkfs(1) parts.
    """

    logger = logging.getLogger(__name__)
    logger.info("looking for disks...")
    disks = get_disks()
    assert len(disks) > 0, "found no disks"

    logger.info(f"got {len(disks)} disks {str(disks)}")

    check_unmounted(logger, disks)

    logger.info(f"checking if device exists [{ConfigWork.device_file}]")
    if os.path.exists(ConfigWork.device_file):
        logger.info(f"stopping md on the current device [{ConfigWork.device_file}]")
        subprocess.check_call([
            ConfigWork.mdadm_binary,
            "--stop",
            ConfigWork.device_file,
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info(f"stopped md on [{ConfigWork.device_file}] successfully...")
    else:
        logger.info(f"no md [{ConfigWork.device_file}], good")

    for disk in disks:
        erase_partition_table(disk)
    reread_partition_table()

    create_new_device(logger, disks)

    if ConfigWork.start_stop_queue:
        subprocess.check_call([
            "/sbin/udevadm",
            "control",
            "--start-exec-queue",
        ])

    # removed writing /etc/mdadm because it was causing problems
    if ConfigWork.write_etc_mdadm:
        logger.info(f"writing the details of the new device in [{ConfigWork.mdadm_config_file}]")
        with open(ConfigWork.mdadm_config_file, "at") as mdadm_handle:
            subprocess.check_call([
                ConfigWork.mdadm_binary,
                "--detail",
                "--scan",
                "--verbose",
            ], stdout=mdadm_handle, stderr=subprocess.DEVNULL)

    format_device(ConfigWork.device_file, label=ConfigWork.name_of_raid_device)

    mount_disk(disk=ConfigWork.device_file, folder=ConfigWork.mount_point)

    if ConfigWork.add_line_to_fstab:
        logger.info(f"checking if need to add line to [{ConfigWork.fstab_filename}] for mount on reboot...")
        line_to_add = " ".join([
            # ConfigWork.device_file,
            f"LABEL={ConfigWork.name_of_raid_device}",
            ConfigWork.mount_point,
            ConfigWork.file_system_type,
            "defaults",
            "0",
            "0",
        ])
        found_line_to_add = False
        with open(ConfigWork.fstab_filename) as file_handle:
            for line in file_handle:
                line = line.rstrip()
                if line == line_to_add:
                    found_line_to_add = True
                    break
        if found_line_to_add:
            logger.info("found the line to add. not doing anything...")
        else:
            logger.info("adding line to [%s]", ConfigWork.fstab_filename)
            with open(ConfigWork.fstab_filename, "at") as file_handle:
                file_handle.write(line_to_add + "\n")
    # create ubuntu folder and chown it to ubuntu


@register_main(
    main_description=DESCRIPTION,
    app_name=APP_NAME,
    version=VERSION_STR,
)
def main():
    setup()
    config_arg_parse_and_launch()


def create_new_device(logger, disks):
    logger.info("creating the new md device...")
    if ConfigWork.start_stop_queue:
        subprocess.check_call([
            "/sbin/udevadm",
            "control",
            "--stop-exec-queue",
        ])
    args = [
        ConfigWork.mdadm_binary,
        "--create",
        ConfigWork.device_file,
        "--level=0",  # RAID 0 for performance
        f"--name={ConfigWork.name_of_raid_device}",
        # "-c256",
        f"--raid-devices={len(disks)}",
    ]
    args.extend(disks)
    subprocess.check_call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def check_unmounted(logger, disks):
    logger.info(f"checking if any of the disks are mounted [{'.'.join(disks)}]")
    manager = pymount.mgr.Manager()
    for disk in disks:
        if manager.is_mounted(disk):
            mount_point = manager.get_mount_point(disk)
            logger.info(f"unmounting device [{ConfigWork.device_file}] from [{mount_point}]")
            subprocess.check_call([
                "/bin/umount",
                mount_point,
            ])
        else:
            logger.info(f"device [{ConfigWork.device_file}] is not mounted, good")
    logger.info(f"checking if the md device is mounted...[{ConfigWork.device_file}]")
    if manager.is_mounted(ConfigWork.device_file):
        mount_point = manager.get_mount_point(ConfigWork.device_file)
        logger.info(f"unmounting device [{ConfigWork.device_file}] from [{mount_point}]")
        subprocess.check_call([
            "/bin/umount",
            mount_point,
        ])
        logger.info(f"unmount of [{ConfigWork.device_file}] was ok")
    else:
        logger.info(f"device [{ConfigWork.device_file}] is not mounted, good...")


if __name__ == '__main__':
    main()
