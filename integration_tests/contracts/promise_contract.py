"""
Minimal contract for testing the Promise API in near-sdk-py.

This contract is extremely simplified to minimize gas consumption:
- Basic storage operations
- Direct cross-contract calls with no callbacks when possible
- Minimal Python imports
"""

from near_sdk_py import call, view, Storage
from near_sdk_py.promises import Contract, callback, PromiseResult, multi_callback
from near_sdk_py import ONE_TGAS
from typing import List
import near


class MinimalPromiseContract:
    """A minimal contract for testing the Promise API with lowest gas usage"""

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
    def direct_call(self, contract_id: str, key: str):
        """Make a cross-contract call with no callback.

        This is the simplest possible cross-contract call pattern,
        which should use the minimum amount of gas.
        """
        contract = Contract(contract_id)
        # Call get_value and return the promise directly
        return contract.call("get_value", key=key).value()

    @call
    def echo(self, message: str):
        """Simple method that just returns the input.

        Useful for testing gas usage of a basic call.
        """
        return message

    @call
    def call_with_callback(self, contract_id: str, key: str):
        """Make a cross-contract call with a callback.

        This tests the Promise API's callback functionality.
        """
        contract = Contract(contract_id, gas=10 * ONE_TGAS)
        # Call get_value on the other contract
        promise = contract.call("get_value", key=key)

        promise = promise.then("process_callback", key=key)
        return promise.value()

    @callback
    def process_callback(self, result: PromiseResult, key: str):
        """Process the result of a cross-contract call."""
        near.log_utf8("Processing callback")
        near.log_utf8(f"Key: {key}")
        near.log_utf8(f"Status: {result.status_code}")
        near.log_utf8(f"Data: {result.data}")

        # Do some minimal processing to show we accessed the value
        return {"success": True, "key": key, "value": result.data, "processed": True}

    @call
    def join_promises(self, contract_id1: str, contract_id2: str, key1: str, key2: str):
        """Join promises from two contracts and process their results together."""
        # Create first promise to get value from contract1
        contract1 = Contract(contract_id1)
        promise1 = contract1.call("get_value", key=key1)

        # Create second promise to get value from contract2
        contract2 = Contract(contract_id2)
        promise2 = contract2.call("get_value", key=key2)

        # Join the promises and add a callback
        combined_promise = promise1.join(
            [promise2], "process_join_callback", keys=[key1, key2]
        )

        return combined_promise.value()

    @multi_callback
    def process_join_callback(self, results: List[PromiseResult], keys: list):
        """Process the results of multiple joined promises."""
        values = []

        # Process each result
        for i, result in enumerate(results):
            if result.success:
                # The data might be a simple string in quotes
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

        This demonstrates how to chain promises to process data in sequence, with each
        promise depending on the result of the previous one.
        """
        # Create contract objects
        contract1 = Contract(contract_id1)

        # Start the chain by calling the first contract
        promise1 = contract1.call("get_value", key=key1)

        # Then call the second contract, passing along the key for the second value
        # Notice we don't need to create a Contract object for contract2 here
        combined_promise = promise1.gas(20 * ONE_TGAS).then(
            "process_first_call", second_contract=contract_id2, key2=key2
        )

        # Return the final promise result
        return combined_promise.value()

    @callback
    def process_first_call(
        self, result: PromiseResult, second_contract: str, key2: str
    ):
        """Process the result from the first call and make the next call in the chain."""
        if not result.success:
            return {"success": False, "error": "First promise failed"}

        # Store the result from the first call
        first_value = result.data

        # Create a contract object for the second call
        contract2 = Contract(second_contract)

        # Make the second call, passing the result from the first call in the arguments
        promise2 = contract2.call("get_value", key=key2)

        # Add another callback to process the second result
        final_promise = promise2.then("process_second_call", original_value=first_value)

        return final_promise.value()

    @callback
    def process_second_call(self, result: PromiseResult, original_value: str):
        """Process the result from the second call and combine with the first result."""
        if not result.success:
            return {"success": False, "error": "Second promise failed"}

        # Combine results from both calls
        return {
            "success": True,
            "original_value": original_value,
            "chained_value": result.data,
        }

    @call
    def call_nonexistent_method(self, contract_id: str):
        """Call a method that doesn't exist to test error handling.

        This demonstrates how to handle promise failures gracefully.
        """
        near.log_utf8("Starting call to nonexistent method")

        # Create a contract object with enough gas
        contract = Contract(contract_id, gas=100 * ONE_TGAS)

        # Call a method that doesn't exist on the target contract
        promise = contract.call("this_method_does_not_exist")

        # Add a callback to handle the result (which will be an error)
        final_promise = promise.then("handle_error").gas(100 * ONE_TGAS)

        return final_promise.value()

    @callback
    def handle_error(self, result: PromiseResult):
        """Handle error from a failed promise call.

        This demonstrates error handling in callbacks.
        """
        near.log_utf8(f"Handling promise result: success={result.success}")

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
    def execute_batch(
        self,
        self_key: str,
        self_value: str,
        other_contract_id: str,
        other_key: str,
        other_value: str,
    ):
        """Execute multiple operations as a batch.

        This demonstrates using Promise.batch to perform multiple operations atomically.
        """
        near.log_utf8("Starting batch execution")

        # First, update our own state directly
        Storage.set(self_key, self_value)

        # Create a batch for the other contract
        contract2 = Contract(other_contract_id)
        batch = contract2.batch()

        # Add operations to the batch
        batch.function_call(
            "set_value", {"key": other_key, "value": other_value}, gas=50 * ONE_TGAS
        )

        # Add a callback to handle completion
        promise = batch.then("contract1.test.near").function_call(
            "batch_callback",
            {"self_key": self_key, "other_key": other_key},
            gas=50 * ONE_TGAS,
        )

        return promise.value()

    @callback
    def batch_callback(self, result: PromiseResult, self_key: str, other_key: str):
        """Handle completion of the batch operations."""
        near.log_utf8(f"Batch callback: success={result.success}")

        if not result.success:
            return {
                "success": False,
                "error": f"Batch execution failed: status_code={result.status_code}",
            }

        # Return success with info about what was updated
        return {
            "success": True,
            "message": "Batch operations completed successfully",
            "updated_keys": [self_key, other_key],
        }

    @call
    def multi_contract_chain(
        self,
        contract1_id: str,
        contract2_id: str,
        start_key: str,
        middle_key: str,
        final_key: str,
    ):
        """Execute a promise chain across multiple contracts."""
        near.log_utf8("Starting multi-contract promise chain")

        promise = (
            Contract(contract1_id, gas=30 * ONE_TGAS)
            .call("get_value", key=start_key)
            .then(
                "chain_to_contract2",
                contract2_id=contract2_id,
                middle_key=middle_key,
                final_key=final_key,
            )
        )

        return promise.value()

    @callback
    def chain_to_contract2(
        self, result: PromiseResult, contract2_id: str, middle_key: str, final_key: str
    ):
        """Chain from contract1 to contract2."""
        near.log_utf8("Chain to contract2 callback")

        if not result.success:
            return {"success": False, "error": "Failed to get value from contract1"}

        # Get result from contract1
        value1 = result.data

        final_promise = (
            Contract(contract2_id)
            .call("get_value", key=middle_key)
            .then("final_callback", value1=value1, final_key=final_key)
        )

        return final_promise.value()

    @callback
    def final_callback(self, result: PromiseResult, value1: str, final_key: str):
        """Final callback to process results from both contracts."""
        near.log_utf8("Final callback")

        if not result.success:
            return {"success": False, "error": "Failed to get value from contract2"}

        # Get result from contract2
        value2 = result.data

        # Combine results from both contracts
        combined_value = f"Values from contract1: {value1} and contract2: {value2}"

        # Store the combined result
        Storage.set(final_key, combined_value)

        # Return success with all collected values
        return {
            "success": True,
            "message": "Multi-contract chain completed successfully",
            "chain_values": [value1, value2],
            "combined": combined_value,
        }


# Create an instance and export the methods
contract = MinimalPromiseContract()

# Export contract methods
get_value = contract.get_value
set_value = contract.set_value
direct_call = contract.direct_call
echo = contract.echo
call_with_callback = contract.call_with_callback
process_callback = contract.process_callback
join_promises = contract.join_promises
process_join_callback = contract.process_join_callback
chain_calls = contract.chain_calls
process_first_call = contract.process_first_call
process_second_call = contract.process_second_call
call_nonexistent_method = contract.call_nonexistent_method
handle_error = contract.handle_error
execute_batch = contract.execute_batch
batch_callback = contract.batch_callback
multi_contract_chain = contract.multi_contract_chain
chain_to_contract2 = contract.chain_to_contract2
final_callback = contract.final_callback
