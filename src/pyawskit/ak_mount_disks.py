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
    # TODO: check that we are running as root
    # if not then recommend sudo(1) and exit
    # TODO: ask the user for yes/no confirmation since we are brutally
    # erasing all of the local disks...
    disks = pyawskit.common.get_disks()
    for disk in disks:
        folder = "/mnt/{}".format(disk)
        pyawskit.common.erase_partition_table(disk=disk)
        pyawskit.common.format_device(disk=disk)
        pyawskit.common.mount_disk(disk=disk, folder=folder)


if __name__ == "__main__":
    main()
