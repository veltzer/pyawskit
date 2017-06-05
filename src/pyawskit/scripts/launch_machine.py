#!/usr/bin/python3

"""
This script launches a new machine via boto3

References:
- http://boto3.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.run_instances
- http://boto3.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.request_spot_instances
- https://stackoverflow.com/questions/35721557/boto3-spot-instance-creation
- https://github.com/abdul/ec2-spot-instance-launcher
- https://peteris.rocks/blog/script-to-launch-amazon-ec2-spot-instances/
"""

import boto3
import logging

from pyfakeuse.pyfakeuse import fake_use

from pyawskit.common import load_json_config, setup


def main(
):

    setup()
    logger = logging.getLogger(__name__)

    client = boto3.client('ec2')
    # parameters
    p_launch_configuration = load_json_config("launch_configuration")
    p_spot_request_tags = load_json_config("spot_request_tags")
    p_instance_tags = load_json_config("instance_tags")
    p_instance_count = 1
    p_spot_price = "4"
    p_dry_run = False
    p_type = "one-time"

    logger.info("Sending the request")
    r_request_spot_instances = client.request_spot_instances(
        DryRun=p_dry_run,
        SpotPrice=p_spot_price,
        InstanceCount=p_instance_count,
        LaunchSpecification=p_launch_configuration,
        Type=p_type,
    )
    logger.info("Tagging the requests")
    request_ids = [r['SpotInstanceRequestId'] for r in r_request_spot_instances['SpotInstanceRequests']]
    r_create_tags = client.create_tags(
        Resources=request_ids,
        Tags=p_spot_request_tags,
    )
    logger.info("All requests tagged")
    waiter = client.get_waiter('spot_instance_request_fulfilled')
    waiter.wait(
        DryRun=p_dry_run,
        SpotInstanceRequestIds=request_ids,
    )
    fake_use(r_create_tags)
    fake_use(p_instance_tags)

if __name__ == "__main__":
    main()

