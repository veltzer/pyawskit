"""
A python version of the bash script here:
https://gist.github.com/joemiller/6049831

bash
- apt-get update
- apt-get dist-upgrade
- install python3-pip python3-dev python-pip python-dev
- upgrade pip using
    $ sudo -H pip install pip --upgrade
    $ sudo -H pip3 install pip --upgrade
- a reboot may be necessary if a new kernel was installed

- remove old kernels
- install a list of packages on the system:
- format and mount all disks
    use mdadm
- copy ~/.aws ~/.ssh ~/.s3cfg ~/.gitconfig ~/.passwd-s3fs to it
- set the hostname of the machine (it's usually hostname is ip-XXX-XXX-XXX-XXX).
- set the hostname in /etc/hosts beside
    127.0.0.1 localhost
    to avoid problems resolving the host name.
- set quiet login using:
    $ touch ~/.hushlogin
- configure vim to do correct python editing and save editing positions.
- install fancy prompt on it.
- put the git repositories you want on it.
"""

import subprocess
import os
import sys
import enum
from typing import List


class OSType(enum.Enum):
    ubuntu = 1
    aml = 2


def run(args: List[str]) -> None:
    # print('running', args)
    subprocess.check_call(
        args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


os_type = None


# first find out if we are on ubuntu or amazon linux
def detect_os() -> None:
    global os_type
    # noinspection PyBroadException
    try:
        if subprocess.check_output(['lsb_release', '--id', '-s']).decode().rstrip() == 'Ubuntu':
            os_type = OSType.ubuntu
    except:
        pass
    # noinspection PyBroadException
    try:
        with open('/etc/issue') as f:
            d = f.read()
            if d.startswith('Amazon Linux AMI'):
                os_type = OSType.aml
    except:
        pass

    if os_type is None:
        sys.exit('could not detect the os running')


def is_os_type(t) -> bool:
    global os_type
    return os_type == t


# check that we are running as root
def check_root() -> None:
    if not os.geteuid() == 0:
        sys.exit('script must be run as root')


def update_machine() -> None:
    if is_os_type(OSType.ubuntu):
        run(['apt-get', 'update'])
        run(['apt-get', 'upgrade'])
    if is_os_type(OSType.aml):
        run(['yum', 'update'])
        run(['yum', 'upgrade'])


# install necessary package per platform
def install_packages() -> None:
    list_of_packages = {
        OSType.ubuntu: [
            'python-pip',
            'python-dev',
            'python3-pip',
            'python3-dev',
            'git',
            'parallel',
            'jq',  # for analyzing json files
            'tree',  # for tree(1)
            'zip',
            'awscli',
            's3cmd',
            'mdadm',  # is already installed on ubuntu on aws
            'lrzip',  # for lrzip(1), lrunzip(1)
            'bc',  # nice to have tool
            's3fs',  # s3 file system
            'apt-file',  # for finding package names by files
            'sysstat',  # for iostat(1) and such
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


def main() -> None:
    check_root()
    detect_os()
    update_machine()
    install_packages()


if __name__ == '__main__':
    main()
