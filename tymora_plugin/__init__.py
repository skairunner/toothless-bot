from tymora import parse


async def do_dice(client, message, roll, verbose):
    print(verbose)
    try:
        result = parse(roll)
    except Exception as e:
        if verbose:
            await client.send_message(message.channel, str(e))
        else:
            await client.send_message(message.channel, "Didn't recognize syntax.")
        return
    mention = message.author.mention
    reply = f'{mention}: `{roll}` = {result}'
    await client.send_message(message.channel, reply)
