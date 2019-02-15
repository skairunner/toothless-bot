from .commandrouter import path, include
from .eventhandlers import on_start
from .toothless import Toothless
from . import configwrapper as config

def run_bot():
    client = Toothless()
    client.run(config.TOKEN)
