"""
NEAR types and constants.

This module provides type definitions and constants for the NEAR blockchain.
"""

from enum import IntEnum
from typing import NewType

# Type definitions
AccountId = NewType("AccountId", str)
Balance = NewType("Balance", int)  # In yoctoNEAR (10^-24 NEAR)
Gas = NewType("Gas", int)  # In gas units
PublicKey = NewType("PublicKey", bytes)
PromiseIndex = NewType("PromiseIndex", int)
RegisterId = NewType("RegisterId", int)

# Constants
NEAR = 10**24  # 1 NEAR in yoctoNEAR


# Enumerations
class PromiseResult(IntEnum):
    """Enumeration of possible promise result statuses."""

    SUCCESS = 0
    FAILURE = 1
