from dataclasses import dataclass
from enum import StrEnum, auto

type ManeuverSpeed = int


@dataclass(kw_only=True, frozen=True)
class Maneuver:
    bearing: ManeuverBearing
    speed: ManeuverSpeed
    difficulty: ManeuverDifficulty


class ManeuverBearing(StrEnum):
    STRAIGHT = auto()
    REVERSE_STRAIGHT = auto()
    BANK_LEFT = auto()
    BANK_RIGHT = auto()
    REVERSE_BANK_LEFT = auto()
    REVERSE_BANK_RIGHT = auto()
    TURN_LEFT = auto()
    TURN_RIGHT = auto()
    KOIOGRAN_TURN = auto()
    SEGNORS_LOOP_LEFT = auto()
    SEGNORS_LOOP_RIGHT = auto()
    TALLON_ROLL_LEFT = auto()
    TALLON_ROLL_RIGHT = auto()
    STATIONARY = auto()


class ManeuverDifficulty(StrEnum):
    BLUE = auto()
    WHITE = auto()
    RED = auto()
