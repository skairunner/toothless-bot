from datetime import datetime, timezone, timedelta
import asyncio

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
    if user in storage['users']:
        sprintid = storage['users'][user]
        timestr = get_sprint_timeleft(storage['sprints'][sprintid])
        return f"You're already in sprint {sprintid}, ending in {timestr}."
    sprint = storage['sprints'][sprintid]
    sprint['users'].add(user)
    storage['users'][user] = sprintid
    timestr = get_sprint_timeleft(sprint)
    return f'Joined sprint {sprintid} ending in {timestr}.'

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
    loop.create_task(client.edit_message(msg, f'Ending in 00:00:00.'))
    users = list(sprint['users'])
    for user in users:
        storage['users'][user] = None
    s = ', '.join([x.mention for x in users])
    announce = f':tada: Sprint {sprintid} is over :tada:\n{s}'
    await client.send_message(msg.channel, announce)

async def start_sprint(client, message, endtime=None):
    server = message.server
    storage = TEMPORARY_STORAGE.get(server, {'sprints': {}, 'users': {}})
    TEMPORARY_STORAGE[server] = storage
    sprintid = inc_counter()
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
    return 'stop_sprint()'

async def join_sprint(client, message, sprintid=-1):
    return 'join_sprint()'

async def leave_sprint(client, message, sprintid=-1):
    return 'leave_sprint()'
