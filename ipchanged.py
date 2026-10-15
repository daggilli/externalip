# pylint: disable = missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=unused-import
# query Redis to see if IP address has changed

import redis

IPKEY = "externalip"


def ipchanged(ip: str) -> bool:
    client = redis.Redis(host="localhost", password="pw6380", port=6380, decode_responses=True)
    curip = client.get(IPKEY)
    changed = curip is None or curip != ip
    if changed:
        client.set(IPKEY, ip)

    return changed
