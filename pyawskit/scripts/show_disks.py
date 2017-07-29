import click

from pyawskit.common import setup, get_disks


@click.command()
def main():
    """
    This script simply shows all the disks you have on an AWS machine
    """
    setup()
    print(get_disks())


if __name__ == "__main__":
    main()
