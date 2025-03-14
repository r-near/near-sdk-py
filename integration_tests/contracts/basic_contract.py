"""
Basic Promise Contract for testing the fundamental Promise API.

This contract demonstrates the simplest forms of Promise usage:
- Simple storage operations
- Basic cross-contract calls
- Direct return of promise results
"""

from near_sdk_py import call, view, Storage
from near_sdk_py.promises import CrossContract


class BasicContract:
    """A minimal contract for basic Promise API demonstrations"""

    @view
    def get_value(self, key: str):
        """Get a value from storage or return default."""
        return Storage.get_string(key) or "default_value"

    @call
    def set_value(self, key: str, value: str):
        """Set a value in storage."""
        Storage.set(key, value)
        return {"success": True, "key": key, "value": value}

    @call
    def direct_call(self, contract_id: str, key: str):
        """Make a cross-contract call with no callback.

        This is the simplest possible cross-contract call pattern,
        which directly returns the promise result to the caller.
        """
        contract = CrossContract(contract_id)
        # Call get_value and return the promise directly
        return contract.call("get_value", key=key).value()

    @call
    def echo(self, message: str):
        """Simple method that just returns the input.

        Useful for testing gas usage of a basic call.
        """
        return message
