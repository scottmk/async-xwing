from enum import StrEnum, auto
from typing import Annotated

import msgspec


class Ability(msgspec.Struct):
    text: str
    automations: set[str]
    is_action: bool


class ActionName(StrEnum):
    FOCUS = auto()
    EVADE = auto()
    BARREL_ROLL = auto()
    BOOST = auto()
    LOCK = auto()
    CALCULATE = auto()
    CLOAK = auto()
    COORDINATE = auto()
    JAM = auto()
    REINFORCE = auto()
    RELOAD = auto()
    ROTATE = auto()
    SLAM = auto()


class ActionDifficulty(StrEnum):
    WHITE = auto()
    RED = auto()
    PURPLE = auto()


class Action(msgspec.Struct):
    action_name: ActionName
    color: ActionDifficulty = ActionDifficulty.WHITE
    linked_action: 'Action | None' = None


class Arc(StrEnum):
    FRONT = auto()
    FULL_FRONT = auto()
    LEFT = auto()
    RIGHT = auto()
    REAR = auto()
    FULL_REAR = auto()
    BULLSEYE = auto()
    SINGLE_TURRET = auto()
    DOUBLE_TURRET = auto()


class Attack(msgspec.Struct):
    arc: Arc
    val: int


class AttackRequirement(StrEnum):
    FOCUS = auto()
    CALCULATE = auto()
    LOCK = auto()


class SpecialAttack(Attack, kw_only=True):
    range: set[int]
    requirement: Annotated[
        set[AttackRequirement] | None,
        msgspec.Meta(
            description='Set of requirements for the attack of which any one will suffice'
        ),
    ] = None
    is_ordnance: bool
    text: str
    automations: set[str]


class ChargeType(StrEnum):
    STANDARD = auto()
    FORCE = auto()
    ENERGY = auto()


class ChargeValues(msgspec.Struct):
    limit: int
    recurring_val: int = 0


class Card(msgspec.Struct, kw_only=True, frozen=True):
    id: str
    amg_cost: int | None = None
    xwa_cost: int
    xwa_restricted_count: Annotated[
        int | None, msgspec.Meta(description='Maximum number of this card allowed in XWA games')
    ] = None


class Keyword(StrEnum):
    A_WING = 'A-wing'
    B_WING = 'B-wing'
    X_WING = 'X-wing'
    Y_WING = 'Y-wing'
    YT_1300 = 'YT-1300'
    TIE = 'TIE'
    FREIGHTER = 'Freighter'
    LIGHT_SIDE = 'Light Side'
    DARK_SIDE = 'Dark Side'
    BOUNTY_HUNTER = 'Bounty Hunter'
    CLONE = 'Clone'
    DROID = 'Droid'
    JEDI = 'Jedi'
    MANDALORIAN = 'Mandalorian'
    PARTISAN = 'Partisan'
    SITH = 'Sith'
    SPECTRE = 'Spectre'
