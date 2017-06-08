import subprocess
import sys
import os.path

import click

from pyawskit.common import setup


@click.command()
def main():
    """
    This script copies important files to a machine like key files and such.

    TODO:
    - do not copy ~/.aws/shell (it is big)
    """
    setup()
    folders_to_copy = [
        "~/.aws",
        "~/.ssh",
        "~/.s3cfg",
        "~/.gitconfig",
        "~/.passwd-s3fs",
    ]

    assert len(sys.argv) == 2
    machine_name = sys.argv[1]
    args = [
        "scp",
        "-r",
    ]
    args.extend(map(os.path.expanduser, folders_to_copy))
    args.append("{machine_name}:~".format(machine_name=machine_name))
    # subprocess.check_call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.check_call(args)


if __name__ == '__main__':
    main()
