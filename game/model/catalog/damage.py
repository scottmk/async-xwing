from enum import StrEnum, auto

import msgspec


class DamageCardType(StrEnum):
    PILOT = auto()
    SHIP = auto()


class DamageCard(msgspec.Struct, kw_only=True, frozen=True):
    id_: str
    name: str
    type_: DamageCardType
    text: str
    count: int
    automations: list[str] | None = None
