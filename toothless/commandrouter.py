from importlib import import_module


class WrongBoxedType(BaseException):
    pass


class Path:
    def __init__(self, prefix, inner):
        self.prefix = prefix
        self.inner = inner
        self.pattern = 

    def is_list(self):
        return isinstance(self.inner, list)

    def __call__(self, *args, **kwargs):
        if not callable(self.inner):
            raise WrongBoxedType('The boxed type is not callable.')
        return self.inner(*args, **kwargs)

    def __iter__(self):
        try:
            return iter(self.inner)
        except TypeError:
            raise WrongBoxedType('The boxed type is not iterable')


"""
Parses prefix and either calls the provided function, or
passes rest of message to another set of paths
:param prefix: The prefix pattern to match on
:param func: The function to call to parse the command
:returns: A modified instance of `func`
"""
def path(prefix, func):
    return Path(prefix, func)


"""
includes a prefix_patterns list from the given module
:param modulename: The import name of the module
"""
def include(modulename):
    return getattr(import_module(modulename), 'prefix_patterns')


def match_path(paths, client, message, chopped):
    for p in paths:
        prefixlen = len(p.prefix)
        if chopped.startswith(p.prefix):
            matched = False
            if chopped == p.prefix:
                chopped = ''
                matched = True
            elif chopped[prefixlen] == ' ':
                chopped = chopped[prefixlen + 1:]
                matched = True
            if matched:
                # Must continue recursion until reaching a callable or None
                if p.is_list():
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
