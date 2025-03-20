"""
UnorderedSet collection for NEAR smart contracts.
"""

from typing import Any, Iterator, Optional  # Keep typing for docs

import near

from .adapter import CollectionStorageAdapter
from .base import PrefixType
from .lookup_set import LookupSet
from .vector import Vector


class UnorderedSet(LookupSet):
    """
    An iterable persistent set implementation for NEAR.

    Similar to Python's set with full iteration support.
    Uses additional storage to track values for iteration.
    """

    def __init__(self, prefix: str):
        """
        Initialize a new UnorderedSet with the given prefix.

        Args:
            prefix: A unique string prefix for this collection
        """
        super().__init__(prefix)
        # Override the collection type
        self._update_metadata({"type": PrefixType.UNORDERED_SET})

        # Vector for storing the values for iteration
        self._values_prefix = f"{prefix}:values"
        self._values_vector = Vector(self._values_prefix)
        # dict for storing value -> index.  Key is serialized value.
        self._indices_prefix = f"{prefix}:indices"  # New prefix for tracking indices

    def add(self, value: Any) -> None:
        """
        Add a value to the set and track it for iteration.

        Args:
            value: The value to add
        """
        storage_key = self._make_key(value)
        exists = near.storage_has_key(storage_key)

        if not exists:
            # Store the marker
            CollectionStorageAdapter.write(storage_key, True)
            # Track the value and get its index
            index = len(self._values_vector)
            self._values_vector.append(value)
            # Store index, using raw value as key
            index_key = self._make_index_key(value)
            CollectionStorageAdapter.write(index_key, index)
            self._set_length(len(self) + 1)

    def remove(self, value: Any) -> None:
        """
        Remove a value from the set and untrack it.  O(1) time complexity.

        Args:
            value: The value to remove

        Raises:
            KeyError: If the value doesn't exist
        """
        storage_key = self._make_key(value)

        if not near.storage_has_key(storage_key):
            raise KeyError(value)

        # Get the index of the value in the vector
        index_key = self._make_index_key(value)
        if not near.storage_has_key(index_key):
            raise Exception("Inconsistent contract state: value index not found.")

        index = CollectionStorageAdapter.read(index_key)
        assert index is not None, "Inconsistent contract state: value index not found."

        if index < len(self._values_vector):
            # If we do a swap_remove, we need to update the index of the key that gets moved
            if index != len(self._values_vector) - 1:  # Not removing the last element
                # Get the key that will be moved from the end
                moved_key = self._values_vector[len(self._values_vector) - 1]
                # Update its index in the storage
                moved_key_index = self._make_index_key(moved_key)
                CollectionStorageAdapter.write(moved_key_index, index)

            # Remove the key from the vector
            self._values_vector.swap_remove(index)

        # Remove the index mapping
        CollectionStorageAdapter.remove(index_key)

        # Remove the value and decrease length
        CollectionStorageAdapter.remove(storage_key)
        self._set_length(len(self) - 1)

    def _make_index_key(self, key: Any) -> str:
        """Create a storage key for the index of a key"""
        return f"{self._indices_prefix}:{key}"

    def __iter__(self) -> Iterator:
        """Return an iterator over the values"""
        return iter(self.values())

    def values(
        self, start_index: int = 0, limit: Optional[int] = None
    ) -> Iterator[Any]:
        """
        Return an iterator over the values with pagination support.

        Args:
            start_index: Index to start iterating from (0-based)
            limit: Maximum number of values to return

        Returns:
            Iterator over values
        """
        values_count = len(self._values_vector)

        if start_index >= values_count:
            return

        end_index = (
            values_count if limit is None else min(start_index + limit, values_count)
        )

        for i in range(start_index, end_index):
            yield self._values_vector[i]

    def seek(self, start_index: int = 0, limit: Optional[int] = None) -> Iterator[Any]:
        """
        Efficiently seek to a specific position and return values.

        Args:
            start_index: Index to start from (0-based)
            limit: Maximum number of values to return

        Returns:
            Iterator over values
        """
        return self.values(start_index, limit)

    def clear(self) -> None:
        """Remove all elements from the set"""
        # Clear all values and indices
        for value in self._values_vector:
            storage_key = self._make_key(value)
            CollectionStorageAdapter.remove(storage_key)

            index_key = self._make_index_key(value)
            CollectionStorageAdapter.remove(index_key)

        # Clear the values vector
        self._values_vector.clear()

        # Reset length
        self._set_length(0)


# Define IterableSet as an alias for UnorderedSet for compatibility
IterableSet = UnorderedSet
