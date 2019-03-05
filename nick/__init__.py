from toothless import path
import re
import discord


async def changenick(client, message, newnick=None):
    try:
        await client.change_nickname(message.author, newnick)
    except discord.errors.Forbidden:
        return "I'm sorry, but I don't have permission to do that."
    return f'Changed your nickname to: {newnick}'

prefix_patterns = [
    path('', changenick),
    path('<newnick:*>', changenick)
]
