from toothless.eventhandlers import on_connect, on_match
import logging

EMOJI = {}

@on_connect
async def load_emoji(client):
    global EMOJI
    EMOJI = {}
    for emoji in client.emojis:
        EMOJI[emoji.name] = emoji
    logging.info(f'fakenitro - Loaded {len(EMOJI.keys())} emoji.')

@on_match(r':(?P<name>[\w_]+):(?!\d+>)')
async def add_reactions(client, message, matchobj, name=None):
    if name in EMOJI:
        emoji = EMOJI[name]
        await message.add_reaction(emoji)
