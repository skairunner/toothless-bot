import functools

@functools.total_ordering
class Reminder:
    """
    :param user: The reminder user
    :param time: The time to remind user
    :param msg: The reminder content to embed
    :param client: The active client
    :param dest: Where to remind the user. Is a User or Channel.
    """
    def __init__(self, user, time, msg, dest):
        # The meat of the reminder
        self.user = user
        self.time = time
        self.msg = msg
        # The metadata in order to send a reply
        self.dest = dest

    def __lt__(self, other):
        return self.time < other.time

    def __eq__(self, other):
        return self.time == other.time
