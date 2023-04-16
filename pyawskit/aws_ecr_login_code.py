import os
import sys
import json

from pyawskit.configs import ConfigAwsEcrLogin


def run() -> None:
    env_ecr_region = ConfigAwsEcrLogin.env_ecr_region
    env_ecr_account_id = ConfigAwsEcrLogin.env_ecr_account_id
    filename = os.path.expanduser("~/.docker/config.json")
    with open(filename) as file_handle:
        config = json.load(file_handle)
    ecr_url = f"{env_ecr_account_id}.dkr.ecr.{env_ecr_region}.amazonaws.com"
    if ecr_url in config["auths"]:
        sys.exit()
    print("logging in to docker")
    cmd = f"aws ecr get-login-password --region \"{env_ecr_region}\"\
        | docker login --username AWS --password-stdin \"{ecr_url}\" > /dev/null"
    # print(f"cmd is {cmd}")
    os.system(cmd)
