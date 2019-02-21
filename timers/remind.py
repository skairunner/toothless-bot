import pytz
from toothless import on_start, path
from toothless.tokens import DateProto
from hierkeyval import get_default

HKV = get_default('reminders')

@on_start
async def initialize(client):
    # if not initialized, set dicts
    HKV.get_default('g', None, 'timezones', {})
    HKV.get_default('g', None, 'reminders', [])
    print('Reminder initialized')

# Users can specify their timezone for shorthand
def get_user_tz(user):
    timezones = HKV.get_val_ident('g', None, 'timezones')
    if user in timezones:
        return timezones[user]
    return None

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
    return f"Default timezone set to {tzname}!"

"""
Iterates list of reminders and queues any that are slated to happen in the next hour.
"""
async def queue_reminders():
    pass

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
        when = when.replace(tzinfo=maybe_tz)
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
