"""
This script will update ~/.aws/config file with the names of your machines.
Notice that you must hold all of your .pem files in ~/.aws/keys
"""

from pyawskit.common import update_file, setup
import click


# noinspection PyShadowingBuiltins
@click.command()
@click.option("--all/--filter", default=False, help="filter or add all instances")
def main(all):
    setup()
    update_file(filename="~/.hosts", pattern="{ip} {host}\n", do_all=all)

if __name__ == "__main__":
    main()
