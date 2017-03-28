#!/usr/bin/python3

import logging

import pyawskit.common

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


"""
This script simply shows all the disks you have on an AWS machine
"""


def main():
    print(pyawskit.common.get_disks())


if __name__ == "__main__":
    main()
