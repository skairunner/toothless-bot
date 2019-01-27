import discord
import asyncio
import re
import sqlite3
import ssl
import aiohttp
import functools

from .commandrouter import match_path


client = discord.Client()
prefix_patterns = []


def run_bot(token, prefixes):
    global prefix_patterns
    prefix_patterns = prefixes
    client.run(token)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)


@client.event
async def on_message(message):
    loop = asyncio.get_event_loop()
    coro = match_path(prefix_patterns, client, message)
    if coro:
        loop.create_task(coro)
