from collections.abc import MutableMapping
from typing import Generic, Iterator, TypeVar, Optional

from ..storage import Storage

KT = TypeVar('KT')
VT = TypeVar('VT')

class UnorderedMap(MutableMapping[KT, VT], Generic[KT, VT]):
    """
    An efficient key-value store that supports O(1) removals using swap-remove strategy.
    Maintains indices for fast lookups while allowing quick removals.
    """
    
    def __init__(self, prefix: str):
        self.prefix = prefix
        self._keys_prefix = f"{prefix}:keys"
        self._values_prefix = f"{prefix}:values"
        self._indices_prefix = f"{prefix}:indices"
        
        # Initialize storage if needed
        if not Storage.has(self._keys_prefix):
            Storage.set_json(self._keys_prefix, [])
            Storage.set_json(self._values_prefix, [])
            Storage.set_json(self._indices_prefix, {})
    
    def __getitem__(self, key: KT) -> VT:
        indices = Storage.get_json(self._indices_prefix) or {}
        index = indices.get(str(key))
        
        if index is None:
            raise KeyError(key)
            
        values = Storage.get_json(self._values_prefix)
        return values[index]
    
    def __setitem__(self, key: KT, value: VT) -> None:
        indices = Storage.get_json(self._indices_prefix) or {}
        keys = Storage.get_json(self._keys_prefix) or []
        values = Storage.get_json(self._values_prefix) or []
        
        str_key = str(key)
        if str_key in indices:
            # Update existing
            index = indices[str_key]
            values[index] = value
            Storage.set_json(self._values_prefix, values)
        else:
            # Insert new
            index = len(values)
            indices[str_key] = index
            keys.append(str_key)
            values.append(value)
            
            Storage.set_json(self._indices_prefix, indices)
            Storage.set_json(self._keys_prefix, keys)
            Storage.set_json(self._values_prefix, values)
    
    def __delitem__(self, key: KT) -> None:
        indices = Storage.get_json(self._indices_prefix) or {}
        str_key = str(key)
        
        if str_key not in indices:
            raise KeyError(key)
            
        index = indices[str_key]
        keys = Storage.get_json(self._keys_prefix)
        values = Storage.get_json(self._values_prefix)
        
        # Swap with last element if not last
        last_idx = len(values) - 1
        if index != last_idx:
            # Move last element to the removed position
            last_key = keys[last_idx]
            keys[index] = last_key
            values[index] = values[last_idx]
            indices[last_key] = index
        
        # Remove last element
        keys.pop()
        values.pop()
        del indices[str_key]
        
        Storage.set_json(self._indices_prefix, indices)
        Storage.set_json(self._keys_prefix, keys)
        Storage.set_json(self._values_prefix, values)
    
    def __iter__(self) -> Iterator[KT]:
        keys = Storage.get_json(self._keys_prefix) or []
        return iter(keys)
    
    def __len__(self) -> int:
        keys = Storage.get_json(self._keys_prefix) or []
        return len(keys)