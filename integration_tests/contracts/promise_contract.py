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
