import discord
import re
from toothless import utils


MODSTATE_STRING = "Please acknowledge (if appropriate to do so)."


async def modstate(client, message, statecontent):
    if utils.check_admin_or_mod(message):
        await do_the_state(client, message, statecontent)
        return
    # if not right role
    author = message.author.name
    discrim = message.author.discriminator
    return f"{author}#{discrim} is not in the sudoers file. This incident will be reported."


async def do_the_state(client, message, statecontent):
    target_channel = message.channel
    maybematch = re.match(r'<#(\d+)>', statecontent)
    if maybematch:
        targetchannelid = maybematch.group(1)
        target_channel = client.get_channel(targetchannelid)
        # If message is only a channel, treat it as a msg
        if len(statecontent[maybematch.end():].strip()) == 0:
            statecontent = target_channel.mention
            target_channel = message.channel
        else:
            statecontent = statecontent[maybematch.end():]

    pings = set(re.findall(r'<@!*\d+>', statecontent))
    separator = ' - ' if pings else ''
    content = f'{" ".join(pings)}{separator}{MODSTATE_STRING}'
    embed = discord.Embed(
        title='MOD STATEMENT',
        timestamp=message.timestamp,
        type='rich',
        description=statecontent,
        color=discord.Color.dark_red()
    )
    username = message.author.nick
    if not username:
        username = message.author.name
    avatarurl = message.author.avatar_url
    embed.set_footer(text=username, icon_url=avatarurl)
    await client.send_message(target_channel, content=content, embed=embed)
