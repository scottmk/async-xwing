from enum import Enum, StrEnum, auto
from functools import cache
import random
from typing import Iterable

import msgspec

from discord_helpers.emoji import get_emoji
from game.model import catalog
from game.model.base import CATALOG_ROOT_PATH, FrozenBaseStruct, MutableBaseStruct
from game.model.catalog.card_attr import ChargeType, ChargeValues


class TokenColor(Enum):
    GREEN = auto()
    ORANGE = auto()
    BLUE = auto()
    RED = auto()


class TokenType(StrEnum):
    # GREEN
    FOCUS = auto()
    CALCULATE = auto()
    EVADE = auto()
    REINFORCE_AFT = auto()
    REINFORCE_FORE = auto()

    # ORANGE
    DISARM = auto()
    JAM = auto()
    TRACTOR = auto()

    # BLUE
    CLOAK = auto()

    # RED
    DEPLETE = auto()
    ION = auto()
    LOCK = auto()
    STRAIN = auto()
    STRESS = auto()

    @property
    def color(self) -> TokenColor:
        match self:
            case (
                self.FOCUS | self.CALCULATE | self.EVADE | self.REINFORCE_AFT | self.REINFORCE_FORE
            ):
                return TokenColor.GREEN
            case self.DISARM | self.JAM | self.TRACTOR:
                return TokenColor.ORANGE
            case self.CLOAK:
                return TokenColor.BLUE
            case self.DEPLETE | self.ION | self.LOCK | self.STRAIN | self.STRESS:
                return TokenColor.RED


class DamageCard(MutableBaseStruct, kw_only=True):
    faceup: bool  # self.id_ is a secret if this is False

    @staticmethod
    def card_type() -> str:
        return 'damage'

    @staticmethod
    def deck_size() -> int:
        return 33

    @classmethod
    def get_random_card(cls, faceup: bool = False) -> DamageCard:
        random_id: str = random.choice(list(cls._read_card_file().values())).id_
        return DamageCard(random_id, faceup=faceup)

    @classmethod
    def get_all_card_ids(cls) -> Iterable[str]:
        return cls._read_card_file().keys()

    @classmethod
    @cache
    def _read_card_file(cls, type_: str | None = None) -> dict[str, catalog.DamageCard]:
        filepath = CATALOG_ROOT_PATH / 'damage.yaml'
        return msgspec.yaml.decode(filepath.read_bytes(), type=dict[str, catalog.DamageCard])

    @classmethod
    def _lookup_catalog_entry(cls, id_: str) -> catalog.DamageCard | None:
        return super()._lookup_catalog_entry(id_)

    def pretty_str(self) -> str:
        return f'dmg_card:{self.id_ if self.faceup else "facedown"}'


class Condition(FrozenBaseStruct, frozen=True):
    @staticmethod
    def card_type():
        return 'condition'

    @classmethod
    @cache
    def _read_card_file(cls, type_: str | None = None) -> dict[str, catalog.ConditionCard]:
        filepath = CATALOG_ROOT_PATH / 'condition.yaml'
        return msgspec.yaml.decode(filepath.read_bytes(), type=dict[str, catalog.ConditionCard])

    @classmethod
    def _lookup_catalog_entry(cls, id_: str) -> catalog.ConditionCard | None:
        return super()._lookup_catalog_entry(id_)

    def pretty_str(self) -> str:
        return f'condition:{self.id_}'


class Upgrade(FrozenBaseStruct, frozen=True):
    id_: str

    @staticmethod
    def card_type():
        return 'upgrade'

    @classmethod
    @cache
    def _read_card_file(cls, type_: str | None) -> dict[str, catalog.UpgradeCard]:
        if not type_:
            raise ValueError('No upgrade type found')
        filepath = CATALOG_ROOT_PATH / 'upgrade' / f'{type_}.yaml'
        return msgspec.yaml.decode(filepath.read_bytes(), type=dict[str, catalog.UpgradeCard])

    @classmethod
    def _lookup_catalog_entry(cls, id_: str) -> catalog.UpgradeCard | None:
        return super()._lookup_catalog_entry(id_)

    def pretty_str(self) -> str:
        return f'upgrade:{self.id_}'


class Ship(MutableBaseStruct, kw_only=True):
    id_: str
    ship_name: str
    pilot_name: str
    faction: str
    shields: int
    energy: int | None = None
    damage_cards: list[DamageCard]
    force_charges: int | None = None
    std_charges: int | None = None
    tokens: dict[TokenType, int]
    target_lock: int | None = None
    conditions: list[Condition]
    upgrades: list[Upgrade]

    def get_hull_damage(self) -> int:
        return len(self.damage_cards)

    def partition_damage_cards(self) -> tuple[list[DamageCard], list[DamageCard]]:
        faceup: list[DamageCard] = []
        facedown: list[DamageCard] = []
        for card in self.damage_cards:
            if card.faceup:
                faceup.append(card)
            else:
                facedown.append(card)

        return faceup, facedown

    def get_pilot_card(self) -> catalog.PilotCard:
        ship_attr: catalog.ShipAttr | None = self.get_catalog_entry()
        if not ship_attr:
            raise ValueError(f'Unable to find ship data for {self.id_}')
        return ship_attr.pilots.get(self.faction).get(self.id_)

    @classmethod
    def get_pilot_card_for_id(cls, id_: str) -> catalog.PilotCard:
        ship_attr: catalog.ShipAttr | None = cls.get_catalog_entry_for_id(id_)
        faction: str | None = (
            entry.get('faction') if (entry := cls._get_manifest().get(id_)) else None
        )
        if not ship_attr:
            raise ValueError(f'Unable to find ship data for {id_}')
        return ship_attr.pilots.get(faction).get(id_)

    @staticmethod
    def card_type():
        return 'ship'

    @classmethod
    @cache
    def _read_card_file(cls, type_: str | None) -> dict[str, catalog.ShipAttr]:
        if not type_:
            raise ValueError('No ship type found')
        filepath = CATALOG_ROOT_PATH / 'ship' / f'{type_}.yaml'
        ship_attr: catalog.ShipAttr = msgspec.yaml.decode(
            filepath.read_bytes(), type=catalog.ShipAttr
        )
        # This is because ships are handled differently in the catalog, where there is only 1 ship per file
        #  that has a member 'pilots' which is the actual dict
        return {type_: ship_attr}

    @classmethod
    def _lookup_catalog_entry(cls, id_: str) -> catalog.ShipAttr | None:
        type_: str | None = entry.get('type') if (entry := cls._get_manifest().get(id_)) else None
        if not type_:
            raise ValueError(
                f'Ship manifest missing or malformed or entry for {id_} missing from manifest'
            )

        return cls._read_card_file(type_).get(type_)

    def _str_tokens(self) -> str:
        return '\n'.join(
            [
                f'\t\t{get_emoji(token.value + "_tkn")} `{token.value}: {count}`'
                for token, count in self.tokens.items()
            ]
        )

    def pretty_str(self) -> str:
        faceup_dmg_cards, facedown_dmg_cards = self.partition_damage_cards()
        ship_attr: catalog.ShipAttr | None = self.get_catalog_entry()
        pilot_card: catalog.PilotCard = self.get_pilot_card()

        hull_max, shields_max, energy_max = '?', '?', '?'
        if ship_attr:
            hull_max, shields_max, energy_max = (
                ship_attr.hull_val,
                ship_attr.shield_val,
                ship_attr.energy,
            )

        str_repr: str = (
            f'\t**Catalog ID**: `{self.id_}`\n'
            f'\t**Ship Name**: {self.ship_name}\n'
            f'\t**Pilot Name**: {self.pilot_name}\n'
            f'\t{get_emoji("shield")} **Shields**: `{self.shields}/{shields_max}`\n'
            f'\t{get_emoji("hit")} **Face-down Damage Cards**: `{len(facedown_dmg_cards)}`\n'
            f'\t{get_emoji("crit_tkn")} **Face-up Damage Cards**: `{[card.id_ for card in faceup_dmg_cards]}`\n'
        )

        hull_health = self.get_hull_damage()
        if isinstance(hull_max, int):
            hull_health = hull_max - self.get_hull_damage()
        str_repr += f'\t{get_emoji("hull")} **Hull Health**: `{hull_health}/{hull_max}`\n'

        if self.energy:
            str_repr += f'\t{get_emoji("energy")} **Energy**: `{self.energy}/{energy_max}`\n'

        force_charge_entry, std_charge_entry = None, None
        if ship_attr and pilot_card and pilot_card.charges:
            force_charge_entry: ChargeValues | None = pilot_card.charges.get(ChargeType.FORCE)
            std_charge_entry: ChargeValues | None = pilot_card.charges.get(ChargeType.STANDARD)

        if force_charge_entry and self.force_charges:
            str_repr += f'\t{get_emoji("force_charge")} **Force Charges**: `{self.force_charges}/{force_charge_entry.limit}`\n'
        if std_charge_entry and self.std_charges:
            str_repr += f'\t{get_emoji("std_charge")} **Standard Charges**: `{self.std_charges}/{std_charge_entry.limit}`\n'

        str_repr += (
            f'\tTokens:\n{self._str_tokens()}\n'
            f'\t{get_emoji("lock_tkn")} **Target Lock**: `{self.target_lock}`\n'
            f'\t**Conditions**: `{[condition.id_ for condition in self.conditions]}`\n'
            f'\t**Upgrades**:  `{[upgrade.id_ for upgrade in self.upgrades]}`\n'
        )
        return str_repr
