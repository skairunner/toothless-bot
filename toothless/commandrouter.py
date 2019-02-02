from importlib import import_module
import re
from .commandparser import parse_pathstr
from .tokens import TokenMismatch, RemainderProto, StaticProto
from .utils import smart_split
from enum import Enum
from pprint import pprint


# Raised if attempting to () on a Path's inner list, or
# if attempting to [] on a Path's inner function.
class WrongBoxedType(BaseException):
    pass


# Raised if the tokens don't fit the current path
class PathMismatch(BaseException):
    pass


# Raised if the tokens don't match the path,but it may be recoverable
# eg. by recursing more
class ContinueMatching(BaseException):
    pass


# A path may only have static args if it contains a list
class InvalidPath(BaseException):
    pass


class PathWrappedType(Enum):
    CALLABLE = 1,
    LIST = 2


def curry_inner(inner):
    async def newinner(*args, **kwargs):
        msgs = await inner(*args, **kwargs)
        client = args[0]
        message = args[1]
        if isinstance(msgs, str):
            msgs = smart_split(msgs)
        if isinstance(msgs, list):
            for msg in msgs:
                await client.send_message(
                    message.channel,
                    msg
                )
    return newinner


class Path:
    def __init__(self, pathstr, inner):
        self.pathstr = pathstr
        self.prototokens = parse_pathstr(pathstr)
        if callable(inner):
            self.wrapped = PathWrappedType.CALLABLE
            self.inner = curry_inner(inner)
        elif isinstance(inner, list):
            self.wrapped = PathWrappedType.LIST
            self.inner = inner
        else:
            raise WrongBoxedType(
                f'Inner object of Path must be type list or a callable'
                f'. It is actually type {type(inner)}')

    def __str__(self):
        return f'Path<{self.pathstr}>'

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
:param pathstr: The path pattern to match on
:param func: The function to call to parse the command
:returns: A modified instance of `func`
"""
def path(pathstr, func):
    return Path(pathstr, func)


"""
includes a prefix_patterns list from the given module
:param modulename: The import name of the module
"""
def include(modulename):
    try:
        return getattr(import_module(modulename + '.patterns'), 'prefix_patterns')
    except ImportError:
        try:
            return getattr(import_module(modulename), 'prefix_patterns')
        except ImportError:
            raise ImportError(
                'Could not find prefix_patterns specified by import'
                f'"{modulename}" in either patterns.py or the module main.'
            )

"""
Helper function used by match_tokens. Matches as many tokens as possible
until reaching the end of either array, then returns the matched results
+ how many were matched, respectively.

Raises PathMismatch if an incorrect token was matched.

:param prototokens: A list of prototokens to match against.
:param tokens: A list of tokens to match vs the prototokens.
:returns: (result list, number of tokens matched)
:raises: PathMismatch if a token doesn't match the prototoken
"""
def match_prototokens_to_tokens(prototokens, tokens):
    pathlen = len(prototokens)
    tokenslen = len(tokens)
    results = []
    if len(prototokens) == 0:
        return ([], (0, 0))
    # Remainder tokens glob everything left
    if isinstance(prototokens[-1], RemainderProto):
        # If there's too many prototokens, can't match
        if tokenslen < pathlen - 1:
            raise PathMismatch(f'Too many tokens vs prototokens ({tokenslen}, {pathlen})')
        # all tokens before Remainder must match
        for i in range(pathlen - 1):
            arg = prototokens[i]
            token = tokens[i]
            try:
                results.append(arg.verify(token))
            except TokenMismatch:
                if isinstance(token, StaticProto):
                    raise PathMismatch(
                        f'The staticstr {token.staticstr}'
                        f'could not be matched to token "{token}"')
                raise PathMismatch(
                    f'The arg "{arg.name}" could not be matched'
                    f'to token "{token}"')
        # All tokens have been matched.
        # Join remaining tokens into one string and return
        results.append(prototokens[-1].verify(' '.join(tokens[pathlen - 1:])))
        return (results, (pathlen, tokenslen))
    # If there's more protos than tokens, cannot match.
    if pathlen > tokenslen:
        raise PathMismatch(f'Not enough tokens. ({pathlen} > {tokenslen})')
    # Otherwise, if tokens >= paths, try matching
    for i in range(pathlen):
        proto = prototokens[i]
        token = tokens[i]
        try:
            results.append(proto.verify(token))
        except TokenMismatch:
            if isinstance(proto, StaticProto):
                raise PathMismatch(
                    f'The staticstr {proto.staticstr}'
                    f'could not be matched to token "{token}"')
            raise PathMismatch(
                f'The arg "{proto.name}" could not be matched'
                f'to token "{token}"')
    # Return the matches
    return (results, (pathlen, pathlen))


"""
Attempt to match the path's prototokens against the tokens provided.
:param path: a Path object to match the tokens against
:param tokens: A list of tokens (=strings) to match.
:raises: PathMismatch if the tokens don't match the path. ContinueMatching
if the path might be matchable by a subpath
"""
def match_tokens(path, tokens):
    results, matchcount = match_prototokens_to_tokens(path.prototokens, tokens)
    # If both path and tokens 0, could possibly do more
    if matchcount == (0, 0):
        if path.wrapped == PathWrappedType.LIST:
            raise ContinueMatching()
    if matchcount[1] != len(tokens):
        # Not all tokens were matched.
        # If Path is not a List, error.
        if path.wrapped == PathWrappedType.LIST:
            raise ContinueMatching()
        raise PathMismatch('Not all tokens were matched.')
    # Other possibilities (1) Globbed (2) Matched normally
    return results


"""
Will try to match. If all input tokens are consumed and the content of the Path
is a list, attempt to match the remaining tokens to those paths. If it fails,
return to attempting to match against the existing path list.

:param paths: List of Path to match against
:param tokens: Input list of tokens
:param client: The active discord client
:param message: The discord.py message
:param timeout: The time after which to send a timeout message and cancel the coroutine.
"""
def match_path(paths, tokens, client, message, timeout=5):
    for p in paths:
        try:
            results = match_tokens(p, tokens)
            # build a name->match dict
            args = {}
            for i, result in enumerate(results):
                if not isinstance(p.prototokens[i], StaticProto):
                    args[p.prototokens[i].name] = result
            return p(client, message, **args)
        except PathMismatch:
            # This path doesn't match. Go to next.
            continue
        except ContinueMatching:
            return match_path(p.inner, tokens[len(p.prototokens):], client, message)
    raise PathMismatch('Could not find a path that matches the tokens.')

"""
A command that uses route matching.

If a list is returned by the function, it will be sent as-is via Discord.py.
When a message is too long, a 'reply too long' message will be sent instead.

If a string is returned by the function, Toothless will attempt to break it up
into 2000-ch chunks, respecting tag boundaries and preferring newlines.
Edit: Discord's markdown implementation is very inconsistent, so formatting
cannot be preserved over messages.

Otherwise, nothing is output.

:param client: the active discord.py client
:param message: discord.py Message
:returns: A list of strings, a string, or None.
"""
async def example_command(client, message, **kwargs):
    return
