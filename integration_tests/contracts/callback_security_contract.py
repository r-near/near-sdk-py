"""
Contract for testing the security features of the callback decorator.

This contract includes methods to test:
1. Normal cross-contract call with callback
2. Direct callback access (should fail)
3. Callback access from another contract (should fail)
"""

from near_sdk_py import ONE_TGAS, Context, Log, Storage, call, view
from near_sdk_py.promises import CrossContract, PromiseResult, callback


class CallbackSecurityContract:
    """Contract for testing callback security."""

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
    def self_call_with_callback(self, key: str):
        """
        Make a cross-contract call to self with a callback.

        This tests the legitimate usage of a callback.
        """
        # Log the current account for debugging
        current_account = Context.current_account_id()
        Log.info(f"Current account: {current_account}")

        # Create a contract object (to self)
        contract = CrossContract(current_account, gas=10 * ONE_TGAS)

        # Call get_value on self
        promise = contract.call("get_value", key=key)

        # Chain a callback to process the result
        promise = promise.then("process_callback", key=key)

        # Return the promise result
        return promise.value()

    @callback
    def process_callback(self, result: PromiseResult, key: str):
        """
        Process the result of a cross-contract call.

        This callback should only be callable in a promise context
        and only by the contract itself.
        """
        Log.info("Processing callback")
        Log.info(f"Key: {key}")
        Log.info(f"Success: {result.success}")
        Log.info(f"Data: {result.data}")

        # Process the result and return structured data
        return {"success": True, "key": key, "value": result.data, "processed": True}

    @call
    def external_callback_call(self, target_contract: str):
        """
        Attempt to call another contract's callback.

        This tests the security check that prevents external contracts
        from calling callbacks directly.
        """
        # Create a contract object
        other_contract = CrossContract(target_contract, gas=10 * ONE_TGAS)

        # Attempt to call the callback directly
        promise = other_contract.call("process_callback", key="some_key")

        # Return the promise result
        return promise.value()

    @call
    def create_fake_callback_context(self, target_contract: str):
        """
        Attempt to create a fake callback context by first calling a legitimate function,
        then trying to call the other contract's callback in the resulting callback.

        This would test the second security check (contract self-call) by potentially
        bypassing the first check (callback context).
        """
        # First make a legitimate cross-contract call to self
        current_account = Context.current_account_id()

        # Call get_value on self
        contract = CrossContract(current_account, gas=50 * ONE_TGAS)
        promise = contract.call("get_value", key="test_key")

        # Chain a callback that will try to call the other contract's callback
        promise = promise.then("try_external_callback", target_contract=target_contract)

        # Return the promise result
        return promise.value()

    @callback
    def try_external_callback(self, result: PromiseResult, target_contract: str):
        """
        This callback tries to call another contract's callback.

        Because this is called in a legitimate callback context, it tests
        specifically the "contract self-call" security check.
        """
        Log.info(f"In try_external_callback, calling {target_contract}'s callback")

        # Create a contract object for the target contract
        other_contract = CrossContract(target_contract, gas=20 * ONE_TGAS)

        # Try to call the other contract's callback
        promise = other_contract.call("process_callback", key="from_callback_context")

        # Return the promise result
        return promise.value()
