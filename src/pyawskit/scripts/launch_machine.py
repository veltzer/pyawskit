#!/usr/bin/python3

"""
This script launches a new machine via boto3

References:
- http://boto3.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.run_instances
- https://stackoverflow.com/questions/35721557/boto3-spot-instance-creation
- https://github.com/abdul/ec2-spot-instance-launcher
- https://peteris.rocks/blog/script-to-launch-amazon-ec2-spot-instances/
"""

import boto3

from pyfakeuse.pyfakeuse import fake_use


def main():
    client = boto3.client('ec2')
    response = client.request_spot_instances(
        DryRun=False,
        SpotPrice='4',
        ClientToken='string',
        InstanceCount=1,
        Type='one-time',
        LaunchSpecification={
            'ImageId': 'ami-fce3c696',
            'KeyName': 'awskey.pem',
            'SecurityGroups': ['name of the security group'],
            'InstanceType': 'm4.large',
            'Placement': {
                'AvailabilityZone': 'us-east-1a',
            },
            'BlockDeviceMappings': [
                {
                    'Ebs': {
                        'SnapshotId': '[snapshot-id',
                        'VolumeSize': 100,
                        'DeleteOnTermination': True,
                        'VolumeType': 'gp2',
                        'Iops': 300,
                        'Encrypted': False
                    },
                },
            ],
            'EbsOptimized': True,
            'Monitoring': {
                'Enabled': False,
            },
            'SecurityGroupIds': [
                'sg-709f8709',
            ]
        }
    )
    fake_use(response)

