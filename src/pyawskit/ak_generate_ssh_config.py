"""
This script will update ~/.aws/config file with the names of your machines.
Notice that you must hold all of your .pem files in ~/.aws/keys
"""

from pyawskit.common import update_file
import click

pattern = """Host {host}
\tHostName {ip}
\tIdentityFile ~/.aws/keys/{key_name}.pem
\tIdentitiesOnly yes
\tUser ubuntu
"""


# noinspection PyShadowingBuiltins
@click.command()
@click.option("--all/--filter", default=False, help="filter or add all instances")
def main(all):
    update_file(filename="~/.ssh/config", pattern=pattern, do_all=all)

if __name__ == "__main__":
    main()
