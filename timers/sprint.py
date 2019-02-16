from datetime import datetime, timezone, timedelta
import asyncio
from toothless import path
from hierkeyval import get_default

# server: { sprints: {...id : endtime...}, users: {...id: sprint }, count: 0}
TEMPORARY_STORAGE = get_default('sprints')  # Until a permanent solution found

def inc_counter(msg):
    counter = TEMPORARY_STORAGE.get_default('s', msg.server.id, 'sprint counter', 0)
    TEMPORARY_STORAGE.set_val('s', msg, 'sprint counter', counter + 1)
    return counter

# returns a tz-aware utc tz datetime obj
def get_utcnow():
    return datetime.now(timezone.utc)

def is_already_in_sprint(server, user):
    users, _ = get_server_info(server.id)
    if user not in users:
        return False
    return users[user] is not None

def get_timedelta_string(delta):
    seconds = delta.seconds
    hoursleft = seconds // 3600
    seconds %= 3600
    minutesleft = seconds // 60
    secondsleft = seconds % 60
    return f'{hoursleft:02}:{minutesleft:02}:{secondsleft:02}'

def get_sprint_timeleft(sprint):
    delta = sprint['ends'] - get_utcnow()
    return get_timedelta_string(delta)

def get_server_info(serverid):
    users = TEMPORARY_STORAGE.get_default('s', serverid, 'users', {})
    sprints = TEMPORARY_STORAGE.get_default('s', serverid, 'sprints', {})
    return users, sprints

def add_user(server, sprintid, user):
    users, sprints = get_server_info(server.id)
    if is_already_in_sprint(server, user):
        sprintid = users[user]
        timestr = get_sprint_timeleft(sprints[sprintid])
        return f"You're already in sprint {sprintid}, ending in {timestr}."
    try:
        sprint = sprints[sprintid]
    except KeyError:
        return f"Couldn't find sprint {sprintid}"
    sprint['users'].add(user)
    users[user] = sprintid
    TEMPORARY_STORAGE.flush()
    timestr = get_sprint_timeleft(sprint)
    return f'Joined sprint {sprintid} ending in {timestr}.'

def remove_user(server, user):
    users, sprints = get_server_info(server.id)
    if user in users:
        if users[user] is not None:
            sprintid = users[user]
            users[user] = None  # one way or another, will be set to none
            try:
                sprint = sprints[sprintid]
            except KeyError:
                TEMPORARY_STORAGE.flush()
                return f"You're not in a sprint."
            try:
                sprint['users'].remove(user)
            except KeyError:
                pass  # can ignore key missing
            reply = f"Left sprint <:giveup:544502573617512448>"
            if len(sprint['users']) == 0:
                del sprints[sprintid]
                reply += '\nNo users left in sprint. Ending :sob:'
            TEMPORARY_STORAGE.flush()
            return reply
    return "You're not in a sprint."


"""
Does the counting-down and finishing of the sprint.

:param client: the discord.py client
:param msg: The announcement message to be edited with times
:param sprint: the sprint object
"""
async def count_sprint(client, msg, sprint, sprintid):
    users, sprints = get_server_info(msg.server.id)
    endtime = sprint['ends']
    loop = asyncio.get_event_loop()
    while get_utcnow() < endtime:
        # Quit if sprint is over
        if sprintid not in sprints:
            return
        timestr = get_sprint_timeleft(sprint)
        loop.create_task(client.edit_message(
            msg, f'Ending in {timestr}.'))
        if endtime - get_utcnow() < timedelta(seconds=30):
            time = (endtime - get_utcnow()).seconds + 1
        else:
            time = 30
        await asyncio.sleep(time)
    # again, quit if sprint is over
    if sprintid not in sprints:
        return
    loop.create_task(client.edit_message(msg, f'Ending in 00:00:00.'))
    sprintusers = list(sprint['users'])
    for user in sprintusers:
        users[user] = None
    s = ', '.join([x.mention for x in users])
    del sprints[sprintid]
    announce = f':tada: Sprint {sprintid} is over :tada:\n{s}'
    await client.send_message(msg.channel, announce)

async def start_sprint(client, message, endtime=None):
    sprintid = inc_counter(message)
    server = message.server
    if is_already_in_sprint(server, message.author):
        return "You're already in a sprint."
    # Not already in a sprint, can create
    sprint = {'ends': endtime, 'users': set()}
    _, sprints = get_server_info(server.id)
    sprints[sprintid] = sprint
    add_user(server, sprintid, message.author)

    loop = asyncio.get_event_loop()
    await client.send_message(message.channel, f'Sprint {sprintid} started.')
    loop.create_task(client.send_message(message.channel, f'{sprintid}'))
    msg = await client.wait_for_message(content=f'{sprintid}', author=client.user)
    loop.create_task(count_sprint(client, msg, sprint, sprintid))

async def stop_sprint(client, message, sprintid=-1):
    users, sprints = get_server_info(message.server.id)
    if sprintid not in sprints:
        return f'Sprint {sprintid} is not running.'
    # Stop the sprint and report time left
    sprint = sprints[sprintid]
    timestr = get_sprint_timeleft(sprint)
    for user in sprint['users']:
        users[user] = None
    del sprints[sprintid]
    TEMPORARY_STORAGE.flush()
    return f'Sprint {sprintid} stopped with {timestr} left :pensive:'

async def join_sprint(client, message, sprintid=-1):
    return add_user(message.server, sprintid, message.author)

async def leave_sprint(client, message):
    return remove_user(message.server, message.author)

prefix_patterns = [
    path('<endtime:date*>', start_sprint),
    path('start <endtime:date*>', start_sprint),
    path('stop <sprintid:int>', stop_sprint),
    path('join <sprintid:int>', join_sprint),
    path('giveup', leave_sprint)
]
