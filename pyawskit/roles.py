import json
import boto3
from pyawskit.configs import ConfigRoleDuplicate, ConfigRoleDelete


def role_duplicate():
    client = boto3.client("iam")
    response1 = client.get_role(
        RoleName=ConfigRoleDuplicate.from_role,
    )
    assert response1["ResponseMetadata"]["HTTPStatusCode"] == 200
    params = response1["Role"]
    del params["RoleId"]
    del params["Arn"]
    del params["CreateDate"]
    del params["RoleLastUsed"]
    params["AssumeRolePolicyDocument"] = json.dumps(params["AssumeRolePolicyDocument"])
    params["RoleName"] = ConfigRoleDuplicate.to_role
    response2 = client.create_role(**params)
    assert response2["ResponseMetadata"]["HTTPStatusCode"] == 200


def role_delete():
    client = boto3.client("iam")
    response = client.get_role(
        RoleName=ConfigRoleDelete.role,
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
