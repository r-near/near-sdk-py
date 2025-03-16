"""
Token and Gas Management with NEAR Promises API

This module demonstrates how to manage tokens and gas with NEAR's Promises API:
- Attaching NEAR tokens to function calls
- Setting gas limits for promises
- Using proportional gas allocation
- Transferring tokens between accounts

These examples show how to work with NEAR's economic model in promises.
"""

import json

from near_pytest.testing import NearTestCase


class TestTokenGasManagement(NearTestCase):
    """Demonstrates token and gas management with the Promises API."""

    @classmethod
    def setup_class(cls):
        """Set up contract instances and test accounts."""
        # Call parent setup method first
        super().setup_class()

        # Compile the contract
        wasm_path = cls.compile_contract(
            "integration_tests/contracts/token_gas_contract.py", single_file=True
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

    def test_attaching_tokens(self):
        """
        Example: Attach NEAR tokens to a cross-contract call.

        This demonstrates how to send NEAR tokens along with a function call.

        Promise API used:
        - Contract.deposit() - Sets the token amount
        - Contract.call() - Makes the call with attached tokens
        """
        # Test token attachment
        amount = 10**23  # 0.1 NEAR

        result = self.instance1.call_as(
            account=self.alice,
            method_name="call_with_tokens",
            args={
                "contract_id": self.instance2.account_id,
                "method": "receive_funds",
                "args": {},
                "amount": amount,
            },
            gas=300 * 10**12,
        )

        # Parse the JSON result
        response = json.loads(result)

        # Verify the tokens were attached and received
        assert response["success"] is True
        assert response["tokens_attached"] is True

        # Parse the inner result
        inner_result = response["result"]

        # Check the received funds details
        assert inner_result["success"] is True
        assert int(inner_result["deposit"]) == amount
        assert "Received" in inner_result["message"]

        print(f"Successfully attached tokens: {response}")

    def test_fixed_gas_limit(self):
        """
        Example: Set a fixed gas limit for a cross-contract call.

        This demonstrates how to allocate a specific amount of gas
        to a promise call.

        Promise API used:
        - Contract(gas=amount) - Sets the gas limit at creation
        - Promise.gas() - Sets the gas limit for a promise
        """
        # Set a value to retrieve
        test_key = "gas_test_key"
        test_value = "gas_test_value"

        self.instance2.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": test_key, "value": test_value},
        )

        # Test with a fixed gas amount
        gas_amount = 20 * 10**12  # 20 TGas

        result = self.instance1.call_as(
            account=self.alice,
            method_name="call_with_fixed_gas",
            args={
                "contract_id": self.instance2.account_id,
                "method": "get_value",
                "args": {"key": test_key},
                "gas_amount": gas_amount,
            },
            gas=300 * 10**12,  # Total gas for the entire operation
        )

        # Parse the JSON result
        response = json.loads(result)

        # Verify the fixed gas call worked
        assert response["success"] is True
        assert response["fixed_gas_used"] is True

        # Check the retrieved value
        inner_result = response["result"]
        assert inner_result == test_value

        print(f"Successfully used fixed gas amount: {response}")

    def test_proportional_gas(self):
        """
        Example: Allocate gas proportionally based on available gas.

        This demonstrates how to dynamically allocate gas based on
        what's available to the contract.

        Promise API used:
        - Context.prepaid_gas() - Gets total gas available
        - Context.used_gas() - Gets gas used so far
        - Dynamic gas calculation
        """
        # Set a value to retrieve
        test_key = "prop_gas_key"
        test_value = "prop_gas_value"

        self.instance2.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": test_key, "value": test_value},
        )

        # Test with proportional gas allocation
        # Use 1/3 of available gas for the call
        gas_fraction = 3

        result = self.instance1.call_as(
            account=self.alice,
            method_name="call_with_proportional_gas",
            args={
                "contract_id": self.instance2.account_id,
                "method": "get_value",
                "args": {"key": test_key},
                "gas_fraction": gas_fraction,
            },
            gas=300 * 10**12,  # Total gas for the entire operation
        )

        # Parse the JSON result
        response = json.loads(result)

        # Verify the proportional gas call worked
        assert response["success"] is True
        assert response["proportional_gas_used"] is True

        # Check the retrieved value
        inner_result = response["result"]
        assert inner_result == test_value

        print(f"Successfully used proportional gas allocation: {response}")

    def test_transfer_and_call(self):
        """
        Example: Transfer tokens and call a method in a single operation.

        This demonstrates the common pattern of sending tokens to a contract
        and calling a method on it in the same transaction.

        Promise API used:
        - Promise.create_batch() - Creates a batch of operations
        - PromiseBatch.transfer() - Transfers tokens
        - PromiseBatch.function_call() - Calls a function after transfer
        """
        # Amount to transfer
        amount = 10**23  # 0.1 NEAR

        result = self.instance1.call_as(
            account=self.alice,
            method_name="transfer_and_call",
            args={
                "recipient_id": self.instance2.account_id,
                "amount": amount,
                "method": "receive_funds",
                "args": {},
            },
            gas=300 * 10**12,
        )

        # Parse the JSON result
        response = json.loads(result)

        # Verify the transfer succeeded
        assert response["success"] is True
        assert response["recipient_id"] == self.instance2.account_id
        assert response["amount"] == amount
        assert "Successfully transferred" in response["message"]

        print(f"Successfully transferred tokens and called method: {response}")
