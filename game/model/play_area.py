from typing import Final

import msgspec

from game.measurement import Distance
from game.measurement.measurement import Size

DEFAULT_PLAY_AREA_SIZE: Final[Size] = Size(width=914.4, height=914.4)


class PlayArea(msgspec.Struct, kw_only=True, frozen=True):
    width: Distance
    height: Distance
