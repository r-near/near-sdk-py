"""
Decorator utilities for NEAR smart contracts.
"""

import near
from .input import Input
from .log import Log
import json
from .value_return import ValueReturn
from .contract import ContractPanic, ContractError
from functools import wraps


def contract_method(func):
    """
    Enhanced contract method decorator that handles exceptions and input/output serialization.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # If no kwargs were provided and this appears to be a blockchain call
            if len(kwargs) == 0 and len(args) <= 1:
                try:
                    data = Input.string()
                    if len(data) > 0:
                        # Try parsing it as JSON
                        kwargs = json.loads(data)
                except Exception as e:
                    # Don't panic, but we might want to log this
                    Log.warning(f"Failed to parse input as JSON: {e}")
                    pass

            # Call the actual function
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

        except ContractPanic as e:
            # Directly panic with the exception message
            near.panic_utf8(str(e))
        except ContractError as e:
            # Handle other contract errors with a structured message
            near.panic_utf8(f"{e.__class__.__name__}: {str(e)}")
        except Exception as e:
            # Unexpected errors
            near.panic_utf8(f"Unexpected error: {str(e)}")

    # Export the function to make it callable from the blockchain
    return near.export(wrapper)


def view(func):
    """Decorator for view methods (read-only)"""
    return contract_method(func)


def call(func):
    """Decorator for call methods (mutable)"""
    return contract_method(func)


def init(func):
    """Decorator for contract initialization methods"""
    return contract_method(func)
