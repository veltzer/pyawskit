"""
References:
- http://boto3.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.run_instances
- http://boto3.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.request_spot_instances
- https://stackoverflow.com/questions/35721557/boto3-spot-instance-creation
- https://github.com/abdul/ec2-spot-instance-launcher
- https://peteris.rocks/blog/script-to-launch-amazon-ec2-spot-instances/

This is the real script where most of this one is from:
- https://gist.github.com/aloysius-lim/b77f6d62a595ae329e41
"""

import boto3
import click

from pyawskit.aws import ProcessData, request_spot_instances, tag_resources, poll_instances_till_done, wait_for_ssh, \
    attach_disks
from pyawskit.common import setup, update_ssh_config


@click.command()
@click.option(
    "--name",
    default=None,
    type=str,
    required=True,
    help="What config to launch?",
    show_default=True,
)
def main(
        name: str,
):
    """
    This script launches a new machine via boto3 with configuration from
    ~/.pyawskit/launch_config.json

    If you want to know how to edit this file look at:
    http://boto3.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.request_spot_instances
    """
    setup()
    pd = ProcessData(name=name)

    client = boto3.client('ec2', region_name=pd.p_region)
    ec2 = boto3.resource('ec2', region_name=pd.p_region)

    r_request_spot_instances = request_spot_instances(client, pd)
    request_ids = [r['SpotInstanceRequestId'] for r in r_request_spot_instances['SpotInstanceRequests']]
    tag_resources(client, request_ids, pd.p_launch_config[pd.p_name]["spot_request_tags"])
    # other way of waiting...
    # wait_using_waiter(client, pd, request_ids)
    instances = poll_instances_till_done(ec2, pd, request_ids)
    instance_ids = [i.id for i in instances]
    tag_resources(client, instance_ids, pd.p_launch_config[pd.p_name]["instance_tags"])
    wait_for_ssh(instances)

    # TODO: we just need to add the instances we created
    update_ssh_config(all_hosts=False)

    attach_disks(ec2, instance_ids, pd.p_launch_config[pd.p_name]["disks_to_attach"])


if __name__ == "__main__":
    main()

