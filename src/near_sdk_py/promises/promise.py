"""
Pythonic API for NEAR cross-contract calls.

This module provides a more intuitive, Pythonic interface for NEAR's
cross-contract calls with method chaining and modern Python syntax.
"""

import json
from typing import List, TypeVar

import near
from near_sdk_py.constants import ONE_TGAS

from .batch import PromiseBatch

T = TypeVar("T")
STATUS_NAMES = ["NotReady", "Successful", "Failed"]


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

    @classmethod
    def create_batch(cls, account_id: str) -> PromiseBatch:
        """
        Create a new promise batch for the given account.

        Args:
            account_id: The account to create the batch for

        Returns:
            A new PromiseBatch instance
        """
        promise_id = near.promise_batch_create(account_id)
        return PromiseBatch(promise_id)

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
        if kwargs is None:
            args_str = ""
        elif isinstance(kwargs, str):
            args_str = kwargs
        else:
            args_str = json.dumps(kwargs)

        promise_id = near.promise_then(
            self._promise_id, near.current_account_id(), method, args_str, 0, self._gas
        )
        return Promise(promise_id)

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
        if kwargs is None:
            args_str = ""
        elif isinstance(kwargs, str):
            args_str = kwargs
        else:
            args_str = json.dumps(kwargs)

        promise_id = near.promise_then(
            self._promise_id, contract_id, method, args_str, self._deposit, self._gas
        )

        return Promise(promise_id)

    def then_batch(self, account_id: str) -> PromiseBatch:
        """
        Chain a batch of actions to be executed after this promise completes.

        Args:
            account_id: Account ID to execute the batch on

        Returns:
            A new PromiseBatch for adding actions
        """
        promise_id = near.promise_batch_then(self._promise_id, account_id)
        return PromiseBatch(promise_id, self._gas)

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

        combined_promise = near.promise_and(promise_ids)
        if kwargs is None:
            args_str = ""
        elif isinstance(kwargs, str):
            args_str = kwargs
        else:
            args_str = json.dumps(kwargs)

        promise_id = near.promise_then(
            combined_promise,
            near.current_account_id(),
            callback,
            args_str,
            0,
            self._gas,
        )
        return Promise(promise_id)

    @staticmethod
    def all(promises: List["Promise"]) -> int:
        """
        Create a promise that resolves when all input promises resolve.

        Args:
            promises: List of promises to join

        Returns:
            A promise ID for the combined promise
        """
        promise_ids = [p._promise_id for p in promises]
        return near.promise_and(promise_ids)

    def value(self):
        """
        Return this promise's result to the caller.

        This should be the final operation in your promise chain.
        """
        return near.promise_return(self._promise_id)


class PromiseResult:
    """Minimal wrapper for cross-contract call results."""

    def __init__(self, status_code, data):
        self.status_code = status_code
        self.data = data
        self.success = status_code == 1

    def unwrap(self):
        """Get data or raise exception if failed."""
        if not self.success:
            status_name = (
                STATUS_NAMES[self.status_code]
                if 0 <= self.status_code <= 2
                else "Unknown"
            )
            raise Exception(f"Promise failed with status: {status_name}")
        return self.data

    def unwrap_or(self, default):
        """Get data or return default if failed."""
        return self.data if self.success else default
