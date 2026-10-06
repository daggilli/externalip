#!/usr/bin/env python3.12
# Find external IP address and notify via Pushover ifi it has changed


# pylint: disable = missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=unused-import
import json
import redis
import getopt
import sys

import requests

IPKEY = "externalip"
IPLOOKUP_URL = "https://api.ipify.org?format=json"
EXPRESS_URL = "http://localhost:9238/notify"


def externalip() -> str:
    try:
        extip: requests.Response = requests.get(IPLOOKUP_URL, timeout=10)
    except requests.exceptions.Timeout:
        return "TIMEOUT"
    ipstr = extip.text
    ipdict = json.loads(ipstr)
    return ipdict["ip"]


def ipchanged(ip: str) -> bool:
    client = redis.Redis(host="localhost", password="pw6380", port=6380, decode_responses=True)
    curip = client.get(IPKEY)
    changed = curip is None or curip != ip
    if changed:
        client.set(IPKEY, ip)

    return changed


def create_message(ip: str) -> dict:
    payload = {
        "title": "EXTERNAL IP CHANGED",
        "message": f"NEW IP ADDRESS {ip}",
    }

    return payload


def send_message(message: dict) -> int:
    response: requests.Response = requests.post(url=EXPRESS_URL, json=message, timeout=15)
    return response.status_code


def notifychange(ip: str) -> None:
    message = create_message(ip)
    send_message(message)


def main() -> None:
    verbose = False

    argv: list[str] = sys.argv[1:]
    opts = "v"
    longopts = "verbose"

    args, vals = getopt.getopt(argv, opts, longopts)
    for curarg, curval in args:
        if curarg in ("-v", "--verbose"):
            verbose = True

    ip = externalip()
    if verbose:
        print(f"IP: {ip}")
        return
    else:
        if ip != "TIMEOUT" and ipchanged(ip):
            notifychange(ip)


if __name__ == "__main__":
    main()
