from enum import IntEnum

from game.measurement.distance import Distance


class RangeMeasurement(IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3

    def distance(self) -> Distance:
        return float(self.value * 100)
