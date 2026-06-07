from enum import StrEnum, auto
from typing import Annotated

import msgspec

from game.measurement import Size
from game.model import Faction
from game.model.catalog.card_attr import (
    Ability,
    Action,
    Attack,
    Card,
    ChargeType,
    ChargeValues,
    Keyword,
)
from game.model.catalog.upgrade import UpgradeType
from game.movement.maneuver import ManeuverBearing, ManeuverDifficulty, ManeuverSpeed


class ShipSize(StrEnum):
    SMALL = auto()
    MEDIUM = auto()
    LARGE = auto()
    HUGE = auto()

    # TODO - Move this out into game logic. It can't go in measurement because that creates a circular dependency.
    @property
    def base_size(self) -> Size:
        match self:
            case ShipSize.SMALL:
                return Size(width=40.0, height=40.0)
            case ShipSize.MEDIUM:
                return Size(width=60.0, height=60.0)
            case ShipSize.LARGE:
                return Size(width=80.0, height=80.0)
            case ShipSize.HUGE:
                # HUGE ships are two LARGE bases with a custom connector piece that is unique to each ship.
                # TODO - Huge ships: Figure out how to define huge ship base sizes. For now, just return the size of two LARGE bases.
                return Size(width=80.0, height=160.0)


class PilotCard(Card, kw_only=True, frozen=True):
    name: str
    unique: bool
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
    shield_val: int
    action_bar: list[Action]
    ship_ability: Ability | None = None
    maneuver_dial: dict[ManeuverBearing, dict[ManeuverSpeed, ManeuverDifficulty]]
    pilots: dict[str, PilotCard]
