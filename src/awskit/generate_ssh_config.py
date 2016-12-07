#!/usr/bin/python3

"""
This script will update ~/.aws/config file with the names of your machines.
Notice that you must hold all of your .pem files in ~/.aws/keys
"""

import os.path
import boto3
import boto3.resources
import ujson
import sys
from typing import List

pattern = """Host {host}
\tHostName {public_ip}
\tIdentityFile ~/.aws/keys/{key_name}.pem
\tIdentitiesOnly yes
\tUser ubuntu"""


def main():
    comment_line = "# DO NOT EDIT BEYOND THIS LINE - LEAVE THIS LINE AS IS\n"
    config_file = os.path.expanduser("~/.ssh/config")
    filter_file = os.path.expanduser("~/.ssh/aws_filter")
    # no need to expand this as ~/.ssh/config can work with ~...
    pem_pattern = "~/.awk/keys/{key_name}.pem"

    with open(filter_file) as file_handle:
        filters = ujson.loads(file_handle.read())
    # print(filters)

    with open(config_file) as file_handle:
        lines = file_handle.readlines()

    # cut down auto generated lines if they exist...
    try:
        location_of_comment_line = lines.index(comment_line)
        lines = lines[:location_of_comment_line]
    except ValueError:
        pass
    # print("lines is {}".format(lines), file=sys.stderr)

    ec2 = boto3.resource('ec2')
    instances = list(ec2.instances.filter(Filters=filters))  # type: List[boto3.resources.collection.ec2.instancesCollection]
    num_of_instances = len(instances)
    print("Found {} instances".format(num_of_instances), file=sys.stderr)
    assert num_of_instances > 0

    lines.append(comment_line)

    # add bunch of lines for each server
    for instance in instances:  # type: boto3.resources.factory.ec2.Instance
        tags_dict = {}
        for tag in instance.tags:
            tags_dict[tag["Key"]] = tag["Value"]
        pattern_to_add = pattern.format(
            host=tags_dict["Name"],
            public_ip=instance.public_dns_name,
            key_name=instance.key_name,
        )
        lines.extend(pattern_to_add)
    # print("lines is {}".format(lines), file=sys.stderr)

    # print the final lines to the config file
    with open(config_file, "wt") as file_handle:
        file_handle.writelines(lines)
    print("written {}".format(config_file))

if __name__ == "__main__":
    main()
