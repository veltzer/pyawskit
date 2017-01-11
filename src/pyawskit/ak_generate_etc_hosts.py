"""
This script will update ~/.aws/config file with the names of your machines.
Notice that you must hold all of your .pem files in ~/.aws/keys
"""
import os
import sys

from pyawskit.common import update_file


def main():
    if not os.geteuid() == 0:
        sys.exit('Script must be run as root')
    update_file(filename="/etc/hosts", pattern="{ip} {host}\n")

if __name__ == "__main__":
    main()
