"""
Error Handling with NEAR Promises API

This module demonstrates how to handle errors with NEAR's Promises API:
- Detecting and handling failed promises
- Implementing error recovery strategies
- Conditional processing based on promise results

These examples show how to build robust cross-contract interactions
that can handle failure cases gracefully.
"""

import json

from near_pytest.testing import NearTestCase


class TestPromiseErrorHandling(NearTestCase):
    """Demonstrates error handling patterns with the Promises API."""

    @classmethod
    def setup_class(cls):
        """Set up contract instances and test accounts."""
        # Call parent setup method first
        super().setup_class()

        # Compile the contract
        wasm_path = cls.compile_contract(
            "integration_tests/contracts/error_handling_contract.py", single_file=True
        )

        # Deploy two instances of the contract
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

    def test_handling_method_not_found(self):
        """
        Example: Gracefully handling calls to non-existent methods.

        This demonstrates how to detect and handle the case where
        a cross-contract call fails because the method doesn't exist.

        Promise API used:
        - Error detection in callbacks
        - Structured error responses
        """
        # Set a value we can verify doesn't change on error
        self.instance1.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": "original_key", "value": "original_value"},
        )

        # Call a method that tries to call a non-existent method on contract2
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
        assert "handled" in response and response["handled"] is True

        # Check that the method has useful error information
        assert (
            "failed" in response["error"].lower()
            or "does not exist" in response["error"].lower()
        )

        print(f"Successfully handled non-existent method call: {response}")

    def test_fallback_strategy(self):
        """
        Example: Implementing a fallback strategy when a primary call fails.

        This demonstrates how to try one contract first, then fall back to
        another contract if the first call fails.

        Promise API used:
        - Error detection and recovery
        - Chaining promises conditionally
        """
        # Set up values in both contracts
        test_key = "fallback_key"
        primary_value = "primary_value"
        fallback_value = "fallback_value"

        # Set up values in both contracts
        self.instance1.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": test_key, "value": primary_value},
        )

        self.instance2.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": test_key, "value": fallback_value},
        )

        # First test the happy path - primary contract succeeds
        result = self.instance1.call_as(
            account=self.alice,
            method_name="call_with_fallback",
            args={
                "primary_contract_id": self.instance1.account_id,
                "fallback_contract_id": self.instance2.account_id,
                "key": test_key,
            },
            gas=300 * 10**12,
        )

        # Parse the JSON result
        response = json.loads(result)

        # Verify primary call succeeded
        assert response["success"] is True
        assert response["value"] == primary_value
        assert response["source"] == "primary"

        print(f"Successfully used primary contract: {response}")

        # Now test the fallback path by using an invalid contract as primary
        nonexistent_account = "nonexistent.near"

        result = self.instance1.call_as(
            account=self.alice,
            method_name="call_with_fallback",
            args={
                "primary_contract_id": nonexistent_account,
                "fallback_contract_id": self.instance2.account_id,
                "key": test_key,
            },
            gas=300 * 10**12,
        )

        # Parse the JSON result
        response = json.loads(result)

        # Verify fallback was used
        assert response["success"] is True
        assert response["value"] == fallback_value
        assert response["source"] == "fallback"

        print(f"Successfully used fallback contract: {response}")

    def test_conditional_processing(self):
        """
        Example: Conditionally processing results based on criteria.

        This demonstrates how to check if a promise result meets certain
        criteria before processing it further.

        Promise API used:
        - Conditional logic in callbacks
        - Data validation in promise chains
        """
        # Set up test values of different lengths
        short_key = "short_key"
        short_value = "abc"  # 3 chars

        long_key = "long_key"
        long_value = "abcdefghijklmnopqrstuvwxyz"  # 26 chars

        # Set values in the contract
        self.instance2.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": short_key, "value": short_value},
        )

        self.instance2.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": long_key, "value": long_value},
        )

        # Test with short value (should not meet criteria)
        min_length = 10
        result = self.instance1.call_as(
            account=self.alice,
            method_name="conditional_callback",
            args={
                "contract_id": self.instance2.account_id,
                "key": short_key,
                "min_length": min_length,
            },
            gas=200 * 10**12,
        )

        # Parse the JSON result
        response = json.loads(result)

        # Verify criteria check failed but call succeeded
        assert response["success"] is True
        assert response["meets_criteria"] is False
        assert "error" in response

        print(f"Short value correctly failed criteria check: {response}")

        # Test with long value (should meet criteria)
        result = self.instance1.call_as(
            account=self.alice,
            method_name="conditional_callback",
            args={
                "contract_id": self.instance2.account_id,
                "key": long_key,
                "min_length": min_length,
            },
            gas=200 * 10**12,
        )

        # Parse the JSON result
        response = json.loads(result)

        # Verify criteria check passed
        assert response["success"] is True
        assert response["meets_criteria"] is True
        assert response["value"] == long_value
        assert response["length"] > min_length

        print(f"Long value correctly passed criteria check: {response}")
