import msgspec

from game.measurement.size import Distance


class PlayArea(msgspec.Struct, kw_only=True, frozen=True):
    width: Distance
    height: Distance
