"""
This script will update ~/.aws/config file with the names of your machines.
Notice that you must hold all of your .pem files in ~/.aws/keys
"""

from pyawskit.common import update_file


def main():
    update_file(filename="~/.hosts", pattern="{ip} {host}\n")

if __name__ == "__main__":
    main()
