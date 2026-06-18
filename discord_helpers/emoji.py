import os
import discord
import re

from caseconverter import snakecase
from discord.ext import commands


SERVER_EMOJI_CACHE: dict[str, discord.Emoji] = {}


async def load_emoji_cache(bot: commands.Bot) -> bool:
    # TODO regularly update this cache
    global SERVER_EMOJI_CACHE
    emoji_guild_id: str | None = os.getenv('EMOJI_SERVER_ID')
    if emoji_guild_id:
        await bot.fetch_guild(int(emoji_guild_id))
        SERVER_EMOJI_CACHE = {emoji.name: emoji for emoji in bot.emojis}
        return True
    else:
        return False


def get_emoji(name: str) -> str:
    global SERVER_EMOJI_CACHE
    emoji: discord.Emoji | None = SERVER_EMOJI_CACHE.get(name)
    return str(emoji if emoji else f':{name}:')


def _get_emoji_from_placeholder(placeholder: str) -> str:
    formatted_placeholder: str = snakecase(placeholder)
    match formatted_placeholder:
        case 'force':
            return get_emoji('force_charge')
        case 'lock':
            return get_emoji('target_lock')
        case _:
            return get_emoji(formatted_placeholder)


def replace_emoji_placeholders(text: str) -> str:
    return re.sub(
        r'\[([\w ]+)\]', lambda match: str(_get_emoji_from_placeholder(match.group(1))), text
    )
