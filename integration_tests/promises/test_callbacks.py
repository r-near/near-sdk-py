"""
Callback Handling with NEAR Promises API

This module demonstrates how to use callbacks with NEAR's Promises API:
- Processing results from cross-contract calls
- Using the @callback decorator
- Joining multiple promises with a single callback
- Creating promise chains for sequential operations

These examples show how to process data returned from other contracts.
"""

from near_pytest.testing import NearTestCase
import json


class TestPromiseCallbacks(NearTestCase):
    """Demonstrates callback patterns with the Promises API."""

    @classmethod
    def setup_class(cls):
        """Set up two contract instances and test accounts."""
        # Call parent setup method first
        super().setup_class()

        # Compile the contract
        wasm_path = cls.compile_contract(
            "integration_tests/contracts/callback_contract.py", single_file=True
        )

        # Deploy two instances of the contract to test cross-contract calls
        cls.contract1 = cls.create_account("contract1")
        cls.contract2 = cls.create_account("contract2")

        cls.instance1 = cls.deploy_contract(cls.contract1, wasm_path)
        cls.instance2 = cls.deploy_contract(cls.contract2, wasm_path)

        # Create test user
        cls.alice = cls.create_account("alice")

        # Save initial state for future resets
        cls.save_state()

    def setup_method(self):
        """Reset state before each test method."""
        # Reset to initial state before each test method
        self.reset_state()

    def test_simple_callback_processing(self):
        """
        Example: Process the result of a cross-contract call with a callback.

        This demonstrates the basic callback pattern where a result from
        another contract is processed before being returned to the caller.

        Promise API used:
        - Contract.call() - Makes the cross-contract call
        - Promise.then() - Adds a callback to process the result
        - @callback decorator - Marks the callback function
        """
        # First set a value in contract2 that we'll retrieve
        self.instance2.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": "callback_key", "value": "callback_value"},
        )

        # Call the method that uses a callback
        result = self.instance1.call_as(
            account=self.alice,
            method_name="call_with_callback",
            args={"contract_id": self.instance2.account_id, "key": "callback_key"},
            gas=300 * 10**12,  # Allocate more gas for the callback
        )

        # Parse the JSON result
        response = json.loads(result)

        # Verify that the callback processed the result correctly
        assert response["success"] is True
        assert response["key"] == "callback_key"
        assert response["value"] == "callback_value"
        assert response["processed"] is True

        print(f"Callback successfully processed data: {response}")

    def test_joining_multiple_promises(self):
        """
        Example: Join results from multiple contracts in a single callback.

        This demonstrates how to make parallel calls to different contracts
        and process all results together in a single callback.

        Promise API used:
        - Promise.join() - Combines multiple promises
        - @multi_callback decorator - Handles multiple promise results
        """
        # Set values in both contracts
        self.instance1.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": "join_key1", "value": "join_value1"},
        )

        self.instance2.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": "join_key2", "value": "join_value2"},
        )

        # Call the method that joins promises
        result = self.instance1.call_as(
            account=self.alice,
            method_name="join_promises",
            args={
                "contract_id1": self.instance1.account_id,
                "contract_id2": self.instance2.account_id,
                "key1": "join_key1",
                "key2": "join_key2",
            },
            gas=300 * 10**12,  # Allocate more gas for multiple promises
        )

        # Parse the JSON result
        response = json.loads(result)

        # Verify that both values were retrieved and combined
        assert response["success"] is True
        assert response["values"] == ["join_value1", "join_value2"]

        print(f"Successfully joined and processed multiple promises: {response}")

    def test_promise_chaining(self):
        """
        Example: Chain multiple promises to execute sequentially.

        This demonstrates how to create a sequence of operations where each
        step depends on the result of the previous step.

        Promise API used:
        - Promise.then() - Chains a callback after a promise
        - Passing data between promise steps
        """
        # Set values in both contracts
        self.instance1.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": "chain_key1", "value": "chain_value1"},
        )

        self.instance2.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": "chain_key2", "value": "chain_value2"},
        )

        # Call the chaining method
        result = self.instance1.call_as(
            account=self.alice,
            method_name="chain_calls",
            args={
                "contract_id1": self.instance1.account_id,
                "contract_id2": self.instance2.account_id,
                "key1": "chain_key1",
                "key2": "chain_key2",
            },
            gas=300 * 10**12,  # Allocate more gas for the chain
        )

        # Parse the JSON result
        response = json.loads(result)

        # Verify the chained operations worked
        assert response["success"] is True
        assert response["original_value"] == "chain_value1"
        assert response["chained_value"] == "chain_value2"

        print(f"Successfully chained multiple promises: {response}")
