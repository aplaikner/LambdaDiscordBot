import json
import requests
import wikipedia
import wolframalpha
import random
import praw

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

PUBLIC_KEY_DISCORD = 'a826dbc40ee095cef951f027d10a13f0f3518424e6775ea82637cfebc2fc18f9'
PUBLIC_KEY_SERVER = "64fd9f9deda0129271cb035fdfe5501a79062c692436bf08bd63a99185b58ee2"

PING_PONG = {"type": 1}

RESPONSE_TYPES = {
    "PONG": 1,
    "ACK_NO_SOURCE": 2,
    "MESSAGE_NO_SOURCE": 3,
    "MESSAGE_WITH_SOURCE": 4,
    "ACK_WITH_SOURCE": 5
}
REDDIT = praw.Reddit(client_id='CLIENT_ID',
                     client_secret='CLIENT_SECRET',
                     user_agent='AGENT_NAME')


def verify_signature(event):
    raw_body = event.get("rawBody")
    auth_sig = event['params']['header'].get('x-signature-ed25519')
    auth_ts = event['params']['header'].get('x-signature-timestamp')

    message = auth_ts.encode() + raw_body.encode()
    verify_key_discord = VerifyKey(bytes.fromhex(PUBLIC_KEY_DISCORD))
    verify_key_server = VerifyKey(bytes.fromhex(PUBLIC_KEY_SERVER))
    # raises an error if unequal
    try:
        verify_key_discord.verify(message, bytes.fromhex(auth_sig))
    except BadSignatureError:
        verify_key_server.verify(message, bytes.fromhex(auth_sig))


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
    posts = subreddit.hot(limit=100)

    extensions = ['png', 'jpg', 'gif']
    images = []

    for post in posts:
        url = post.url.split(".")

        if url[len(url) - 1] in extensions:
            image = {
                "url": post.url,
                "title": post.title,
                "link": "https://reddit.com" + post.permalink
            }

            images.append(image)

    rand = random.randint(0, len(images) - 1)
    image = images[rand]

    return {
        "type": RESPONSE_TYPES["MESSAGE_NO_SOURCE"],
        "data": {
            "tts": False,
            "content": "",
            "embeds": [{
                "color": 0x0099ff,
                "title": image["title"],
                "url": image["link"],
                "image": {
                    "url": image["url"],
                }
            }],
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

    if body.get("data").get("name") == "dank":
        return meme()
