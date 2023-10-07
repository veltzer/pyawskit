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
    role_name = ConfigRoleDelete.role
    attached_policies = client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']
    instance_profiles = client.list_instance_profiles_for_role(RoleName=role_name)['InstanceProfiles']
    # Detach policies and instance profiles
    for policy in attached_policies:
        client.detach_role_policy(RoleName=role_name, PolicyArn=policy['PolicyArn'])

    for profile in instance_profiles:
        client.remove_role_from_instance_profile(InstanceProfileName=profile['InstanceProfileName'], RoleName=role_name)

    # Delete the IAM role
    response = client.delete_role(
        RoleName=role_name,
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
