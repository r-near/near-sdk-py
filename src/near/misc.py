"""
NEAR Miscellaneous API functions.

This module provides miscellaneous functions for NEAR smart contracts,
including logging, panic, and result handling.
"""

from typing import Union


def value_return(value: Union[bytes, str]) -> None:
    """
    Return a value from the current function.

    Args:
        value: The value to return

    Note:
        This is a mock function in the local environment and has no effect.
    """
    pass


def panic() -> None:
    """
    Panic and abort the current execution.

    Note:
        This is a mock function in the local environment and has no effect.
        In a real environment, this function would never return.
    """
    pass


def panic_utf8(msg: str) -> None:
    """
    Panic with the given UTF-8 message and abort the current execution.

    Args:
        msg: The message to panic with

    Note:
        This is a mock function in the local environment and has no effect.
        In a real environment, this function would never return.
    """
    pass


def log_utf8(msg: Union[bytes, str]) -> None:
    """
    Log the given UTF-8 message.

    Args:
        msg: The message to log

    Note:
        This is a mock function in the local environment and has no effect.
    """
    pass


def log(msg: Union[bytes, str]) -> None:
    """
    Alias for log_utf8.

    Args:
        msg: The message to log

    Note:
        This is a mock function in the local environment and has no effect.
    """
    pass


def log_utf16(msg: bytes) -> None:
    """
    Log the given UTF-16 message.

    Args:
        msg: The UTF-16 encoded message to log

    Note:
        This is a mock function in the local environment and has no effect.
    """
    pass


def abort(msg: str, filename: str, line: int, col: int) -> None:
    """
    Abort the current execution with detailed information.

    Args:
        msg: The message to abort with
        filename: The filename where the abort was triggered
        line: The line number where the abort was triggered
        col: The column number where the abort was triggered

    Note:
        This is a mock function in the local environment and has no effect.
        In a real environment, this function would never return.
    """
    pass
