from toothless.eventhandlers import on_match
from toothless import path
from toothless import utils
from hierkeyval import get_default
from datetime import datetime
import logging

STORE = get_default('pingme')

def get_pingchannel(client, server):
    id = STORE.get_default('s', server, 'pingchannel', None)
    if id is None:
        return None
    return client.get_channel(id)

def set_pingchannel(msg):
    STORE.set_val('s', msg, 'pingchannel', msg.channel.id)

def unset_pingchannel(msg):
    STORE.set_val('s', msg, 'pingchannel', None)

# Get all those who are eligible for being pinged.
# returns a set of user ids
def get_pingees(msg):
    serverpings = STORE.get_default('s', msg.server, 'serverpingees', set())
    channels = STORE.get_default('s', msg.server, 'channelpingees', {})
    if msg.channel.id in channels:
        channelpings = channels[msg.channel.id]
    else:
        channelpings = set()
    return serverpings | channelpings

# Adds the user to the server ping list
def add_to_server(msg):
    serverpings = STORE.get_default('s', msg.server, 'serverpingees', set())
    serverpings.add(msg.author.id)
    STORE.flush()

def remove_from_server(msg):
    serverpings = STORE.get_default('s', msg.server, 'serverpingees', set())
    try:
        serverpings.remove(msg.author.id)
    except KeyError:  # Don't error even if it isn't there to remove
        return
    STORE.flush()

# Add the user to the channel's ping list
def add_to_channel(msg, channelid):
    channels = STORE.get_default('s', msg.server, 'channelpingees', {})
    if channelid in channels:
        channels[channelid].add(msg.author.id)
    else:
        channels[channelid] = set([msg.author.id])
    STORE.flush()

# Removes the user from the channel's ping list.
# Doesn't error even if the user doesn't exist.
def remove_from_channel(msg, channelid):
    channels = STORE.get_default('s', msg.server, 'channelpingees', {})
    if channelid in channels:
        try:
            channels[channelid].remove(msg.author.id)
            STORE.flush()
        except KeyError:
            return

@on_match(r'')
async def do_ping(client, msg, match):
    channel = get_pingchannel(client, msg.server)
    if channel is None:
        return
    # Also don't ping if the msg is in the pingchannel
    if msg.channel.id == channel.id:
        return
    # If a message from that channel has been pinged recently, don't re-ping
    cooldowns = STORE.get_default('s', msg.server, f'cooldowns', {})
    cooldown = cooldowns.setdefault(msg.channel.id, datetime.min)
    if (datetime.now() - cooldown).total_seconds() < 10:
        return  # Don't send message if cooldown isn't sufficient
    # Otherwise update cooldown and send ping
    cooldowns[msg.channel.id] = datetime.now()
    STORE.flush()
    # Send the actual msg
    pingees = get_pingees(msg)
    pingees = [msg.server.get_member(x) for x in pingees]
    if len(pingees) != 0:
        content = f'Message in {msg.channel.mention}: ' + ''.join([x.mention for x in pingees])
        # Send the message to the designated ping channel
        await client.send_message(channel, content)

async def subscribe(client, message, channel=None):
    if channel:
        id = utils.get_or_extract_id(channel)
        add_to_channel(message, id)
        return f'Subscribed to pings from <#{id}>!'
    add_to_server(message)
    return f'Subscribed to pings from all channels.'

async def unsubscribe(client, message, channel=None):
    if channel:
        id = utils.get_or_extract_id(channel)
        remove_from_channel(message, id)
        return f'Unsubscribed from <#{id}> pings.'
    remove_from_server(message)
    return f'Unsubscribed from server pings. Any channel pings may still be active.'

async def subscription_list(client, msg):
    serverpings = STORE.get_default('s', msg.server, 'serverpingees', set())
    server_msg = '[Server]' if msg.author.id in serverpings else ''
    channelpings = STORE.get_default('s', msg.server, 'channelpingees', {})
    channels = []
    for channelid, users in channelpings.items():
        if msg.author.id in users:
            channels.append(channelid)
    channel_msg = '\n'.join([f'<#{x}>' for x in channels])
    if server_msg == '' and channel_msg == '':
        return "You aren't subscribed to any message pings on this server."
    return f"You're subscribed to:\n{server_msg}\n{channel_msg}"

# Choose a channel, per server, to send pings in.
async def designate_pingchannel(client, message):
    if utils.check_admin_or_mod(message):
        set_pingchannel(message)
        return 'Set this channel to put message pings in.'
    return 'Only a mod or admin can do that.'

async def undesignate_pingchannel(client, message):
    if utils.check_admin_or_mod(message):
        unset_pingchannel(message)
        return 'Unset ping channel.'
    return 'Only a mod or admin can do that.'

prefix_patterns = [
    path('', subscription_list),
    path('sub', subscribe),
    path('sub <channel:*>', subscribe),
    path('unsub', unsubscribe),
    path('unsub <channel:*>', unsubscribe),
    path('designate', designate_pingchannel),
    path('undesignate', undesignate_pingchannel),
]
