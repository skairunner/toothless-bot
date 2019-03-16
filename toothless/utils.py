from hierkeyval import get_default
import re


'''
Provided a discord.py user, returns <username>#<discriminator>,
e.g. Discorder#1029.
'''
def get_full_username(user):
    return f'{user.name}#{user.discriminator:0>4}'

# Splits input into 2000ch or less blocks, attempting to preserve
# formatting and prefering to split on \n and space over mid-word
# :returns: array of strings
def smart_split(string, maxlen=2000, searchcount=50):
    out = []
    while len(string) > maxlen:
        # Find nearest \n
        found = False
        for i in range(maxlen - 1, maxlen - searchcount + 1, -1):
            if string[i] == '\n':
                out.append(string[:i])
                string = string[i+1:]
                found = True
                break
        if not found:
            # find nearest space instead
            for i in range(maxlen - 1, maxlen - searchcount + 1, -1):
                if string[i] == ' ':
                    out.append(string[:i])
                    string = string[i+1:]
                    found = True
                    break
        if not found:
            # just hard break
            out.append(string[:maxlen])
            string = string[maxlen:]
    out.append(string)
    return out

# Checks if user has a given role by comparing role ids
def user_has_role(user, roleid):
    for r in user.roles:
        if r.id == roleid:
            return True
    return False


PERM_STORE = get_default('toothless-perms')
"""
Checks that a user has at least one of the perms

:param permnames: A permission name, or a list of permission names. If it's a list, it will be OR'd.
:param msg: The Discord.py message
:returns: True if the user has at least one of the permissions provided
"""
def has_perm(permnames, msg):
    if isinstance(permnames, str):
        permnames = [permnames]

    try:
        for permname in permnames:
            roles = PERM_STORE.get_val('csg', msg, permname)
            if isinstance(roles, list):
                for roleid in roles:
                    if user_has_role(msg.author, roleid):
                        return True
            elif user_has_role(msg.author, roles):
                return True
        return False
    except KeyError:
        return False


def is_admin(msg):
    return msg.author.server_permissions.administrator


"""
Given a string, it either finds a series of numbers that could be an id,
or extracts an id from a mention (eg. <#21309123902>)
"""
def get_or_extract_id(string):
    return re.search(r'\d+', string).group(0)

def check_admin_or_mod(message):
    return is_admin(message) or has_perm('mod', message)

def get_role_by_id(server, roleid):
    for role in server.roles:
        if role.id == roleid:
            return role
    raise KeyError(f"Could not find role with roleid '{roleid}'.")
