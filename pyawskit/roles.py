import json
import boto3
from pyawskit.configs import ConfigRoleDuplicate, ConfigRole


def role_duplicate():
    client = boto3.client("iam")
    from_role = ConfigRoleDuplicate.from_role
    to_role = ConfigRoleDuplicate.to_role
    response1 = client.get_role(
        RoleName=from_role,
    )
    assert response1["ResponseMetadata"]["HTTPStatusCode"] == 200
    params = response1["Role"]
    del params["RoleId"]
    del params["Arn"]
    del params["CreateDate"]
    del params["RoleLastUsed"]
    params["AssumeRolePolicyDocument"] = json.dumps(params["AssumeRolePolicyDocument"])
    params["RoleName"] = to_role
    response2 = client.create_role(**params)
    assert response2["ResponseMetadata"]["HTTPStatusCode"] == 200

    # attach role_policies
    policies = client.list_attached_role_policies(RoleName=from_role)["AttachedPolicies"]
    for policy in policies:
        response3 = client.attach_role_policy(
            RoleName=to_role,
            PolicyArn=policy["PolicyArn"],
        )
        assert response3["ResponseMetadata"]["HTTPStatusCode"] == 200

    # attach instance_profiles
    instance_profiles = client.list_instance_profiles_for_role(RoleName=from_role)["InstanceProfiles"]
    for profile in instance_profiles:
        response3 = client.create_instance_profile(
            InstanceProfileName=to_role,
            Path=profile["Path"],
            Tags=[],
        )
        assert response3["ResponseMetadata"]["HTTPStatusCode"] == 200
        response3 = client.add_role_to_instance_profile(
            InstanceProfileName=to_role,
            RoleName=to_role,
        )
        assert response3["ResponseMetadata"]["HTTPStatusCode"] == 200


def role_delete():
    client = boto3.client("iam")
    role_name = ConfigRole.role
    attached_policies = client.list_attached_role_policies(RoleName=role_name)["AttachedPolicies"]
    instance_profiles = client.list_instance_profiles_for_role(RoleName=role_name)["InstanceProfiles"]
    # Detach policies and instance profiles
    for policy in attached_policies:
        client.detach_role_policy(RoleName=role_name, PolicyArn=policy["PolicyArn"])

    for profile in instance_profiles:
        profile_name = profile["InstanceProfileName"]
        response = client.delete_instance_profile(
            InstanceProfileName=profile_name,
        )
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        client.remove_role_from_instance_profile(InstanceProfileName=profile_name, RoleName=role_name)

    # Delete the IAM role
    response = client.delete_role(
        RoleName=role_name,
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


def role_get():
    client = boto3.client("iam")
    role_name = ConfigRole.role
    response = client.get_role(
        RoleName=role_name,
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
    print(response)
    print("policies")
    policies = client.list_attached_role_policies(RoleName=role_name)["AttachedPolicies"]
    for policy in policies:
        print(policy)
    print("instance profiles")
    instance_profiles = client.list_instance_profiles_for_role(RoleName=role_name)["InstanceProfiles"]
    for profile in instance_profiles:
        print(profile)
