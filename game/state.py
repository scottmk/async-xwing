from functools import singledispatch
import json
from typing import Any

import discord

from game import config


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


@singledispatch
def get_game_state(identifier) -> dict[str, Any]:
    """
    Retrieves the game state from disk.

    :param identifier: Either a discord.TextChannel or a string ID
    :type game_channel: discord.TextChannel | str
    :return: Description
    :rtype: dict[str, Any]
    """
    raise NotImplementedError()


@get_game_state.register
def _(game_channel: discord.TextChannel) -> dict[str, Any]:
    game_state_path = config.get_game_state_path()
    game_id = get_game_id_from_channel(game_channel)
    with open(f"{game_state_path}/{game_id}.json", "r") as file:
        return json.load(file)


@get_game_state.register
def _(game_id: str) -> dict[str, Any]:
    game_state_path = config.get_game_state_path()
    with open(f"{game_state_path}/{game_id}.json", "r") as file:
        return json.load(file)


@singledispatch
def update(identifier, game_state: dict[str, Any]) -> None:
    """
    Updates the game state to disk for the given game channel or the game ID.

    :param identifier: Either a discord.TextChannel or a string ID
    :type identifier: discord.TextChannel | str
    :param game_state: The dictionary representing the state of the game to be updated
    :type game_state: dict[str, Any]
    """
    raise NotImplementedError()


@update.register
def _(game_channel: discord.TextChannel, game_state: dict[str, Any]) -> None:
    game_state_path = config.get_game_state_path()
    game_id = get_game_id_from_channel(game_channel)
    with open(f"{game_state_path}/{game_id}.json", "w") as file:
        json.dump(game_state, file)


@update.register
def _(game_id: str, game_state: dict[str, Any]) -> None:
    game_state_path = config.get_game_state_path()
    with open(f"{game_state_path}/{game_id}.json", "w") as file:
        json.dump(game_state, file)
