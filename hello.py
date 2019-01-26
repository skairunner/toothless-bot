async def hello_world(client, message, chopped):
    channel = message.channel
    await client.send_message(channel, 'Hello World!')
