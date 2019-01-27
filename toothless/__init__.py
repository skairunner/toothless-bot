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
COMMAND_PREFIX = '/'


class ConfigError(BaseException):
    pass


def run_bot(token, prefixes, commandprefix='/'):
    global prefix_patterns, COMMAND_PREFIX
    prefix_patterns = prefixes
    if len(commandprefix) > 1:
        raise ConfigError(f'Command prefixes can only be 0 or 1 characters. It is currently {len(commandprefix)}.')
    COMMAND_PREFIX = commandprefix
    client.run(token)


@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')


@client.event
async def on_message(message):
    if message.content.startswith(COMMAND_PREFIX):
        prefixlen = len(COMMAND_PREFIX)
        loop = asyncio.get_event_loop()
        coro = match_path(prefix_patterns, client, message, message.content[prefixlen:])
        if coro:
            loop.create_task(coro)
