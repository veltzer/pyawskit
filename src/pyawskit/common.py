import os

import ujson

import boto3
import sys


def update_file(filename=None, pattern=None):
    assert filename is not None
    assert pattern is not None

    config_file = os.path.expanduser(filename)
    if os.path.isfile(config_file):
        with open(config_file) as file_handle:
            lines = file_handle.readlines()
    else:
        lines = []

    # cut down auto generated lines if they exist...
    comment_line = "# DO NOT EDIT BEYOND THIS LINE - LEAVE THIS LINE AS IS\n"
    try:
        location_of_comment_line = lines.index(comment_line)
        lines = lines[:location_of_comment_line]
    except ValueError:
        pass

    filter_file = os.path.expanduser("~/.aws/aws_filter")
    if os.path.isfile(filter_file):
        print('reading [{0}]...'.format(filter_file))
        with open(filter_file) as file_handle:
            filters = ujson.loads(file_handle.read())
    else:
        print('no filter file [{0}] exists...'.format(filter_file))
        filters = []

    # look for servers matching the query
    ec2 = boto3.resource('ec2')
    instances = list(ec2.instances.filter(Filters=filters))
    num_of_instances = len(instances)
    print("Found {} instances".format(num_of_instances), file=sys.stderr)
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
        if host == "":
            continue
        new_host = host.replace(' ','')
        if new_host != host:
            print('Name [{0}] for host is bad. Try names without spaces...'.format(host))
        host = new_host
        # public_ip = instance.public_dns_name
        # if public_ip == "":
        #    continue
        # print(dir(instance))
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
    print("Added {} instances".format(added), file=sys.stderr)
    print("written {}".format(config_file))
