#!/usr/bin/python3

import logging

import pyawskit.common

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


"""
This script mounts all the local disks as individuals

TODO:
- make this run in parallel on multiple cores and enable the user to choose (via
command line option) whether to run this multi-core or not.
"""


def main():
    disks = pyawskit.common.get_disks()
    for disk in disks:
        folder = "/mnt/{}".format(disk)
        pyawskit.common.erase_partition_table(disk=disk)
        pyawskit.common.format_device(disk=disk)
        pyawskit.common.mount_disk(disk=disk, folder=folder)


if __name__ == "__main__":
    main()
