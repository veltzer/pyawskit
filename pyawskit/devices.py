import subprocess
import pymount.mgr


from pyawskit.configs import ConfigWork


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
