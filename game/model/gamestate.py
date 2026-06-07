import msgspec

from game.model.player import Player


class GameState(msgspec.Struct, kw_only=True):
    game_id: str
    game_name: str | None = None
    players: dict[str, Player] = {}
