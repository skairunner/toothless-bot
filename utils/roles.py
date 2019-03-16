"""
A series of commands that allow for role management.
"""
import asyncio
import discord
from hierkeyval import get_default
from toothless import path
from toothless import utils
from toothless.utils import check_admin_or_mod, get_or_extract_id, get_role_by_id

STORE = get_default('role-management')

"""
Bind a keyword to a role, for purposes of bot role management.
:param role: Either a role ping or id number
:param keyword: The words.
"""
async def bind_role(client, message, role=None, keyword=None):
    if not check_admin_or_mod(message):
        return "You don't have permission to do that."

    bindings = STORE.get_default('s', message.server, 'bindings', {})
    keyword = keyword.strip()
    if len(keyword) == 0:
        return "Keywords need to not be empty."
    if keyword in bindings:
        return f"The keyword '{keyword}' is already bound to <@&{bindings[keyword]}>."
    # Bind role!
    roleid = get_or_extract_id(role)
    bindings[keyword] = roleid
    STORE.set_val('s', message, 'bindings', bindings)
    return f"Bound role <@&{roleid}> to '{keyword}'."


async def unbind_role(client, message, keyword=None):
    if not check_admin_or_mod(message):
        return "You don't have permission to do that."
    keyword = keyword.strip()
    bindings = STORE.get_default('s', message.server, 'bindings', {})
    if keyword in bindings:
        roleid = bindings.pop(keyword)
        STORE.set_val('s', message, 'bindings', bindings)
        return f"Unbound <@&{roleid}> from '{keyword}'."
    return f"There's nothing bound to '{keyword}'."


async def toggle_roles(client, message, keywords=None):
    keywords = [x.strip() for x in keywords.split(',')]
    bindings = STORE.get_default('s', message.server, 'bindings', {})
    roles_added = []
    roles_removed = []
    roles_not_found = []
    for keyword in keywords:
        if keyword not in bindings:
            roles_not_found.append(keyword)
        else:
            removed = False
            if utils.user_has_role(message.author, bindings[keyword]):
                roles_removed.append(bindings[keyword])
                removed = True
            if not removed:
                roles_added.append(bindings[keyword])
    roles_added = [get_role_by_id(message.server, roleid) for roleid in roles_added]
    roles_removed = [get_role_by_id(message.server, roleid) for roleid in roles_removed]
    # Now batch add & remove
    try:
        for role in roles_added:
            await client.add_roles(message.author, role)
            await asyncio.sleep(0.1)
        for role in roles_removed:
            await client.remove_roles(message.author, role)
            await asyncio.sleep(0.1)
    except discord.Forbidden:
        return "It seems I don't have the permission to manage roles."

    roles_added_desc = ', '.join([f"@{x.name}" for x in roles_added])
    roles_removed_desc = ', '.join([f"@{x.name}" for x in roles_removed])
    roles_not_found_desc = ', '.join(roles_not_found)
    result = '```asciidoc'
    if len(roles_added_desc) > 0:
        result += f'\nRoles added :: {roles_added_desc}'
    if len(roles_removed_desc) > 0:
        result += f'\nRoles removed :: {roles_removed_desc}'
    if len(roles_not_found_desc) > 0:
        result += f'\nInvalid keywords :: {roles_not_found_desc}'
    result += '```'
    return result


async def list_roles(client, message):
    desc = """
Type `/role <keywords>` to toggle a role on yourself. You can separate keywords by comma.
"""
    embed = discord.Embed(title='ROLE LIST', description=desc)
    bindings = STORE.get_default('s', message.server, 'bindings', {})
    keyworddesc = '\n'.join([f'`{i+2}.` {x}' for i, x in enumerate(bindings.keys())])
    roledesc = '\n'.join([f'`for` <@&{x}>' for x in bindings.values()])
    if keyworddesc == '':
        return "No roles have been bound yet."
    embed.add_field(name='KEYWORDS', value=keyworddesc)
    embed.add_field(name='ROLES', value=roledesc)
    embed.color = message.author.color
    await client.send_message(message.channel, embed=embed)



async def help(client, message):
    return """```asciidoc
<keywords> :: Toggle roles on yourself. You can toggle multiple at once, just separate the keywords with commas.
bind <roleid> <keyword> :: (Mod only) Add a keyword-role binding.
unbind <keyword> :: (Mod only) Removes a keyword-role binding.
"""


prefix_patterns = [
    path('help', help),
    path('bind <role:str> <keyword:*>', bind_role),
    path('unbind <keyword:*>', bind_role),
    path('<keywords:*>', toggle_roles),
]
