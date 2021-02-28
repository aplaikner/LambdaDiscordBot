1. [Introduction](#introduction)
2. [Setup](#setup)
    * [Prerequisites](#prerequisites)
        * [Serverless](#serverless-python-dependencies)
        * [Server](#server-python-dependencies)
        * [Database](#mysql-database)
    * [Execution](#execution)
3. [Features & Roadmap](#features--roadmap)
    * [Current Discord commands](#current-discord-commands)
    * [HonorPoint](#honorpoints)
    * [Listener](#listener)
    * [Planned](#planned)

# Introduction

As the name suggests, this project is a Discord bot, based for the most part on serverless functions and written in
Python. Only functionalities that do not work serverless, because they need a listener, were outsourced to a server.

# Setup

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


