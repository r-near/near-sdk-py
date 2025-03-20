"""
UnorderedMap collection for NEAR smart contracts optimized with Rust-like semantics.
Uses separate vectors for keys and values with index tracking for O(1) operations.
"""

from typing import Any, Iterator, Optional, Tuple

from .adapter import CollectionStorageAdapter
from .base import Collection, PrefixType
from .vector import Vector


class UnorderedMap(Collection):
    """
    A persistent map optimized for NEAR with efficient insertion, deletion, and iteration.
    Mimics Rust's UnorderedMap using key and value vectors with index tracking.
    """

    def __init__(self, prefix: str):
        """
        Initialize a new UnorderedMap with the given prefix.

        Args:
            prefix: A unique string prefix for storage keys.
        """
        super().__init__(prefix, PrefixType.UNORDERED_MAP)
        self.prefix = prefix
        self.keys_vector = Vector(f"{prefix}_keys")  # Stores keys in order
        self.values_vector = Vector(f"{prefix}_vals")  # Stores values in order
        self.index_prefix = f"{prefix}_indices"  # Maps key -> index in vectors

    def _serialize_key(self, key: Any) -> bytes:
        """Serialize key deterministically (replace with Borsh or similar)."""
        return str(key).encode()

    def _index_key(self, key: Any) -> str:
        """Generate storage key for the index of a given key."""
        serialized = self._serialize_key(key)
        return f"{self.index_prefix}:{serialized.hex()}"

    def __setitem__(self, key: Any, value: Any) -> None:
        """Insert or update a key-value pair."""
        index_storage_key = self._index_key(key)
        existing_index = CollectionStorageAdapter.read(index_storage_key)

        if existing_index is not None:
            # Update existing value
            self.values_vector[existing_index] = value
        else:
            # Append new entry
            new_index = len(self.keys_vector)
            self.keys_vector.append(key)
            self.values_vector.append(value)
            CollectionStorageAdapter.write(index_storage_key, new_index)

    def __delitem__(self, key: Any) -> None:
        """Remove a key-value pair using swap_remove for O(1) operation."""
        index_storage_key = self._index_key(key)
        index = CollectionStorageAdapter.read(index_storage_key)

        if index is None:
            raise KeyError(key)

        # Perform swap_remove on both vectors
        last_idx = len(self.keys_vector) - 1
        last_key = self.keys_vector[last_idx]

        self.keys_vector.swap_remove(index)
        self.values_vector.swap_remove(index)

        # Update the index of the last element if it was moved
        if index != last_idx:
            last_key_index = self._index_key(last_key)
            CollectionStorageAdapter.write(last_key_index, index)

        # Remove the index entry for the deleted key
        CollectionStorageAdapter.remove(index_storage_key)

    def __getitem__(self, key: Any) -> Any:
        """Retrieve the value for a key."""
        index_storage_key = self._index_key(key)
        index = CollectionStorageAdapter.read(index_storage_key)
        if index is None:
            raise KeyError(key)
        return self.values_vector[index]

    def __len__(self) -> int:
        """Return the number of elements in the map."""
        return len(self.keys_vector)

    def __iter__(self) -> Iterator[Any]:
        """Iterate over keys in insertion-agnostic order (due to swaps)."""
        return iter(self.keys_vector)

    def keys(self) -> Iterator[Any]:
        """Return an iterator over keys."""
        return self.__iter__()

    def values(self) -> Iterator[Any]:
        """Return an iterator over values."""
        return iter(self.values_vector)

    def items(
        self, start: int = 0, limit: Optional[int] = None
    ) -> Iterator[Tuple[Any, Any]]:
        """
        Efficient paginated iteration using vector indices, similar to Rust's seek/take.

        Args:
            start: Starting index (0-based)
            limit: Maximum number of items to return

        Yields:
            (key, value) tuples
        """
        total_len = len(self.keys_vector)

        # Handle negative start (Python-style slicing)
        if start < 0:
            start += total_len
        start = max(start, 0)

        # Calculate end index
        end = start + (limit if limit is not None else total_len)
        end = min(end, total_len)

        # Direct index-based access for efficient pagination
        for i in range(start, end):
            yield (self.keys_vector[i], self.values_vector[i])

    def seek(
        self, start: int = 0, limit: Optional[int] = None
    ) -> Iterator[Tuple[Any, Any]]:
        """Alias for items() with Rust-style naming"""
        return self.items(start, limit)

    def clear(self) -> None:
        """Remove all elements from the map."""
        # Remove all indices
        for key in self.keys_vector:
            CollectionStorageAdapter.remove(self._index_key(key))

        # Clear vectors
        self.keys_vector.clear()
        self.values_vector.clear()

    def get(self, key: Any, default: Optional[Any] = None) -> Any:
        """Safely get a value or return default if missing."""
        try:
            return self[key]
        except KeyError:
            return default

    def remove(self, key: Any) -> Optional[Any]:
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
        except Exception:
            return None

    def __contains__(self, key: Any) -> bool:
        """Check if the key exists in the map."""
        return CollectionStorageAdapter.has(self._index_key(key))

    def is_empty(self) -> bool:
        return self.keys_vector.is_empty() and self.values_vector.is_empty()


IterableMap = UnorderedMap
