"""
NEAR Storage API functions.

This module provides functions for interacting with the persistent on-chain storage
of a NEAR smart contract.
"""

from typing import Optional, Union, Tuple


def storage_write(key: Union[bytes, str], value: Union[bytes, str]) -> Optional[bytes]:
    """
    Write the key-value pair to storage.

    Args:
        key: The key to write to
        value: The value to write

    Returns:
        The previous value if the key existed, None otherwise

    Note:
        This is a mock function in the local environment and will return None.
    """
    return None


def storage_read(key: Union[bytes, str]) -> Optional[bytes]:
    """
    Read the value at the given key from storage.

    Args:
        key: The key to read from

    Returns:
        The value if the key exists, None otherwise

    Note:
        This is a mock function in the local environment and will return None.
    """
    return None


def storage_remove(key: Union[bytes, str]) -> Optional[bytes]:
    """
    Remove the value at the given key from storage.

    Args:
        key: The key to remove

    Returns:
        The previous value if the key existed, None otherwise

    Note:
        This is a mock function in the local environment and will return None.
    """
    return None


def storage_has_key(key: Union[bytes, str]) -> bool:
    """
    Check if the given key exists in storage.

    Args:
        key: The key to check

    Returns:
        True if the key exists, False otherwise

    Note:
        This is a mock function in the local environment and will return False.
    """
    return False


def storage_iter_prefix(prefix: Union[bytes, str]) -> int:
    """
    Creates a storage iterator for keys with the given prefix.

    Args:
        prefix: The key prefix to iterate over

    Returns:
        An iterator ID that can be used with storage_iter_next

    Note:
        This is a mock function in the local environment and will return 0.
    """
    return 0


def storage_iter_range(start: Union[bytes, str], end: Union[bytes, str]) -> int:
    """
    Creates a storage iterator for keys in the given range.

    Args:
        start: The start key (inclusive)
        end: The end key (exclusive)

    Returns:
        An iterator ID that can be used with storage_iter_next

    Note:
        This is a mock function in the local environment and will return 0.
    """
    return 0


def storage_iter_next(iterator_id: int) -> Tuple[bool, bytes, bytes]:
    """
    Gets the next key-value pair from a storage iterator.

    Args:
        iterator_id: The ID of the storage iterator

    Returns:
        A tuple of (valid, key, value), where valid is True if there was a next item

    Note:
        This is a mock function in the local environment and will return (False, b"", b"").
    """
    return (False, b"", b"")
