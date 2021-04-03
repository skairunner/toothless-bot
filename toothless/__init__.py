from .commandrouter import path, include
from .eventhandlers import on_start, on_connect
from .toothless import Toothless
from . import configwrapper as config
import discord


def run_bot():
    intent = discord.Intents.default()
    intent.members = True
    client = Toothless(intent=intent)
    client.run(config.TOKEN)
