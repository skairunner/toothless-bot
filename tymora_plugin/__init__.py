from tymora import parse


async def do_dice(client, message, chopped):
    result = parse(chopped)
    mention = message.author.mention
    reply = f'{mention}: `{chopped}` = {result}'
    await client.send_message(message.channel, reply)
