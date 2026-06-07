from functools import cache
from pathlib import Path
from typing import Generic, TypeVar

import msgspec

from abc import ABC, ABCMeta, abstractmethod


CATALOG_ROOT_PATH: Path = Path('./resources/')


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
    def _get_manifest(cls) -> dict[str, str]:
        dirpath: Path = CATALOG_ROOT_PATH / cls.card_type()
        manifest_filepath: Path = dirpath / 'manifest.yaml'
        if not manifest_filepath.is_file():
            return {}
        return msgspec.yaml.decode(manifest_filepath.read_bytes(), type=dict[str, str])

    @classmethod
    @cache
    @abstractmethod
    def _read_card_file(cls, type_: str | None = None) -> dict[str, T_Struct]:
        pass

    @classmethod
    def _lookup_catalog_entry(cls, id_: str) -> T_Struct | None:
        type_: str | None = cls._get_manifest().get(id_)
        return cls._read_card_file(type_).get(id_)


class MutableBaseStruct(msgspec.Struct, BaseStruct):
    id_: str


class FrozenBaseStruct(msgspec.Struct, BaseStruct, frozen=True):
    id_: str
