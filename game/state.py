from functools import singledispatch

import discord
import msgspec

from game import config
from game.model.gamestate import GameState


def get_game_id_from_channel(game_channel: discord.TextChannel) -> str:
    """
    Extracts the game ID from the channel name.
    All game channels start with the game ID.

    :param game_channel: The Discord text channel for the game
    :type game_channel: discord.TextChannel
    :return: The ID of the game
    :rtype: str
    """
    name = game_channel.name
    return name.split("-")[0] if "-" in name else name


def _get_game_state_path_for_game_id(game_id: str) -> str:
    game_state_path = config.get_game_state_path()
    return f"{game_state_path}/{game_id}.json"


@singledispatch
def get_game_state(identifier) -> GameState:
    """
    Retrieves the game state from disk.

    :param identifier: Either a discord.TextChannel or a string ID
    :type game_channel: discord.TextChannel | str
    :return: The struct representing the state of the game
    :rtype: GameState
    """
    raise NotImplementedError()


@get_game_state.register
def _(game_channel: discord.TextChannel) -> GameState:
    game_id = get_game_id_from_channel(game_channel)
    with open(_get_game_state_path_for_game_id(game_id), "r") as file:
        file_bytes = file.read()
        return msgspec.json.decode(file_bytes, type=GameState)


@get_game_state.register
def _(game_id: str) -> GameState:
    with open(_get_game_state_path_for_game_id(game_id), "r") as file:
        file_bytes = file.read()
        return msgspec.json.decode(file_bytes, type=GameState)


@singledispatch
def update(identifier, game_state: GameState) -> None:
    """
    Updates the game state to disk for the given game channel or the game ID.

    :param identifier: Either a discord.TextChannel or a string ID
    :type identifier: discord.TextChannel | str
    :param game_state: The struct representing the state of the game to be updated
    :type game_state: GameState
    """
    raise NotImplementedError()


@update.register
def _(game_channel: discord.TextChannel, game_state: GameState) -> None:
    game_id = get_game_id_from_channel(game_channel)
    updated_game_state = msgspec.json.encode(game_state)
    with open(_get_game_state_path_for_game_id(game_id), "wb") as file:
        file.write(updated_game_state)


@update.register
def _(game_id: str, game_state: GameState) -> None:
    updated_game_state = msgspec.json.encode(game_state)
    with open(_get_game_state_path_for_game_id(game_id), "wb") as file:
        file.write(updated_game_state)
