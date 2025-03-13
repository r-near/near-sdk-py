"""
Basic Cross-Contract Calls with NEAR Promises API

This module demonstrates the simplest usage patterns for NEAR's Promises API:
- Simple direct cross-contract calls
- Basic usage of the Contract wrapper
- Return value handling from promises

These examples serve as a foundation for understanding more complex Promise patterns.
"""

from near_pytest.testing import NearTestCase


class TestBasicPromiseCalls(NearTestCase):
    """Demonstrates basic cross-contract calls with the Promises API."""

    @classmethod
    def setup_class(cls):
        """Set up two contract instances and test accounts."""
        # Call parent setup method first
        super().setup_class()

        # Compile the contract
        wasm_path = cls.compile_contract(
            "integration_tests/contracts/basic_contract.py", single_file=True
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

    def test_simple_cross_contract_call(self):
        """
        Example: Make a simple cross-contract call from contract1 to contract2.

        This demonstrates the most basic form of cross-contract call - retrieving
        data from another contract and returning it directly.

        Promise API used:
        - Contract.call() - Makes the cross-contract call
        - Promise.value() - Returns the promise result directly
        """
        # First set a value in contract2 that we'll retrieve
        self.instance2.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": "greeting", "value": "Hello from Contract 2!"},
        )

        # Now use contract1 to call contract2 and retrieve the value
        result = self.instance1.call_as(
            account=self.alice,
            method_name="direct_call",
            args={"contract_id": self.instance2.account_id, "key": "greeting"},
            gas=100 * 10**12,  # Allocate sufficient gas for the cross-contract call
        )

        # Verify we got the value from contract2
        assert result == "Hello from Contract 2!"
        print(f"Successfully retrieved cross-contract data: {result}")

    def test_cross_contract_default_values(self):
        """
        Example: Making a cross-contract call for a non-existent key.

        This example shows what happens when the requested data doesn't exist
        in the target contract - the contract returns a default value instead.
        """
        # Call for a key that doesn't exist in contract2
        result = self.instance1.call_as(
            account=self.alice,
            method_name="direct_call",
            args={"contract_id": self.instance2.account_id, "key": "nonexistent_key"},
            gas=100 * 10**12,
        )

        # The contract should return the default value
        assert result == "default_value"
        print(f"Retrieved default value for non-existent key: {result}")

    def test_echo_method(self):
        """
        Example: Call a simple method that returns its input.

        This demonstrates a basic contract method with no storage or cross-contract
        interaction - useful for measuring baseline gas costs.
        """
        # Test the echo method which simply returns its input
        message = "This is a test message"
        result = self.instance1.call_as(
            account=self.alice,
            method_name="echo",
            args={"message": message},
        )

        assert result == message
        print(f"Echo method successfully returned: {result}")

    def test_writing_and_reading_values(self):
        """
        Example: Write values to storage and read them back.

        This demonstrates the contract's basic storage functionality, which
        is often combined with Promises for more complex operations.
        """
        # Set a value
        test_key = "test_key"
        test_value = "test_value_123"

        self.instance1.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": test_key, "value": test_value},
        )

        # Get the value back
        result = self.instance1.call_as(
            account=self.alice,
            method_name="get_value",
            args={"key": test_key},
        )

        assert result == test_value
        print(f"Successfully stored and retrieved value: {result}")
