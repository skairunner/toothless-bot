import discord
import asyncio

from .commandrouter import match_path, PathMismatch, path, include
from .commandparser import tokenize


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
        if message.content.startswith(self.commandprefix):
            prefixlen = len(self.commandprefix)
            tokens = tokenize(message.content[prefixlen:])
            loop = asyncio.get_event_loop()
            try:
                coro = match_path(self.prefix_patterns, tokens, self, message)
                loop.create_task(coro)
            except PathMismatch:
                await self.send_message(message.channel, 'Command not recognized.')
