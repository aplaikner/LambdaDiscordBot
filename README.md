1. [Introduction](#introduction)
    * [Implementation](#implementation)
        * [Serverless Code](#serverless-code)
        * [Discord and Server](#discord-and-server)
        * [Backend](#backend)
2. [Setup](#setup)
    * [Important resources](#important-resources)
    * [Prerequisites](#prerequisites)
        * [Serverless](#serverless-python-dependencies)
        * [Server](#server-python-dependencies)
        * [Database](#mysql-database)
    * [Execution](#execution)
3. [Features & Roadmap](#features--roadmap)
    * [Current Discord commands](#current-discord-commands)
    * [HonorPoints](#honorpoints)
    * [Listener](#listener)
    * [Planned](#planned)
4. [Problems](#problems)
5. [Conclusion](#conclusion)

# Introduction

As the name suggests, this project is a Discord bot, based for the most part on serverless functions and written in
Python. Only functionalities that do not work serverless, because they need a listener, were outsourced to a server.

## Implementation

### Serverless Code

The python code was deployed as a Lambda function on AWS. In order for the code to be called, a Rest API 
endpoint had to be created. This endpoint points to the code, so when someone sends a post request to the url, the 
code is called with the given parameters. 

### Discord and Server

In order for Discord to send events, the endpoint had to be specified at the Discord Developer Portal. For the server,
a program had to be written that would connect to the bot, capture events, and send them to the endpoint.
<br> 
Since our lambda function should only process packets from Discord and our server, we check the signature of the packets.
This way we can be sure that the request comes from someone trustworthy.  

### Backend

The server is used to handle events like when a user sends chat messages, adds reactions or removes reactions. 
These are then sent directly to the function without further processing, so the server serves only as an interface.
<br>
The Lambda function contains all the functionality like sending a random meme or reading content from the database.

# Setup

## Important resources

- Set up Lambda as a Discord bot API: https://oozio.medium.com/serverless-discord-bot-55f95f26f743
- Deploy layers on AWS: https://docs.aws.amazon.com/lambda/latest/dg/python-package.html
- Discord documentation to set up slash
  commands: https://discord.com/developers/docs/interactions/slash-commands#registering-a-command

## Prerequisites

### Serverless python dependencies

- `requests`
- `wikipedia`
- `wolframalpha`
- `random`
- `praw`
- `pymysql`
- `json`
- `nacl`

### Server python dependencies

- `requests`
- `discord`
- `time`
- `json`
- `nacl`

### Keys file

To use services such as the Reddit, Wolfram Alpha or even the Discord API, a `keys.json` file is used to read all
relevant login information from. It has the following format, you'll have to fill out your own credentials:

```json
{
  "private_key": "DISCORD_PRIVATE_KEY",
  "public_keys": {
    "discord": "DISCORD_PUBLIC_KEY",
    "server": "DISCORD_SERVER_PUBLIC_KEY"
  },
  "reddit": {
    "client_id": "REDDIT_CLIENT_ID",
    "client_secret": "REDDIT_CLIENT_SECRET",
    "user_agent": "REDDIT_USER_AGENT"
  },
  "endpoint_url": "SERVERLESS_FUNCTION_URL",
  "bot_token": "BOT_TOKEN",
  "wolfram_id": "WOLFRAM_ID",
  "database": {
    "host": "DATABASE_HOSTNAME",
    "user": "DATABASE_USER",
    "password": "DATABASE_PASSWORD",
    "database": "discordBot"
  }
}
```

### MySQL Database

- Create a database named: `discordBot`
- Run following command to create the table for HonorPoints:

```mysql
create TABLE Users
(
    id     BIGINT UNSIGNED primary key,
    name   varchar(40),
    points BIGINT
);
```

## Execution

The serverless code was tested on AWS Lambda and can be executed there without any problems after setup. The code, which
has to be executed on the server, and which then listens for certain user inputs and forwards them to the serverless
function, has to be started on a separate server. Here it is recommended to create a service for the code and run it at
startup.

# Features & Roadmap

## Current Discord commands

- `/chuck`: Returns random Chuck Norris joke fetched from another site
- `/btc`: Returns current BTC price fetched from BitMEX
- `/dank`: Returns a random hot dank meme fetched from reddit.com/r/dankmemes
- `/scoreboard`: Returns ordered scoreboard where users and there HonorPoints are displayed
- `/wikipedia`: Returns information about the searched term
- `/wolfram`: Returns information about the searched term or equation

## HonorPoints

The HonorPoints system works in such a way that when a user's post gets an upvote emoji, they are credited with points
in a database. If he gets a downvote emoji, he loses points. Every time a user posts, there is a 5% chance that he will
get a small amount of HonorPoints. This is to increase the activity of the users.

## Listener

The listener that runs on a server is there to listen for new reactions on a users message. If a reaction is received, a
message is sent to the serverless function, that than accesses the database and performs the wished operation.

## Planned

- Add more funny discord commands 

# Problems

There occurred some problems with the libraries during the setup of the Lambda function, but otherwise it went smoothly.

# Conclusion

It has to be said that there are better uses for serverless applications than for a bot, an example being database access.
Nevertheless, the bot responded without any problems and did what it was supposed to do. However, if you want to program
a Discord bot on your own, you should still use a server because it supports more functionalities.
