import os
import sys
import json


def aws_ecr_login(env_region: str, env_account_id: str) -> None:
    filename = os.path.expanduser("~/.docker/config.json")
    with open(filename) as file_handle:
        config = json.load(file_handle)
    ecr_url = f"{env_account_id}.dkr.ecr.{env_region}.amazonaws.com"
    if ecr_url in config["auths"]:
        sys.exit()
    print("logging in to docker")
    cmd = f"aws ecr get-login-password --region \"{env_region}\"\
        | docker login --username AWS --password-stdin \"{ecr_url}\" > /dev/null"
    # print(f"cmd is {cmd}")
    os.system(cmd)
