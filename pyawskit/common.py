import errno
import json
import logging
import os
import socket
import stat
import subprocess
import sys
import time
from typing import List, Optional

import boto3
import requests


def load_json_config(
    name: str,
):
    home = os.getenv("HOME")
    assert home is not None
    path = os.path.join(
        home,
        ".pyawskit",
        name + ".json",
    )
    with open(path, "rt") as input_handle:
        obj = json.load(input_handle)
    return obj


def wait_net_service(
    server: str,
    port: int,
    timeout: int = 600,
) -> bool:
    """
        Wait for network service to appear
        http://code.activestate.com/recipes/576655-wait-for-network-service-to-appear/
        :param port:
        :param server:
        :param timeout
    """
    s = socket.socket()
    end: float
    if timeout:
        # time module is needed to calc timeout shared between two exceptions
        end = time.time() + timeout

    while True:
        try:
            if timeout:
                next_timeout = end - time.time()
                if next_timeout < 0:
                    return False
                s.settimeout(next_timeout)

            s.connect((server, port))

        except socket.timeout:
            # this exception occurs only if timeout is set
            if timeout:
                return False

        except socket.error as err:
            # catch timeout exception from underlying network library
            # this one is different from socket.timeout
            if err.errno != errno.ETIMEDOUT:
                raise
        else:
            s.close()
            return True


def get_disks() -> List[str]:
    # another option is to take the output of lsblk(1)
    # which is not amazon specific and has nice format of data.
    url = "http://169.254.169.254/latest/meta-data/block-device-mapping"
    r = requests.get(url, timeout=5)
    disks = []
    for line in r.content.decode().split("\n"):
        if not line.startswith("ephemeral"):
            continue
        ephemeral_url = f"http://169.254.169.254/latest/meta-data/block-device-mapping/{line}"
        r = requests.get(ephemeral_url, timeout=5)
        assert r.status_code == 200
        content = r.content.decode()
        assert content.startswith("sd")
        assert len(content) == 3
        letter = content[2]
        device = f"/dev/xvd{letter}"
        mode = os.stat(device).st_mode
        if not stat.S_ISBLK(mode):
            continue
        disks.append(device)
    return disks


def erase_partition_table(disk: str) -> None:
    logger = logging.getLogger(__name__)
    logger.info("erasing partition table on disk [%s]", disk)
    subprocess.check_call([
        "/bin/dd",
        "if=/dev/zero",
        f"of={disk}"
        "bs=4096",
        "count=1024",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def reread_partition_table() -> None:
    logger = logging.getLogger(__name__)
    logger.info("making OS re-read partition tables...")
    subprocess.check_call([
        "/sbin/partprobe",
    ])


def all_regions() -> List[str]:
    client = boto3.client("ec2")
    regions = [region["RegionName"] for region in client.describe_regions()["Regions"]]
    return regions


def format_device(disk: str, label: Optional[str] = None) -> None:
    logger = logging.getLogger(__name__)
    logger.info(f"formatting the new device [{disk}]")
    args = [
        "/sbin/mkfs.ext4",
        disk,
    ]
    if label is not None:
        args.extend([
            "-L",
            label,
        ])
    subprocess.check_call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def update_file(
    filename: str,
    pattern: str,
    do_all: bool = False,
):
    logger = logging.getLogger(__name__)

    config_file = os.path.expanduser(filename)
    if os.path.isfile(config_file):
        with open(config_file) as file_handle:
            lines = file_handle.readlines()
    else:
        lines = []

    # cut down auto generated lines if they exist...
    comment_line = "# DO NOT EDIT BEYOND THIS LINE - LEAVE THIS LINE AS IS\n"
    if comment_line in lines:
        location_of_comment_line = lines.index(comment_line)
        lines = lines[:location_of_comment_line]

    filter_file = os.path.expanduser("~/.pyawskit/aws_filter.json")
    if os.path.isfile(filter_file):
        logger.info(f"reading [{filter_file}]...")
        with open(filter_file) as file_handle:
            filters = json.loads(file_handle.read())
    else:
        logger.info(f"no filter file [{filter_file}] exists...")
        filters = []

    # look for servers matching the query, in all regions
    instances = []
    for region in all_regions():
        ec2 = boto3.resource("ec2", region_name=region)
        if do_all:
            instances.extend(list(ec2.instances.all()))
        else:
            instances.extend(list(ec2.instances.filter(Filters=filters)))
    num_of_instances = len(instances)
    logger.info(f"Found {num_of_instances} instance(s)")
    # assert num_of_instances > 0

    # add the comment line
    lines.append(comment_line)

    # add bunch of lines for each server
    added = 0
    for instance in instances:
        if instance.tags is None:
            continue
        tags_dict = {}
        for tag in instance.tags:
            tags_dict[tag["Key"]] = tag["Value"]
        if "Name" not in tags_dict:
            continue
        host = tags_dict["Name"]
        if host == "" or " " in host:
            logger.info(f"Name [{host}] for host is bad. Try non empty names without spaces...")
            continue
        # public_ip = instance.public_dns_name
        # if public_ip == "":
        #    continue
        # logger.info(dir(instance))
        private_ip = instance.private_ip_address
        if private_ip == "":
            continue
        pattern_to_add = pattern.format(
            host=host,
            ip=private_ip,
            key_name=instance.key_name,
        )
        lines.extend(pattern_to_add)
        added += 1

    # print the final lines to the config file
    with open(config_file, "wt") as file_handle:
        file_handle.writelines(lines)
    logger.info(f"Added {added} instance(s)")
    logger.info(f"Written {config_file}")


def mount_disk(disk: str, folder: str) -> None:
    logger = logging.getLogger(__name__)
    logger.info("mounting the new device [%s, %s]", disk, folder)
    if not os.path.isdir(folder):
        os.makedirs(folder)
    subprocess.check_call([
        "/bin/mount",
        disk,
        folder,
    ])


ssh_config_pattern = """Host {host}
\tHostName {ip}
\tIdentityFile ~/.pyawskit/keys/{key_name}.pem
\tIdentitiesOnly yes
\tUser ubuntu
\tStrictHostKeyChecking no
\tLogLevel ERROR
\tCheckHostIP no
\t# UserKnownHostsFile /dev/null
"""

etc_hosts_pattern = "{ip} {host}\n"


def update_ssh_config(all_hosts: bool):
    update_file(filename="~/.ssh/config.d/99_dynamic.conf", pattern=ssh_config_pattern, do_all=all_hosts)


def update_etc_hosts(all_hosts: bool):
    update_file(filename="/etc/hosts", pattern=etc_hosts_pattern, do_all=all_hosts)


def run_devnull(args: List[str]) -> None:
    subprocess.check_call(
        args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def check_root() -> None:
    """
    check that we are running as root
    """
    if not os.geteuid() == 0:
        sys.exit("script must be run as root")


def touch(filename: str) -> None:
    with open(filename, "w"):
        pass


def do_hush_login():
    filename = os.path.expanduser("~/.hushlogin")
    touch(filename)
