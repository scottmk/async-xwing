from functools import cache
import logging
from typing import Any, cast

import discord
from discord_helpers.emoji import get_emoji, replace_emoji_placeholders
from game.model.base import BaseStruct
from game.model import catalog, Faction, Ship
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


logger = logging.getLogger()


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
            stats_str += f'{"▴" * shields_recurring}'

    charges: dict[catalog.card_attr.ChargeType, catalog.card_attr.ChargeValues] | None = (
        pilot_info.charges
    )
    if charges:
        if force_charges := charges.get(catalog.card_attr.ChargeType.FORCE):
            stats_str += f'\u2001{get_emoji("force_charge")} **{force_charges.limit}**{"▴" * force_charges.recurring_val}'
        if std_charges := charges.get(catalog.card_attr.ChargeType.STANDARD):
            stats_str += f'\u2001{get_emoji("std_charge")} **{std_charges.limit}**{"▴" * std_charges.recurring_val}'

    if energy_val := ship_info.energy_val:
        stats_str += f'\u2001{get_emoji("energy")} **{energy_val}**'
        if energy_recurring := ship_info.energy_recurring:
            stats_str += f'{"▴" * energy_recurring}'

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


@cache
def get_card_embed(card_id: str, card_type: type[BaseStruct[Any]]) -> discord.Embed | None:
    if issubclass(card_type, Ship):
        return _get_ship_embed(card_id)
    else:
        raise ValueError(f'{card_type} is not supported for embeds')
