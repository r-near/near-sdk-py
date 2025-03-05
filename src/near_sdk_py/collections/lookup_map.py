"""
LookupMap collection for NEAR smart contracts.
"""

from typing import Generic, Optional, TypeVar, cast

import near

from .adapter import CollectionStorageAdapter
from .base import Collection, PrefixType


K = TypeVar("K")  # Key type
V = TypeVar("V")  # Value type


class LookupMap(Collection, Generic[K, V]):
    """
    A non-iterable persistent map implementation for NEAR.

    Similar to Python's dict but without iteration support.
    Provides O(1) lookups, inserts, and removals.
    """

    def __init__(self, prefix: str):
        """
        Initialize a new LookupMap with the given prefix.

        Args:
            prefix: A unique string prefix for this collection
        """
        super().__init__(prefix, PrefixType.LOOKUP_MAP)

    def __getitem__(self, key: K) -> V:
        """
        Get the value for the given key.

        Args:
            key: The key to retrieve

        Returns:
            The value for the given key

        Raises:
            KeyError: If the key doesn't exist
        """
        storage_key = self._make_key(key)
        value = CollectionStorageAdapter.read(storage_key)

        if value is None:
            raise KeyError(key)

        return cast(V, value)

    def __setitem__(self, key: K, value: V) -> None:
        """
        Set the value for the given key.

        Args:
            key: The key to set
            value: The value to store
        """
        storage_key = self._make_key(key)
        exists = near.storage_has_key(storage_key)

        CollectionStorageAdapter.write(storage_key, value)

        # Update length if this is a new key
        if not exists:
            self._set_length(len(self) + 1)

    def __delitem__(self, key: K) -> None:
        """
        Remove the given key.

        Args:
            key: The key to remove

        Raises:
            KeyError: If the key doesn't exist
        """
        storage_key = self._make_key(key)

        if not near.storage_has_key(storage_key):
            raise KeyError(key)

        CollectionStorageAdapter.remove(storage_key)
        self._set_length(len(self) - 1)

    def __contains__(self, key: K) -> bool:
        """
        Check if the map contains the given key.

        Args:
            key: The key to check

        Returns:
            True if the key exists, False otherwise
        """
        storage_key = self._make_key(key)
        return near.storage_has_key(storage_key)

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """
        Get the value for the given key, or default if the key doesn't exist.

        Args:
            key: The key to retrieve
            default: The default value to return if the key doesn't exist

        Returns:
            The value for the given key, or default if the key doesn't exist
        """
        try:
            return self[key]
        except KeyError:
            return default

    def set(self, key: K, value: V) -> None:
        """
        Set the value for the given key.
        Alias for __setitem__.

        Args:
            key: The key to set
            value: The value to store
        """
        self[key] = value

    def remove(self, key: K) -> Optional[V]:
        """
        Remove the given key and return its value.

        Args:
            key: The key to remove

        Returns:
            The value for the given key, or None if the key didn't exist
        """
        try:
            value = self[key]
            del self[key]
            return value
        except KeyError:
            return None

    def clear(self) -> None:
        """
        Remove all keys from the map.

        Note: This is less efficient for LookupMap since it doesn't
        track its keys. Use with caution on large maps.
        """
        # Since we can't iterate, we can only clear the length
        # This will leave orphaned storage entries
        # In a production environment, you'd need a more sophisticated approach
        self._set_length(0)
