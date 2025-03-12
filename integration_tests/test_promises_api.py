from near_pytest.testing import NearTestCase
import json


class TestPromisesAPI(NearTestCase):
    @classmethod
    def setup_class(cls):
        # Call parent setup method first
        super().setup_class()

        # Compile the contract
        wasm_path = cls.compile_contract(
            "integration_tests/contracts/promise_contract.py", single_file=True
        )

        # Deploy two instances of the contract to test cross-contract calls
        cls.contract1 = cls.create_account("contract1")
        cls.contract2 = cls.create_account("contract2")

        cls.instance1 = cls.deploy_contract(cls.contract1, wasm_path)
        cls.instance2 = cls.deploy_contract(cls.contract2, wasm_path)

        # Create test accounts
        cls.alice = cls.create_account("alice")

        # Save initial state for future resets
        cls.save_state()

    def setup_method(self):
        # Reset to initial state before each test method
        self.reset_state()

    def test_basic_functionality(self):
        """Test that the contract's basic methods work."""
        # Set a value
        self.instance1.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": "test_key", "value": "test_value"},
        )

        # Get the value
        get_result = self.instance1.call_as(
            account=self.alice,
            method_name="get_value",
            args={"key": "test_key"},
        )

        # Verify result
        assert get_result == "test_value"

        # Test echo method
        echo_result = self.instance1.call_as(
            account=self.alice,
            method_name="echo",
            args={"message": "hello world"},
        )

        assert echo_result == "hello world"

    def test_cross_contract_call(self):
        """Test the Promise API for cross-contract calls."""
        # First set a value in contract2
        self.instance2.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": "promise_key", "value": "promise_value"},
        )

        # Call contract1's method that will directly call contract2
        result = self.instance1.call_as(
            account=self.alice,
            method_name="direct_call",
            args={"contract_id": self.instance2.account_id, "key": "promise_key"},
            gas=100 * 10**12,  # Allocate sufficient gas
        )

        # The result should be the value from contract2
        assert result == "promise_value"

    def test_nonexistent_key(self):
        """Test cross-contract call for a key that doesn't exist."""
        # Call for a key that doesn't exist (should return default value)
        result = self.instance1.call_as(
            account=self.alice,
            method_name="direct_call",
            args={"contract_id": self.instance2.account_id, "key": "nonexistent_key"},
            gas=100 * 10**12,
        )

        # Should return the default value from get_value
        assert result == "default_value"

    def test_callback_functionality(self):
        """Test Promise API with callback processing."""
        # First set a value in contract2
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
            gas=300 * 10**12,  # Allocate more gas to accommodate the callback
        )

        # Parse the JSON result
        response = json.loads(result)
        print(result)

        # Verify that the callback processed the result correctly
        assert response["success"] is True
        assert response["key"] == "callback_key"
        assert response["value"] == "callback_value"
        assert response["processed"] is True

    def test_promise_join(self):
        """Test joining multiple promises and executing a callback."""
        # First set values in both contracts to test joining promises
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

    def test_promise_chain_call(self):
        """Test promise chaining to call methods on different contracts in sequence."""
        # First set values in both contracts
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

        # Call a method that chains promises to call the first contract, then the second
        result = self.instance1.call_as(
            account=self.alice,
            method_name="chain_calls",
            args={
                "contract_id1": self.instance1.account_id,
                "contract_id2": self.instance2.account_id,
                "key1": "chain_key1",
                "key2": "chain_key2",
            },
            gas=300 * 10**12,  # Allocate more gas for chained promises
        )

        # Parse the JSON result
        response = json.loads(result)

        # Verify the chained operations worked
        assert response["success"] is True
        assert response["original_value"] == "chain_value1"
        assert response["chained_value"] == "chain_value2"

    def test_promise_error_handling(self):
        """Test how the Promise API handles errors in cross-contract calls."""
        # Set a value in contract1 for our test
        self.instance1.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": "error_key", "value": "original_value"},
        )

        # Call a method that will invoke a non-existent method on contract2
        # This should fail, but our contract should handle it gracefully
        result = self.instance1.call_as(
            account=self.alice,
            method_name="call_nonexistent_method",
            args={"contract_id": self.instance2.account_id},
            gas=300 * 10**12,  # Allocate plenty of gas
        )

        # Parse the JSON result
        response = json.loads(result)

        # Verify that the error was properly detected and handled
        assert response["success"] is False
        assert "error" in response
        assert (
            "method does not exist" in response["error"].lower()
            or "failed" in response["error"].lower()
        )

        # Verify that the original state remains unchanged
        check_value = self.instance1.call_as(
            account=self.alice,
            method_name="get_value",
            args={"key": "error_key"},
        )
        assert check_value == "original_value"

    def test_promise_batch_operations(self):
        """Test batch operations using the Promise API."""
        # First, set an initial value
        self.instance1.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": "batch_key", "value": "initial_value"},
        )

        # Now call a method that uses batch operations to:
        # 1. Set a value on the contract itself
        # 2. Call another contract
        # All in a single atomic operation
        result = self.instance1.call_as(
            account=self.alice,
            method_name="execute_batch",
            args={
                "self_key": "batch_key",
                "self_value": "updated_value",
                "other_contract_id": self.instance2.account_id,
                "other_key": "remote_batch_key",
                "other_value": "remote_value",
            },
            gas=300 * 10**12,  # Allocate plenty of gas
        )

        # Parse the JSON result
        response = json.loads(result)

        # Verify the batch operation succeeded
        assert response["success"] is True

        # Verify the local value was updated
        local_value = self.instance1.call_as(
            account=self.alice,
            method_name="get_value",
            args={"key": "batch_key"},
        )
        assert local_value == "updated_value"

        # Verify the remote value was set
        remote_value = self.instance2.call_as(
            account=self.alice,
            method_name="get_value",
            args={"key": "remote_batch_key"},
        )
        assert remote_value == "remote_value"

    def test_multi_contract_promise_chain(self):
        """Test chaining promises across multiple contracts in sequence."""
        # Setup initial values in both contracts
        self.instance1.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": "chain_start", "value": "value_from_contract1"},
        )

        self.instance2.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": "chain_middle", "value": "value_from_contract2"},
        )

        # Call a method that creates a chain: contract1 -> contract2 -> contract1
        result = self.instance1.call_as(
            account=self.alice,
            method_name="multi_contract_chain",
            args={
                "contract1_id": self.instance1.account_id,
                "contract2_id": self.instance2.account_id,
                "start_key": "chain_start",
                "middle_key": "chain_middle",
                "final_key": "chain_result",
            },
            gas=300 * 10**12,  # Allocate plenty of gas
        )

        # Parse the JSON result
        response = json.loads(result)

        # Verify the chain execution succeeded
        assert response["success"] is True
        assert "chain_values" in response
        assert len(response["chain_values"]) == 2
        assert response["chain_values"][0] == "value_from_contract1"
        assert response["chain_values"][1] == "value_from_contract2"

        # Verify the final value was stored correctly
        final_value = self.instance1.call_as(
            account=self.alice,
            method_name="get_value",
            args={"key": "chain_result"},
        )

        # The final value should contain combined information from both contracts
        assert "contract1" in final_value
        assert "contract2" in final_value
