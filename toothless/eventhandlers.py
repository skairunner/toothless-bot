from toothless.commandrouter import curry_inner
import re


ON_START = []
ON_RECONNECT = []
ON_MATCH = []

"""
Decorates a function to call on bot start (only one time)
Function must not be async.
"""
def on_start(f):
    ON_START.append(f)
    return f

"""
Decorated function calls on bot (re)connect (may be multiple times)
Function must be async.
"""
def on_connect(f):
    ON_RECONNECT.append(f)
    return f

"""
Decorated function is called when the given regex matches, as the re.search
function. The match object is passed, as well as any named groups.
"""
def on_match(pattern):
    def _on_match(f):
        ON_MATCH.append((re.compile(pattern), curry_inner(f)))
        return f
    return _on_match
