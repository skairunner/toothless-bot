from tymora import parse


async def do_dice(client, message, roll, verbose=False):
    try:
        result = parse(roll)
    except Exception as e:
        if verbose:
            return str(e)
        else:
            return "Didn't recognize syntax."
        return
    mention = message.author.mention
    return f'{mention}: `{roll}` = {result}'
