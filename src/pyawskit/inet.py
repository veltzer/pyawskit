""" inet.py """

import urllib.request

import requests


def check():
    try:
        requests.get("https://google.com", timeout=5)
    except requests.ConnectionError:
        return False
    else:
        return True


def my_ip():
    return urllib.request.urlopen("https://ident.me").read().decode("utf8")
