import logging
import multiprocessing
import os
import os.path
import subprocess
import sys

import boto3
import pymount.mgr
import tqdm
from pytconf.config import register_function_group, register_endpoint
from sultan import Sultan

import pyawskit.common
from pyawskit.aws import ProcessData, request_spot_instances, tag_resources, poll_instances_till_done, wait_for_ssh, \
    attach_disks
from pyawskit.common import update_etc_hosts, update_ssh_config, update_file, do_hush_login, wait_net_service, \
    get_disks, erase_partition_table, reread_partition_table, format_device, mount_disk
from pyawskit.configs import ConfigFilter, ConfigName
from pyawskit.utils import object_exists, process_one_file, print_exception

GROUP_NAME_DEFAULT = "default"
GROUP_DESCRIPTION_DEFAULT = "standard pyawskit commands"


def register_group_default():
    register_function_group(
        function_group_name=GROUP_NAME_DEFAULT,
        function_group_description=GROUP_DESCRIPTION_DEFAULT,
    )


@register_endpoint(
    configs=[
    ],
    suggest_configs=[
    ],
    group=GROUP_NAME_DEFAULT,
)
def compress_s3_folder() -> None:
    """
    Compress an S3 folder
    """
    """
    This script accepts three parameters: bucket, in-folder, out-folder
    It reads every file in in-folder, gzip it, and then writes it with the suffix '.gz'
    to the out folder.

    The credentials for this are NOT stored in this script
    but rather are in ~/.aws/credentials.
    """
    bucket_name = 'twiggle-click-streams'
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
        print('doing [{}]'.format(object_summary.key))
        full_name = object_summary.key
        basename = os.path.basename(full_name)
        compressed_basename = basename + '.gz'
        full_compressed_name = os.path.join(folder_out, compressed_basename)
        if object_exists(s3, bucket_name, full_compressed_name):
            print('object exists, skipping')
            continue
        jobs.append([basename, full_name, compressed_basename, full_compressed_name, bucket_name])
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    pool.map_async(process_one_file, jobs, error_callback=print_exception)
    pool.close()
    pool.join()


@register_endpoint(
    configs=[
    ],
    suggest_configs=[
    ],
    group=GROUP_NAME_DEFAULT,
)
def copy_to_machine() -> None:
    """
    This script copies important files to a machine like key files and such
    """
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
    args.append("{machine_name}:~".format(machine_name=machine_name))
    # subprocess.check_call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.check_call(args)


@register_endpoint(
    configs=[
        ConfigFilter,
    ],
    suggest_configs=[
    ],
    group=GROUP_NAME_DEFAULT,
)
def generate_eth_hosts() -> None:
    """
    Generate /etc/hosts file for you. Must be run as root
    """
    """
    This script will update ~/.aws/config file with the names of your machines.
    Notice that you must hold all of your .pem files in ~/.aws/keys
    """
    filename = "/etc/hosts"
    if not os.geteuid() == 0 and not os.access(filename, os.W_OK):
        sys.exit('script must be run as root or {} must be writable'.format(filename))
    update_etc_hosts(all_hosts=not ConfigFilter.filter)


@register_endpoint(
    configs=[
        ConfigFilter,
    ],
    suggest_configs=[
    ],
    group=GROUP_NAME_DEFAULT,
)
def generate_ssh_config() -> None:
    """
    Generate ~/ssh/config or ~/.ssh/config.d/99_dynamic.conf file for you
    """
    """
    This script will update ~/.aws/config file with the names of your machines.
    Notice that you must hold all of your .pem files in ~/.aws/keys
    """
    update_ssh_config(not ConfigFilter.filter)


@register_endpoint(
    configs=[
        ConfigFilter,
    ],
    suggest_configs=[
    ],
    group=GROUP_NAME_DEFAULT,
)
def generate_tilde_hosts() -> None:
    """
    Generate ~/.hosts for you
    """
    """
    This script will update ~/.hosts file with the names of your machines.
    You must use something like libnss_homehosts to use this file for each app.
    """
    update_file(filename="~/.hosts", pattern="{ip} {host}\n", do_all=not ConfigFilter.filter)


@register_endpoint(
    configs=[
        ConfigName,
    ],
    suggest_configs=[
    ],
    group=GROUP_NAME_DEFAULT,
)
def launch_machine() -> None:
    """
    Lauch a machine on AWS via a json configuration.
    """
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
    """
    """
    TODO:
    - make this run in parallel on multiple cores and enable the user to choose (via
    command line option) whether to run this multi-core or not.
    """
    pyawskit.common.check_root()
    # TODO: ask the user for yes/no confirmation since we are brutally
    # erasing all of the local disks...
    disks = pyawskit.common.get_disks()
    for disk in disks:
        folder = "/mnt/{}".format(disk)
        pyawskit.common.erase_partition_table(disk=disk)
        pyawskit.common.format_device(disk=disk)
        pyawskit.common.mount_disk(disk=disk, folder=folder)


@register_endpoint(
    configs=[
    ],
    suggest_configs=[
    ],
    group=GROUP_NAME_DEFAULT,
)
def prep_account():
    """
    This script prepares your account on a new AWS machine
    """
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
    configs=[
    ],
    suggest_configs=[
    ],
    group=GROUP_NAME_DEFAULT,
)
def prep_machine(name: str) -> None:
    """
    Prepare a machine for work
    """
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
    configs=[
    ],
    suggest_configs=[
    ],
    group=GROUP_NAME_DEFAULT,
)
def show_disks() -> None:
    """
    This script simply shows all the disks you have on an AWS machine
    """
    print(get_disks())


def unify_disks() -> None:
    """
    unify disks of a machine in raid 0
    """
    """
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
    device_file = "/dev/md0"
    mount_point = "/mnt/raid0"
    mdadm_config_file = '/etc/mdadm/mdadm.conf'
    mdadm_binary = "/sbin/mdadm"
    fstab_filename = "/etc/fstab"
    file_system_type = "ext4"
    name_of_raid_device = "MY_RAID"
    start_stop_queue = False
    write_etc_mdadm = False
    add_line_to_fstab = False

    logger = logging.getLogger(__name__)
    logger.info("looking for disks...")
    disks = get_disks()
    if len(disks) == 0:
        print('found no disks, exiting...', file=sys.stderr)
        sys.exit(1)

    logger.info("got %d disks %s", len(disks), str(disks))

    logger.info("checking if any of the disks are mounted [%s]", ','.join(disks))
    manager = pymount.mgr.Manager()
    for disk in disks:
        if manager.is_mounted(disk):
            mount_point = manager.get_mount_point(disk)
            logger.info("unmounting device [%s] from [%s]", device_file, mount_point)
            subprocess.check_call([
                "/bin/umount",
                mount_point,
            ])
        else:
            logger.info("device [%s] is not mounted, good", device_file)

    logger.info("checking if the md device is mounted...[%s]", device_file)
    if manager.is_mounted(device_file):
        mount_point = manager.get_mount_point(device_file)
        logger.info("unmounting device [%s] from [%s]", device_file, mount_point)
        subprocess.check_call([
            "/bin/umount",
            mount_point,
        ])
        logger.info("unmount of [%s] was ok", device_file)
    else:
        logger.info("device [%s] is not mounted, good...", device_file)

    logger.info("checking if device exists [%s]", device_file)
    if os.path.exists(device_file):
        logger.info("stopping md on the current device [%s]", device_file)
        subprocess.check_call([
            mdadm_binary,
            "--stop",
            device_file,
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info("stopped md on [%s] successfully...", device_file)
    else:
        logger.info("no md [%s], good", device_file)

    for disk in disks:
        erase_partition_table(disk)
    reread_partition_table()

    logger.info("creating the new md device...")
    if start_stop_queue:
        subprocess.check_call([
            "/sbin/udevadm",
            "control",
            "--stop-exec-queue",
        ])
    args = [
        mdadm_binary,
        "--create",
        device_file,
        "--level=0",  # RAID 0 for performance
        "--name={}".format(name_of_raid_device),
        # "-c256",
        "--raid-devices={}".format(len(disks)),
    ]
    args.extend(disks)
    subprocess.check_call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if start_stop_queue:
        subprocess.check_call([
            "/sbin/udevadm",
            "control",
            "--start-exec-queue",
        ])

    # removed writing /etc/mdadm because it was causing problems
    if write_etc_mdadm:
        logger.info("writing the details of the new device in [%s]", mdadm_config_file)
        mdadm_handle = open(mdadm_config_file, "at")
        subprocess.check_call([
            mdadm_binary,
            "--detail",
            "--scan",
            "--verbose",
        ], stdout=mdadm_handle, stderr=subprocess.DEVNULL)

    format_device(device_file, label=name_of_raid_device)

    mount_disk(disk=device_file, folder=mount_point)

    if add_line_to_fstab:
        logger.info("checking if need to add line to [%s] for mount on reboot...", fstab_filename)
        line_to_add = " ".join([
            # device_file,
            "LABEL={}".format(name_of_raid_device),
            mount_point,
            file_system_type,
            "defaults",
            "0",
            "0",
        ])
        found_line_to_add = False
        with open(fstab_filename) as file_handle:
            for line in file_handle:
                line = line.rstrip()
                if line == line_to_add:
                    found_line_to_add = True
                    break
        if found_line_to_add:
            logger.info("found the line to add. not doing anything...")
        else:
            logger.info("adding line to [%s]", fstab_filename)
            with open(fstab_filename, "at") as file_handle:
                file_handle.write(line_to_add+"\n")
    # create ubuntu folder and chown it to ubuntu
