import boto3
from pyawskit.configs import ConfigDuplicateRole


def duplicate_role():
    client = boto3.client("iam")
    print(ConfigDuplicateRole.to_role)
    print(ConfigDuplicateRole.from_role)
    response = client.get_role(
        RoleName=ConfigDuplicateRole.from_role,
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
    print(response)
