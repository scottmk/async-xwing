import msgspec


class ConditionCard(msgspec.Struct, kw_only=True, frozen=True):
    id_: str
    name: str
    is_unique: bool
    limit: int
    text: str
    automations: list[str] | None = None
