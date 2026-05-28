import random
from enum import StrEnum
from typing import Sequence

import discord
from discord import app_commands
from discord.ext import commands

from main import AsyncXwingBot


class AttackDie(StrEnum):
    Hit = "hit"
    Crit = "crit"
    Focus = "focus"
    Blank = "blank"


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
    Evade = "evade"
    Focus = "focus"
    Blank = "blank"


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


class DiceCog(commands.GroupCog, name="roll", description="A cog "):
    def __init__(self, bot):
        self.bot: AsyncXwingBot = bot

    @app_commands.command(name="attack", description="Make an attack roll")
    async def attack_roll(self, interaction: discord.Interaction, num_dice: int) -> None:
        emojis: Sequence[discord.Emoji] = interaction.guild.emojis if interaction.guild else []
        rolls: list[AttackDie] = [random.choice(ATTACK_DIE_FACES) for i in range(0, num_dice)]

        result_str: str = "".join([
            str(discord.utils.get(emojis, name=f"die_atk_{roll}")) for roll in rolls
        ])
        await interaction.response.send_message(result_str)

    @app_commands.command(name="defense", description="Make a defense")
    async def defense_roll(self, interaction: discord.Interaction, num_dice: int) -> None:
        emojis: Sequence[discord.Emoji] = interaction.guild.emojis if interaction.guild else []
        rolls: list[DefenseDie] = [random.choice(DEFENSE_DIE_FACES) for i in range(0, num_dice)]
        result_str: str = "".join([
            str(discord.utils.get(emojis, name=f"die_def_{roll}")) for roll in rolls
        ])
        await interaction.response.send_message(result_str)


async def setup(bot):
    await bot.add_cog(DiceCog(bot))


async def teardown(bot):
    bot.logger.info("DiceCog extension unloaded!")
