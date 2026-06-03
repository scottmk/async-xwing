from enum import StrEnum
from game.model.play_area import PlayArea, DEFAULT_PLAY_AREA_SIZE

__all__ = ['Faction', 'PlayArea', 'DEFAULT_PLAY_AREA_SIZE']


class Faction(StrEnum):
    REBEL_ALLIANCE = 'rebellion'
    GALACTIC_EMPIRE = 'empire'
    SCUM_AND_VILLAINY = 'scum'
    RESISTANCE = 'resistance'
    FIRST_ORDER = 'first_order'
    GALACTIC_REPUBLIC = 'republic'
    SEPARATIST_ALLIANCE = 'separatists'
