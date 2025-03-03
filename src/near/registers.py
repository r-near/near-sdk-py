"""
NEAR Register API functions.

This module provides functions for working with NEAR VM registers, which are
used for efficient data transfer between host functions and contract code.
"""

from typing import Union


def read_register(register_id: int) -> bytes:
    """
    Read the value from the given register ID.

    Args:
        register_id: Register ID to read from

    Returns:
        The bytes value stored in the register

    Note:
        This is a mock function in the local environment and will return an empty bytes value.
    """
    return b""


def read_register_as_str(register_id: int) -> str:
    """
    Read the value from the given register ID as a UTF-8 string.

    Args:
        register_id: Register ID to read from

    Returns:
        The UTF-8 string value stored in the register

    Note:
        This is a mock function in the local environment and will return an empty string.
    """
    return ""


def register_len(register_id: int) -> int:
    """
    Get the length of the value stored in the given register ID.

    Args:
        register_id: Register ID to check

    Returns:
        The length in bytes of the value stored in the register

    Note:
        This is a mock function in the local environment and will return 0.
    """
    return 0


def write_register(register_id: int, data: Union[bytes, str]) -> None:
    """
    Write the given data to the given register ID.

    Args:
        register_id: Register ID to write to
        data: The data to write to the register (bytes or string)

    Note:
        This is a mock function in the local environment and has no effect.
    """
    pass
