"""
NEAR Math API functions.

This module provides cryptographic and mathematical functions for NEAR smart contracts.
"""

from typing import Optional


def random_seed() -> bytes:
    """
    Get a random seed from the blockchain.

    Returns:
        32 bytes of randomness from the blockchain

    Note:
        This is a mock function in the local environment and will return empty bytes.
    """
    return b""


def sha256(value: bytes) -> bytes:
    """
    Compute the SHA-256 hash of the given value.

    Args:
        value: The value to hash

    Returns:
        The SHA-256 hash of the value

    Note:
        This is a mock function in the local environment and will return empty bytes.
    """
    return b""


def keccak256(value: bytes) -> bytes:
    """
    Compute the Keccak-256 hash of the given value.

    Args:
        value: The value to hash

    Returns:
        The Keccak-256 hash of the value

    Note:
        This is a mock function in the local environment and will return empty bytes.
    """
    return b""


def keccak512(value: bytes) -> bytes:
    """
    Compute the Keccak-512 hash of the given value.

    Args:
        value: The value to hash

    Returns:
        The Keccak-512 hash of the value

    Note:
        This is a mock function in the local environment and will return empty bytes.
    """
    return b""


def ripemd160(value: bytes) -> bytes:
    """
    Compute the RIPEMD-160 hash of the given value.

    Args:
        value: The value to hash

    Returns:
        The RIPEMD-160 hash of the value

    Note:
        This is a mock function in the local environment and will return empty bytes.
    """
    return b""


def ecrecover(
    hash: bytes, sig: bytes, v: int, malleability_flag: bool
) -> Optional[bytes]:
    """
    Recover the Ethereum address from a signature.

    Args:
        hash: The 32-byte hash that was signed
        sig: The 64-byte signature (r||s)
        v: The recovery ID (0 or 1)
        malleability_flag: Whether to check for signature malleability

    Returns:
        The 64-byte public key or None if recovery failed

    Note:
        This is a mock function in the local environment and will return None.
    """
    return None


def ed25519_verify(sig: bytes, msg: bytes, pub_key: bytes) -> bool:
    """
    Verify an Ed25519 signature.

    Args:
        sig: The 64-byte signature
        msg: The message that was signed
        pub_key: The 32-byte public key

    Returns:
        True if the signature is valid, False otherwise

    Note:
        This is a mock function in the local environment and will return False.
    """
    return False
