#!/usr/bin/python3

import subprocess

import pymount.mgr
import os.path
import sys
import logging

import pyawskit.common

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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


def main():
    device_file = "/dev/md0"
    mount_point = "/mnt/raid0"
    mdadm_config_file = '/etc/mdadm/mdadm.conf'
    mdadm_binary = "/sbin/mdadm"
    fstab_filename = "/etc/fstab"
    file_system_type = "ext4"
    name_of_raid_device = "MY_RAID"
    start_stop_queue = False
    write_etc_mdadm = False

    logger.info("looking for disks...")
    disks = pyawskit.common.get_disks()
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
        pyawskit.common.erase_partition_table(disk)
    pyawskit.common.reread_partition_table()

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
    ].extend(disks)
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

    pyawskit.common.format_device(device_file, label=name_of_raid_device)

    pyawskit.common.mount_disk(disk=device_file, folder=mount_point)

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
            print(line_to_add, file=file_handle)


if __name__ == "__main__":
    main()
