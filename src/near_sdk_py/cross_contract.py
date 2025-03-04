"""
Utilities for cross-contract calls in NEAR smart contracts.
"""

import json
from typing import Any, List

import near

# Import constants
from .constants import ONE_TGAS

MAX_GAS = 300 * ONE_TGAS  # 300 TGas


class CrossContract:
    """
    Utilities for cross-contract calls
    """

    @staticmethod
    def call(
        account_id: str,
        method_name: str,
        args: Any = None,
        amount: int = 0,
        gas: int = MAX_GAS // 3,
    ) -> int:
        """
        Makes a cross-contract call
        Returns the promise index
        """
        if args is None:
            args_str = ""
        elif isinstance(args, str):
            args_str = args
        else:
            args_str = json.dumps(args)

        return near.promise_create(account_id, method_name, args_str, amount, gas)

    @staticmethod
    def then(
        promise_idx: int,
        account_id: str,
        method_name: str,
        args: Any = None,
        amount: int = 0,
        gas: int = MAX_GAS // 3,
    ) -> int:
        """
        Chains a callback to a promise
        Returns the new promise index
        """
        if args is None:
            args_str = ""
        elif isinstance(args, str):
            args_str = args
        else:
            args_str = json.dumps(args)

        return near.promise_then(
            promise_idx, account_id, method_name, args_str, amount, gas
        )

    @staticmethod
    def and_then(
        promise_indices: List[int],
        account_id: str,
        method_name: str,
        args: Any = None,
        amount: int = 0,
        gas: int = MAX_GAS // 3,
    ) -> int:
        """
        Combines multiple promises and chains a callback
        """
        combined_promise = near.promise_and(promise_indices)
        if args is None:
            args_str = ""
        elif isinstance(args, str):
            args_str = args
        else:
            args_str = json.dumps(args)

        return near.promise_then(
            combined_promise, account_id, method_name, args_str, amount, gas
        )

    @staticmethod
    def return_value(promise_idx: int):
        """
        Returns the value of a promise
        """
        near.promise_return(promise_idx)
