import logging
import random
from enum import StrEnum

import discord
from discord import app_commands
from discord.ext import commands

from discord_helpers.emoji import get_emoji


class AttackDie(StrEnum):
    Hit = 'hit'
    Crit = 'crit'
    Focus = 'focus'
    Blank = 'blank'


ATTACK_DIE_FACES = [
    AttackDie.Hit,
    AttackDie.Hit,
    AttackDie.Hit,
    AttackDie.Crit,
    AttackDie.Focus,
    AttackDie.Focus,
    AttackDie.Blank,
    AttackDie.Blank,
]


class DefenseDie(StrEnum):
    Evade = 'evade'
    Focus = 'focus'
    Blank = 'blank'


DEFENSE_DIE_FACES = [
    DefenseDie.Evade,
    DefenseDie.Evade,
    DefenseDie.Evade,
    DefenseDie.Focus,
    DefenseDie.Focus,
    DefenseDie.Blank,
    DefenseDie.Blank,
    DefenseDie.Blank,
]


class EngagementCog(
    commands.GroupCog, name='engage', description='A cog for handling all Engagement phase commands'
):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

    @app_commands.command(name='roll_attack', description='Make an attack roll')
    async def roll_attack(self, interaction: discord.Interaction, num_dice: int) -> None:
        rolls: list[AttackDie] = [random.choice(ATTACK_DIE_FACES) for _ in range(0, num_dice)]

        result_str: str = ''.join([get_emoji(f'die_atk_{roll}') for roll in rolls])
        await interaction.response.send_message(result_str)

    @app_commands.command(name='roll_defense', description='Make a defense')
    async def roll_defense(self, interaction: discord.Interaction, num_dice: int) -> None:
        rolls: list[DefenseDie] = [random.choice(DEFENSE_DIE_FACES) for _ in range(0, num_dice)]
        result_str: str = ''.join([get_emoji(f'die_def_{roll}') for roll in rolls])
        await interaction.response.send_message(result_str)


async def setup(bot):
    await bot.add_cog(EngagementCog(bot))


async def teardown(bot):
    bot.logger.info('EngagementCog extension unloaded!')
