import msgspec

from discord_helpers.emoji import get_emoji
from game.model import Faction, Ship


class Player(msgspec.Struct, kw_only=True):
    name: str
    faction: Faction
    squad: dict[int, Ship]

    def _get_str_header(self) -> str:
        return f"## {get_emoji(self.faction)} {self.name}'s ships\n"

    def _get_ship_str(self, ship_id: int, ship: Ship) -> str:
        return f'## Ship #{ship_id}:\n{ship.pretty_str()}\n'

    def __str__(self) -> str:
        str_repr = self._get_str_header()

        for ship_id, ship in self.squad.items():
            str_repr += self._get_ship_str(ship_id, ship)
        return str_repr

    def to_chunked_str(self) -> list[str]:
        chunked_str: list[str] = []
        chunked_str.append(f'{self._get_str_header()}')
        chunked_str.extend(
            [self._get_ship_str(ship_id, ship) for ship_id, ship in self.squad.items()]
        )
        return chunked_str
