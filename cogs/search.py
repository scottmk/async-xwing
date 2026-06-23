import logging
from typing import Any, Callable, Iterable, cast
import discord
from discord import app_commands
from discord.ext import commands
from discord_helpers.embeds import LazyEmbedPaginatorView, get_card_embed
from game.model import Condition, Ship, catalog
from game.model.base import BaseStruct


class SearchCog(commands.GroupCog, name='search'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

    @staticmethod
    async def _search(
        interaction: discord.Interaction,
        function_name: str,
        target_card_id: str,
        all_card_ids: Iterable[str],
        card_type: type[BaseStruct[Any]],
        search_function: Callable[[str], list[tuple[str, str]]],
    ) -> None:
        await interaction.response.defer(ephemeral=False)

        if not isinstance(interaction.channel, discord.TextChannel):
            # TODO technically we could make this just create a thread in the parent channel
            await interaction.followup.send(
                f'`/search {function_name}` cannot be invoked from this context. You must invoke it from a Text Channel'
            )
            return

        # User clicked a specific dropdown option or entered a valid pilot_id
        if target_card_id in all_card_ids:
            embed: discord.Embed | None = get_card_embed(
                card_id=target_card_id, card_type=card_type
            )
            if not embed:
                await interaction.followup.send(
                    f"No {function_name} catalog entry found for '{target_card_id}'"
                )
            else:
                await interaction.followup.send(embed=embed)
            return

        # User typed search text and hit enter, so create a thread of all matches
        all_matches: list[tuple[str, str]] = search_function(target_card_id)
        if not all_matches:
            await interaction.followup.send(f"No {function_name} matched '{target_card_id}'.")
            return

        if len(all_matches) > 1:
            title_msg: discord.WebhookMessage = await interaction.followup.send(
                f"Found **{len(all_matches)}** matches for query '{target_card_id}'", wait=True
            )
            thread: discord.Thread = await interaction.channel.create_thread(
                name=f'{function_name.capitalize()} search results ({target_card_id})',
                auto_archive_duration=1440,
                message=title_msg,
            )
            paginator_view: LazyEmbedPaginatorView = LazyEmbedPaginatorView(
                embed_pool=(
                    embed
                    for _, match_id in all_matches
                    if (embed := get_card_embed(card_id=match_id, card_type=card_type))
                )
            )
            response_msg: discord.Message = await thread.send(
                embeds=paginator_view.current_embeds, view=paginator_view
            )
            paginator_view.message = response_msg
        else:
            match_id: str = all_matches[0][1]
            embed: discord.Embed | None = get_card_embed(card_id=match_id, card_type=card_type)
            if not embed:
                await interaction.followup.send(f"No {function_name} matched '{target_card_id}'.")
            else:
                await interaction.followup.send(embed=embed)

    @staticmethod
    def _search_pilots(query: str) -> list[tuple[str, str]]:
        pilot_ids: Iterable[str] = Ship.get_manifest().keys()

        matches = []
        for pilot_id in pilot_ids:
            pilot_card: catalog.PilotCard = Ship.get_pilot_card_for_id(pilot_id)
            ship_info: catalog.ShipAttr | None = cast(
                catalog.ShipAttr, Ship.get_catalog_entry_for_id(pilot_id)
            )
            if not ship_info:
                continue

            display_name = f'{pilot_card.name} ({ship_info.name}) [{pilot_id}]'

            # Match against what they see (name) or what is hidden (ID)
            query_lower = query.lower()
            if query_lower in display_name.lower() or query_lower in pilot_id.lower():
                matches.append((display_name, pilot_id))

        return matches

    async def pilot_id_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        choices = self._search_pilots(current)
        return [app_commands.Choice(name=display_name, value=key) for display_name, key in choices][
            :25
        ]

    @app_commands.command(name='ships', description='Search all ships in the catalog by pilot ID')
    @app_commands.autocomplete(pilot_id=pilot_id_autocomplete)
    @app_commands.describe(
        pilot_id='The XWS ID of the ship card',
    )
    async def search_ships(
        self,
        interaction: discord.Interaction,
        pilot_id: str,
    ) -> None:
        return await self._search(
            interaction=interaction,
            function_name='ship',
            target_card_id=pilot_id,
            all_card_ids=Ship.get_manifest().keys(),
            card_type=Ship,
            search_function=self._search_pilots,
        )

    @staticmethod
    def _search_conditions(query: str) -> list[tuple[str, str]]:
        condition_ids: Iterable[str] | None = Condition.get_all_card_ids()

        if not condition_ids:
            return []

        matches = []
        for condition_id in condition_ids:
            condition_card: catalog.ConditionCard | None = cast(
                catalog.ConditionCard, Condition.get_catalog_entry_for_id(condition_id)
            )
            if not condition_card:
                continue

            display_name = f'{condition_card.name} [{condition_id}]'

            # Match against what they see (name) or what is hidden (ID)
            query_lower = query.lower()
            if query_lower in display_name.lower() or query_lower in condition_id.lower():
                matches.append((display_name, condition_id))

        return matches

    async def condition_id_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        choices = self._search_conditions(current)
        return [app_commands.Choice(name=display_name, value=key) for display_name, key in choices][
            :25
        ]

    @app_commands.command(
        name='conditions', description='Search all conditions in the catalog by condition ID'
    )
    @app_commands.autocomplete(condition_id=condition_id_autocomplete)
    @app_commands.describe(
        condition_id='The ID of the condition card',
    )
    async def search_conditions(
        self,
        interaction: discord.Interaction,
        condition_id: str,
    ) -> None:
        return await self._search(
            interaction=interaction,
            function_name='condition',
            target_card_id=condition_id,
            all_card_ids=Condition.get_all_card_ids(),
            card_type=Condition,
            search_function=self._search_conditions,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(SearchCog(bot))


async def teardown(bot: commands.Bot):
    bot.logger.info('SearchCog extension unloaded!')  # pyright: ignore[reportAttributeAccessIssue]
