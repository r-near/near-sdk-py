from collections.abc import MutableMapping
from typing import Any, Generic, Iterator, Optional, TypeVar

from ..storage import Storage

KT = TypeVar('KT')
VT = TypeVar('VT')

class LookupMap(MutableMapping[KT, VT], Generic[KT, VT]):
    """
    A persistent dictionary-like collection that implements the MutableMapping interface.
    Keys are stored with a prefix to provide namespace separation for different collections.
    """
    
    def __init__(self, prefix: str):
        self.prefix = prefix
        self._keys_prefix = f"{prefix}:keys"
        
        # Initialize keys set if it doesn't exist
        if not Storage.has(self._keys_prefix):
            Storage.set_json(self._keys_prefix, [])
    
    def _get_key(self, key: KT) -> str:
        """Convert a key into its storage representation"""
        return f"{self.prefix}:{str(key)}"
    
    def __getitem__(self, key: KT) -> VT:
        storage_key = self._get_key(key)
        value = Storage.get_json(storage_key)
        if value is None:
            raise KeyError(key)
        return value
    
    def __setitem__(self, key: KT, value: VT) -> None:
        storage_key = self._get_key(key)
        if not Storage.has(storage_key):
            keys = Storage.get_json(self._keys_prefix) or []
            keys.append(str(key))
            Storage.set_json(self._keys_prefix, keys)
        Storage.set_json(storage_key, value)
    
    def __delitem__(self, key: KT) -> None:
        storage_key = self._get_key(key)
        if not Storage.has(storage_key):
            raise KeyError(key)
        Storage.remove(storage_key