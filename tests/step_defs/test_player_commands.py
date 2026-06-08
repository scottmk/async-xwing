import asyncio
from collections.abc import Callable
from pathlib import Path
import shutil
from typing import Any
from unittest.mock import AsyncMock, MagicMock, _Call

import discord
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from discord.ext import commands

from cogs.player import PlayerCog
from tests.helpers import assert_ship_stats_message_matches_json


# Link the BDD scenario to the feature file
scenarios('../features/player_commands.feature')


@pytest.fixture
def context() -> dict[str, Any]:
    return {}


@given('the bot is running and ready')
def bot_is_ready(bot: commands.Bot) -> None:
    pass


@given(parsers.cfparse('I am a player "{username}" with two ships "{ship1_num}" and "{ship2_num}"'))
def setup_two_ships_player(
    username: str,
    ship1_num: int,
    ship2_num: int,
    context: dict[str, Any],
    get_squad_data_for_player: Callable[[str, str], dict[str | int, Any]],
) -> None:
    test_game_state_filepath = (
        Path(__file__).parent.parent / 'resources/axw_test_1player_2ships.json'
    )
    dest_filepath = Path(__file__).parent.parent.parent / 'data/gamestates/axw_test.json'
    shutil.copy(test_game_state_filepath, dest_filepath)

    squad = get_squad_data_for_player(username, 'axw_test_1player_2ships.json')
    context['expected_ship1'] = squad[ship1_num]
    context['expected_ship2'] = squad[ship2_num]


@when(parsers.cfparse('I execute the "/player stats" command for "{username}"'))
def execute_player_stats(bot: commands.Bot, username: str, context: dict[str, Any]) -> None:
    cog = PlayerCog(bot)

    mock_interaction: MagicMock = MagicMock(spec=discord.Interaction)
    mock_interaction.response = MagicMock(spec=discord.InteractionResponse)

    mock_user = MagicMock(spec=discord.Member)
    mock_user.name = username
    mock_user.display_name = username
    mock_user.id = 9876543210
    mock_interaction.user = mock_user

    mock_header_msg = MagicMock(spec=discord.Message)
    mock_header_msg.id = 555666777
    mock_send_header = MagicMock(spec=discord.Webhook)
    mock_send_header.send = AsyncMock(return_value=mock_header_msg)
    mock_interaction.followup = mock_send_header
    context['mock_send_header'] = mock_send_header

    mock_channel: MagicMock = MagicMock(spec=discord.TextChannel)
    mock_channel.name = 'axw_test-fun-test-game'
    mock_interaction.channel = mock_channel

    mock_thread: MagicMock = MagicMock(spec=discord.Thread)
    mock_create_thread: AsyncMock = AsyncMock(return_value=mock_thread)
    mock_channel.create_thread = mock_create_thread
    context['mock_create_thread'] = mock_create_thread

    mock_thread_send: AsyncMock = AsyncMock()
    mock_thread.send = mock_thread_send
    context['mock_thread_send'] = mock_thread_send

    event_loop = asyncio.new_event_loop()
    try:
        coroutine = cog.get_player_stats.callback(cog, mock_interaction)  # type: ignore[arg-type, reportArgumentType]
        event_loop.run_until_complete(coroutine)
    finally:
        event_loop.close()


@then(parsers.cfparse('the bot should post a header message for "{username}"'))
def verify_header_message(username: str, context: dict[str, Any]) -> None:
    mock_send_function: AsyncMock = context['mock_send_header'].send
    mock_send_function.assert_called_once()

    mock_send_function_positional_args: tuple = mock_send_function.call_args[0]
    actual_header_message: str = mock_send_function_positional_args[0]
    expected_format = f"{username}'s ships\n"
    # Using endswith here because I don't wanna mess with grabbing the correct faction emoji
    assert actual_header_message.endswith(expected_format)


@then(parsers.cfparse('the bot should create a thread named "{expected_name}"'))
def verify_thread_creation(expected_name: str, context: dict[str, Any]) -> None:
    mock_create_thread: AsyncMock = context['mock_create_thread']
    mock_create_thread.assert_called_once()

    assert mock_create_thread.call_args.kwargs['name'] == expected_name


@then(
    parsers.cfparse(
        'the bot should print "{ship1_num}" and "{ship2_num}" stat blocks to the thread'
    )
)
def verify_ship_stat_blocks(ship1_num: int, ship2_num: int, context: dict[str, Any]) -> None:
    mock_thread_send: AsyncMock = context['mock_thread_send']

    # Fetch all messages sent to the mock thread
    calls: list[_Call] = mock_thread_send.call_args_list
    actual_messages: list[str] = [call[0][0] for call in calls if call]

    assert len(actual_messages) >= 2

    assert_ship_stats_message_matches_json(actual_messages[0], context['expected_ship1'])
    assert_ship_stats_message_matches_json(actual_messages[1], context['expected_ship2'])
