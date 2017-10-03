import click

from pyawskit.common import update_ssh_config, setup


@click.command()
@click.option("--all-hosts/--filter", default=False, help="filter or add all instances")
def main(all_hosts):
    """
    This script will update ~/.aws/config file with the names of your machines.
    Notice that you must hold all of your .pem files in ~/.aws/keys
    """
    setup()
    update_ssh_config(all_hosts)


if __name__ == "__main__":
    main()
