from enum import StrEnum, auto
from typing import Annotated

import msgspec

from game.model import Faction
from game.model.catalog.card_attr import (
    Ability,
    Action,
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
    SHIELD = auto()
    STANDARD_CHARGE_LIMIT = auto()
    FORCE_CHARGE_LIMIT = auto()
    ENERGY_CHARGE_LIMIT = auto()


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
    types: Annotated[
        list[UpgradeType], msgspec.Meta(description='A list because types can be duplciated')
    ]
    name: str
    unique: bool
    ability: Ability | None = None
    flavor_text: str | None = None
    charges: dict[ChargeType, ChargeValues] | None = None
    special_attacks: list[SpecialAttack] | None = None
    bonus_attacks: list[BonusAttack] | None = None
    action_bar: list[Action] | None = None
    ship_stat_modifiers: dict[ShipStat, int] | None = None
    deployable_remote: Remote | None = None
    restrictions: set[UpgradeRestriction] | None = None
    setup_automations: list[str] | None = None
