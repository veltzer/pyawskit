import os
import sys
import click

from pyawskit.common import update_file, setup


@click.command()
@click.option("--all-instances/--filter", default=False, help="filter or add all instances")
def main(all_instances):
    """
    This script will update ~/.aws/config file with the names of your machines.
    Notice that you must hold all of your .pem files in ~/.aws/keys
    """
    setup()
    filename = "/etc/hosts"
    if not os.geteuid() == 0 and not os.access(filename, os.W_OK):
        sys.exit('script must be run as root or {} must be writable'.format(filename))
    update_file(filename=filename, pattern="{ip} {host}\n", do_all=all_instances)

if __name__ == "__main__":
    main()
