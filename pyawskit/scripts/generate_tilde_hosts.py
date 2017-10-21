from pyawskit.common import update_file, setup
import click


@click.command()
@click.option("--all-instances/--filter", default=False, help="filter or add all instances")
def main(all_instances):
    """
    This script will update ~/.hosts file with the names of your machines.
    You must use something like libnss_homehosts to use this file for each app.
    """
    setup()
    update_file(filename="~/.hosts", pattern="{ip} {host}\n", do_all=all_instances)


if __name__ == "__main__":
    main()
