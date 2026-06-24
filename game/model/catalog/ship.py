from typing import Annotated

import msgspec

from game.model import Faction
from game.model.catalog.card_attr import (
    Ability,
    Action,
    Attack,
    Card,
    ChargeType,
    ChargeValues,
    Keyword,
    ShipSize,
)
from game.model.catalog.upgrade import UpgradeType
from game.movement.maneuver import ManeuverBearing, ManeuverDifficulty, ManeuverSpeed


class PilotCard(Card, kw_only=True, frozen=True):
    name: str
    is_unique: bool
    limit: int | None = None
    subtitle: str | None = None
    initiative: int
    faction: Faction
    is_droid: Annotated[
        bool,
        msgspec.Meta(
            description='Droid pilots have the Calculate action instead of the Focus action'
        ),
    ] = False
    pilot_ability: Ability | None = None
    flavor_text: str | None = None
    charges: dict[ChargeType, ChargeValues] | None = None
    keywords: set[Keyword]
    amg_upgrade_bar: Annotated[
        dict[UpgradeType, int] | None,
        msgspec.Meta(
            description='All upgrade types and number of each type allowed to be equipped on this pilot for XWA'
        ),
    ] = None
    amg_loadout_val: Annotated[
        int | None,
        msgspec.Meta(description='Maximum number of upgrade points this pilot can have for AMG'),
    ] = None
    xwa_upgrade_bar: Annotated[
        dict[UpgradeType, int],
        msgspec.Meta(
            description='All upgrade types and number of each type allowed to be equipped on this pilot for XWA'
        ),
    ]
    xwa_loadout_val: Annotated[
        int,
        msgspec.Meta(description='Maximum number of upgrade points this pilot can have for XWA'),
    ]


class ShipAttr(msgspec.Struct, kw_only=True, frozen=True):
    id_: str
    name: str
    size: ShipSize
    attacks: list[Attack]
    agility_val: int
    hull_val: int
    shield_val: int | None = None
    shields_recurring: int | None = None
    energy_val: int | None = None
    energy_recurring: int | None = None
    action_bar: list[Action]
    ship_ability: Ability | None = None
    maneuver_dial: dict[ManeuverBearing, dict[ManeuverSpeed, ManeuverDifficulty]]
    pilots: Annotated[
        dict[str, dict[str, PilotCard]],
        msgspec.Meta(
            description='Since ships can have pilots in different factions, the catalog file should bucket each pilot by faction for ease of lookup'
        ),
    ]
