"""
Pythonic API for NEAR cross-contract calls.

This module provides a more intuitive, Pythonic interface for NEAR's
cross-contract calls with method chaining and modern Python syntax.
"""

from typing import Any, Callable
from functools import wraps

import near
from near_sdk_py.value_return import ValueReturn
from .promise import PromiseResult


def callback(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator for promise result handlers with automatic unpacking.

    This decorator:
    1. Registers the function as a callback
    2. Parses the promise result and handles errors
    3. Passes the parsed data directly to your function

    Example:
        @callback
        def on_data_received(self, data, token_id=None):
            # Process the already parsed data
            return processed_data
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Get the promise result
        status_code, data = near.promise_result(0)

        # Create a result object
        promise_result = {
            "status_code": status_code,
            "status": ["NotReady", "Successful", "Failed"][status_code]
            if 0 <= status_code <= 2
            else "Unknown",
            "data": data,
        }

        # Convert to PromiseResult for easier handling
        result = PromiseResult(promise_result)

        # Check if successful
        if not result.is_success:
            # Default error handling
            final_result = {"error": f"Call failed: {result.status}"}
        else:
            # Call the handler with parsed data
            try:
                final_result = func(self, result.data, *args, **kwargs)
            except Exception as e:
                final_result = {"error": f"Error processing result: {str(e)}"}

        # Handle the return value
        if final_result is not None:
            if isinstance(final_result, bytes):
                ValueReturn.bytes(final_result)
            elif isinstance(final_result, str):
                ValueReturn.string(final_result)
            else:
                ValueReturn.json(final_result)

        return final_result

    # Export the wrapped function
    return near.export(wrapper)
