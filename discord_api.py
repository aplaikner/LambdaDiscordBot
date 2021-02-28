import discord
import requests
import time
import json

import nacl.utils
import nacl.bindings
import nacl.signing
import nacl.encoding

keys = open('keys.json')
keys_data = json.load(keys)

PRIVATE_KEY = keys_data["private_key"]

url = keys_data["endpoint_url"]
token = keys_data["bot_token"]
client = discord.Client()


def send_event(event, data):
    body = json.dumps({
        "data": {
            "name": event
        },
        "content": data
    })

    print("Sending Event: " + body)

    headers = create_signature(body)

    response = requests.post(url, json=json.loads(body), headers=headers)

    print(response.text)


def create_signature(raw_body):
    timestamp = str(int(time.time()))

    message = timestamp.encode() + raw_body.encode()
    signing_key = nacl.signing.SigningKey(bytes.fromhex(PRIVATE_KEY))

    return {
        "x-signature-timestamp": timestamp,
        "x-signature-ed25519": signing_key.sign(message).signature.hex()
    }


@client.event
async def on_ready():
    print(str(client.user) + " is connected!")
    print("On Guilds:")
    for guild in client.guilds:
        print("\t- " + str(guild.name) + " (" + str(guild.id) + ")")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    send_event("message", {
        "author": {
            "name": message.author.name,
            "id": message.author.id
        },
        "message": message.content
    })


@client.event
async def on_raw_reaction_add(reaction):
    channel = client.get_channel(reaction.channel_id)
    message = await channel.fetch_message(reaction.message_id)

    send_event("reaction_add", {
        "message_author": {
            "name": message.author.name,
            "id": message.author.id
        },
        "emoji": {
            "name": reaction.emoji.name,
            "id": reaction.emoji.id
        }
    })


@client.event
async def on_raw_reaction_remove(reaction):
    channel = client.get_channel(reaction.channel_id)
    message = await channel.fetch_message(reaction.message_id)

    send_event("reaction_remove", {
        "message_author": {
            "name": message.author.name,
            "id": message.author.id
        },
        "emoji": {
            "name": reaction.emoji.name,
            "id": reaction.emoji.id
        }
    })


if __name__ == "__main__":
    print("Connecting to Discord...")
    client.run(token)
