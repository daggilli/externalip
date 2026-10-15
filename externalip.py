#!/usr/bin/env python3.12
# Find external IP address and notify via Pushover if it has changed


# pylint: disable = missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=unused-import
import sys
import getopt

from ipchanged import ipchanged
from apirequests import externalip, send_message, geolocate


def create_message(ip: str) -> dict:
    payload = {
        "title": "EXTERNAL IP CHANGED",
        "message": f"NEW IP ADDRESS {ip}",
    }

    return payload


def notifychange(ip: str) -> None:
    message = create_message(ip)
    send_message(message)


def main() -> None:
    verbose = False
    locate = False
    force = False

    argv: list[str] = sys.argv[1:]
    opts = "vlf"
    longopts = ["verbose", "locate", "force"]

    args, _ = getopt.getopt(argv, opts, longopts)
    for curarg, _ in args:
        if curarg in ("-v", "--verbose"):
            verbose = True
        if curarg in ("-l", "--locate"):
            locate = True
        if curarg in ("-f", "--force"):
            force = True

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
        if not force:
            return

    if ipchanged(ip) or force:
        notifychange(ipstr)


if __name__ == "__main__":
    main()
