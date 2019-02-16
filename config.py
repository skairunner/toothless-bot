import logging
import os
from toothless import path, include

from state import modstate
from tymora_plugin import do_dice
from hello import hello
from timers import ping, pong, sprint


# By default, discord.py is silent to stdout.
# Set so all messages are logged
logging.basicConfig(level=logging.INFO)

# All prefix commands must start with this sigil.
# It must be 0 or 1 characters
COMMAND_PREFIX = '?'

event_handler_modules = [
    'timers.sprint'
]

prefix_patterns = [
    path('state <statecontent:*>', modstate),
    path('r -v <verbose:bool> <roll:*>', do_dice),
    path('r <roll:*>', do_dice),
    path('hello', hello),
    path('ping', ping),
    path('pong', pong),
    path('sprint', include('timers.sprint')),
    path('s', include('timers.sprint')),
]
