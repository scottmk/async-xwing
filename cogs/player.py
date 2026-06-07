import logging
from typing import cast
import discord
from discord import app_commands
from discord.ext import commands
from discord_helpers.emoji import get_emoji
from game.model import Ship, Player, GameState, catalog
from game.model.ship import DamageCard
from game.state import get_game_state, get_player_stats, update_game_state


class PlayerCog(commands.GroupCog, name='player'):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

    async def cog_command_error(self, ctx: commands.Context, error: Exception):
        self.logger.exception('Unhandled exception')
        await ctx.send('Something went wrong')

    @staticmethod
    def _get_player_stats(
        interaction: discord.Interaction, player: discord.Member | None = None
    ) -> Player:
        # these commands run only inside a server, so interaction.user is always a Member
        _player: discord.Member = player if player else interaction.user  # type:ignore
        return get_player_stats(interaction.channel, _player)

    @app_commands.command(name='stats', description="Read player's stats, including all ships")
    async def get_player_stats(
        self,
        interaction: discord.Interaction,
        player: discord.Member | None = None,
    ) -> None:
        await interaction.response.defer(ephemeral=False)
        player_stats: Player = PlayerCog._get_player_stats(interaction, player)
        stats_chunked_str = player_stats.to_chunked_str()
        if not isinstance(interaction.channel, discord.TextChannel):
            await interaction.followup.send(
                '`/player stats` cannot be invoked from this context. You must invoke it from a Text Channel'
            )
            return
        title_msg: discord.WebhookMessage = await interaction.followup.send(
            stats_chunked_str[0], wait=True
        )
        thread: discord.Thread = await interaction.channel.create_thread(
            name=f"{player_stats.name}'s ships", auto_archive_duration=1440, message=title_msg
        )

        for message in stats_chunked_str[1:]:
            await thread.send(message)

    @get_player_stats.error
    async def get_player_stats_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CommandInvokeError) and isinstance(
            error.original, NotImplementedError
        ):
            await interaction.followup.send(
                'This command can only be run from text channels.', ephemeral=True
            )
            return
        self.logger.error('Unhandled exception', exc_info=error)
        await interaction.followup.send('Something went wrong!', ephemeral=True)

    ships_group = app_commands.Group(
        name='ships', description='All player sub-commands to interact with ships'
    )

    @ships_group.command(
        name='stats', description='Read all ship stats or modify some ship stats, for a given ship'
    )
    @app_commands.describe(
        ship_id='The ID of the ship to interact with',
        shields='The current number of available shields; may use +/- to add or subtract',
        damage_cards="Ship's damage cards. Use commas between adjustments like: +facedown:2, -faceup:1, +card_id",
        tokens="Ship's tokens. Use commas between adjustments like: +focus:1, -evade:2",
        conditions="Ship's conditions. Use commas between adjustments like: +marked_for_elimination, -primed_for_speed",
        upgrades="Ship's upgrades. Use commas between adjustments like: +marked_for_elimination, -primed_for_speed",
        player='(Optional) The player whose ships you want to interact with. Default is the invoking player',
    )
    async def get_ship_stats(
        self,
        interaction: discord.Interaction,
        ship_id: int,
        shields: int | None,
        damage_cards: str | None,
        tokens: str | None,
        conditions: str | None,
        upgrades: str | None,
        player: discord.Member | None = None,
    ):
        await interaction.response.defer(ephemeral=False)
        player_stats: Player = PlayerCog._get_player_stats(interaction, player)
        ship: Ship | None = player_stats.squad.get(ship_id)

        if ship is None:
            await interaction.followup.send(f'No ship with ID {ship_id} found')
            return

        if not any([shields, damage_cards, tokens, conditions, upgrades]):
            # No args means this is a read command
            response_str: str = f"## Stats for {get_emoji(player_stats.faction)} {player_stats.name}'s ship #{ship_id}:\n {ship.pretty_str()}"
            await interaction.followup.send(response_str)
            return

        response_str_builder: list[str] = [
            f"## Adjustments for {get_emoji(player_stats.faction)} {player_stats.name}'s ship #{ship_id}:"
        ]
        if shields:
            new_shields_val = ship.shields + shields
            max_shields: int = cast(catalog.ShipAttr, ship.get_catalog_entry()).shield_val
            if new_shields_val < 0:
                response_str_builder.append(
                    f"> - Can't set shields to negative values ({ship.shields + shields})"
                )
            elif new_shields_val > max_shields:
                response_str_builder.append(
                    f"> - Can't set shields to more than maximum ({max_shields})"
                )
            else:
                response_str_builder.append(
                    f'> - Adjusted shields from {ship.shields}/{max_shields} to {new_shields_val}/{max_shields}'
                )
                ship.shields = new_shields_val

        if damage_cards:
            new_dmg_cards, dmg_card_response_str = self._parse_damage_adjustments(
                damage_cards, ship.damage_cards
            )
            response_str_builder.append(
                f'> - Adjusted damage cards from `{[card.pretty_str() for card in ship.damage_cards]}`\n> to `{[card.pretty_str() for card in new_dmg_cards]}`'
            )
            response_str_builder.append(
                dmg_card_response_str
            )  # FIXME there seems to be an extra newline
            ship.damage_cards = new_dmg_cards

        # TODO tokens
        # TODO conditions
        # TODO upgrades

        game_state: GameState = get_game_state(interaction.channel)
        game_state.players[player_stats.name].squad[ship_id] = ship
        update_game_state(interaction.channel, game_state)
        await interaction.followup.send('\n'.join(response_str_builder))

    @staticmethod
    def _parse_damage_adjustments(
        input_str: str, curr_dmg_cards: list[DamageCard]
    ) -> tuple[list[DamageCard], str]:
        """
        Parses a string of damage card adjustments separated by spaces or commas.

        Supported commands:
        +facedown:n   : Add n random facedown damage cards
        -facedown:n   : Remove n random facedown damage cards
        +faceup:n     : Add n random faceup damage card
        -card_id      : Remove a specific faceup damage card (e.g., -marked_for_elimination)
        """
        # TODO
        return curr_dmg_cards, '>    - `damage_cards`: Not yet implemented'

    @get_ship_stats.error
    async def get_ship_stats_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        self.logger.error('Unhandled exception', exc_info=error)
        await interaction.followup.send('Something went wrong!', ephemeral=True)


async def setup(bot):
    await bot.add_cog(PlayerCog(bot))


async def teardown(bot):
    bot.logger.info('PlayerCog extension unloaded!')
