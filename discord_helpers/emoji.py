import logging
import os
import discord
import re

from caseconverter import snakecase
from discord.ext import commands


APP_EMOJI_CACHE: dict[str, discord.Emoji] = {}
SERVER_EMOJI_CACHE: dict[str, discord.Emoji] = {}


logger: logging.Logger = logging.getLogger('async_xwing.emoji')


async def load_emoji_cache(bot: commands.Bot) -> bool:
    global APP_EMOJI_CACHE, SERVER_EMOJI_CACHE

    app_success: bool = False
    server_success: bool = False

    # Fetch and load app emoji
    try:
        app_emojis: list[discord.Emoji] = await bot.fetch_application_emojis()
        APP_EMOJI_CACHE = {emoji.name: emoji for emoji in app_emojis if emoji.name}
        app_success = True
    except discord.HTTPException:
        logger.exception('Loading app emojis failed.')
        APP_EMOJI_CACHE = {}

    # Fetch and load server emoji
    emoji_guild_id: str | None = os.getenv('EMOJI_SERVER_ID')
    if emoji_guild_id:
        try:
            # Ensure the specific target warehouse server is localized in cache
            guild: discord.Guild = await bot.fetch_guild(int(emoji_guild_id))
            SERVER_EMOJI_CACHE = {emoji.name: emoji for emoji in guild.emojis if emoji.name}
            server_success = True
        except discord.HTTPException, ValueError:
            logger.exception('Loading app emojis failed.')
            SERVER_EMOJI_CACHE = {}

    return app_success or server_success


def get_emoji(name: str) -> str:
    global APP_EMOJI_CACHE, SERVER_EMOJI_CACHE

    if name in APP_EMOJI_CACHE:
        return str(APP_EMOJI_CACHE[name])

    if name in SERVER_EMOJI_CACHE:
        return str(SERVER_EMOJI_CACHE[name])

    # Fallback so developer knows which emoji isn't loading
    return f':{name}:'


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
