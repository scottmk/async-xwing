import msgspec


class GameState(msgspec.Struct):
    game_id: str
    game_name: str | None = None
