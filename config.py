from hierkeyval import get_default
import logging
from toothless import path, include

from utils import modstate, roles
from tymora_plugin import do_dice
from hello import hello

CONFIG_STORE = get_default('toothless-config')

# By default, discord.py is silent to stdout.
# Set so all messages are logged
logging.basicConfig(level=logging.INFO)

# All prefix commands must start with this sigil.
# It must be 0 or 1 characters
CONFIG_STORE.set_global('COMMAND_PREFIX', '?')

# More dangerous, but prevents unexpected downtime
GRACEFULLY_CATCH_EXCEPTIONS = False

event_handler_modules = [
    'fakenitro',
]

prefix_patterns = [
    path('config', include('toothless.configplugin.config_prefixpatterns')),
    path('perms', include('toothless.configplugin.perm_prefixpatterns')),
    path('role', include('utils.roles.prefix_patterns')),
    path('roles', roles.list_roles),
    path('state <statecontent:*>', modstate),
    path('r -v <verbose:bool> <roll:*>', do_dice),
    path('r <roll:*>', do_dice),
    path('hello', hello),
    path('nick', include('utils.nick_patterns')),
    path('nickname', include('utils.nick_patterns')),
    path('av', include('utils.avatar_patterns')),
    path('avatar', include('utils.avatar_patterns')),
]
