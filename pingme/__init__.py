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

# Returns the elapsed # of seconds since user's last post
def get_last_post_time(userid, server):
    times = STORE.get_default('s', server, 'lastposted', {})
    if userid in times:
        return (datetime.now() - times[userid]).total_seconds()
    return float('Inf')

# Update the time of user's last post
def set_last_post_time(user, server):
    times = STORE.get_default('s', server, 'lastposted', {})
    times[user.id] = datetime.now()
    STORE.flush()


"""
For every message, ping everyone who has signed up for that ping channel.
- Only ping for a channel every X seconds (default to 20s)
- Only ping a user if they haven't posted in that server for the last Y seconds (default 90s)
"""
@on_match(r'')
async def do_ping(client, msg, match):
    channel = get_pingchannel(client, msg.server)
    if channel is None:
        return
    # Update last posted timer regardless of whether a ping will be sent
    set_last_post_time(msg.author, msg.server)
    # Also don't ping if the msg is in the pingchannel
    if msg.channel.id == channel.id:
        return
    # If a message from that channel has been pinged recently, don't re-ping
    cooldowns = STORE.get_default('s', msg.server, f'cooldowns', {})
    cooldown = cooldowns.setdefault(msg.channel.id, datetime.min)
    if (datetime.now() - cooldown).total_seconds() < 20:
        return  # Don't send message if cooldown isn't sufficient
    # Otherwise update cooldown and send ping
    cooldowns[msg.channel.id] = datetime.now()
    STORE.flush()
    # Send the actual msg
    potential_pingees = get_pingees(msg)
    # Filter out pingee if same as message sent
    if msg.author.id in potential_pingees:
        potential_pingees.remove(msg.author.id)
    pingees = []
    for pingee in potential_pingees:
        t = get_last_post_time(pingee, msg.server)
        if t > 90:
            pingees.append(pingee)
    pingees = [msg.server.get_member(x) for x in pingees]
    if len(pingees) != 0:
        content = f'New message in {msg.channel.mention}: ' + ''.join([x.mention for x in pingees])
        # Send the message to the designated ping channel
        await client.send_message(channel, content)

async def subscribe(client, message, channel=None):
    if channel:
        channels = channel.split(' ')
        ids = [utils.get_or_extract_id(x) for x in channels]
        for id in ids:
            add_to_channel(message, id)
        submsg = ', '.join([f'<#{x}>' for x in ids])
        return f'Subscribed to pings from {submsg}!'
    add_to_server(message)
    return f'Subscribed to pings from all channels.'

async def unsubscribe(client, message, channel=None):
    if channel:
        channels = channel.split(' ')
        ids = [utils.get_or_extract_id(x) for x in channels]
        for id in ids:
            remove_from_channel(message, id)
        unsubmsg = ', '.join([f'<#{x}>' for x in ids])
        return f'Unsubscribed from {unsubmsg}.'
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

async def help(client, message):
    return """```asciidoc
= Pingme
Ping you when new messages have been posted!

(blank) :: List if you are subscribed to the server or any channels.
help :: Show this message.
sub :: Subscribe to entire server.
sub channel1[ channel2...] :: Subscribe to a channel or channels. Separate multiple channels with a space.
unsub :: Unsubscribe from the entire server.
unsub channel1[ channel2...] :: Unsubscribe from a channel or channels.
    NOTE: Even if you turn off channel subs, you can still be pinged by the server sub, and vice versa.
designate :: (mod only) Designate a channel to put message pings.
undesignate :: (mod only) Unset a channel for message pings.
```"""


prefix_patterns = [
    path('', subscription_list),
    path('sub', subscribe),
    path('sub <channel:*>', subscribe),
    path('unsub', unsubscribe),
    path('unsub <channel:*>', unsubscribe),
    path('help', help),
    path('designate', designate_pingchannel),
    path('undesignate', undesignate_pingchannel),
]
