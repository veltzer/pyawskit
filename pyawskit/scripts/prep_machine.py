"""
A python version of the bash script here:
https://gist.github.com/joemiller/6049831

- sudo purge-old-kernels --keep 1 # to remove old kernels
- install a list of packages on the system:
- format and mount all disks
    use mdadm
- set the hostname in /etc/hosts beside
    127.0.0.1 localhost [hostname]
    to avoid problems resolving the host name.
    $ touch ~/.hushlogin
- configure vim to do correct python editing and save editing positions.
- install fancy prompt on it.
- put the git repositories you want on it.
"""

import subprocess
import sys
import enum
from sultan.api import Sultan


import click

from pyawskit.common import setup, run_devnull, wait_net_service


class OSType(enum.Enum):
    ubuntu = 1
    aml = 2


os_type = None


# first find out if we are on ubuntu or amazon linux
def detect_os() -> None:
    global os_type
    # noinspection PyBroadException,PyPep8
    try:
        if subprocess.check_output(['lsb_release', '--id', '-s']).decode().rstrip() == 'Ubuntu':
            os_type = OSType.ubuntu
    except Exception:
        pass
    # noinspection PyBroadException,PyPep8
    try:
        with open('/etc/issue') as f:
            d = f.read()
            if d.startswith('Amazon Linux AMI'):
                os_type = OSType.aml
    except Exception:
        pass

    if os_type is None:
        sys.exit('could not detect the os running')


def is_os_type(t) -> bool:
    global os_type
    return os_type == t


def update_machine() -> None:
    if is_os_type(OSType.ubuntu):
        run_devnull(['apt-get', 'update'])
        run_devnull(['apt-get', 'upgrade'])
    if is_os_type(OSType.aml):
        run_devnull(['yum', 'update'])
        run_devnull(['yum', 'upgrade'])


# install necessary package per platform
def install_packages() -> None:
    list_of_packages = {
        OSType.ubuntu: [
            # python
            'python-pip',
            'python-dev',
            'python3-pip',
            'python3-dev',
            # amazon stuff
            'awscli',  # the basic aws cli
            's3cmd',  # for the s3cmd application
            'libs3-2',  # for the s3 application
            's3fs',  # s3 file system
            # misc
            'mdadm',  # is already installed on ubuntu on aws
            'lrzip',  # for lrzip(1), lrunzip(1)
            'bc',  # nice to have tool
            'apt-file',  # for finding package names by files
            'sysstat',  # for iostat(1) and such
            'jq',  # for analyzing json files
            'tree',  # for tree(1)
            'git',
            'parallel',
            'zip',
            'csvtool',
            'python3-csvkit',
            'myrepos',
            'octave',
            'iotop',
            'tofrodos',
            'makepasswd',
            'lftp',
            'ispell',
            'hspell',
            'pigz',  # for pigz(1) fast gzip compression
            'virtualenv',  # for python virtual envs
            'virtualenvwrapper',  # for a more easy virtual env
        ],
        OSType.aml: [
        ],
    }
    # install the packages
    args = [
        "apt-get",
        "install",
    ]
    args.extend(list_of_packages[OSType.ubuntu])
    subprocess.check_call(args)


def set_timezone() -> None:
    subprocess.check_call([
        "timedatectl",
        "set-timezone",
        "Asia/Jerusalem",
    ])


@click.command()
@click.option(
    "--name",
    default=None,
    type=str,
    required=True,
    help="What config to launch?",
)
def main(name: str) -> None:
    setup()
    with Sultan.load(sudo=False, hostname=name) as sultan:
        sultan.sudo("apt update -y")
        sultan.sudo("apt dist-upgrade -y")
        sultan.sudo("reboot")
    wait_net_service(server=name, port=22)
    with Sultan.load(sudo=False, hostname=name) as sultan:
        sultan.run("touch ~/.hushlogin")


if __name__ == '__main__':
    main()
