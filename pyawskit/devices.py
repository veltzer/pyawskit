import logging
import os
import subprocess
import pymount.mgr


from pyawskit.configs import ConfigWork
import pyawskit.common


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
    logger.info(f"checking if any of the disks are mounted [{disks}]")
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


def mount_disks() -> None:
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


def unify_disks() -> None:
    """
    unify disks of a machine in raid 0

    This script is derived from the following bash script:
    https://gist.github.com/joemiller/6049831

    NOTES:
    - python has no support for "mount" and "umount" system
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
    disks = pyawskit.common.get_disks()
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
        pyawskit.common.erase_partition_table(disk)
    pyawskit.common.reread_partition_table()

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

    pyawskit.common.format_device(ConfigWork.device_file, label=ConfigWork.name_of_raid_device)

    pyawskit.common.mount_disk(disk=ConfigWork.device_file, folder=ConfigWork.mount_point)

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
