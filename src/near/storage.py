"""
NEAR Storage API functions.

This module provides functions for interacting with the persistent on-chain storage
of a NEAR smart contract.
"""

from typing import Optional, Union


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
