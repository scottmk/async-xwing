from dataclasses import dataclass

from game.measurement.distance import Distance


@dataclass(kw_only=True, frozen=True)
class Size:
    width: Distance
    height: Distance
