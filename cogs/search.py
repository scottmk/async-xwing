import logging
from typing import Iterable, cast
import discord
from discord import app_commands
from discord.ext import commands
from discord_helpers.embeds import LazyEmbedPaginatorView, get_card_embed
from game.model import Ship, catalog


class SearchCog(commands.GroupCog, name='search'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

    def _search_pilots(self, query: str) -> list[tuple[str, str]]:
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
        await interaction.response.defer(ephemeral=False)

        if not isinstance(interaction.channel, discord.TextChannel):
            # TODO technically we could make this just create a thread in the parent channel
            await interaction.followup.send(
                '`/search ships` cannot be invoked from this context. You must invoke it from a Text Channel'
            )
            return

        # User clicked a specific dropdown option or entered a valid pilot_id
        all_pilot_ids = Ship.get_manifest().keys()
        if pilot_id in all_pilot_ids:
            embed: discord.Embed | None = get_card_embed(card_id=pilot_id, card_type=Ship)
            if not embed:
                await interaction.followup.send(f"No catalog entry found for pilot_id '{pilot_id}'")
            else:
                await interaction.followup.send(embed=embed)
            return

        # User typed search text and hit enter, so create a thread of all matches
        all_matches: list[tuple[str, str]] = self._search_pilots(pilot_id)
        if not all_matches:
            await interaction.followup.send(f"No pilots matched '{pilot_id}'.")
            return

        if len(all_matches) > 1:
            title_msg: discord.WebhookMessage = await interaction.followup.send(
                f"Found **{len(all_matches)}** matches for query '{pilot_id}'", wait=True
            )
            thread: discord.Thread = await interaction.channel.create_thread(
                name=f'Ship search results ({pilot_id})',
                auto_archive_duration=1440,
                message=title_msg,
            )
            paginator_view: LazyEmbedPaginatorView = LazyEmbedPaginatorView(
                embed_pool=(
                    embed
                    for _, match_id in all_matches
                    if (embed := get_card_embed(card_id=match_id, card_type=Ship))
                )
            )
            response_msg: discord.Message = await thread.send(
                embeds=paginator_view.current_embeds, view=paginator_view
            )
            paginator_view.message = response_msg
        else:
            match_id: str = all_matches[0][1]
            embed: discord.Embed | None = get_card_embed(card_id=match_id, card_type=Ship)
            if not embed:
                await interaction.followup.send(f"No pilots matched '{pilot_id}'.")
            else:
                await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(SearchCog(bot))


async def teardown(bot: commands.Bot):
    bot.logger.info('SearchCog extension unloaded!')  # pyright: ignore[reportAttributeAccessIssue]
