import json
from pathlib import Path
from typing import Any, Callable, Iterator

import pytest

from main import AsyncXwingBot


# Patch the Sentinel object BEFORE importing the bot.
#  This prevents 'is_set' attribute crashes across all discord.py internal classes.
from discord.utils import _MissingSentinel

_MissingSentinel.is_set = lambda *args, **kwargs: True  # type: ignore[attr-defined]


@pytest.fixture(scope='session')
def bot() -> Iterator[AsyncXwingBot]:
    bot = AsyncXwingBot(
        prefix='$',
        ext_dir='cogs',
        application_id=123456789012345678,  # placeholder to prevent the tree lookup failure
    )

    yield bot


@pytest.fixture(scope='session')
def get_squad_data_for_player() -> Callable[[str, str], dict[str | int, Any]]:
    def _getter(username: str, test_filename: str) -> dict[str | int, Any]:
        test_game_state_filepath = Path(__file__).parent / f'resources/{test_filename}'
        return json.loads(test_game_state_filepath.read_bytes())['players'][username]['squad']

    return _getter
