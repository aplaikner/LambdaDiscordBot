import json
import requests
import wikipedia
import wolframalpha
import praw

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

PUBLIC_KEY = 'a826dbc40ee095cef951f027d10a13f0f3518424e6775ea82637cfebc2fc18f9'
PING_PONG = {"type": 1}
RESPONSE_TYPES = {
    "PONG": 1,
    "ACK_NO_SOURCE": 2,
    "MESSAGE_NO_SOURCE": 3,
    "MESSAGE_WITH_SOURCE": 4,
    "ACK_WITH_SOURCE": 5
}
REDDIT = praw.Reddit(client_id='AXF9ouKzaB9pmg',
                     client_secret='9mXfWxduhdNt6FV3o_Bu7fX0MCFQ3w',
                     user_agent='Jefferson')


def verify_signature(event):
    raw_body = event.get("rawBody")
    auth_sig = event['params']['header'].get('x-signature-ed25519')
    auth_ts = event['params']['header'].get('x-signature-timestamp')

    message = auth_ts.encode() + raw_body.encode()
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    # raises an error if unequal
    verify_key.verify(message, bytes.fromhex(auth_sig))


def ping_pong(body):
    if body.get("type") == 1:
        return True
    return False


def chuck_norris():
    response = requests.get("http://api.icndb.com/jokes/random")
    joke = response.json().get("value").get("joke")
    return {
        "type": RESPONSE_TYPES["MESSAGE_NO_SOURCE"],
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
        "type": RESPONSE_TYPES["MESSAGE_NO_SOURCE"],
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
        "type": RESPONSE_TYPES["MESSAGE_NO_SOURCE"],
        "data": {
            "tts": False,
            "content": result,
            "embeds": [],
            "allowed_mentions": []
        }
    }


def wolfram(body):
    term = body.get("data").get("options")[0].get("value")
    app_id = "WTW2H7-RU27T97RER"
    client = wolframalpha.Client(app_id)
    res = client.query(term)
    return {
        "type": RESPONSE_TYPES["MESSAGE_NO_SOURCE"],
        "data": {
            "tts": False,
            "content": next(res.results).text,
            "embeds": [],
            "allowed_mentions": []
        }
    }


def meme():
    subreddit = REDDIT.subreddit('DankMemes')

    extensions = ['png', 'jpg', 'gif']

    image = {
        "url": "",
        "title": "",
        "link": ""
    }

    url = [""]

    while url[len(url) - 1] not in extensions:
        posts = subreddit.random_rising(limit=1)
        post = None

        for p in posts:
            post = p

        url = post.url.split(".")

        image["url"] = post.url
        image["title"] = post.title
        image["link"] = "https://reddit.com" + post.permalink

    return {
        "type": RESPONSE_TYPES["MESSAGE_NO_SOURCE"],
        "data": {
            "tts": False,
            "content": image["url"],
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

    if body.get("data").get("name") == "wolfram":
        return wolfram(body)

    if body.get("data").get("name") == "meme":
        return meme()
