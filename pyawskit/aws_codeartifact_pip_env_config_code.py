"""
This script outputs the url for pip to be used when logging in to aws codeartifact.
"""

import sys
import datetime
import boto3
from furl import furl
import pyapikey

from pyawskit.configs import ConfigAwsCodeartifactPip


KEY = "codeartifact_pip_config"


def handle_data(url: str) -> None:
    """ really do something with the data """
    print(f"export PIP_INDEX_URL=\"{url}\"")


def run() -> None:
    env_pip_domain = ConfigAwsCodeartifactPip.env_pip_domain
    env_pip_domain_owner = ConfigAwsCodeartifactPip.env_pip_domain_owner
    env_pip_repository = ConfigAwsCodeartifactPip.env_pip_repository
    temp_store = pyapikey.core.TempStore()
    if temp_store.has(KEY):
        data = temp_store.get(KEY)
        expiration = data["expiration"]
        now = datetime.datetime.now()
        if expiration > now:
            d_url = data["url"]
            handle_data(url=d_url)
            sys.exit()

    with open("/dev/tty", "wt", encoding="utf-8") as f:
        print("Creating new temp key for codeartifact pip", file=f)

    client = boto3.client("codeartifact")
    res = client.get_authorization_token(
        domain=env_pip_domain,
        domainOwner=env_pip_domain_owner,
        durationSeconds=43200,
    )
    password = res["authorizationToken"]
    d_expiration = res["expiration"]
    res = client.get_repository_endpoint(
        domain=env_pip_domain,
        domainOwner=env_pip_domain_owner,
        repository=env_pip_repository,
        format="pypi",
    )
    data_repositoryEndpoint = res["repositoryEndpoint"]
    d_url = furl(data_repositoryEndpoint)
    d_url.username = "aws"
    d_url.password = password
    d_url.path.add("simple/")

    data = {}
    data["url"] = d_url
    data["expiration"] = d_expiration.replace(tzinfo=None)
    temp_store.set(KEY, data)
    temp_store.save()

    handle_data(url=d_url)
