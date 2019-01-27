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
    client = Toothless(prefixes, commandprefix)
    client.run(token)


class Toothless(discord.Client):
    def __init__(self, prefixes, commandprefix='/', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix_patterns = prefixes
        if len(commandprefix) > 1:
            raise ConfigError(f'Command prefixes can only be 0 or 1 characters. It is currently {len(commandprefix)}.')
        self.commandprefix = commandprefix

    async def on_ready(self):
        print(f'Logged in as {self.user.name}')

    async def on_message(self, message):
        if message.content.startswith(COMMAND_PREFIX):
            prefixlen = len(COMMAND_PREFIX)
            loop = asyncio.get_event_loop()
            coro = match_path(prefix_patterns, self, message, message.content[prefixlen:])
            if coro:
                loop.create_task(coro)
