"""
Error Handling contract for testing the Promise API error handling capabilities.

This contract demonstrates error handling patterns with NEAR Promises:
- Detecting and handling failed promises
- Error recovery strategies
- Graceful error handling in callbacks
"""

from near_sdk_py import ONE_TGAS, Log, Storage, call, view
from near_sdk_py.promises import CrossContract, PromiseResult, callback


class ErrorHandlingContract:
    """Contract demonstrating Promise error handling patterns"""

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
    def call_nonexistent_method(self, contract_id: str):
        """Call a method that doesn't exist to test error handling.

        This demonstrates how to gracefully handle promise failures.

        Args:
            contract_id: ID of the contract to call
        """
        Log.info("Starting call to nonexistent method")

        # Create a contract object with enough gas
        contract = CrossContract(contract_id, gas=100 * ONE_TGAS)

        # Call a method that doesn't exist on the target contract
        promise = contract.call("this_method_does_not_exist")

        # Add a callback to handle the result (which will be an error)
        final_promise = promise.then("handle_error").gas(100 * ONE_TGAS)

        return final_promise.value()

    @callback
    def handle_error(self, result: PromiseResult):
        """Handle error from a failed promise call.

        This demonstrates error handling in callbacks.

        Args:
            result: The PromiseResult containing status and error data
        """
        Log.info(f"Handling promise result: success={result.success}")

        if result.success:
            return {
                "success": True,
                "message": "Method executed successfully (unexpected)",
            }
        else:
            # Handle the error gracefully
            return {
                "success": False,
                "error": f"Method call failed as expected: status_code={result.status_code}",
                "handled": True,
            }

    @call
    def call_with_fallback(
        self, primary_contract_id: str, fallback_contract_id: str, key: str
    ):
        """Try to call a primary contract, but fall back to another if it fails.

        This demonstrates a practical error recovery pattern.

        Args:
            primary_contract_id: First contract to try
            fallback_contract_id: Backup contract to use if first fails
            key: Storage key to retrieve
        """
        # Try the primary contract first
        contract = CrossContract(primary_contract_id, gas=30 * ONE_TGAS)
        promise = contract.call("get_value", key=key)

        # Add callback that will check the result and potentially use the fallback
        final_promise = promise.then(
            "process_with_fallback", fallback_contract_id=fallback_contract_id, key=key
        )

        return final_promise.value()

    @callback
    def process_with_fallback(
        self, result: PromiseResult, fallback_contract_id: str, key: str
    ):
        """Process result with fallback if needed.

        Args:
            result: Result from the primary contract call
            fallback_contract_id: Backup contract ID to use if needed
            key: Storage key to retrieve
        """
        # If primary call succeeded, just return the result
        if result.success:
            return {"success": True, "value": result.data, "source": "primary"}

        # Primary call failed, try the fallback
        Log.info("Primary call failed, using fallback contract")
        fallback_contract = CrossContract(fallback_contract_id)
        fallback_promise = fallback_contract.call("get_value", key=key)

        # Add another callback to process the fallback result
        final_promise = fallback_promise.then("process_fallback_result")

        return final_promise.value()

    @callback
    def process_fallback_result(self, result: PromiseResult):
        """Process the result from the fallback contract.

        Args:
            result: Result from the fallback contract call
        """
        if result.success:
            return {"success": True, "value": result.data, "source": "fallback"}
        else:
            # Both primary and fallback failed
            return {
                "success": False,
                "error": "Both primary and fallback calls failed",
            }

    @call
    def conditional_callback(self, contract_id: str, key: str, min_length: int):
        """Call another contract but only process result if value meets criteria.

        Demonstrates conditional processing based on promise results.

        Args:
            contract_id: Contract to call
            key: Storage key to retrieve
            min_length: Minimum length for the value to be processed
        """
        contract = CrossContract(contract_id, gas=20 * ONE_TGAS)
        promise = contract.call("get_value", key=key)

        # Chain a callback that will check the criteria
        final_promise = promise.then("check_result_criteria", min_length=min_length)

        return final_promise.value()

    @callback
    def check_result_criteria(self, result: PromiseResult, min_length: int):
        """Check if result meets criteria and process accordingly.

        Args:
            result: The promise result
            min_length: Minimum length required
        """
        if not result.success:
            return {"success": False, "error": "Failed to retrieve value"}

        value = result.data
        if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
            value = value.strip('"')

        # Check if value meets criteria
        if len(value) >= min_length:
            # Process the value
            return {
                "success": True,
                "value": value,
                "meets_criteria": True,
                "length": len(value),
            }
        else:
            # Value doesn't meet criteria
            return {
                "success": True,
                "meets_criteria": False,
                "error": f"Value length {len(value)} is less than required {min_length}",
            }
