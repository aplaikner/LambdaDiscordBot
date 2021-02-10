import discord
import requests
import time
import json

import nacl.utils
import nacl.bindings
import nacl.signing
import nacl.encoding

PRIVATE_KEY = "PRIVATE KEY"

url = "ENDPOINT"
token = "TOKEN"
client = discord.Client()


def sendEvent(event, data):
    body = json.dumps({
        "data": {
            "name": event
        },
        "content": data
    })

    print("Sending Event: " + body)

    headers = create_signature(body)

    response = requests.post(url, json=body, headers=headers)

    print(response)
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

    sendEvent("message", {
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

    sendEvent("reaction_add", {
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

    sendEvent("reaction_remove", {
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
