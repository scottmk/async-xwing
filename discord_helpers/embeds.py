from functools import cache
import logging
from typing import Any, Iterable, Iterator, cast

import discord
from discord_helpers.emoji import get_emoji, replace_emoji_placeholders
from game.model.base import BaseStruct
from game.model import catalog, Condition, Faction, Ship
from game import movement


REVERSE_MANEUVERS: set[movement.ManeuverBearing] = {
    movement.ManeuverBearing.REVERSE_STRAIGHT,
    movement.ManeuverBearing.REVERSE_BANK_LEFT,
    movement.ManeuverBearing.REVERSE_BANK_RIGHT,
}

BEARING_POSITIONS_MAP: dict[int, set[movement.ManeuverBearing]] = {
    0: {movement.ManeuverBearing.TALLON_ROLL_LEFT, movement.ManeuverBearing.SEGNORS_LOOP_LEFT},
    1: {
        movement.ManeuverBearing.TURN_LEFT,
    },
    2: {movement.ManeuverBearing.BANK_LEFT, movement.ManeuverBearing.REVERSE_BANK_LEFT},
    3: {
        movement.ManeuverBearing.STRAIGHT,
        movement.ManeuverBearing.REVERSE_STRAIGHT,
        movement.ManeuverBearing.STATIONARY,
    },
    4: {movement.ManeuverBearing.BANK_RIGHT, movement.ManeuverBearing.REVERSE_BANK_RIGHT},
    5: {
        movement.ManeuverBearing.TURN_RIGHT,
    },
    6: {
        movement.ManeuverBearing.TALLON_ROLL_RIGHT,
        movement.ManeuverBearing.SEGNORS_LOOP_RIGHT,
        movement.ManeuverBearing.KOIOGRAN_TURN,
    },
}

EMBED_MESSAGE_MAX_CHARS = 6000
MAX_NUM_EMBEDS = 10


logger = logging.getLogger()


class LazyEmbedPaginatorView(discord.ui.View):
    """An interactive UI View that manages flipping through chunks of embeds, lazily evaluated on-demand."""

    # The message inside the thread, which needs to be set after the view is created
    message: discord.Message | discord.WebhookMessage | None = None

    def __init__(self, embed_pool: Iterable[discord.Embed], timeout_sec: float = 600.0) -> None:
        super().__init__(timeout=timeout_sec)

        # Initialize the generator and track evaluated chunks
        self.chunk_iterator: Iterator[list[discord.Embed]] = self._chunk_generator(embed_pool)
        self.cached_chunks: list[list[discord.Embed]] = []
        self.current_page: int = 0
        self.has_more_pages: bool = True

        self.logger = logging.getLogger(self.__class__.__name__)

        # Pre-load the first two pages from our generator, for lookahead
        self._load_next_page()
        self._load_next_page()
        self._update_button_states()

    @staticmethod
    def _chunk_generator(embeds: Iterable[discord.Embed]) -> Iterator[list[discord.Embed]]:
        """Groups a flat collection of embeds into a collection of chunks, respecting character and array limits."""
        current_chunk: list[discord.Embed] = []
        current_char_count: int = 0
        for embed in embeds:
            embed_len: int = len(embed)
            if embed_len >= EMBED_MESSAGE_MAX_CHARS:
                raise ValueError(
                    f"The '{embed.title}' exceeds the message character limit of {EMBED_MESSAGE_MAX_CHARS} ({embed_len})"
                )

            # Check if adding this embed violates either the character limit or the count limit
            is_over_char_limit: bool = (current_char_count + embed_len) >= EMBED_MESSAGE_MAX_CHARS
            is_over_embed_limit: bool = len(current_chunk) >= MAX_NUM_EMBEDS

            if is_over_char_limit or is_over_embed_limit:
                # Add the current chunk and start a new one
                yield current_chunk
                current_chunk = []
                current_char_count = 0

            # Add the embed to the active chunk
            current_chunk.append(embed)
            current_char_count += embed_len

        # Append the final remaining chunk if it contains any items
        if current_chunk:
            yield current_chunk

    def _load_next_page(self) -> None:
        try:
            next_chunk: list[discord.Embed] = next(self.chunk_iterator)
            self.cached_chunks.append(next_chunk)
        except StopIteration:
            self.has_more_pages = False

    def _update_button_states(self) -> None:
        self.prev_button.disabled = self.current_page == 0
        is_at_cache_end: bool = self.current_page >= len(self.cached_chunks) - 1
        self.next_button.disabled = is_at_cache_end and not self.has_more_pages

    @property
    def current_embeds(self) -> list[discord.Embed]:
        return self.cached_chunks[self.current_page]

    @discord.ui.button(label='◀ Previous', style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        if self.current_page > 0:
            self.current_page -= 1
            self._update_button_states()
            await interaction.response.edit_message(embeds=self.current_embeds, view=self)

    @discord.ui.button(label='Next ▶', style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        if self.current_page < len(self.cached_chunks) - 1:
            self.current_page += 1

            # load next page for lookahead
            if self.current_page == len(self.cached_chunks) - 1:
                self._load_next_page()

            self._update_button_states()
            await interaction.response.edit_message(embeds=self.current_embeds, view=self)

    async def on_timeout(self) -> None:
        """Triggers automatically when the timeout expires to clean up the UI."""
        if not self.message:
            return

        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

        try:
            await self.message.edit(
                content='This search session has timed out due to inactivity.', view=self
            )
        except discord.HTTPException:
            pass


def _get_recurring_emoji(type_: str, recurring: int) -> str:
    if recurring < -1 or recurring > 3:
        logger.warning('Got a request for an OOB recurring value: {recurring}')
        return ''
    if recurring == -1:
        return get_emoji(f'{type_}_recur_neg1')
    return get_emoji(f'{type_}_recur_{recurring}')


def _get_ship_embed(card_id: str) -> discord.Embed | None:
    ship_info: catalog.ShipAttr | None = cast(
        catalog.ShipAttr, Ship.get_catalog_entry_for_id(card_id)
    )

    if ship_info is None:
        return None

    pilot_info = Ship.get_pilot_card_for_id(card_id)
    faction: Faction = pilot_info.faction

    description_lines: list[str] = [
        f'-# *{pilot_info.subtitle}*' if pilot_info.subtitle else '',
        replace_emoji_placeholders(pilot_info.pilot_ability.text)
        if pilot_info.pilot_ability
        else '',
        f'*{pilot_info.flavor_text}*' if pilot_info.flavor_text else '',
    ]
    embed: discord.Embed = discord.Embed(
        color=faction.color,
        title=f'{pilot_info.name} {faction.emoji}',
        description='\n\n'.join(line for line in description_lines if line),
    )

    if (ship_ability := ship_info.ship_ability) is not None:
        embed.add_field(
            name=ship_ability.name,
            value=replace_emoji_placeholders(ship_ability.text),
            inline=False,
        )

    embed.add_field(name='Initiative', value=f'**{pilot_info.initiative}**', inline=True)

    # Stats
    stats_str: str = '\u2001'.join(
        f'{attack.arc.emoji} **{attack.val}**' for attack in ship_info.attacks
    )
    stats_str += f'\u2001{get_emoji("agility")} **{ship_info.agility_val}**\u2001{get_emoji("hull")} **{ship_info.hull_val}**'
    if shield_val := ship_info.shield_val:
        stats_str += f'\u2001{get_emoji("shields")} **{shield_val}**'
        if shields_recurring := ship_info.shields_recurring:
            stats_str += _get_recurring_emoji('shields', shields_recurring)

    charges: dict[catalog.card_attr.ChargeType, catalog.card_attr.ChargeValues] | None = (
        pilot_info.charges
    )
    if charges:
        if force_charges := charges.get(catalog.card_attr.ChargeType.FORCE):
            stats_str += f'\u2001{get_emoji("force_charge")} **{force_charges.limit}**{_get_recurring_emoji("force_charge", force_charges.recurring_val)}'
        if std_charges := charges.get(catalog.card_attr.ChargeType.STANDARD):
            stats_str += f'\u2001{get_emoji("std_charge")} **{std_charges.limit}**{_get_recurring_emoji("std_charge", std_charges.recurring_val)}'

    if energy_val := ship_info.energy_val:
        stats_str += f'\u2001{get_emoji("energy")} **{energy_val}**'
        if energy_recurring := ship_info.energy_recurring:
            stats_str += _get_recurring_emoji('energy', energy_recurring)

    embed.add_field(name='Stats', value=stats_str, inline=False)

    # Maneuver dial
    speed_bearing_to_difficulty: dict[
        tuple[int, movement.ManeuverBearing], movement.ManeuverDifficulty
    ] = {
        (speed * (-1 if bearing in REVERSE_MANEUVERS else 1), bearing): difficulty
        for bearing, speed_difficulty_dict in ship_info.maneuver_dial.items()
        for speed, difficulty in speed_difficulty_dict.items()
    }
    maneuver_lines: list[str] = []
    for speed in sorted(
        {speed for speed, bearing in speed_bearing_to_difficulty.keys()}, reverse=True
    ):
        # Start the line with the current speed
        maneuver_line = f'{abs(speed)}\u20e3'

        for idx in range(7):
            matching_bearing: movement.ManeuverBearing | None = next(
                (
                    bearing
                    for bearing in BEARING_POSITIONS_MAP[idx]
                    if (speed, bearing) in speed_bearing_to_difficulty
                ),
                None,
            )

            if matching_bearing:
                difficulty = speed_bearing_to_difficulty[(speed, matching_bearing)]
                maneuver_line += matching_bearing.get_emoji(difficulty)
            else:
                maneuver_line += '⬛'

        maneuver_lines.append(maneuver_line)

    embed.add_field(name='Maneuver Dial', value='\n'.join(maneuver_lines), inline=True)

    embed.add_field(
        name='Actions',
        value=f'{"\n".join(action.emoji for action in ship_info.action_bar)}',
        inline=True,
    )

    embed.add_field(name='', value=f'-# _{ship_info.name}_', inline=False)

    embed.add_field(
        name='XWA Cost/LV',
        value=f'{pilot_info.xwa_cost} / {pilot_info.xwa_loadout_val}',
        inline=True,
    )
    if pilot_info.amg_cost:
        embed.add_field(
            name='AMG Cost/LV',
            value=f'{pilot_info.amg_cost} / {pilot_info.amg_loadout_val}',
            inline=True,
        )

    # TODO set_image to get an image of the ship
    # embed.set_image(url='attachment://')
    # TODO add icon to footer
    embed.set_footer(text='©LFL ©FFG')  # , icon_url='attachment://')
    return embed


def _get_condition_embed(card_id: str) -> discord.Embed | None:
    condition_info: catalog.ConditionCard | None = cast(
        catalog.ConditionCard, Condition.get_catalog_entry_for_id(card_id)
    )

    if condition_info is None:
        return None

    return discord.Embed(
        color=discord.Color.ash_embed(),
        title=condition_info.name,
        description=replace_emoji_placeholders(condition_info.text),
    )


@cache
def get_card_embed(card_id: str, card_type: type[BaseStruct[Any]]) -> discord.Embed | None:
    if issubclass(card_type, Ship):
        return _get_ship_embed(card_id)
    elif issubclass(card_type, Condition):
        return _get_condition_embed(card_id)
    else:
        raise ValueError(f'{card_type} is not supported for embeds')
