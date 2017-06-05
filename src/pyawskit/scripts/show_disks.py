#!/usr/bin/python3

import pyawskit.common


def main():
    """
    This script simply shows all the disks you have on an AWS machine
    """
    pyawskit.common.setup()
    print(pyawskit.common.get_disks())


if __name__ == "__main__":
    main()
