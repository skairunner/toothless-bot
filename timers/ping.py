from uuid import uuid4
import asyncio

async def get_ping(client, message):
    loop = asyncio.get_event_loop()
    pingmsg = f'Pinging... (id: {uuid4()})'
    loop.create_task(client.send_message(message.channel, pingmsg))
    response = await client.wait_for_message(
        content=pingmsg)
    latency = response.timestamp - message.timestamp
    return (latency, response)

async def ping(client, message):
    latency, response = await get_ping(client, message)
    ping = latency.seconds * 1000 + latency.microseconds / 1000
    await client.edit_message(response, f'Ping: {ping}ms')

async def pong(client, message):
    diff, response = await get_ping(client, message)
    days = diff.days
    hours = diff.seconds // 3600
    minutes = diff.seconds // 60
    ms = diff.microseconds // 1000
    us = diff.microseconds % 1000
    await client.edit_message(
            response, f':ping_pong:: {days} :calendar: {hours} :hourglass:'
            f'{minutes} :horse_racing: {diff.seconds} :stopwatch: {ms}ms {us}μs')
