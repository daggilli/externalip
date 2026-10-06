#!/usr/bin/env python3.12
# Find external IP address and notify via Pushover if it has changed


# pylint: disable = missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=unused-import
import json
import sys
import getopt

import redis
import requests

IPKEY = "externalip"
IPLOOKUP_URL = "https://api.ipify.org?format=json"
EXPRESS_URL = "http://localhost:9238/notify"
GELOCATE_URL = "https://api.ip2location.io/?ip="


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


def geolocate(ip: str) -> dict | str:
    try:
        iploc: requests.Response = requests.get(f"{GELOCATE_URL}{ip}", timeout=10)
    except requests.exceptions.Timeout:
        return "TIMEOUT"
    iplocstr = iploc.text
    iplocdict = json.loads(iplocstr)
    return iplocdict


def main() -> None:
    verbose = False
    locate = False

    argv: list[str] = sys.argv[1:]
    opts = "vl"
    longopts = ["verbose", "locate"]

    args, _ = getopt.getopt(argv, opts, longopts)
    for curarg, _ in args:
        if curarg in ("-v", "--verbose"):
            verbose = True
        if curarg in ("-l", "--locate"):
            locate = True

    ip = externalip()
    if ip == "TIMEOUT":
        print("IP LOOKUP TIMED OUT")
        return

    ipstr = ip
    if locate:
        loc = geolocate(ip)
        if isinstance(loc, dict):
            cou = loc["country_code"]
            city = loc["city_name"]
            ipstr += f" ({cou}/{city})"

    if verbose:
        print(f"IP: {ipstr}")
        return

    if ipchanged(ip):
        notifychange(ipstr)


if __name__ == "__main__":
    main()
