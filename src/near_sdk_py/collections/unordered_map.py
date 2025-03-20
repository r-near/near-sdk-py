"""
UnorderedMap collection for NEAR smart contracts.
"""

from typing import Any, Iterator, Optional, Tuple  # Keep typing for docs

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
        # Add a key_index_prefix for the index lookup
        self._indices_prefix = f"{prefix}:indices"  # New prefix for tracking indices

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
            # Add key to vector and store its index
            index = len(self._keys_vector)
            self._keys_vector.append(key)
            index_key = self._make_index_key(key)
            CollectionStorageAdapter.write(index_key, index)
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

        # Get the index of the key in the vector
        index_key = self._make_index_key(key)
        if not near.storage_has_key(index_key):
            # Fallback to linear search if index not found (should not happen)
            for i, k in enumerate(self._keys_vector):
                if k == key:
                    self._keys_vector.swap_remove(i)
                    break
        else:
            # Use the stored index for O(1) deletion
            index = CollectionStorageAdapter.read(index_key)
            assert index is not None  # Only for mypy
            if index < len(self._keys_vector):
                # If we do a swap_remove, we need to update the index of the key that gets moved
                if index != len(self._keys_vector) - 1:  # Not removing the last element
                    # Get the key that will be moved from the end
                    moved_key = self._keys_vector[len(self._keys_vector) - 1]
                    # Update its index in the storage
                    moved_key_index = self._make_index_key(moved_key)
                    CollectionStorageAdapter.write(moved_key_index, index)

                # Remove the key from the vector
                self._keys_vector.swap_remove(index)

            # Remove the index mapping
            CollectionStorageAdapter.remove(index_key)

        # Remove the value and decrease length
        CollectionStorageAdapter.remove(storage_key)
        self._set_length(len(self) - 1)

    def _make_index_key(self, key: Any) -> str:
        """Create a storage key for the index of a key"""
        return f"{self._indices_prefix}:{key}"

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

    def items(
        self, start_index: int = 0, limit: Optional[int] = None
    ) -> Iterator[Tuple[Any, Any]]:
        """
        Return an iterator over the (key, value) pairs with pagination support.

        Args:
            start_index: Index to start iterating from (0-based)
            limit: Maximum number of items to return

        Returns:
            Iterator over (key, value) pairs
        """
        keys_count = len(self._keys_vector)

        if start_index >= keys_count:
            return

        end_index = (
            keys_count if limit is None else min(start_index + limit, keys_count)
        )

        for i in range(start_index, end_index):
            key = self._keys_vector[i]
            yield (key, self[key])

    def seek(
        self, start_index: int = 0, limit: Optional[int] = None
    ) -> Iterator[Tuple[Any, Any]]:
        """
        Efficiently seek to a specific position and return items.

        Args:
            start_index: Index to start from (0-based)
            limit: Maximum number of items to return

        Returns:
            Iterator over (key, value) pairs
        """
        return self.items(start_index, limit)

    def clear(self) -> None:
        """Remove all elements from the map"""
        # Clear all values and indices
        for key in self._keys_vector:
            storage_key = self._make_key(key)
            CollectionStorageAdapter.remove(storage_key)

            index_key = self._make_index_key(key)
            CollectionStorageAdapter.remove(index_key)

        # Clear the keys vector
        self._keys_vector.clear()

        # Reset length
        self._set_length(0)


# Define IterableMap as an alias for UnorderedMap for compatibility
IterableMap = UnorderedMap
