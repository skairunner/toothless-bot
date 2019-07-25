import discord
from tymora import parse
from toothless import path
from random import choices
from enum import Enum


async def do_dice(client, message, roll, verbose=False):
    try:
        result = parse(roll)
    except Exception as e:
        if verbose:
            return str(e)
        else:
            return "Didn't recognize syntax."
        return
    mention = message.author.mention
    return f'{mention}: `{roll}` = {result}'


class Dice(Enum):
    PLUS = '+'
    BLANK = ' '
    MINUS = '-'

FATE = {
    Dice.MINUS: -1,
    Dice.BLANK: 0,
    Dice.PLUS: 1
}

FATE_EMOJI = {
    Dice.PLUS: '<:1p:603971809007632394>',
    Dice.BLANK: '<:1n:603971809020346380>',
    Dice.MINUS: '<:1m:603971808852705296>',
}

VOLATILE_FATE = {
    Dice.MINUS: -2,
    Dice.BLANK: 0,
    Dice.PLUS: 2
}

VOLATILE_EMOJI = {
    Dice.MINUS: '<:2m:603971808991117312>',
    Dice.BLANK: '<:2n:603971808747847682>',
    Dice.PLUS: '<:2p:603971808747585546>'
}

FATE_ARRAY = [Dice.PLUS, Dice.MINUS, Dice.BLANK]

async def do_fate(client, message, mod=0, comment='', *, volatile=False):
    dice = 2 if volatile else 4
    results = choices(FATE_ARRAY, k=dice)

    # Decide how to display it.
    sign = '+' if mod > 0 else '-'
    modtext = '0' if mod == 0 else f'{sign}{abs(mod)}'
    dicelambda = (lambda x: VOLATILE_EMOJI[x]) if volatile else (lambda x: FATE_EMOJI[x])
    dicetext = ''.join([x for x in map(dicelambda, results)])

    # Calculate the numerical total
    total = sum(map(lambda x: VOLATILE_FATE[x] if volatile else FATE[x], results))

    ping = message.author.mention

    title = 'Volatile roll' if volatile else 'Fate roll'
    if comment != '':
        title = comment + (' (volatile)' if volatile else '')
    embed = discord.Embed(title=title, color=message.author.color, description=dicetext)
    embed.add_field(name='Mod', value=f'{mod:+}')
    embed.add_field(name='Result', value=f'**{total + mod:}**')

    await client.send_message(message.channel, ping, embed=embed)

async def do_volatile(client, message, mod=0, comment=None):
    return await do_fate(client, message, mod, comment, volatile=True)

fate_patterns = [
    path('<mod:int> <comment:*>', do_fate),
    path('<comment:*>', do_fate),
]

volatile_patterns = [
    path('<mod:int> <comment:*>', do_volatile),
    path('<comment:*>', do_volatile),
]
