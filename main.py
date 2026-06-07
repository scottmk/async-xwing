import asyncio
import datetime
import logging
import os
import sys
import time
import traceback
import typing
from logging.handlers import RotatingFileHandler

import aiohttp
import click
import discord
from discord.ext import commands
from dotenv import load_dotenv

from discord_helpers.emoji import load_emoji_cache
import game.config as config


root_logger: logging.Logger = logging.getLogger()

if root_logger.handlers:
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

discord_logger: logging.Logger = logging.getLogger('discord')
discord_http_logger: logging.Logger = logging.getLogger('discord.http')

root_logger.setLevel(logging.DEBUG)
discord_logger.setLevel(logging.DEBUG)
discord_http_logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

file_handler = RotatingFileHandler(
    filename='xwing.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    fmt='[{asctime}] [{levelname:^10}] {name}: {message}',
    datefmt='%Y-%m-%d %H:%M:%S',
    style='{',
)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

if not root_logger.handlers:
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


class AsyncXwingBot(commands.Bot):
    client: aiohttp.ClientSession
    _uptime: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)

    def __init__(self, prefix: str, ext_dir: str, *args, **kwargs) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(
            *args, **kwargs, command_prefix=commands.when_mentioned_or(prefix), intents=intents
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.NOTSET)
        self.ext_dir = ext_dir
        self.synced = False

    async def on_error(self, event_method: str, *args, **kwargs) -> None:
        self.logger.error(f'An error occurred in {event_method}.\n{traceback.format_exc()}')

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        # Ignore errors that have their own local handlers or are expected check failures
        if hasattr(ctx.command, 'on_error') or isinstance(error, commands.CommandNotFound):
            return

        # Log the unhandled command exception
        self.logger.error(f'Unhandled exception in command {ctx.command}:', exc_info=error)
        await ctx.channel.send('Something went wrong.')

    async def on_ready(self) -> None:
        emoji_loaded: bool = await load_emoji_cache(self)
        if emoji_loaded:
            self.logger.info('Emoji cache updated')
        else:
            emoji_guild_id = os.getenv('EMOJI_SERVER_ID')
            self.logger.warning(f'Emoji not found. Server ID {emoji_guild_id} not valid')
        await self.user.edit(username='AsyncXwing')
        self.logger.info(f'Logged in as {self.user} ({self.user.id})')

    async def setup_hook(self) -> None:
        self.client = aiohttp.ClientSession()
        await self._load_extensions()
        if not self.synced:
            await self.tree.sync()
            self.synced = True
            self.logger.info('Synced command tree')
        self._watcher = self.loop.create_task(self._cog_watcher())

    async def _load_extensions(self) -> None:
        if not os.path.isdir(self.ext_dir):
            self.logger.error(f'Extension directory {self.ext_dir} does not exist.')
            return
        for filename in os.listdir(self.ext_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                try:
                    await self.load_extension(f'{self.ext_dir}.{filename[:-3]}')
                    self.logger.info(f'Loaded extension {filename[:-3]}')
                except commands.ExtensionError:
                    self.logger.exception(f'Failed to load extension {filename[:-3]}')

    async def _cog_watcher(self):
        self.logger.debug('Watching for changes...')
        last = time.time()
        while True:
            extensions: set[str] = set()
            for name, module in self.extensions.items():
                if module.__file__ and os.stat(module.__file__).st_mtime > last:
                    extensions.add(name)
            for ext in extensions:
                try:
                    await self.reload_extension(ext)
                    self.logger.debug(f'Reloaded {ext}')
                except commands.ExtensionError as e:
                    self.logger.debug(f'Failed to reload {ext}: {e}')
            last = time.time()
            await asyncio.sleep(1)

    async def close(self) -> None:
        await super().close()
        await self.client.close()

    def run(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        load_dotenv()
        try:
            token: str | None = config.get_value(config.ConfigKey.TOKEN)
            super().run(str(token), log_handler=None, *args, **kwargs)
        except discord.LoginFailure, KeyboardInterrupt:
            self.logger.exception('Failure. Exiting...')
            exit()

    @property
    def user(self) -> discord.ClientUser:
        assert super().user, 'Bot is not ready yet'
        return typing.cast(discord.ClientUser, super().user)

    @property
    def uptime(self) -> datetime.timedelta:
        return datetime.datetime.now(datetime.timezone.utc) - self._uptime


@click.command()
@click.option(
    '--no-inc', is_flag=True, help="Don't increment the latest game number in the environment."
)
def main(no_inc) -> None:
    bot = AsyncXwingBot(prefix='$', ext_dir='cogs')
    asyncio.run(bot.load_extension('jishaku'))
    if not no_inc:
        config.increment_game_number()
    bot.run()


if __name__ == '__main__':
    main()
