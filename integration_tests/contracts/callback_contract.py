"""
Callback Promise Contract for testing the Promise callback API.

This contract demonstrates callback patterns with NEAR Promises:
- Simple callbacks after cross-contract calls
- Multi-promise callbacks with join operations
- Data passing between promises in a chain
"""

from typing import List

from near_sdk_py import ONE_TGAS, Log, Storage, call, view
from near_sdk_py.promises import CrossContract, PromiseResult, callback, multi_callback


class CallbackContract:
    """Contract demonstrating Promise callback patterns"""

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
    def call_with_callback(self, contract_id: str, key: str):
        """Make a cross-contract call with a callback.

        This demonstrates how to receive and process results from
        another contract using the callback pattern.

        Args:
            contract_id: ID of the contract to call
            key: Storage key to retrieve from the other contract
        """
        contract = CrossContract(contract_id, gas=10 * ONE_TGAS)

        # Call get_value on the other contract
        promise = contract.call("get_value", key=key)

        # Chain a callback to process the result when it returns
        promise = promise.then("process_callback", key=key)

        # Return the promise result
        return promise.value()

    @callback
    def process_callback(self, result: PromiseResult, key: str):
        """Process the result of a cross-contract call.

        This function receives the raw result from the other contract
        and can perform additional processing on it.

        Args:
            result: The PromiseResult containing status and data
            key: The original key requested (passed from the calling function)
        """
        Log.info("Processing callback")
        Log.info(f"Key: {key}")
        Log.info(f"Status: {result.status_code}")
        Log.info(f"Data: {result.data}")

        # Process the result and return structured data
        return {"success": True, "key": key, "value": result.data, "processed": True}

    @call
    def join_promises(self, contract_id1: str, contract_id2: str, key1: str, key2: str):
        """Join promises from two contracts and process their results together.

        This demonstrates how to make multiple independent contract calls
        and process all results together in a single callback.

        Args:
            contract_id1: ID of the first contract
            contract_id2: ID of the second contract
            key1: Key to retrieve from first contract
            key2: Key to retrieve from second contract
        """
        # Create first promise to get value from contract1
        contract1 = CrossContract(contract_id1)
        promise1 = contract1.call("get_value", key=key1)

        # Create second promise to get value from contract2
        contract2 = CrossContract(contract_id2)
        promise2 = contract2.call("get_value", key=key2)

        # Join the promises and add a callback
        combined_promise = promise1.join(
            [promise2], "process_join_callback", keys=[key1, key2]
        )

        return combined_promise.value()

    @multi_callback
    def process_join_callback(self, results: List[PromiseResult], keys: list):
        """Process the results of multiple joined promises.

        This callback receives an array of results from all joined promises.

        Args:
            results: List of PromiseResult objects
            keys: The original keys requested
        """
        values = []

        # Process each result
        for i, result in enumerate(results):
            if result.success:
                # Handle different data formats
                if (
                    isinstance(result.data, str)
                    and result.data.startswith('"')
                    and result.data.endswith('"')
                ):
                    value = result.data.strip('"')
                else:
                    value = result.data
                values.append(value)
            else:
                return {"success": False, "error": f"Promise {i} failed"}

        # Return combined results
        return {"success": True, "keys": keys, "values": values}

    @call
    def chain_calls(self, contract_id1: str, contract_id2: str, key1: str, key2: str):
        """Chain calls to retrieve values from multiple contracts sequentially.

        This demonstrates how to chain promises to process data in sequence,
        with each promise depending on the result of the previous one.

        Args:
            contract_id1: ID of the first contract
            contract_id2: ID of the second contract
            key1: Key to retrieve from first contract
            key2: Key to retrieve from second contract
        """
        # Create the first contract
        contract1 = CrossContract(contract_id1)

        # Start the chain by calling the first contract
        promise1 = contract1.call("get_value", key=key1)

        # Then call the second contract, passing along the key for the second value
        combined_promise = promise1.gas(30 * ONE_TGAS).then(
            "process_first_call", second_contract=contract_id2, key2=key2
        )

        # Return the final promise result
        return combined_promise.value()

    @callback
    def process_first_call(
        self, result: PromiseResult, second_contract: str, key2: str
    ):
        """Process the result from the first call and make the next call in the chain.

        Args:
            result: Result from the first contract call
            second_contract: ID of the second contract
            key2: Key to retrieve from second contract
        """
        if not result.success:
            return {"success": False, "error": "First promise failed"}

        # Store the result from the first call
        first_value = result.data

        # Create a contract object for the second call
        contract2 = CrossContract(second_contract)

        # Make the second call
        promise2 = contract2.call("get_value", key=key2)

        # Add another callback to process the second result
        final_promise = promise2.then("process_second_call", original_value=first_value)

        return final_promise.value()

    @callback
    def process_second_call(self, result: PromiseResult, original_value: str):
        """Process the result from the second call and combine with the first result.

        Args:
            result: Result from the second contract call
            original_value: Value from the first contract call
        """
        if not result.success:
            return {"success": False, "error": "Second promise failed"}

        # Combine results from both calls
        return {
            "success": True,
            "original_value": original_value,
            "chained_value": result.data,
        }
