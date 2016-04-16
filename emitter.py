import json
from config import access_token
from urllib import quote_plus

import requests


def emit_subscription(attributes):
    url = "https://api.particle.io/v1/devices/events"
    data = {
        "name": "subscription",
        "data": "?username={0}&months={1}".format(
            attributes["username"], attributes["months"]),
        "ttl": 60,
        "access_token": access_token
    }
    resp = requests.post(url=url, data=data)
    data = json.loads(resp.content)
    return data


def emit_donation(attributes):
    url = "https://api.particle.io/v1/devices/events"
    data = {
        "name": "donation",
        "data": "?username={0}&amount={1}&currency={2}&message={3}".format(
            attributes["username"], attributes["amount"],
            attributes["currency"], quote_plus(attributes["message"])),
        "ttl": 60,
        "access_token": access_token
    }
    resp = requests.post(url=url, data=data)
    data = json.loads(resp.content)
    return data

if __name__ == "__main__":
    print emit_donation(
        {
            "username": "singlerider",
            "amount": 45,
            "currency": "USD",
            "message": "GREAT JOB!"
        }
    )
    print emit_subscription(
        {
            "username": "singlerider",
            "months": 5
        }
    )
