"""
NEAR Context API functions.

This module provides functions for accessing blockchain contextual information
such as account IDs, block details, and transaction inputs.
"""


def current_account_id() -> str:
    """
    Get the account ID of the current contract.

    Returns:
        The account ID of the current contract

    Note:
        This is a mock function in the local environment and will return an empty string.
    """
    return ""


def signer_account_id() -> str:
    """
    Get the account ID that signed the transaction.

    Returns:
        The account ID of the transaction signer

    Note:
        This is a mock function in the local environment and will return an empty string.
    """
    return ""


def signer_account_pk() -> bytes:
    """
    Get the public key of the account that signed the transaction.

    Returns:
        The public key bytes of the transaction signer

    Note:
        This is a mock function in the local environment and will return empty bytes.
    """
    return b""


def predecessor_account_id() -> str:
    """
    Get the account ID of the immediate caller.

    Returns:
        The account ID of the immediate caller

    Note:
        This is a mock function in the local environment and will return an empty string.
    """
    return ""


def input() -> bytes:
    """
    Get the input arguments to the function call as bytes.

    Returns:
        The input arguments as bytes

    Note:
        This is a mock function in the local environment and will return empty bytes.
    """
    return b""


def input_as_str() -> str:
    """
    Get the input arguments to the function call as a UTF-8 string.

    Returns:
        The input arguments as a UTF-8 string

    Note:
        This is a mock function in the local environment and will return an empty string.
    """
    return ""


def block_height() -> int:
    """
    Get the current block height.

    Returns:
        The current block height

    Note:
        This is a mock function in the local environment and will return 0.
    """
    return 0


def block_timestamp() -> int:
    """
    Get the current block timestamp (in nanoseconds).

    Returns:
        The current block timestamp

    Note:
        This is a mock function in the local environment and will return 0.
    """
    return 0


def epoch_height() -> int:
    """
    Get the current epoch height.

    Returns:
        The current epoch height

    Note:
        This is a mock function in the local environment and will return 0.
    """
    return 0


def storage_usage() -> int:
    """
    Get the storage usage for the current contract.

    Returns:
        The storage usage in bytes

    Note:
        This is a mock function in the local environment and will return 0.
    """
    return 0
