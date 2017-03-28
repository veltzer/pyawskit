"""
This script will update ~/.aws/config file with the names of your machines.
Notice that you must hold all of your .pem files in ~/.aws/keys
"""
import os
import sys
import click

from pyawskit.common import update_file


# noinspection PyShadowingBuiltins
@click.command()
@click.option("--all/--filter", default=False, help="filter or add all instances")
def main(all):
    if not os.geteuid() == 0:
        sys.exit('Script must be run as root')
    update_file(filename="/etc/hosts", pattern="{ip} {host}\n", do_all=all)

if __name__ == "__main__":
    main()
