import enum
import subprocess
import sys
import shutil
import os.path

from typing import List, Dict

from pyawskit.common import run_devnull


class OSType(enum.Enum):
    ubuntu = 1
    aml = 2


os_data = {}
OS_TYPE = "OS_TYPE"


def set_timezone() -> None:
    subprocess.check_call([
        "timedatectl",
        "set-timezone",
        "Asia/Jerusalem",
    ])


def detect_os() -> None:
    """
    first find out if we are on ubuntu or amazon linux
    :return:
    """
    lsb_release = shutil.which("lsb_release")
    if lsb_release is not None:
        if subprocess.check_output([lsb_release, "--id", "-s"]).decode().rstrip() == "Ubuntu":
            os_data[OS_TYPE] = OSType.ubuntu
    if os.path.isfile("/etc/issue"):
        with open("/etc/issue") as f:
            d = f.read()
            if d.startswith("Amazon Linux AMI"):
                os_type = OSType.aml
    if os_type is None:
        sys.exit("could not detect the os running")


def is_os_type(t) -> bool:
    return os_data["OS_TYPE"] == t


def update_machine() -> None:
    if is_os_type(OSType.ubuntu):
        run_devnull(["apt-get", "update"])
        run_devnull(["apt-get", "upgrade"])
    if is_os_type(OSType.aml):
        run_devnull(["yum", "update"])
        run_devnull(["yum", "upgrade"])


def install_packages() -> None:
    """
    install necessary package per platform
    :return:
    """
    list_of_packages: Dict[OSType, List[str]] = {
        OSType.ubuntu: [
            # python
            "python-pip",
            "python-dev",
            "python3-pip",
            "python3-dev",
            # amazon stuff
            "awscli",  # the basic aws cli
            "s3cmd",  # for the s3cmd application
            "libs3-2",  # for the s3 application
            "s3fs",  # s3 file system
            # misc
            "mdadm",  # is already installed on ubuntu on aws
            "lrzip",  # for lrzip(1), lrunzip(1)
            "bc",  # nice to have tool
            "apt-file",  # for finding package names by files
            "sysstat",  # for iostat(1) and such
            "jq",  # for analyzing json files
            "tree",  # for tree(1)
            "git",
            "parallel",
            "zip",
            "csvtool",
            "python3-csvkit",
            "myrepos",
            "octave",
            "iotop",
            "tofrodos",
            "makepasswd",
            "lftp",
            "ispell",
            "hspell",
            "pigz",  # for pigz(1) fast gzip compression
            "virtualenv",  # for python virtual envs
            "virtualenvwrapper",  # for a more easy virtual env
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
