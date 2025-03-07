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


def alt_bn128_g1_multiexp(value: bytes) -> bytes:
    """
    Performs multi-exponentiation on the Alt BN128 G1 curve.

    This is used for efficient computation of multiple exponentiations, which is
    a common operation in zero-knowledge proofs.

    Args:
        value: Input for the operation, which should be formatted as a series of points and scalars

    Returns:
        The resulting G1 point

    Note:
        This is a mock function in the local environment and will return empty bytes.
    """
    return b""


def alt_bn128_g1_sum(value: bytes) -> bytes:
    """
    Performs point addition on the Alt BN128 G1 curve.

    This adds multiple G1 points together.

    Args:
        value: Input for the operation, which should be formatted as a series of G1 points

    Returns:
        The resulting G1 point from adding all input points

    Note:
        This is a mock function in the local environment and will return empty bytes.
    """
    return b""


def alt_bn128_pairing_check(value: bytes) -> bool:
    """
    Performs a pairing check on the Alt BN128 curve.

    This checks if the product of pairings equals 1, which is used for verifying
    zero-knowledge proofs and other cryptographic protocols.

    Args:
        value: Input for the operation, which should be formatted as a series of G1 and G2 points

    Returns:
        True if the pairing check passes, False otherwise

    Note:
        This is a mock function in the local environment and will return False.
    """
    return False
