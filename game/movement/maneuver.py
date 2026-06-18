from dataclasses import dataclass
from enum import StrEnum, auto
from functools import cache

from discord_helpers.emoji import get_emoji

type ManeuverSpeed = int


@dataclass(kw_only=True, frozen=True)
class Maneuver:
    bearing: ManeuverBearing
    speed: ManeuverSpeed
    difficulty: ManeuverDifficulty


class ManeuverBearing(StrEnum):
    STATIONARY = auto()
    REVERSE_BANK_LEFT = auto()
    REVERSE_STRAIGHT = auto()
    REVERSE_BANK_RIGHT = auto()
    SEGNORS_LOOP_LEFT = auto()
    TALLON_ROLL_LEFT = auto()
    TURN_LEFT = auto()
    BANK_LEFT = auto()
    STRAIGHT = auto()
    BANK_RIGHT = auto()
    TURN_RIGHT = auto()
    TALLON_ROLL_RIGHT = auto()
    SEGNORS_LOOP_RIGHT = auto()
    KOIOGRAN_TURN = auto()

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            members = list(self.__class__)
            return members.index(self) < members.index(other)
        return NotImplemented

    @property
    def blue_emoji(self) -> str:
        return self.get_emoji(ManeuverDifficulty.BLUE)

    @property
    def white_emoji(self) -> str:
        return self.get_emoji(ManeuverDifficulty.WHITE)

    @property
    def red_emoji(self) -> str:
        return self.get_emoji(ManeuverDifficulty.RED)

    @property
    def purple_emoji(self) -> str:
        return self.get_emoji(ManeuverDifficulty.PURPLE)

    @cache
    def get_emoji(self, difficulty: ManeuverDifficulty) -> str:
        emoji_str: str = ''
        match self:
            case ManeuverBearing.STRAIGHT:
                emoji_str = 'maneuver_straight'
            case ManeuverBearing.BANK_LEFT:
                emoji_str = 'maneuver_bank_left'
            case ManeuverBearing.BANK_RIGHT:
                emoji_str = 'maneuver_bank_right'
            case ManeuverBearing.TURN_LEFT:
                emoji_str = 'maneuver_turn_left'
            case ManeuverBearing.TURN_RIGHT:
                emoji_str = 'maneuver_turn_right'
            case ManeuverBearing.TALLON_ROLL_LEFT:
                emoji_str = 'maneuver_t_roll_left'
            case ManeuverBearing.TALLON_ROLL_RIGHT:
                emoji_str = 'maneuver_t_roll_right'
            case ManeuverBearing.SEGNORS_LOOP_LEFT:
                emoji_str = 'maneuver_s_loop_left'
            case ManeuverBearing.SEGNORS_LOOP_RIGHT:
                emoji_str = 'maneuver_s_loop_right'
            case ManeuverBearing.KOIOGRAN_TURN:
                emoji_str = 'maneuver_k_turn'
            case ManeuverBearing.REVERSE_BANK_LEFT:
                emoji_str = 'maneuver_rev_bank_left'
            case ManeuverBearing.REVERSE_BANK_RIGHT:
                emoji_str = 'maneuver_rev_bank_right'
            case ManeuverBearing.REVERSE_STRAIGHT:
                emoji_str = 'maneuver_rev_straight'
            case ManeuverBearing.STATIONARY:
                emoji_str = 'maneuver_stationary'

        match difficulty:
            case ManeuverDifficulty.PURPLE:
                emoji_str += '_purple'
            case ManeuverDifficulty.RED:
                emoji_str += '_red'
            case ManeuverDifficulty.BLUE:
                emoji_str += '_blue'
            case _:
                pass

        return get_emoji(emoji_str)


class ManeuverDifficulty(StrEnum):
    BLUE = auto()
    WHITE = auto()
    RED = auto()
    PURPLE = auto()
