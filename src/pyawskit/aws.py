# http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-requests.html
from time import sleep
from typing import List

from pyawskit.common import load_json_config

aws_spot_instance_types = {
    "c3.8xlarge",
    "c4.8xlarge",
    "d2.8xlarge",
    "g2.8xlarge",
    "i2.8xlarge",
    "m4.10xlarge",
    "m4.16xlarge",
    "p2.16xlarge",
    "r3.8xlarge",
    "r4.16xlarge",
    "x1.32xlarge",
}


class ProcessData:
    def __init__(self):
        self.p_launch_configuration = load_json_config("launch_configuration")  # type:object
        self.p_spot_request_tags = load_json_config("spot_request_tags")  # type: object
        self.p_instance_tags = load_json_config("instance_tags")  # type: object
        self.p_instance_count = 1  # type: int
        self.p_spot_price = "4"  # type: string
        self.p_dry_run = False  # type: bool
        self.p_type = "one-time"  # type: string


def request_spot_instances(client, pd: ProcessData):
    r_request_spot_instances = client.request_spot_instances(
        DryRun=pd.p_dry_run,
        SpotPrice=pd.p_spot_price,
        InstanceCount=pd.p_instance_count,
        LaunchSpecification=pd.p_launch_configuration,
        Type=pd.p_type,
    )
    return r_request_spot_instances


def wait_using_waiter(client, pd: ProcessData, request_ids: List[str]):
    waiter = client.get_waiter('spot_instance_request_fulfilled')
    ret = waiter.wait(
        DryRun=pd.p_dry_run,
        SpotInstanceRequestIds=request_ids,
    )
    return ret


def poll_requests_till_done(client, pd: ProcessData, request_ids: List[str]):
    response = client.describe_spot_instance_requests(
        DryRun=pd.p_dry_run,
        SpotInstanceRequestIds=request_ids,
    )
    print(response)
    return response


def poll_instances_till_done(ec2, pd: ProcessData, request_ids: List[str], show_progress: bool):
    instances = ec2.instances.filter(Filters=[{'Name': 'spot-instance-request-id', 'Values': request_ids}])
    while len(list(instances)) < pd.p_instance_count:
        sleep(1)
        instances = ec2.instances.filter(Filters=[{'Name': 'spot-instance-request-id', 'Values': request_ids}])
    return instances


def tag_spot_instance_requests(client, pd: ProcessData, request_ids: List[str]):
    response = client.create_tags(
        Resources=request_ids,
        Tags=pd.p_spot_request_tags,
    )
    return response



