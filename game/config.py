import os
from enum import StrEnum
from pathlib import Path

from dotenv import set_key


class ConfigKey(StrEnum):
    GAME_NUMBER = "GAME_NUMBER"
    GAME_STATE_PATH = "GAME_STATE_PATH"
    TOKEN = "TOKEN"


def get_value(key: ConfigKey, default_val: str = "") -> str:
    return os.getenv(key.value, default_val)


def get_game_state_path() -> str:
    return os.getenv(ConfigKey.GAME_STATE_PATH, "")


def increment_game_number():
    env_file_path = Path("./.env")
    # Create the file if it does not exist.
    env_file_path.touch(mode=0o600, exist_ok=True)
    game_number: int = int(get_value(ConfigKey.GAME_NUMBER, "0"))
    set_key(
        dotenv_path=env_file_path,
        key_to_set=ConfigKey.GAME_NUMBER,
        value_to_set=str(game_number + 1),
    )
