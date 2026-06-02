import os
import discord
import re

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
    return str(emoji if emoji else '❓')


def _get_emoji_from_placeholder(match: re.Match) -> str:
    return get_emoji(match.group(1))


def replace_emoji_placeholders(interaction: discord.Interaction, text: str) -> str:
    return re.sub(r':(\w+):', _get_emoji_from_placeholder, text)
