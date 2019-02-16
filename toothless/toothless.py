import asyncio
import discord
from importlib import import_module
import traceback

from .commandparser import tokenize
from .commandrouter import match_path, PathMismatch
from .eventhandlers import ON_START
from . import configwrapper as config


class ConfigError(BaseException):
    pass


class Toothless(discord.Client):
    def __init__(self):
        super().__init__()
        self.prefix_patterns = config.prefix_patterns
        if len(config.COMMAND_PREFIX) > 1:
            raise ConfigError(f'Command prefixes can only be 0 or 1 characters. It is currently {len(config.COMMAND_PREFIX)}.')
        self.commandprefix = config.COMMAND_PREFIX

    async def on_ready(self):
        print(f'Logged in as {self.user.name}')
        loop = asyncio.get_event_loop()
        for name in config.event_handler_modules:
            import_module(name)

        for handler in ON_START:
            loop.create_task(handler(self))

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
            except BaseException as e:
                if config.GRACEFULLY_CATCH_EXCEPTIONS:
                    traceback.print_exc()
                else:
                    raise e
