"""
Pythonic API for NEAR cross-contract calls.

This module provides a more intuitive, Pythonic interface for NEAR's
cross-contract calls with method chaining and modern Python syntax.
"""

from typing import Any, Callable
from functools import wraps

import json
import near
from near_sdk_py.value_return import ValueReturn
from .promise import PromiseResult
from near_sdk_py.input import Input

STATUS_NOT_READY = 0
STATUS_SUCCESSFUL = 1
STATUS_FAILED = 2
STATUS_NAMES = ["NotReady", "Successful", "Failed"]


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

        # Parse the data as JSON
        try:
            data = json.loads(data)
        except Exception:
            pass

        promise_result = PromiseResult(status_code, data)

        # Check if we have any args as well
        kwargs = {}
        try:
            kwargs = Input.json()
        except Exception:
            pass

        # Call the wrapped function with simplified parameters
        final_result = func(self, promise_result, *args, **kwargs)

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
