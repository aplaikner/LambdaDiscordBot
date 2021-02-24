import requests
import wikipedia
import wolframalpha
import random
import praw
import pymysql
import json

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

keys = open('keys.json')
keys_data = json.load(keys)

PUBLIC_KEY_DISCORD = 'a826dbc40ee095cef951f027d10a13f0f3518424e6775ea82637cfebc2fc18f9'
PUBLIC_KEY_SERVER = "64fd9f9deda0129271cb035fdfe5501a79062c692436bf08bd63a99185b58ee2"

R_CLIENT_ID = keys_data['reddit']['client_id']
R_CLIENT_SECRET = keys_data['reddit']['client_secret']
R_USER_AGENT = keys_data['reddit']['user_agent']

DB_HOST = keys_data['database']['host']
DB_USER = keys_data['database']['user']
DB_PASSWORD = keys_data['database']['password']
DB_NAME = keys_data['database']['database']

WOLFRAM_ALPHA_ID = keys_data['wolfram_id']

PING_PONG = {"type": 1}

RESPONSE_TYPES = {
    "PONG": 1,
    "ACK_NO_SOURCE": 2,
    "MESSAGE_NO_SOURCE": 3,
    "MESSAGE_WITH_SOURCE": 4,
    "ACK_WITH_SOURCE": 5
}

REDDIT = praw.Reddit(client_id=R_CLIENT_ID, client_secret=R_CLIENT_SECRET, user_agent=R_USER_AGENT)


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
    app_id = WOLFRAM_ALPHA_ID
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


def on_message(body):
    content = body.get("content")

    author_name = content.get("author").get("name")
    author_id = content.get("author").get("id")
    message = content.get("message")

    if not message.startswith("/"):
        if random.random() > 0.95:
            points = 50
            add_points(author_id, author_name, points)

    return {}


def on_reaction(body, add):
    content = body.get("content")

    author_name = content.get("message_author").get("name")
    author_id = content.get("message_author").get("id")

    emoji = content.get("emoji")

    if is_upvote(emoji):
        points = 100 * (1 if add else -1)
    elif is_downvote(emoji):
        points = 100 * (-1 if add else 1)
    else:
        return {}

    add_points(author_id, author_name, points)

    return {}


def is_upvote(emoji):
    emoji_name = emoji.get("name")
    emoji_id = emoji.get("id")

    return emoji_id == "755112940792840272" and emoji_name == "upvote"


def is_downvote(emoji):
    emoji_name = emoji.get("name")
    emoji_id = emoji.get("id")

    return emoji_id == "755112958916558959" and emoji_name == "downvote"


def add_points(id, name, points):
    if exists_user(id):
        old_points = get_points_from_user(id)
        new_points = old_points + points
        update_user(id, new_points)
    else:
        create_user(id, name, points)


def update_user(id, points):
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, connect_timeout=5)

    with conn:
        with conn.cursor() as cur:
            query = "UPDATE Users Set points = %s where id = %s"
            data = (points, id)
            cur.execute(query, data)

        conn.commit()


def create_user(id, name, points):
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, connect_timeout=5)

    with conn:
        with conn.cursor() as cur:
            query = "INSERT INTO Users(id, name, points) VALUES (%s, %s, %s)"
            data = (id, name, points)
            cur.execute(query, data)

        conn.commit()


def exists_user(id):
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, connect_timeout=5)

    with conn:
        with conn.cursor() as cur:
            query = "SELECT EXISTS(SELECT * FROM Users WHERE id = %s)"
            data = (id,)
            cur.execute(query, data)
            result = cur.fetchone()

    return result[0] == 1


def get_points_from_user(id):
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, connect_timeout=5)

    with conn:
        with conn.cursor() as cur:
            sql = "SELECT points FROM Users WHERE id=%s"
            cur.execute(sql, (id,))
            result = cur.fetchone()

    return result[0]


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

    if body.get("data").get("name") == "message":
        return on_message(body)

    if body.get("data").get("name") == "reaction_add":
        return on_reaction(body, True)

    if body.get("data").get("name") == "reaction_remove":
        return on_reaction(body, False)
