import colorlog
import logging
import os
import sys
import discord
from discord.ext import commands
from dotenv import load_dotenv

from game import config


SCRIPT_DIR: str = os.path.dirname(os.path.abspath(__file__))
EMOJI_FOLDER: str = os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'assets', 'emoji'))


logger: logging.Logger = logging.getLogger('async_xwing.setup')
logger.setLevel(logging.INFO)
if logger.hasHandlers():
    logger.handlers.clear()

console_handler: logging.StreamHandler = logging.StreamHandler(sys.stdout)
color_formatter = colorlog.ColoredFormatter(
    fmt='%(asctime_log_color)s%(asctime)s%(reset)s %(log_color)s%(levelname)-8s%(reset)s %(name_log_color)s%(name)s%(reset)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'INFO': 'blue',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={
        'asctime': {
            'DEBUG': 'bold_black',
            'INFO': 'bold_black',
            'WARNING': 'bold_black',
            'ERROR': 'bold_black',
            'CRITICAL': 'bold_black',
        },
        'name': {
            'DEBUG': 'purple',
            'INFO': 'purple',
            'WARNING': 'purple',
            'ERROR': 'purple',
            'CRITICAL': 'purple',
        },
    },
)
console_handler.setFormatter(color_formatter)
logger.addHandler(console_handler)
logger.propagate = False


bot = commands.Bot(command_prefix='$', intents=discord.Intents.none())


@bot.event
async def on_ready() -> None:
    logger.info(f'Connected as {bot.user}. Syncing App Emojis...')

    # Check what emojis this specific test bot already has
    existing_emojis: list[discord.Emoji] = await bot.fetch_application_emojis()
    existing_names: set[str] = {emoji.name for emoji in existing_emojis if emoji.name}

    # Scan local directory for missing assets
    for root, _, filenames in os.walk(EMOJI_FOLDER):
        for filename in filenames:
            if not filename.endswith(('.png', '.jpg', '.gif')):
                continue

            emoji_name: str = os.path.splitext(filename)[0]

            # Skip if the developer's test bot portal already has this name uploaded
            if emoji_name in existing_names:
                logger.info(f"'{emoji_name}' is already up to date.")
                continue

            # Read the image payload and push it directly to developer's App Portal
            file_path: str = os.path.join(root, filename)
            with open(file_path, 'rb') as image_file:
                image_bytes: bytes = image_file.read()
                try:
                    # This directly modifies the developer's bot configuration via API
                    new_emoji = await bot.create_application_emoji(
                        name=emoji_name, image=image_bytes
                    )
                    logger.info(f'✅ Successfully uploaded: {new_emoji.name}')
                except discord.HTTPException:
                    logger.exception(f'❌ Failed uploading {emoji_name}')

    logger.info('App emoji sync complete!')
    await bot.close()


load_dotenv()
try:
    token: str | None = config.get_value(config.ConfigKey.TOKEN)
    bot.run(token)
except discord.LoginFailure, KeyboardInterrupt:
    logger.exception('Failure. Exiting...')
    exit()
