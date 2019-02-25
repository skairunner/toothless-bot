ON_START = []
ON_RECONNECT = []

"""
Decorates a function to call on bot start (only one time)
Function must not be async.
"""
def on_start(f):
    ON_START.append(f)
    return f

"""
Decorated function calls on bot (re)connect (may be multiple times)
Funciton must be async.
"""
def on_connect(f):
    ON_RECONNECT.append(f)
    return f
