from toothless import path
import re
import discord

from .state import modstate

async def changenick(client, message, newnick=None):
    try:
        await client.change_nickname(message.author, newnick)
    except discord.errors.Forbidden:
        return "I'm sorry, but I don't have permission to do that. :slight_smile:"
    if newnick is None:
        return f'Reset your nickname <:snug:552493084810674207>'
    return f'Changed your nickname to: {newnick}'

nick_patterns = [
    path('', changenick),
    path('<newnick:*>', changenick)
]

async def get_avatar(client, message, search=None):
    if search is None:
        user = message.author
    else:
        # A ping
        maybeid = re.match(r'<@!*(\d+)>', search)
        if maybeid is None:
            user = message.guild.get_member_named(search)
        else:
            # A search
            user = await client.fetch_user(maybeid.group(1))
        if user is None:
            # Also try matching the message as a hash
            try:
                user = await client.fetch_user(int(search))
            except Exception:
                pass
    if user is None:
        return f"Couldn't find user named '{search}'. Try typing the full name, or search by discriminator."
    if user.avatar_url == '':
        return f"{user.display_name} doesn't have an avatar!"
    embed = discord.Embed(title=f"{user.display_name}'s avatar",
                          url=str(user.avatar_url),
                          description=f"")
    embed.set_image(url=user.avatar_url)
    embed.color = user.color
    await message.channel.send(embed=embed)

avatar_patterns = [
    path('', get_avatar),
    path('<search:*>', get_avatar)
]
