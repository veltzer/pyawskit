#!/usr/bin/python3

"""
This script copies important files to a machine like key files and such.
"""


import subprocess
import sys
import os.path


def main():
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
