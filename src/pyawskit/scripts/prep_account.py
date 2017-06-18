"""
These are the types of things it does:
- copy ~/.aws ~/.ssh ~/.s3cfg ~/.gitconfig ~/.passwd-s3fs to it
- set quiet login using:
    $ touch ~/.hushlogin
- configure vim to do correct python editing and save editing positions.
- install fancy prompt on it.
- put the git repositories you want on it.
"""
import os

import click

from pyawskit.common import setup, touch


def do_hush_login():
    filename = os.path.expanduser("~/.hushlogin")
    touch(filename)


@click.command()
def main():
    """
    This script prepares your account on a new aws machine.
    """
    setup()
    do_hush_login()


if __name__ == '__main__':
    main()
