from functools import cache
import os
from pathlib import Path
from typing import Generic, TypeVar

import msgspec

from abc import ABC, ABCMeta, abstractmethod

catalog_root_path_str = os.getenv('CATALOG_ROOT_PATH')
if catalog_root_path_str is None:
    raise Exception('CATALOG_ROOT_PATH not set in .env')
CATALOG_ROOT_PATH: Path = Path(catalog_root_path_str)


class BaseStructMeta(msgspec.StructMeta, ABCMeta):
    pass


T_Struct = TypeVar('T_Struct', bound=msgspec.Struct, covariant=True)


class BaseStruct(ABC, Generic[T_Struct], metaclass=BaseStructMeta):
    id_: str

    def get_catalog_entry(self) -> T_Struct | None:
        """Get the corresponding catalog entry for this struct."""
        return self._lookup_catalog_entry(self.id_)

    @classmethod
    def get_catalog_entry_for_id(cls, id_: str) -> T_Struct | None:
        """Get the corresponding catalog entry for the given ID."""
        return cls._lookup_catalog_entry(id_)

    @staticmethod
    @abstractmethod
    def card_type() -> str:
        pass

    @classmethod
    @cache
    def _get_manifest(cls) -> dict[str, dict[str, str]]:
        dirpath: Path = CATALOG_ROOT_PATH / cls.card_type()
        manifest_filepath: Path = dirpath / 'manifest.yaml'
        if not manifest_filepath.is_file():
            return {}
        return msgspec.yaml.decode(manifest_filepath.read_bytes(), type=dict[str, dict[str, str]])

    @classmethod
    @cache
    @abstractmethod
    def _read_card_file(cls, type_: str | None = None) -> dict[str, T_Struct]:
        pass

    @classmethod
    def _lookup_catalog_entry(cls, id_: str) -> T_Struct | None:
        type_: str | None = entry.get('type') if (entry := cls._get_manifest().get(id_)) else None
        return cls._read_card_file(type_).get(id_)


class MutableBaseStruct(msgspec.Struct, BaseStruct):
    id_: str


class FrozenBaseStruct(msgspec.Struct, BaseStruct, frozen=True):
    id_: str
