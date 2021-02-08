import json
import requests
import wikipedia

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

PUBLIC_KEY = 'a826dbc40ee095cef951f027d10a13f0f3518424e6775ea82637cfebc2fc18f9'  # found on Discord Application -> General Information page
PING_PONG = {"type": 1}
RESPONSE_TYPES = {
    "PONG": 1,
    "ACK_NO_SOURCE": 2,
    "MESSAGE_NO_SOURCE": 3,
    "MESSAGE_WITH_SOURCE": 4,
    "ACK_WITH_SOURCE": 5
}


def verify_signature(event):
    raw_body = event.get("rawBody")
    auth_sig = event['params']['header'].get('x-signature-ed25519')
    auth_ts = event['params']['header'].get('x-signature-timestamp')

    message = auth_ts.encode() + raw_body.encode()
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    verify_key.verify(message, bytes.fromhex(auth_sig))  # raises an error if unequal


def ping_pong(body):
    if body.get("type") == 1:
        return True
    return False


def chuck_norris():
    response = requests.get("http://api.icndb.com/jokes/random")
    joke = response.json().get("value").get("joke")
    return {
        "type": 3,
        "data": {
            "tts": False,
            "content": joke,
            "embeds": [],
            "allowed_mentions": []
        }
    }


def bitcoin():
    response = requests.get("https://www.bitmex.com/api/v1/orderBook/L2?symbol=xbt&depth=1")
    return {
        "type": 3,
        "data": {
            "tts": False,
            "content": str(response.json()[0]["price"]) + " USD",
            "embeds": [],
            "allowed_mentions": []
        }
    }


def wiki(body):
    term = body.get("data").get("options")[0].get("value")
    result = wikipedia.summary(term.replace(" ", ""), sentences=1)
    return {
        "type": 3,
        "data": {
            "tts": False,
            "content": result,
            "embeds": [],
            "allowed_mentions": []
        }
    }


def lambda_handler(event, context):
    # verify the signature
    try:
        verify_signature(event)
    except Exception as e:
        raise Exception(f"[UNAUTHORIZED] Invalid request signature: {e}")

    # check if message is a ping
    body = event.get('body-json')
    if ping_pong(body):
        return PING_PONG

    if body.get("data").get("name") == "chuck":
        return chuck_norris()

    if body.get("data").get("name") == "btc":
        return bitcoin()

    if body.get("data").get("name") == "wikipedia":
        return wiki(body)
