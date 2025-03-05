"""
Pythonic API for NEAR cross-contract calls.

This module provides a more intuitive, Pythonic interface for NEAR's
cross-contract calls with method chaining and modern Python syntax.
"""

import json
from typing import Any, List, Union, TypeVar, Callable
from functools import wraps

import near
from .constants import ONE_TGAS
from .cross_contract import CrossContract
from .value_return import ValueReturn
from .input import Input
from .log import Log

T = TypeVar("T")


class Promise:
    """A fluent wrapper around NEAR promises with method chaining support."""

    def __init__(self, promise_id: int, gas: int = 5 * ONE_TGAS, deposit: int = 0):
        """
        Initialize a Promise wrapper.

        Args:
            promise_id: The NEAR promise ID to wrap
            gas: Gas to use for subsequent operations (default: 5 TGas)
            deposit: Deposit amount for subsequent operations (default: 0)
        """
        self._promise_id = promise_id
        self._gas = gas
        self._deposit = deposit

    def gas(self, amount: int) -> "Promise":
        """
        Set the gas amount for the next operation.

        Args:
            amount: Gas amount in gas units

        Returns:
            A new Promise with updated gas setting
        """
        return Promise(self._promise_id, gas=amount, deposit=self._deposit)

    def deposit(self, amount: int) -> "Promise":
        """
        Set the deposit amount for the next operation.

        Args:
            amount: Deposit amount in yoctoNEAR

        Returns:
            A new Promise with updated deposit setting
        """
        return Promise(self._promise_id, gas=self._gas, deposit=amount)

    def then(self, method: str, **kwargs) -> "Promise":
        """
        Chain a callback to the current contract after this promise.

        Args:
            method: Method name in the current contract to call as callback
            **kwargs: Keyword arguments to pass to the callback

        Returns:
            A new Promise representing the chained operation
        """
        promise = CrossContract.then(
            self._promise_id,
            near.current_account_id(),
            method,
            kwargs,
            0,  # No deposit for callbacks to self
            self._gas,
        )

        return Promise(promise)

    def then_call(self, contract_id: str, method: str, **kwargs) -> "Promise":
        """
        Chain a call to another contract after this promise.

        Args:
            contract_id: Account ID of the contract to call
            method: Method name to call on the target contract
            **kwargs: Keyword arguments to pass to the method

        Returns:
            A new Promise representing the chained call
        """
        promise = CrossContract.then(
            self._promise_id, contract_id, method, kwargs, self._deposit, self._gas
        )

        return Promise(promise)

    def join(
        self, other_promises: List["Promise"], callback: str, **kwargs
    ) -> "Promise":
        """
        Join this promise with others and add a callback.

        Args:
            other_promises: List of other Promise objects to join with
            callback: Method name to call as callback
            **kwargs: Keyword arguments to pass to the callback

        Returns:
            A new Promise representing the joined operation
        """
        # Convert Promise objects to their IDs
        promise_ids = [self._promise_id] + [p._promise_id for p in other_promises]

        combined = CrossContract.and_then(
            promise_ids,
            near.current_account_id(),
            callback,
            kwargs,
            0,  # No deposit
            self._gas,
        )

        return Promise(combined)

    def value(self):
        """
        Return this promise's result to the caller.

        This should be the final operation in your promise chain.
        """
        return CrossContract.return_value(self._promise_id)


class Contract:
    """Fluent interface for calling contract methods."""

    def __init__(self, account_id: str, gas: int = 5 * ONE_TGAS, deposit: int = 0):
        """
        Initialize a contract proxy.

        Args:
            account_id: The contract's account ID
            gas: Default gas to use for calls (default: 5 TGas)
            deposit: Default deposit amount (default: 0)
        """
        self.account_id = account_id
        self._gas = gas
        self._deposit = deposit

    def gas(self, amount: int) -> "Contract":
        """
        Set the default gas amount for calls to this contract.

        Args:
            amount: Gas amount in gas units

        Returns:
            A new Contract with updated gas setting
        """
        return Contract(self.account_id, gas=amount, deposit=self._deposit)

    def deposit(self, amount: int) -> "Contract":
        """
        Set the default deposit amount for calls to this contract.

        Args:
            amount: Deposit amount in yoctoNEAR

        Returns:
            A new Contract with updated deposit setting
        """
        return Contract(self.account_id, gas=self._gas, deposit=amount)

    def call(self, method: str, **kwargs) -> Promise:
        """
        Call a method on this contract with keyword arguments.

        Args:
            method: The method name to call
            **kwargs: Keyword arguments to pass to the method

        Returns:
            A Promise object representing the call
        """
        promise_id = CrossContract.call(
            account_id=self.account_id,
            method_name=method,
            args=kwargs,
            amount=self._deposit,
            gas=self._gas,
        )

        return Promise(promise_id, gas=self._gas)


class PromiseResult:
    """Wrapper for cross-contract call results with error handling."""

    def __init__(self, promise_result: dict):
        """
        Initialize from a raw promise result.

        Args:
            promise_result: The raw promise result from CrossContract.get_result()
        """
        self.raw_result = promise_result
        self.status = promise_result.get("status", "Unknown")
        self.status_code = promise_result.get("status_code", 0)
        self._data = promise_result.get("data", None)

    @property
    def is_success(self) -> bool:
        """Whether the promise completed successfully."""
        return self.status == "Successful"

    @property
    def is_error(self) -> bool:
        """Whether the promise completed with an error."""
        return self.status == "Failed"

    @property
    def data(self) -> Any:
        """
        Get deserialized data from the result.

        Returns:
            The parsed JSON data, or raw data if not JSON
        """
        if not self._data:
            return None

        try:
            return json.loads(self._data.decode("utf-8"))
        except Exception:
            # Return raw data if it can't be parsed as JSON
            return self._data

    def unwrap(self) -> Any:
        """
        Get the data or raise an exception if failed.

        Returns:
            The parsed result data

        Raises:
            Exception: If the promise failed or is not ready
        """
        if not self.is_success:
            raise Exception(f"Promise failed with status: {self.status}")
        return self.data

    def unwrap_or(self, default: T) -> Union[Any, T]:
        """
        Get the data or return a default value if failed.

        Args:
            default: Value to return if the promise failed

        Returns:
            The parsed data or the default value
        """
        return self.data if self.is_success else default


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
        if near.predecessor_account_id != near.current_account_id:
            near.panic_utf8("This function is private")

        # Get the `input` - these would be extra args passed in to the callback
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
