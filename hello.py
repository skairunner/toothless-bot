async def hello(client, message):
    await client.send_message(message.channel, 'Hi!')
