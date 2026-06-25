from enum import StrEnum, auto
from typing import Annotated

from game.measurement.measurement import Size
import msgspec

from discord_helpers.emoji import get_emoji


class Ability(msgspec.Struct, kw_only=True):
    name: str | None = None
    text: str
    automations: list[str]
    is_action: bool


class ActionName(StrEnum):
    FOCUS = auto()
    CALCULATE = auto()
    EVADE = auto()
    BARREL_ROLL = auto()
    BOOST = auto()
    LOCK = auto()
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


class Action(msgspec.Struct, frozen=True):
    action_name: ActionName
    color: ActionDifficulty = ActionDifficulty.WHITE
    linked_action: 'Action | None' = None

    @property
    def emoji(self) -> str:
        emoji_name: str = self.action_name if self.action_name != 'lock' else 'target_lock'
        if self.color != ActionDifficulty.WHITE:
            emoji_name += f'_{self.color}'
        emoji_str: str = get_emoji(emoji_name)

        if self.linked_action:
            emoji_str += f' ► {self.linked_action.emoji}'
        return emoji_str


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

    def __str__(self):
        return get_emoji(f'{self.value}_arc_txt')

    @property
    def emoji(self) -> str:
        return get_emoji(f'{self.value}_arc')


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
    text: str | None = None
    automations: list[str]


class ChargeType(StrEnum):
    STANDARD = auto()
    FORCE = auto()


class ChargeValues(msgspec.Struct):
    limit: int
    recurring_val: int = 0


class Card(msgspec.Struct, kw_only=True, frozen=True):
    id_: str
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
