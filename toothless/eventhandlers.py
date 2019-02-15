ON_START = []

# Decorates a function to call on bot start
def on_start(f):
    ON_START.append(f)
    return f
