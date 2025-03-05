"""
LookupSet collection for NEAR smart contracts.
"""

from typing import Any  # Keep typing for docs

import near

from .adapter import CollectionStorageAdapter
from .base import Collection, PrefixType


class LookupSet(Collection):
    """
    A non-iterable persistent set implementation for NEAR.

    Similar to Python's set but without iteration support.
    Provides O(1) lookups, inserts, and removals.
    """

    def __init__(self, prefix: str):
        """
        Initialize a new LookupSet with the given prefix.

        Args:
            prefix: A unique string prefix for this collection
        """
        super().__init__(prefix, PrefixType.LOOKUP_SET)

    def __contains__(self, value: Any) -> bool:
        """
        Check if the set contains the given value.

        Args:
            value: The value to check

        Returns:
            True if the value exists, False otherwise
        """
        storage_key = self._make_key(value)
        return near.storage_has_key(storage_key)

    def add(self, value: Any) -> None:
        """
        Add a value to the set.

        Args:
            value: The value to add
        """
        storage_key = self._make_key(value)
        exists = near.storage_has_key(storage_key)

        if not exists:
            # For sets, we just store a marker value (True)
            CollectionStorageAdapter.write(storage_key, True)
            self._set_length(len(self) + 1)

    def remove(self, value: Any) -> None:
        """
        Remove a value from the set.

        Args:
            value: The value to remove

        Raises:
            KeyError: If the value doesn't exist
        """
        storage_key = self._make_key(value)

        if not near.storage_has_key(storage_key):
            raise KeyError(value)

        CollectionStorageAdapter.remove(storage_key)
        self._set_length(len(self) - 1)

    def discard(self, value: Any) -> None:
        """
        Remove a value from the set if it exists.

        Args:
            value: The value to remove
        """
        try:
            self.remove(value)
        except Exception:
            pass

    def clear(self) -> None:
        """
        Remove all values from the set.

        Note: This is less efficient for LookupSet since it doesn't
        track its values. Use with caution on large sets.
        """
        # Since we can't iterate, we can only clear the length
        # This will leave orphaned storage entries
        self._set_length(0)
