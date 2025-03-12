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
