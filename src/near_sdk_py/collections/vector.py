"""
Vector collection for NEAR smart contracts.
"""

from typing import (
    Any,
    Iterable,
    Iterator,
    Optional,
    Union,
)

from near_sdk_py.contract import StorageError

from .adapter import CollectionStorageAdapter
from .base import Collection, PrefixType


class Vector(Collection):
    """
    A persistent vector (array) implementation for NEAR.

    Similar to Python's list, Vector provides ordered, indexable storage with O(1) append
    and O(1) random access. Elements are stored individually in the contract's storage.
    """

    def __init__(self, prefix: str):
        """
        Initialize a new Vector with the given prefix.

        Args:
            prefix: A unique string prefix for this collection
        """
        super().__init__(prefix, PrefixType.VECTOR)

    def __getitem__(self, index: Union[int, slice]) -> Any:
        """
        Get an item or slice of items from the vector.

        Args:
            index: The index or slice to retrieve

        Returns:
            The item at the specified index, or a list for slices

        Raises:
            IndexError: If the index is out of bounds
        """
        if isinstance(index, slice):
            # Handle slices
            start, stop, step = index.indices(len(self))
            result = []
            for i in range(start, stop, step):
                item = self[i]
                result.append(item)
            return result

        # Handle negative indices
        length = len(self)
        if index < 0:
            index += length

        # Check bounds
        if index < 0 or index >= length:
            raise IndexError("Vector index out of range")

        # Get the item
        key = self._make_index_key(index)
        value = CollectionStorageAdapter.read(key)

        if value is None:
            raise StorageError(f"Missing value for index {index}")

        return value

    def __setitem__(self, index: int, value: Any) -> None:
        """
        Set an item at the specified index.

        Args:
            index: The index to set
            value: The value to store

        Raises:
            IndexError: If the index is out of bounds
        """
        # Handle negative indices
        length = len(self)
        if index < 0:
            index += length

        # Check bounds
        if index < 0 or index >= length:
            raise IndexError("Vector index out of range")

        # Set the item
        key = self._make_index_key(index)
        CollectionStorageAdapter.write(key, value)

    def append(self, value: Any) -> None:
        """
        Add an element to the end of the vector.

        Args:
            value: The value to add
        """
        length = len(self)
        key = self._make_index_key(length)
        CollectionStorageAdapter.write(key, value)
        self._set_length(length + 1)

    def pop(self, index: int = -1) -> Any:
        """
        Remove and return an element at the given index.
        Default is to remove the last element.

        Args:
            index: The index to remove (default: -1, the last element)

        Returns:
            The removed element

        Raises:
            IndexError: If the vector is empty or index is out of bounds
        """
        length = len(self)
        if length == 0:
            raise IndexError("pop from empty Vector")

        # Handle negative indices
        if index < 0:
            index += length

        # Check bounds
        if index < 0 or index >= length:
            raise IndexError("Vector index out of range")

        # Get the value before removing it
        key = self._make_index_key(index)
        value = CollectionStorageAdapter.read(key)

        if value is None:
            raise StorageError(f"Missing value for index {index}")

        # If not the last element, shift elements
        if index < length - 1:
            for i in range(index, length - 1):
                next_key = self._make_index_key(i + 1)
                next_value = CollectionStorageAdapter.read(next_key)
                CollectionStorageAdapter.write(self._make_index_key(i), next_value)

        # Remove the last element
        last_key = self._make_index_key(length - 1)
        CollectionStorageAdapter.remove(last_key)

        # Update length
        self._set_length(length - 1)

        return value

    def swap_remove(self, index: int) -> Any:
        """
        Remove an element by swapping it with the last element and then removing it.
        This is more efficient than pop() for cases where order doesn't matter.

        Args:
            index: The index to remove

        Returns:
            The removed element

        Raises:
            IndexError: If the vector is empty or index is out of bounds
        """
        length = len(self)
        if length == 0:
            raise IndexError("swap_remove from empty Vector")

        # Handle negative indices
        if index < 0:
            index += length

        # Check bounds
        if index < 0 or index >= length:
            raise IndexError("Vector index out of range")

        # Get the value before removing it
        key = self._make_index_key(index)
        value = CollectionStorageAdapter.read(key)

        if value is None:
            raise StorageError(f"Missing value for index {index}")

        # If not the last element, swap with the last element
        if index < length - 1:
            last_key = self._make_index_key(length - 1)
            last_value = CollectionStorageAdapter.read(last_key)
            CollectionStorageAdapter.write(key, last_value)

        # Remove the last element
        last_key = self._make_index_key(length - 1)
        CollectionStorageAdapter.remove(last_key)

        # Update length
        self._set_length(length - 1)

        return value

    def extend(self, items: Iterable) -> None:
        """
        Append multiple items to the vector.

        Args:
            items: The items to append
        """
        length = len(self)
        i = 0
        for item in items:
            key = self._make_index_key(length + i)
            CollectionStorageAdapter.write(key, item)
            i += 1

        if i > 0:
            self._set_length(length + i)

    def clear(self) -> None:
        """Remove all elements from the vector"""
        length = len(self)

        # Remove all elements
        for i in range(length):
            key = self._make_index_key(i)
            CollectionStorageAdapter.remove(key)

        # Reset length
        self._set_length(0)

    def __iter__(self) -> Iterator:
        """Return an iterator over the elements"""
        for i in range(len(self)):
            yield self[i]

    def get(self, index: int, default: Optional[Any] = None) -> Any:
        """
        Get an element at the specified index, or return default if index is out of bounds.

        Args:
            index: The index to retrieve
            default: The default value to return if index is out of bounds

        Returns:
            The element at the specified index, or default if index is out of bounds
        """
        try:
            return self[index]
        except IndexError:
            return default
