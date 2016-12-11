"""
This script will update ~/.aws/config file with the names of your machines.
Notice that you must hold all of your .pem files in ~/.aws/keys
"""

import os.path
import boto3
import boto3.resources.factory
import ujson
import sys


pattern = """Host {host}
\tHostName {public_ip}
\tIdentityFile ~/.aws/keys/{key_name}.pem
\tIdentitiesOnly yes
\tUser ubuntu"""


def main():
    comment_line = "# DO NOT EDIT BEYOND THIS LINE - LEAVE THIS LINE AS IS\n"
    config_file = os.path.expanduser("~/.ssh/config")
    filter_file = os.path.expanduser("~/.ssh/aws_filter")

    if os.path.isfile(filter_file):
        with open(filter_file) as file_handle:
            filters = ujson.loads(file_handle.read())
    else:
        filters = []

    if os.path.isfile(config_file):
        with open(config_file) as file_handle:
            lines = file_handle.readlines()
    else:
        lines = []

    # cut down auto generated lines if they exist...
    try:
        location_of_comment_line = lines.index(comment_line)
        lines = lines[:location_of_comment_line]
    except ValueError:
        pass

    # look for servers matching the query
    ec2 = boto3.resource('ec2')
    instances = list(ec2.instances.filter(Filters=filters))
    num_of_instances = len(instances)
    print("Found {} instances".format(num_of_instances), file=sys.stderr)
    assert num_of_instances > 0

    # add the comment line
    lines.append(comment_line)

    # add bunch of lines for each server
    for instance in instances:
        tags_dict = {}
        for tag in instance.tags:
            tags_dict[tag["Key"]] = tag["Value"]
        if "Name" in tags_dict:
            pattern_to_add = pattern.format(
                host=tags_dict["Name"],
                public_ip=instance.public_dns_name,
                key_name=instance.key_name,
            )
            lines.extend(pattern_to_add)

    # print the final lines to the config file
    with open(config_file, "wt") as file_handle:
        file_handle.writelines(lines)
    print("written {}".format(config_file))

if __name__ == "__main__":
    main()
