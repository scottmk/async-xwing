# Hello World example taken from https://discordpy.readthedocs.io/en/stable/quickstart.html
# This example requires the 'message_content' intent.

import discord
import logging

from logging.handlers import RotatingFileHandler

logger = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = RotatingFileHandler(
    filename='hello_world.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
formatter = logging.Formatter(
    fmt='[{asctime}] [{levelname:^10}] {name}: {message}', 
    datefmt='%Y-%m-%d %H:%M:%S', 
    style='{'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    logger.info(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        logger.debug("Received valid message; responding...")
        await message.channel.send('Hello!')

client.run(
    token='<YOUR_BOT_TOKEN_HERE>',
    log_handler=None
)
