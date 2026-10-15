# pylint: disable = missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=unused-import# HTTP requests to APIs
import json
import requests

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


def send_message(message: dict) -> int | None:
    code: int | None = None

    try:
        response: requests.Response = requests.post(url=EXPRESS_URL, json=message, timeout=15)
        response.raise_for_status()
        code = response.status_code
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error")
        print(errh.args[0])
    except requests.exceptions.ReadTimeout:
        print("TIMEOUT")
    except requests.exceptions.ConnectionError:
        print("Connection error")
    except requests.exceptions.RequestException:
        print("Request exception")

    return code


def geolocate(ip: str) -> dict | str:
    try:
        iploc: requests.Response = requests.get(url=f"{GELOCATE_URL}{ip}", timeout=10)
    except requests.exceptions.Timeout:
        return "TIMEOUT"
    iplocstr = iploc.text
    iplocdict = json.loads(iplocstr)
    return iplocdict
