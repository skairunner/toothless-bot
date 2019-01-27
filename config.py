import logging
import os
from toothless import commandrouter as cr

from state import modstate
from tymora_plugin import do_dice


# By default, discord.py is silent to stdout.
# Set so all messages are logged
logging.basicConfig(level=logging.INFO)


# The token to authenticate to Discord with
TOKEN = os.environ['BOTTOKEN']

# All prefix commands must start with this sigil.
# It must be 0 or 1 characters
COMMAND_PREFIX = '/'

prefix_patterns = [
    cr.path('state', modstate),
    cr.path('r', do_dice)
]
