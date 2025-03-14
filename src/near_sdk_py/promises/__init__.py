"""
Pythonic API for NEAR cross-contract calls.

This module provides a more intuitive, Pythonic interface for NEAR's
cross-contract calls with method chaining and modern Python syntax.
"""

from .batch import BatchAction, PromiseBatch
from .contract import CrossContract
from .promise import Promise, PromiseResult
from .decorators import callback, multi_callback

__all__ = [
    "BatchAction",
    "PromiseBatch",
    "CrossContract",
    "Promise",
    "PromiseResult",
    "callback",
    "multi_callback",
]
