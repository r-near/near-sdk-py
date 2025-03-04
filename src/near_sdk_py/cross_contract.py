"""
Utilities for cross-contract calls in NEAR smart contracts.
"""

import json
from typing import Any, Dict, List, Optional

import near

# Import constants
from .constants import ONE_TGAS

MAX_GAS = 300 * ONE_TGAS  # 300 TGas


class CrossContract:
    """
    Utilities for cross-contract calls

    Examples:
    ---------

    # Simple cross-contract call
    promise = CrossContract.call("example.near", "get_data")

    # Cross-contract call with automatic callback
    promise = CrossContract.call_with_callback(
        "example.near",           # Target contract
        "get_data",               # Target method
        callback_method="on_data_received"  # Local callback method
    )

    # Complex promise chain
    promise = CrossContract.call("contract1.near", "method1")
    callback = CrossContract.then(promise, "contract2.near", "method2")
    CrossContract.return_value(callback)
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
    def call_with_callback(
        account_id: str,
        method_name: str,
        args: Any = None,
        amount: int = 0,
        gas: int = MAX_GAS // 3,
        callback_gas: Optional[int] = None,
        callback_method: Optional[str] = None,
        callback_args: Any = None,
    ) -> int:
        """
        Makes a cross-contract call with an automatic callback to the current contract

        Returns the final promise index that can be used with return_value()
        """
        if callback_method is None:
            raise ValueError("callback_method is required for call_with_callback")

        # Default callback gas to be one-third of the remaining gas
        if callback_gas is None:
            callback_gas = gas // 3

        # Make the initial cross-contract call
        promise_idx = CrossContract.call(account_id, method_name, args, amount, gas)

        # Chain the callback
        current_account = near.current_account_id()
        final_promise = CrossContract.then(
            promise_idx,
            current_account,
            callback_method,
            callback_args,
            0,
            callback_gas,
        )
        return final_promise

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
    def get_result(promise_idx: int = 0) -> Dict[str, Any]:
        """
        Gets the result of a promise for callback processing

        Returns a dictionary with:
            - 'status': 'NotReady', 'Successful', or 'Failed'
            - 'data': bytes object containing the result data if successful
        """
        status_code, data = near.promise_result(promise_idx)
        status = (
            ["NotReady", "Successful", "Failed"][status_code]
            if 0 <= status_code <= 2
            else "Unknown"
        )

        return {"status": status, "data": data, "status_code": status_code}

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
