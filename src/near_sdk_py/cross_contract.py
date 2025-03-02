"""
Utilities for cross-contract calls in NEAR smart contracts.
"""

import json
import functools
from typing import Any, List, Callable, Optional, TypeVar, TYPE_CHECKING
from .context import Context

if TYPE_CHECKING:
    from near_py_tool import near
else:
    import near
# Import constants
from .constants import ONE_TGAS

MAX_GAS = 300 * ONE_TGAS  # 300 TGas
T = TypeVar('T')


def callback(gas: int = MAX_GAS // 3):
    """
    Decorator to mark a method as a callback for cross-contract calls.
    
    Example:
        @callback(gas=5 * ONE_TGAS)
        def on_transfer_complete(self):
            # Handle callback logic here
            pass
    """
    def decorator(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        
        # Mark this function as a callback and store gas
        wrapper._is_callback = True
        wrapper._callback_gas = gas
        return wrapper
    return decorator


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
        callback_method: Optional[Callable] = None,
    ) -> int:
        """
        Makes a cross-contract call with optional callback
        
        Args:
            account_id: Target contract account ID
            method_name: Method to call on target contract
            args: Arguments to pass to the method
            amount: Amount of NEAR tokens to attach
            gas: Gas to allocate for the call
            callback_method: Optional callback method (must be decorated with @callback)
            
        Returns:
            The promise index
            
        Example:
            # With callback
            promise = CrossContract.call(
                "nft.example.near",
                "nft_transfer",
                {"receiver_id": "bob.near", "token_id": "123"},
                callback_method=self.on_transfer_complete
            )
            CrossContract.return_value(promise)
            
            # Without callback
            promise = CrossContract.call("contract.near", "method", {"arg": "value"})
        """
        # Serialize arguments
        if args is None:
            args_str = ""
        elif isinstance(args, str):
            args_str = args
        else:
            args_str = json.dumps(args)

        # Create the initial promise
        promise_idx = near.promise_create(account_id, method_name, args_str, amount, gas)
        
        # If a callback was provided, chain it
        if callback_method is not None:
            if not getattr(callback_method, '_is_callback', False):
                raise ValueError("Callback must be decorated with @callback")
            
            callback_gas = getattr(callback_method, '_callback_gas', MAX_GAS // 3)
            promise_idx = near.promise_then(
                promise_idx,
                Context.current_account_id(),
                callback_method.__name__,
                "",  # No additional args needed
                0,   # No deposit for callbacks
                callback_gas
            )
            
        return promise_idx

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
    def all(promise_indices: List[int]) -> int:
        """
        Combines multiple promises into one that succeeds when all succeed
        Returns the combined promise index
        """
        return near.promise_and(promise_indices)

    @staticmethod
    def return_value(promise_idx: int):
        """
        Returns the value of a promise
        """
        near.promise_return(promise_idx)
        
    @staticmethod
    def result_success() -> bool:
        """
        Checks if the current callback execution is from a successful promise
        Must be called from within a callback function
        """
        return near.promise_result_is_success()
    
    @staticmethod
    def result_value() -> Any:
        """
        Gets the result value from a successful promise
        Must be called from within a callback function
        Returns the parsed JSON result
        """
        result = near.promise_result_value()
        if result:
            try:
                return json.loads(result.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return result
        return None
    
    @staticmethod
    def result_error() -> Optional[str]:
        """
        Gets the error message if the promise failed
        Must be called from within a callback function
        """
        if not near.promise_result_is_success():
            return near.promise_result_error()
        return None
