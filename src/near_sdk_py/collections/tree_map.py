"""
TreeMap collection for NEAR smart contracts.
"""

from typing import (
    Generic,
    Iterator,
    List,
    Optional,
    Tuple,
    TypeVar,
    cast,
    Protocol,
)

import near
from near_sdk_py.contract import StorageError

from .adapter import CollectionStorageAdapter
from .base import Collection, PrefixType
from .vector import Vector


class Comparable(Protocol):
    """Protocol for comparable types"""

    def __lt__(self, other: "Comparable") -> bool: ...
    def __gt__(self, other: "Comparable") -> bool: ...
    def __le__(self, other: "Comparable") -> bool: ...
    def __ge__(self, other: "Comparable") -> bool: ...


K = TypeVar("K", bound=Comparable)  # Key type (must be comparable)
V = TypeVar("V")  # Value type


class TreeMap(Collection, Generic[K, V]):
    """
    An ordered persistent map implementation for NEAR.

    Similar to a sorted dictionary where keys are kept in order.
    This implementation uses a simple approach that may not be as efficient
    as a true tree-based implementation for very large datasets.

    Note: Keys must be comparable (support < and > operators) AND all keys
    in a TreeMap must be of the same type. You cannot mix different key types
    (like strings and integers) in the same TreeMap instance as this will
    cause TypeError when comparing keys.

    Examples:
        # Create a TreeMap with integer keys
        int_map = TreeMap("int_map")
        int_map[1] = "one"
        int_map[2] = "two"

        # Create a TreeMap with string keys
        string_map = TreeMap("string_map")
        string_map["a"] = "A"
        string_map["b"] = "B"
    """

    def __init__(self, prefix: str):
        """
        Initialize a new TreeMap with the given prefix.

        Args:
            prefix: A unique string prefix for this collection
        """
        super().__init__(prefix, PrefixType.TREE_MAP)

        # Vector for storing the sorted keys
        self._keys_prefix = f"{prefix}:keys"
        self._keys_vector = Vector[K](self._keys_prefix)

    def _find_key_index(self, key: K) -> int:
        """Find the index where key is or should be inserted"""
        # Simple binary search
        left, right = 0, len(self._keys_vector) - 1

        while left <= right:
            mid = (left + right) // 2
            mid_key = cast(K, self._keys_vector[mid])

            if mid_key == key:
                return mid
            elif mid_key < key:
                left = mid + 1
            else:
                right = mid - 1

        return left  # This is where the key should be inserted

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
        if key not in self:
            raise KeyError(key)

        storage_key = self._make_key(key)
        value = CollectionStorageAdapter.read(storage_key)

        if value is None:
            raise StorageError(f"Missing value for key {key}")

        return cast(V, value)

    def __setitem__(self, key: K, value: V) -> None:
        """
        Set the value for the given key.

        Args:
            key: The key to set
            value: The value to store
        """
        storage_key = self._make_key(key)
        exists = key in self

        # Store the value
        CollectionStorageAdapter.write(storage_key, value)

        # Track the key if it's new
        if not exists:
            index = self._find_key_index(key)

            # Insert the key at the correct position
            keys = list(self._keys_vector)
            keys.insert(index, key)

            # Update the keys vector
            self._keys_vector.clear()
            self._keys_vector.extend(keys)

            self._set_length(len(self) + 1)

    def __delitem__(self, key: K) -> None:
        """
        Remove the given key.

        Args:
            key: The key to remove

        Raises:
            KeyError: If the key doesn't exist
        """
        if key not in self:
            raise KeyError(key)

        storage_key = self._make_key(key)

        # Remove the value
        CollectionStorageAdapter.remove(storage_key)

        # Find and remove the key from the keys vector
        index = self._find_key_index(key)
        if index < len(self._keys_vector) and cast(K, self._keys_vector[index]) == key:
            # Remove the key
            keys = list(self._keys_vector)
            keys.pop(index)

            # Update the keys vector
            self._keys_vector.clear()
            self._keys_vector.extend(keys)

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

    def __iter__(self) -> Iterator[K]:
        """Return an iterator over the keys"""
        for i in range(len(self._keys_vector)):
            yield cast(K, self._keys_vector[i])

    def keys(self) -> List[K]:
        """Return a list of all keys"""
        return [cast(K, key) for key in self._keys_vector]

    def values(self) -> List[V]:
        """Return a list of all values"""
        return [self[cast(K, key)] for key in self._keys_vector]

    def items(self) -> List[Tuple[K, V]]:
        """Return a list of all (key, value) pairs"""
        return [(cast(K, key), self[cast(K, key)]) for key in self._keys_vector]

    def clear(self) -> None:
        """Remove all elements from the map"""
        # Clear all values
        for key in self._keys_vector:
            storage_key = self._make_key(cast(K, key))
            CollectionStorageAdapter.remove(storage_key)

        # Clear the keys vector
        self._keys_vector.clear()

        # Reset length
        self._set_length(0)

    def floor_key(self, key: K) -> Optional[K]:
        """
        Find the greatest key less than or equal to the given key.

        Args:
            key: The key to find the floor of

        Returns:
            The greatest key less than or equal to the given key, or None if no such key exists
        """
        if self.is_empty():
            return None

        index = self._find_key_index(key)

        # If exact match, return it
        if index < len(self._keys_vector) and cast(K, self._keys_vector[index]) == key:
            return cast(K, self._keys_vector[index])

        # Otherwise, return the key before it
        if index > 0:
            return cast(K, self._keys_vector[index - 1])

        return None

    def ceiling_key(self, key: K) -> Optional[K]:
        """
        Find the least key greater than or equal to the given key.

        Args:
            key: The key to find the ceiling of

        Returns:
            The least key greater than or equal to the given key, or None if no such key exists
        """
        if self.is_empty():
            return None

        index = self._find_key_index(key)

        # If within bounds, return it
        if index < len(self._keys_vector):
            return cast(K, self._keys_vector[index])

        return None

    def min_key(self) -> Optional[K]:
        """Get the minimum key in the map, or None if empty"""
        if self.is_empty():
            return None
        return cast(K, self._keys_vector[0])

    def max_key(self) -> Optional[K]:
        """Get the maximum key in the map, or None if empty"""
        if self.is_empty():
            return None
        return cast(K, self._keys_vector[len(self._keys_vector) - 1])

    def range(
        self, from_key: Optional[K] = None, to_key: Optional[K] = None
    ) -> List[K]:
        """
        Get keys in the given range, inclusive of from_key and exclusive of to_key.

        Args:
            from_key: The minimum key to include (default: None, no minimum)
            to_key: The maximum key to exclude (default: None, no maximum)

        Returns:
            A list of keys in the range
        """
        # Get all keys
        all_keys = [cast(K, key) for key in self._keys_vector]

        # Find the start and end indices
        start_idx = 0
        end_idx = len(all_keys)

        if from_key is not None:
            for i, key in enumerate(all_keys):
                if key >= from_key:
                    start_idx = i
                    break

        if to_key is not None:
            for i, key in enumerate(all_keys[start_idx:], start_idx):
                if key >= to_key:
                    end_idx = i
                    break

        # Return the keys in the range
        return all_keys[start_idx:end_idx]
