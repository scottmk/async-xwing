from enum import StrEnum, auto
from typing import Annotated

from discord_helpers.emoji import get_emoji
import msgspec

from caseconverter import titlecase
from game.model import Faction
from game.model.catalog.card_attr import (
    Ability,
    Action,
    ActionDifficulty,
    ActionName,
    Arc,
    Card,
    ChargeType,
    ChargeValues,
    Keyword,
    ShipSize,
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

    @property
    def emoji(self) -> str:
        return get_emoji(f'upg_{self}')


class UpgradeRestrictionAction(msgspec.Struct, kw_only=True, frozen=True):
    action_name: ActionName
    color: ActionDifficulty | None = None

    def __str__(self) -> str:
        base_emoji: str = get_emoji(
            f'{self.action_name if self.action_name != "lock" else "target_lock"}_txt'
        )
        return f'{titlecase(self.color)} {base_emoji}' if self.color else base_emoji


class UpgradeRestrictionShip(msgspec.Struct, kw_only=True, frozen=True):
    name: str
    id_: str

    def __str__(self) -> str:
        return self.name

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.name < other.name
        return NotImplemented


class UpgradeRestrictions(msgspec.Struct, kw_only=True, frozen=True):
    factions: set[Faction] | None = None
    names: set[str] | None = None
    ships: set[UpgradeRestrictionShip] | None = None
    ship_sizes: set[ShipSize] | None = None
    actions: set[UpgradeRestrictionAction] | None = None
    arcs: set[Arc] | None = None
    ship_ability: str | None = None
    equipped_upgrades: set[UpgradeType] | None = None
    min_shields: int | None = None
    keywords: set[Keyword] | None = None
    solitary: bool = False
    standardized: bool = False

    def __str__(self):
        items: list[str] = []
        if self.factions:
            items.append(f'*{" or ".join(sorted(self.factions))}*')
        if self.names:
            prefix_str: str = ''
            if self.factions:
                prefix_str: str = 'OR squad including'
            else:
                prefix_str: str = 'Squad including'
            items.append(f'*{prefix_str} {" or ".join(sorted(self.names))}*')
        if self.ships:
            items.append(f'*{", ".join(sorted([ship.name for ship in self.ships]))}*')
        if self.ship_sizes:
            items.append(
                f'*{" or ".join(sorted(titlecase(ship_size) for ship_size in self.ship_sizes))} Ship*'
            )
        if self.actions:
            items.append(f'*{", ".join(sorted([str(action) for action in self.actions]))}*')
        if self.arcs:
            items.append(f'*{", ".join(sorted([str(arc) for arc in self.arcs]))}*')
        if self.ship_ability:
            items.append(f'***{self.ship_ability}***')
        if self.equipped_upgrades:
            items.append(
                f'*Equipped {" or ".join(sorted(titlecase(upg) for upg in self.equipped_upgrades))}*'
            )
        if self.min_shields:
            items.append(f'*Shield value of {self.min_shields} or more*')
        if self.keywords:
            items.append(', '.join(sorted(self.keywords)))
        if self.solitary:
            items.append('*Solitary*')
        if self.standardized:
            items.append('*Standardized*')
        if len(items) == 0:
            return '*None*'
        return '\n'.join(items)


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
    restrictions: UpgradeRestrictions | None = None
    is_reverse: bool = False
    reverse_side_id: str | None = None
    setup_automations: list[str] | None = None

    def __post_init__(self):
        if len(self.slots) == 0:
            object.__setattr__(self, 'slots', [self.type_])
