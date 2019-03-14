import logging
import os
from toothless import path, include

from state import modstate
from tymora_plugin import do_dice
from hello import hello
from timers import ping, pong


# By default, discord.py is silent to stdout.
# Set so all messages are logged
logging.basicConfig(level=logging.INFO)

# All prefix commands must start with this sigil.
# It must be 0 or 1 characters
COMMAND_PREFIX = '?'

# More dangerous, but prevents unexpected downtime
GRACEFULLY_CATCH_EXCEPTIONS = False

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
    path('nick', include('utils.nick_patterns')),
    path('nickname', include('utils.nick_patterns')),
    path('av', include('utils.avatar_patterns')),
    path('avatar', include('utils.avatar_patterns')),
    path('sprint', include('timers.sprint.prefix_patterns')),
    path('s', include('timers.sprint.prefix_patterns')),
    path('remind me', include('timers.remind.prefix_patterns')),
    path('remindme', include('timers.remind.prefix_patterns')),
    path('remind', include('timers.remind.prefix_patterns'))
]
