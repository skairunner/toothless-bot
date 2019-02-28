import asyncio
import datetime
import discord
import heapq
from hierkeyval import get_default
import logging
import pytz
from toothless import on_start, on_connect, path
from toothless.tokens import DateProto
from toothless.utils import get_full_username
from .reminder_class import Reminder

from dateparser import parse

HKV = get_default('reminders')
QUEUE_LOOP = None


@on_start
def initialize():
    # if not initialized, set dicts
    HKV.get_default('g', None, 'timezones', {})
    HKV.get_default('g', None, 'reminders', [])
    HKV.get_default('g', None, 'queued', [])  # reminders that will fire soon
    HKV.get_default('g', None, 'backedoff', [])  # failed send, must resend
    logging.info('[timers] Reminders initialized')

@on_connect
async def connected(client):
    global QUEUE_LOOP
    loop = asyncio.get_event_loop()
    # Periodically check tasks
    if QUEUE_LOOP is None:
        QUEUE_LOOP = loop.create_task(queue_reminders(client))
    reminders = HKV.get_val_ident('g', None, 'backedoff')
    # Fire all messages that failed to send
    for reminder in reminders:
        loop.create_task(send_reminder(client, reminder))
    logging.info(f'[timers] Reminders - Sent {len(reminders)} backlogged reminders')
    del reminders[:]
    HKV.flush()

# Users can specify their timezone for shorthand
def get_user_tz(user):
    timezones = HKV.get_val_ident('g', None, 'timezones')
    if user in timezones:
        return timezones[user]
    return None


def add_reminder_to_hkv(reminder):
    reminders = HKV.get_val('g', None, 'reminders')
    heapq.heappush(reminders, reminder)
    HKV.flush()

async def search_tz(client, message, term=''):
    return term

async def set_tz(client, message, tzname=''):
    if tzname == '':
        try:
            tz = HKV.get_val_ident('g', None, 'timezones')[message.author]
            return f"Your current default timezone is {tz.zone}."
        except KeyError:
            return f"You don't currently have a default timezone set."
    # otherwise set
    try:
        tz = pytz.timezone(tzname)
    except pytz.exceptions.UnknownTimeZoneError:
        return f"Unknown timezone '{tzname}'. Try using /remindme timezone search to find a name. Google works too."
    tzs = HKV.get_val_ident('g', None, 'timezones')
    tzs[message.author] = tz
    HKV.flush()
    return f"Default timezone set to {tzname}!"

# Actually formats the reminder to send
def send_reminder(client, reminder):
    embed = discord.Embed(
        timestamp=reminder.time,
        type='rich',
        description=reminder.msg,
        color=discord.Color(0x6b7072)
    )
    avatarurl = reminder.user.avatar_url
    username = get_full_username(reminder.user)
    embed.set_footer(text=username, icon_url=avatarurl)
    return client.send_message(reminder.dest, f"{reminder.user.mention}: Reminder fired!", embed=embed)


"""
Waits for the reminder time, then fires it and deletes.
"""
async def fire_reminder(client, reminder):
    delta = reminder.time - datetime.datetime.now(pytz.utc)
    asyncio.sleep(delta.seconds)
    # Remove from queued reminders
    queued = HKV.get_val('g', None, 'queued')
    queued.remove(reminder)
    HKV.flush()
    try:
        await send_reminder(client, reminder)
    except discord.HTTPException as e:
        logging.warning(f"[timers] Sending reminder raised {e}, trying again in 60s...")
        asyncio.sleep(60)
        try:
            await send_reminder(client, reminder)
        except discord.HTTPException:
            logging.warning(f"[timers] Sending reminder raised {e}. Backing off.")
            backoff = HKV.get_val_ident('g', None, 'backedoff')
            backoff.append(reminder)
            HKV.flush()

async def queue_on_loop(client):
    while True:
        asyncio.sleep(60 * 60)  # 1 hour
        await queue_reminders(client)

"""
Iterates list of reminders and queues any that are slated to happen in the next hour.
"""
async def queue_reminders(client):
    reminders = HKV.get_val('g', None, 'reminders')
    queued = HKV.get_val('g', None, 'queued')
    now = datetime.datetime.now(pytz.utc)
    one_hour = datetime.timedelta(hours=1)
    loop = asyncio.get_event_loop()
    while len(reminders) > 0 and reminders[0].time < now + one_hour:
        queued.append(heapq.heappop(reminders))
        loop.create_task(fire_reminder(client, queued[-1]))
    HKV.flush()

async def add_reminder(client, message, when=None, in_=None, what=''):
    if when is None:
        # Must convert relatively
        when = DateProto.verify('in ' + in_)
        # Is not a proper date format, error.
        if when is None:
            return r'"{in_}" is not a proper date.'
    # Must add TZ if is ambiguous
    if when.tzinfo is None:
        maybe_tz = get_user_tz(message.author)
        if maybe_tz is None:
            return "It looks like you wrote a date with an ambiguous timezone. Try setting a timezone with /remindme timezone, or adding a timezone (like 'UTC') to the end of your date."
        # Just forcibly change tz, not convert it
        when = maybe_tz.localize(when)
        # change it to UTC
        when = when.astimezone(pytz.utc)
    add_reminder_to_hkv(Reminder(message.author, when, what, message.channel))
    asyncio.get_event_loop().create_task(queue_reminders(client))
    return str(when)

abs_paths = [
    path('<when:rawdate*>', add_reminder),
    path('<when:rawdate> <what:*>', add_reminder)
]

# hacky way to distinguish between rel & abs times.
# would be nice if could get a better dateparser
rel_paths = [
    path('<in_:*>', add_reminder),
    path('<in_:str> <what:*>', add_reminder)
]

# remindme...
prefix_patterns = [
    path('timezone search <term:*>', search_tz),
    path('timezone <tzname:*>', set_tz),
    path('at', abs_paths),
    path('by', abs_paths),
    path('in', rel_paths),
    path('for', rel_paths),
]
