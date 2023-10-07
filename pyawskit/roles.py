import boto3
from pyawskit.configs import ConfigDuplicateRole


def duplicate_role():
    client = boto3.client("iam")
    print(ConfigDuplicateRole.to_role)
    print(ConfigDuplicateRole.from_role)
    response = client.get_role(ConfigDuplicateRole.from_role)
    print(response)