from dataclasses import dataclass
from enum import Enum


type Distance = float


@dataclass(kw_only=True, frozen=True)
class Size:
    width: Distance
    height: Distance


class RangeMeasurement(Enum):
    ONE = 1
    TWO = 2
    THREE = 3

    def distance(self) -> Distance:
        return self.value * 100
