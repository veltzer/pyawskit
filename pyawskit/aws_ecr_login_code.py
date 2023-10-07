import sys
import os.path
import datetime
import base64
import subprocess
from urllib.parse import urlparse
import json

# import requests.exceptions
# import docker
import boto3
import pyapikey

KEY = "ecr_password"


def handle_data(user: str, password: str, proxyEndpoint: str) -> None:
    """ really do something with the data
    It seems that the docker-py is broken as far as auth goes so we use the command line instead.
    client = docker.Client()
    try:
        client.login(
            username=user,
            password=password,
            registry=proxyEndpoint,
        )
    except requests.exceptions.ConnectionError:
        print(f"ConnectionError for {user} {password} {proxyEndpoint}", file=sys.stderr)
        sys.exit(1)
    """
    if not is_logged_in(proxyEndpoint):
        subprocess.check_call([
            "docker",
            "login",
            "--username", user,
            "--password", password,
            proxyEndpoint,
        ])


def strip_scheme(url: str) -> str:
    """ strip scheme from url
    References:
    - https://stackoverflow.com/questions/21687408/how-to-remove-scheme-from-url-in-python
    """
    schemaless = urlparse(url)._replace(scheme="").geturl()
    return schemaless[2:]


def is_logged_in(proxyEndpoint: str) -> bool:
    """ return if you are currently logged in to a specific server
    References:
    - https://stackoverflow.com/questions/36022892/how-to-know-if-docker-is-already-logged-in-to-a-docker-registry-server
    """
    config_file = os.path.expanduser("~/.docker/config.json")
    if os.path.isfile(config_file):
        with open(config_file, "r") as stream:
            data = json.load(stream)
            if "auths" not in data:
                return False
            return strip_scheme(proxyEndpoint) in data["auths"]
    else:
        return False


def logout(proxyEndpoint: str) -> None:
    """ logout of docker """
    subprocess.check_call([
        "docker",
        "login",
        proxyEndpoint,
    ])


def run() -> None:
    temp_store = pyapikey.core.TempStore()
    if temp_store.has(KEY):
        data = temp_store.get(KEY)
        expiration = data["expiration"]
        now = datetime.datetime.now()
        if expiration > now:
            d_user = data["user"]
            d_password = data["password"]
            d_proxyEndpoint = data["proxyEndpoint"]
            handle_data(
                user=d_user,
                password=d_password,
                proxyEndpoint=d_proxyEndpoint,
            )
            sys.exit()

    with open("/dev/tty", "wt", encoding="utf-8") as f:
        print("Creating new temp key for ecr", file=f)

    client = boto3.client("ecr")
    res = client.get_authorization_token()
    authorizationData = res["authorizationData"][0]
    d_authorizationToken = authorizationData["authorizationToken"]
    d_expiresAt = authorizationData["expiresAt"]
    d_proxyEndpoint = authorizationData["proxyEndpoint"]

    # decode the password
    base64decode = base64.b64decode(d_authorizationToken).decode("ASCII")
    (d_user, d_password) = base64decode.split(":")
    handle_data(
        user=d_user,
        password=d_password,
        proxyEndpoint=d_proxyEndpoint,
    )

    # save the token
    data = {}
    data["user"] = d_user
    data["password"] = d_password
    data["proxyEndpoint"] = d_proxyEndpoint
    data["expiration"] = d_expiresAt.replace(tzinfo=None)
    temp_store.set(KEY, data)
    temp_store.save()
