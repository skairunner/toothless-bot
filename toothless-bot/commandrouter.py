from importlib import import_module


"""
Parses prefix and either calls the provided function, or
passes rest of message to another set of paths
:param prefix: The prefix pattern to match on
:param func: The function to call to parse the command
:returns: A modified instance of `func`
"""
def path(prefix, func):
    async def inner(client, message, chopped):
        await func(client, message, chopped)
    inner.prefix = prefix
    return inner


"""
includes a prefix_patterns list from the given module
:param modulename: The import name of the module
"""
def include(modulename):
    return getattr(import_module(modulename), 'prefix_patterns')


def match_path(paths, client, message, chopped=None):
    if chopped is None:
        chopped = message.content

    for p in paths:
        prefixlen = len(p.prefix)
        if chopped.startswith(p.prefix):
            matched = False
            if chopped == p.prefix:
                chopped = ''
                matched = True
            elif chopped[prefixlen] == ' ':
                chopped = chopped[prefixlen + 1]
                matched = True
            if matched:
                if isinstance(p, list):
                    return match_path(p, client, message, chopped)
                else:
                    return p(client, message, chopped)
    return None


"""
A command that has a prefix

:param client: the active discord.py client
:param message: discord.py Message
:param chopped: The message content with prefixes removed
"""
async def example_command(client, message, chopped):
    return
