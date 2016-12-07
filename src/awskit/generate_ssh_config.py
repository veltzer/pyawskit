"""
This script will update ~/.aws/config file with the names of your machines.
Notice that you must hold all of your .pem files in ~/.aws/keys
"""
import os.path

import boto.ec2
from boto.ec2.instance import Instance

comment_line = "# DO NOT EDIT BEYOND THIS LINE - LEAVE THIS LINE AS IS\n"
config_file = os.path.expanduser("~/.ssh/config")
filter_file = os.path.expanduser("~/.ssh/aws_filter")
pem_pattern = os.path.expanduser("~/.awk/keys/{pem_name}.pem")

filters={}
with open(filter_file) as file_handle:
    content = file_handle.read()
    filters=eval(content)

with open(config_file) as file_handle:
    lines = file_handle.readlines()

location_of_comment_line = lines.find(comment_line)
if location_of_comment_line != -1:
    lines

instance_name = argv[-1]
stderr.write('Wildcard: {}\n'.format(instance_name))
client = boto.ec2.connect_to_region('us-west-2')

pattern = """
Host {host}
       User ubuntu
       HostName {public_ip}
       IdentityFile ~/.ssh/{pem_file}.pem
"""
response = client.get_only_instances(filters={
    'tag:Name': instance_name,
})

stderr.write('Found {} instances\n'.format(len(response)))
for instance in response:  # type Instance
    print pattern.format(host=instance.tags['Name'], public_ip=instance.public_dns_name, pem_file=instance.key_name)
