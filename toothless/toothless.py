import asyncio
import discord
from hierkeyval import get_default
from importlib import import_module
import traceback

from .commandparser import tokenize
from .commandrouter import match_path, PathMismatch
from .eventhandlers import ON_START, ON_RECONNECT
from . import configwrapper as config


class ConfigError(BaseException):
    pass


CONFIG_STORE = get_default('toothless-config')
class Toothless(discord.Client):
    def __init__(self):
        super().__init__()
        self.prefix_patterns = config.prefix_patterns
        COMMAND_PREFIX = CONFIG_STORE.get_global('COMMAND_PREFIX')
        if len(COMMAND_PREFIX) > 1:
            raise ConfigError(f'Command prefixes can only be 0 or 1 characters. It is currently {len(COMMAND_PREFIX)}.')

        for handler in ON_START:
            handler()

    async def on_ready(self):
        print(f'Logged in as {self.user.name}')
        loop = asyncio.get_event_loop()
        for name in config.event_handler_modules:
            import_module(name)

        for handler in ON_RECONNECT:
            loop.create_task(handler(self))

    async def on_message(self, message):
        # respect per-server settings
        COMMAND_PREFIX = CONFIG_STORE.get_val('sg', message, 'COMMAND_PREFIX')
        COMPLAIN = CONFIG_STORE.get_val('sg', message, 'COMPLAIN_IF_COMMAND_NOT_RECOGNIZED')
        if message.content.startswith(COMMAND_PREFIX):
            prefixlen = len(COMMAND_PREFIX)
            tokens = tokenize(message.content[prefixlen:])
            loop = asyncio.get_event_loop()
            try:
                coro = match_path(self.prefix_patterns, tokens, self, message)
                loop.create_task(coro)
            except PathMismatch:
                if COMPLAIN:
                    await self.send_message(message.channel, 'Command not recognized.')
            except BaseException as e:
                if config.GRACEFULLY_CATCH_EXCEPTIONS:
                    traceback.print_exc()
                else:
                    raise e
