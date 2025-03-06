"""
Decorator utilities for NEAR smart contracts.
"""

from typing import Any, Callable, TypeVar

import near
from .input import Input
from .log import Log
from .value_return import ValueReturn

T = TypeVar("T")


def contract_method(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator for contract methods that handles input deserialization
    and return value serialization. Much simpler version compatible with MicroPython.

    When using this decorator:
    - Your method will receive parsed JSON input as kwargs when called by the blockchain
    - Your method's return value will be properly serialized for the blockchain
    """

    def wrapper(*args, **kwargs):
        # If no kwargs were provided and this appears to be a blockchain call
        # (typically just the self argument, or empty for module-level functions)
        if len(kwargs) == 0 and len(args) <= 1:
            try:
                # Parse input JSON and use it as kwargs
                input_json = Input.json()
                if isinstance(input_json, dict):
                    kwargs = input_json
            except Exception as e:
                # If JSON parsing fails, just log and continue
                # Your method will need to handle getting input another way
                Log.warning(f"Failed to parse input as JSON: {e}")

        # Call the actual function with the processed args and kwargs
        result = func(*args, **kwargs)

        # Handle the return value
        if result is not None:
            if isinstance(result, bytes):
                ValueReturn.bytes(result)
            elif isinstance(result, str):
                ValueReturn.string(result)
            else:
                ValueReturn.json(result)

        return result

    return wrapper


def export(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator for exported contract methods
    Combines with @near.export to expose the method to the blockchain
    """
    return near.export(contract_method(func))


def view(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator for view methods (read-only)
    """
    return export(func)


def call(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator for call methods (mutable)
    """
    return export(func)


def init(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator for contract initialization methods
    """
    return export(func)
