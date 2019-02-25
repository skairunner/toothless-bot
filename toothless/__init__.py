from .commandrouter import path, include
from .eventhandlers import on_start, on_connect
from .toothless import Toothless
from . import configwrapper as config


def run_bot():
    client = Toothless()
    client.run(config.TOKEN)
