from hierkeyval import get_default
from .commandrouter import path
from .tokens import TokenMismatch, BoolProto
from toothless.utils import is_admin, has_perm, get_or_extract_id

CONFIG_STORE = get_default('toothless-config')
PERM_STORE = get_default('toothless-perms')

"""
Some utilities for configuring Toothless per-server.
"""

class ConfigOptions:
    # Parser can be any callable that takes 1 param and returns a parsed result,
    # or raises TokenMismatch if invalid input
    def __init__(self, name, desc, parser):
        self.name = name
        self.desc = desc
        self.parser = parser

    def get_desc(self):
        return self.desc.format(CONFIG_STORE.get_global(self.name))

    def parse_and_set(self, server, input):
        newconfig = self.parser(input)
        CONFIG_STORE.set_val('s', server, self.name, newconfig, hasident=True)

async def set_config(client, message, config=None, input=None):
    if config not in CONFIG_OPTIONS:
        options = '\n'.join(CONFIG_OPTIONS.keys())
        return f"'{config}' isn't a valid configuration option. Valid options are: ```{options}```"
    option = CONFIG_OPTIONS[config]

    if input is None:
        return option.desc.format(CONFIG_STORE.get_global(config))

    try:
        option.parse_and_set(message.server, input)
        return f"Set {config} to '{input}'."
    except TokenMismatch as e:
        return f"The provided value '{input}' isn't valid for {config} because: {str(e)}"

async def unset_config(client, message, config=None):
    if config not in CONFIG_OPTIONS:
        options = '\n'.join(CONFIG_OPTIONS.keys())
        return f"'{config}' isn't a valid configuration option. Valid options are: ```{options}```"
    CONFIG_STORE.del_val('s', message, config)
    return f":tada: Reset {config} to its default of {CONFIG_STORE.get_global(config)}"

async def help(client, message):
    options = '\n'.join(CONFIG_OPTIONS.keys())
    return """```asciidoc
help                 :: Shows this.
<configname>         :: Shows a description of the setting.
<configname> <value> :: Sets the server-specific setting to the value.
unset <configname>   :: Clears the server-specific setting for the config, using the global default instead.
```
""" f"Valid options: ```{options}```"

def parse_command_prefix(input):
    if len(input) > 1:
        raise TokenMismatch(f'Command must be zero or one characters, not {len(input)} :angry:')
    return input

def parse_bool(input):
    return BoolProto.verify(input)

# would be nice if there was some way to read these descriptions from 
# configwrapper.py and keep it DRY
CONFIG_OPTIONS = {
    'COMMAND_PREFIX': ConfigOptions('COMMAND_PREFIX', 'The character that prefixes any command. Defaults to "{}"', parse_command_prefix),
    'COMPLAIN_IF_COMMAND_NOT_RECOGNIZED': ConfigOptions('COMPLAIN_IF_COMMAND_NOT_RECOGNIZED', 'If true, Toothless will say "Command not recognized" if an invalid command is sent. Defaults to "{}"', parse_bool),
}


config_prefixpatterns = [
    path('', help),
    path('help', help),
    path('unset <config:str>', unset_config),
    path('<config:str>', set_config),
    path('<config:str> <input:*>', set_config),
]


"""
Admins or mods can add a roleid for a permission on a server.
"""
async def add_perm_role(client, message, permname=None, role=None):
    # Check that user has permissions to use this cmd
    if not (is_admin(message) or has_perm('mod', message)):
        return "You don't have permission to do that."
    roles = PERM_STORE.get_default('s', message.server, permname, [])
    roleid = get_or_extract_id(role)
    roles.append(roleid)
    PERM_STORE.set_val('s', message, permname, roles)
    return f"Added <@&{roleid}> to perm '{permname}'."


async def list_perm_roles(client, message, permname):
    roles = PERM_STORE.get_default('s', message.server, permname, [])
    rolestring = '\n'.join(roles)
    return f"Roles for perm '{permname}' ```\n{rolestring}```"


async def remove_perm_role(client, message, permname=None, role=None):
    # Check that user has permissions to use this cmd
    if not (is_admin(message) or has_perm('mod', message)):
        return "You don't have permission to do that."
    roles = PERM_STORE.get_default('s', message.server, permname, [])
    roleid = get_or_extract_id(role)
    if roleid in roles:
        roles.remove(roleid)
    PERM_STORE.set_val('s', message, permname, roles)
    return f"Removed <@&{roleid}> from perm '{permname}.'"

perm_prefixpatterns = [
    path('add <permname:str> <role:str>', add_perm_role),
    path('list <permname:str>', list_perm_roles),
    path('remove <permname:str> <role:str>', remove_perm_role),
]
