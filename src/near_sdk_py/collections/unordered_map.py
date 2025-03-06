"""
UnorderedMap collection for NEAR smart contracts.
"""

from typing import Any, Iterator, Tuple  # Keep typing for docs

import near

from .adapter import CollectionStorageAdapter
from .base import PrefixType
from .lookup_map import LookupMap
from .vector import Vector


class UnorderedMap(LookupMap):
    """
    An iterable persistent map implementation for NEAR.

    Similar to Python's dict with full iteration support.
    Uses additional storage to track keys for iteration.
    """

    def __init__(self, prefix: str):
        """
        Initialize a new UnorderedMap with the given prefix.

        Args:
            prefix: A unique string prefix for this collection
        """
        super().__init__(prefix)
        # Override the collection type
        self._update_metadata({"type": PrefixType.UNORDERED_MAP})

        # Key for storing the list of keys
        self._keys_prefix = f"{prefix}:keys"
        self._keys_vector = Vector(self._keys_prefix)

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Set the value for the given key and track the key for iteration.

        Args:
            key: The key to set
            value: The value to store
        """
        storage_key = self._make_key(key)
        exists = near.storage_has_key(storage_key)

        # Store the value
        CollectionStorageAdapter.write(storage_key, value)

        # Track the key if it's new
        if not exists:
            self._keys_vector.append(key)
            self._set_length(len(self) + 1)

    def __delitem__(self, key: Any) -> None:
        """
        Remove the given key and untrack it.

        Args:
            key: The key to remove

        Raises:
            KeyError: If the key doesn't exist
        """
        storage_key = self._make_key(key)

        if not near.storage_has_key(storage_key):
            raise KeyError(key)

        # Remove the value
        CollectionStorageAdapter.remove(storage_key)

        # Find and remove the key from the keys vector
        for i, k in enumerate(self._keys_vector):
            if k == key:
                self._keys_vector.swap_remove(i)
                break

        self._set_length(len(self) - 1)

    def __iter__(self) -> Iterator:
        """Return an iterator over the keys"""
        return iter(self._keys_vector)

    def keys(self) -> Iterator[Any]:
        """Return an iterator over the keys"""
        return iter(self._keys_vector)

    def values(self) -> Iterator[Any]:
        """Return an iterator over the values"""
        for key in self._keys_vector:
            yield self[key]

    def items(self) -> Iterator[Tuple[Any, Any]]:
        """Return an iterator over the (key, value) pairs"""
        for key in self._keys_vector:
            yield (key, self[key])

    def clear(self) -> None:
        """Remove all elements from the map"""
        # Clear all values
        for key in self._keys_vector:
            storage_key = self._make_key(key)
            CollectionStorageAdapter.remove(storage_key)

        # Clear the keys vector
        self._keys_vector.clear()

        # Reset length
        self._set_length(0)


# Define IterableMap as an alias for UnorderedMap for compatibility
IterableMap = UnorderedMap
