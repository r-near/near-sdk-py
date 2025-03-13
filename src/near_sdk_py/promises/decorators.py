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
        # Security check 1: Verify this is actually being called as a callback
        results_count = near.promise_results_count()
        if results_count == 0:
            near.panic_utf8("This function can only be called as a callback")
            return

        # Security check 2: Verify this is being called by the contract itself
        if near.predecessor_account_id() != near.current_account_id():
            near.panic_utf8("Callbacks can only be called by the contract itself")
            return

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


def multi_callback(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator for handling multiple promise results when using Promise.join or Promise.all.

    This decorator:
    1. Registers the function as a multi-promise callback
    2. Collects all available promise results
    3. Passes them to your function as a list of PromiseResult objects

    Example:
        @multi_callback
        def on_multiple_results(self, results, extra_arg=None):
            # Process the list of PromiseResult objects
            return processed_data
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Security check 1: Verify this is actually being called as a callback
        results_count = near.promise_results_count()
        if results_count == 0:
            near.panic_utf8("This function can only be called as a callback")
            return

        # Security check 2: Verify this is being called by the contract itself
        if near.predecessor_account_id() != near.current_account_id():
            near.panic_utf8("Callbacks can only be called by the contract itself")
            return

        # Get the number of promise results
        results_count = near.promise_results_count()

        # Collect all results
        promise_results = []
        for i in range(results_count):
            status_code, data = near.promise_result(i)

            # Try to parse JSON data if it looks like JSON
            parsed_data = data
            try:
                if data:
                    parsed_data = json.loads(data)
            except Exception:
                # If parsing fails, keep the original data
                pass

            # Add the result to our collection
            promise_results.append(PromiseResult(status_code, parsed_data))

        # Parse input arguments
        try:
            input_kwargs = Input.json()
            if isinstance(input_kwargs, dict):
                kwargs.update(input_kwargs)
        except Exception:
            # If JSON parsing fails, continue with existing kwargs
            pass

        # Call the wrapped function with the collected results
        final_result = func(self, promise_results, *args, **kwargs)

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
