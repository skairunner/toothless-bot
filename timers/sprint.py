from datetime import datetime, timezone, timedelta
import asyncio
import config

# server: { sprints: {...id : endtime...}, users: {...id: sprint }, count: 0}
TEMPORARY_STORAGE = {}  # Until a permanent solution found
SPRINT_COUNTER = 0

def inc_counter():
    global SPRINT_COUNTER
    SPRINT_COUNTER += 1
    return SPRINT_COUNTER - 1

# returns a tz-aware utc tz datetime obj
def get_utcnow():
    return datetime.now(timezone.utc)

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

def add_user(server, sprintid, user):
    storage = TEMPORARY_STORAGE[server]
    if user in storage['users'] and storage['users'][user] is not None:
        sprintid = storage['users'][user]
        timestr = get_sprint_timeleft(storage['sprints'][sprintid])
        return f"You're already in sprint {sprintid}, ending in {timestr}."
    try:
        sprint = storage['sprints'][sprintid]
    except KeyError:
        return f"Couldn't find sprint {sprintid}"
    sprint['users'].add(user)
    storage['users'][user] = sprintid
    timestr = get_sprint_timeleft(sprint)
    return f'Joined sprint {sprintid} ending in {timestr}.'

def get_storage_by_server(server):
    if server not in TEMPORARY_STORAGE:
        TEMPORARY_STORAGE[server] = {'sprints': {}, 'users': {}}
    return TEMPORARY_STORAGE[server]

def remove_user(server, user):
    storage = TEMPORARY_STORAGE[server]
    if user in storage['users']:
        if storage['users'][user] is not None:
            sprintid = storage['users'][user]
            storage['users'][user] = None
            try:
                sprint = storage['sprints'][sprintid]
            except KeyError:
                return f"You're not in a sprint."
            try:
                sprint['users'].remove(user)
            except KeyError:
                pass  # can ignore key missing
            return f"Left sprint <:giveup:308861076668416000>"
    return "You're not in a sprint."

"""
Does the counting-down and finishing of the sprint.

:param client: the discord.py client
:param msg: The announcement message to be edited with times
:param sprint: the sprint object
"""
async def count_sprint(client, msg, sprint, sprintid):
    storage = TEMPORARY_STORAGE[msg.server]
    endtime = sprint['ends']
    loop = asyncio.get_event_loop()
    while get_utcnow() < endtime:
        # Quit if sprint is over
        if sprintid not in storage['sprints']:
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
    if sprintid not in storage['sprints']:
        return
    loop.create_task(client.edit_message(msg, f'Ending in 00:00:00.'))
    users = list(sprint['users'])
    for user in users:
        storage['users'][user] = None
    s = ', '.join([x.mention for x in users])
    del storage['sprints'][sprintid]
    announce = f':tada: Sprint {sprintid} is over :tada:\n{s}'
    await client.send_message(msg.channel, announce)

async def start_sprint(client, message, endtime=None):
    sprintid = inc_counter()
    server = message.server
    storage = get_storage_by_server(server)
    # Not already in a sprint, can create
    storage['sprints'][sprintid] = {'ends': endtime, 'users': set()}
    sprint = storage['sprints'][sprintid]
    add_user(server, sprintid, message.author)
    loop = asyncio.get_event_loop()
    await client.send_message(message.channel, f'Sprint {sprintid} started.')
    loop.create_task(client.send_message(message.channel, f'{sprintid}'))
    msg = await client.wait_for_message(content=f'{sprintid}', author=client.user)
    loop.create_task(count_sprint(client, msg, sprint, sprintid))

async def stop_sprint(client, message, sprintid=-1):
    storage = get_storage_by_server(message.server)
    if sprintid not in storage['sprints']:
        return f'Sprint {sprintid} is not running.'
    # Stop the sprint and report time left
    sprint = storage['sprints'][sprintid]
    timestr = get_sprint_timeleft(sprint)
    for user in sprint['users']:
        storage['users'][user] = None
    del storage['sprints'][sprintid]
    return f'Sprint {sprintid} stopped with {timestr} left :pensive:'

async def join_sprint(client, message, sprintid=-1):
    return add_user(message.server, sprintid, message.author)

async def leave_sprint(client, message):
    return remove_user(message.server, message.author)
