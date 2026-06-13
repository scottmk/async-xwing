from enum import StrEnum, auto
from typing import Annotated

import msgspec

from game.model import Faction
from game.model.catalog.card_attr import (
    Ability,
    Action,
    Arc,
    Card,
    ChargeType,
    ChargeValues,
    Keyword,
    SpecialAttack,
)


class ShipStat(StrEnum):
    ATTACK = auto()
    AGILITY = auto()
    HULL = auto()
    SHIELDS = auto()
    ENERGY = auto()


class UpgradeType(StrEnum):
    ASTROMECH = auto()
    CANNON = auto()
    CARGO = auto()
    COMMAND = auto()
    CONFIGURATION = auto()
    CREW = auto()
    FORCE_POWER = auto()
    GUNNER = auto()
    HARDPOINT = auto()
    HYPERDRIVE = auto()
    ILLICIT = auto()
    MISSILE = auto()
    MODIFICATION = auto()
    PAYLOAD = auto()  # Formerly known as DEVICE
    SENSOR = auto()
    TACTICAL_RELAY = auto()
    TALENT = auto()
    TEAM = auto()
    TECH = auto()
    TITLE = auto()
    TORPEDO = auto()
    TURRET = auto()


class UpgradeRestriction(msgspec.Struct, kw_only=True, frozen=True):
    ship: str | None = None
    faction: Faction | None = None
    keywords: set[Keyword]


class Remote(msgspec.Struct, kw_only=True, frozen=True):
    """Autonomous unit launched from upgrade, e.g., commandos or droids."""

    name: str
    subtitle: str | None = None
    initiative: int
    faction: Faction
    attack: SpecialAttack | None = None
    agility: int
    hull: int
    abilities: list[Ability] | None = None
    flavor_text: str | None = None


class BonusAttack(SpecialAttack):
    pass


class UpgradeCard(Card, kw_only=True, frozen=True):
    type_: UpgradeType
    slots: Annotated[
        list[UpgradeType], msgspec.Meta(description='The slots required to equip this upgrade')
    ] = []
    name: str
    is_unique: bool
    limit: int | None = None
    ability: Ability | None = None
    flavor_text: str | None = None
    charges: dict[ChargeType, ChargeValues] | None = None
    special_attacks: list[SpecialAttack] | None = None
    huge_ship_bonus_attacks: Annotated[
        list[BonusAttack] | None,
        msgspec.Meta(
            description='Special bonus attacks only for hardpoint upgrades, which are for Huge Ships. Different from regular bonus attacks, which are handled by automation strings.'
        ),
    ] = None
    replacement_arc: Annotated[
        Arc | None,
        msgspec.Meta(description='Replaces the attack arc of the ship this is attached to'),
    ] = None
    action_bar: list[Action] | None = None
    ship_stat_modifiers: dict[ShipStat, int] | None = None
    bonus_slots: dict[UpgradeType, int] | None = None
    bonus_keywords: set[Keyword] | None = None
    deployable_remote: Remote | None = None
    restrictions: set[UpgradeRestriction] | None = None
    is_reverse: bool = False
    reverse_side_id: str | None = None
    setup_automations: list[str] | None = None

    def __post_init__(self):
        if len(self.slots) == 0:
            object.__setattr__(self, 'slots', [self.type_])
