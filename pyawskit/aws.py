import logging
from time import sleep
from typing import List, Callable, Dict

from pyawskit.common import load_json_config, wait_net_service

# http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-requests.html
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


def log_func_name(func: Callable):

    def inner(*kw, **tw):
        logger = logging.getLogger(__name__)
        logger.info(func.__name__)
        return func(*kw, **tw)
    return inner


class ProcessData:
    def __init__(self, name: str):
        self.p_name: str = name
        self.p_launch_config = load_json_config("launch_config")
        self.p_config = self.p_launch_config[self.p_name]
        self.p_price = float(self.p_config["price"])
        self.p_count = int(self.p_config["count"])
        self.p_region = self.p_config["region"]
        self.p_dry_run: bool = False
        self.p_type: str = "one-time"

    def get_price(self):
        return self.p_config["price"]


@log_func_name
def request_spot_instances(client, pd: ProcessData):
    r_request_spot_instances = client.request_spot_instances(
        DryRun=pd.p_dry_run,
        SpotPrice=str(pd.p_price),
        InstanceCount=pd.p_count,
        LaunchSpecification=pd.p_config["launch_config"],
        Type=pd.p_type,
    )
    return r_request_spot_instances


@log_func_name
def wait_using_waiter(client, pd: ProcessData, request_ids: List[str]):
    waiter = client.get_waiter("spot_instance_request_fulfilled")
    ret = waiter.wait(
        DryRun=pd.p_dry_run,
        SpotInstanceRequestIds=request_ids,
    )
    return ret


@log_func_name
def poll_requests_till_done(client, pd: ProcessData, request_ids: List[str]):
    response = client.describe_spot_instance_requests(
        DryRun=pd.p_dry_run,
        SpotInstanceRequestIds=request_ids,
    )
    return response


@log_func_name
def poll_instances_till_done(ec2, pd: ProcessData, request_ids: List[str]):
    instances = ec2.instances.filter(Filters=[{"Name": "spot-instance-request-id", "Values": request_ids}])
    while len(list(instances)) < pd.p_count:
        sleep(1)
        instances = ec2.instances.filter(Filters=[{"Name": "spot-instance-request-id", "Values": request_ids}])
    return instances


@log_func_name
def tag_resources(client, resource_ids: List[str], tags: object):
    response = client.create_tags(
        Resources=resource_ids,
        Tags=tags,
    )
    return response


@log_func_name
def attach_disks(ec2, instance_ids: List[str], disks: List[Dict[str, str]]):
    """
    This function attaches a list of disks to the instances in the list
    :param ec2:
    :param instance_ids:
    :param disks:
    :return:
    """
    responses = []
    for p_instance_id in instance_ids:
        for disk in disks:
            response = attach_disk(
                ec2=ec2,
                instance_id=p_instance_id,
                volume_id=disk["volume_id"],
                device=disk["device"],
            )
            responses.append(response)
    return responses


@log_func_name
def wait_for_ssh(instances):
    for instance in instances:
        wait_net_service(
            server=instance.private_ip_address,
            port=22,
        )


@log_func_name
def attach_disk(ec2, instance_id: str, volume_id: str, device: str):
    volume = ec2.Volume(volume_id)
    response = volume.attach_to_instance(
        InstanceId=instance_id,
        Device=device,
    )
    return response
