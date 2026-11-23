""" aws_ecr_login_code.py """

import base64
import datetime
import json
import os.path
import subprocess
import sys
from typing import Any
from urllib.parse import urlparse

# import requests.exceptions
# import docker
import boto3
import pyapikey

KEY = "ecr_password"


def handle_data(user: str, password: str, proxy_endpoint: str) -> None:
    """ really do something with the data
    It seems that the docker-py is broken as far as auth goes so we use the command line instead.
    client = docker.Client()
    try:
        client.login(
            username=user,
            password=password,
            registry=proxy_endpoint,
        )
    except requests.exceptions.ConnectionError:
        print(f"ConnectionError for {user} {password} {proxy_endpoint}", file=sys.stderr)
        sys.exit(1)
    """
    if not is_logged_in(proxy_endpoint):
        subprocess.check_call([
            "docker",
            "login",
            "--username", user,
            "--password", password,
            proxy_endpoint,
        ])


def strip_scheme(url: str) -> str:
    """ strip scheme from url
    References:
    - https://stackoverflow.com/questions/21687408/how-to-remove-scheme-from-url-in-python
    """
    schemaless = urlparse(url)._replace(scheme="").geturl()
    return schemaless[2:]


def is_logged_in(proxy_endpoint: str) -> bool:
    """ return if you are currently logged in to a specific server
    References:
    - https://stackoverflow.com/questions/36022892/how-to-know-if-docker-is-already-logged-in-to-a-docker-registry-server
    """
    config_file = os.path.expanduser("~/.docker/config.json")
    if os.path.isfile(config_file):
        with open(config_file) as stream:
            data = json.load(stream)
            if "auths" not in data:
                return False
            auths: dict[str, Any] = data["auths"]
            return strip_scheme(proxy_endpoint) in auths
    else:
        return False


def logout(proxy_endpoint: str) -> None:
    """ logout of docker """
    subprocess.check_call([
        "docker",
        "login",
        proxy_endpoint,
    ])


def run() -> None:
    temp_store = pyapikey.core.TempStore()
    if temp_store.has(KEY):
        data = temp_store.get(KEY)
        expiration = data["expiration"]
        # naive UTC: stored expirations are AWS UTC times with tzinfo stripped
        now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
        if expiration > now:
            d_user = data["user"]
            d_password = data["password"]
            d_proxy_endpoint = data["proxyEndpoint"]
            handle_data(
                user=d_user,
                password=d_password,
                proxy_endpoint=d_proxy_endpoint,
            )
            sys.exit()

    with open("/dev/tty", "w", encoding="utf-8") as f:
        print("Creating new temp key for ecr", file=f)

    client = boto3.client("ecr")
    res = client.get_authorization_token()
    authorization_data = res["authorizationData"][0]
    d_authorization_token = authorization_data["authorizationToken"]
    d_expires_at = authorization_data["expiresAt"]
    d_proxy_endpoint = authorization_data["proxyEndpoint"]

    # decode the password
    base64decode = base64.b64decode(d_authorization_token).decode("ASCII")
    (d_user, d_password) = base64decode.split(":")
    handle_data(
        user=d_user,
        password=d_password,
        proxy_endpoint=d_proxy_endpoint,
    )

    # save the token
    data = {}
    data["user"] = d_user
    data["password"] = d_password
    data["proxyEndpoint"] = d_proxy_endpoint
    data["expiration"] = d_expires_at.replace(tzinfo=None)
    temp_store.set(KEY, data)
    temp_store.save()
