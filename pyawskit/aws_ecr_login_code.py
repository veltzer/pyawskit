import sys
import datetime

import base64
import docker
import boto3
import pyapikey

KEY = "ecr_password"


def handle_data(user: str, password: str, proxyEndpoint: str) -> None:
    """ really do something with the data """
    client = docker.Client()
    client.login(
        username=user,
        password=password,
        registry=proxyEndpoint,
    )


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
        print("Creating new tepm key for ecr", file=f)

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
