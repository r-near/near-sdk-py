"""
Account Operations with NEAR Promises API

This module demonstrates complex account operations with NEAR's Promises API:
- Creating subaccounts
- Managing access keys
- Executing batches of operations
- Complex multi-step sequences

These examples show how to perform advanced operations with promises.
"""

from near_pytest.testing import NearTestCase
import json
import secrets


class TestAccountOperations(NearTestCase):
    """Demonstrates account operations with the Promises API."""

    @classmethod
    def setup_class(cls):
        """Set up contract instances and test accounts."""
        # Call parent setup method first
        super().setup_class()

        # Compile the contract
        wasm_path = cls.compile_contract(
            "integration_tests/contracts/account_operations_contract.py",
            single_file=True,
        )

        # Deploy the account operations contract
        cls.contract = cls.create_account("account_ops")
        cls.instance = cls.deploy_contract(cls.contract, wasm_path)

        # Create test user
        cls.alice = cls.create_account("alice")

        # Save initial state for future resets
        cls.save_state()

    def setup_method(self):
        """Reset state before each test method."""
        # Reset to initial state before each test method
        self.reset_state()

    def test_create_subaccount(self):
        """
        Example: Create a subaccount of the current contract.

        This demonstrates how to create a new account using Promise batch operations.

        Promise API used:
        - Promise.create_batch() - Creates a batch for the new account
        - batch.create_account() - Adds account creation action
        - batch.transfer() - Provides initial funds
        - batch.add_full_access_key() - Adds an access key
        """
        # Generate a key pair for the new account
        public_key = "00" + secrets.token_hex(32)  # ED25519 key prefix + random bytes
        subaccount_name = "sub1"

        result = self.instance.call_as(
            account=self.alice,
            method_name="create_subaccount",
            args={
                "name": subaccount_name,
                "public_key": public_key,
                "initial_balance": 10**24,  # 1 NEAR
            },
            gas=300 * 10**12,
        )

        # Parse the JSON result
        response = json.loads(result)

        # Verify the subaccount was created
        assert response["success"] is True
        assert (
            f"{subaccount_name}.{self.contract.account_id}" in response["subaccount_id"]
        )
        assert response["initial_balance"] == 10**24
        assert "Successfully created" in response["message"]

        print(f"Successfully created subaccount: {response}")

        # Verify the account exists on chain
        account_info = self._client.view_account(response["subaccount_id"])
        assert int(account_info["amount"]) == 10**24

    def test_access_key_management(self):
        """
        Example: Add access keys to an account.

        This demonstrates how to add different types of access keys to an account.

        Promise API used:
        - batch.add_full_access_key() - Adds a full access key
        - batch.add_access_key() - Adds a function call key
        """
        # Generate a key pair for the access key
        public_key = "00" + secrets.token_hex(32)  # ED25519 key prefix + random bytes

        # Add a full access key
        result = self.instance.call_as(
            account=self.alice,
            method_name="add_access_key",
            args={
                "account_id": self.contract.account_id,
                "public_key": public_key,
                "is_full_access": True,
            },
            gas=300 * 10**12,
        )

        # Parse the JSON result
        response = json.loads(result)

        # Verify the key was added
        assert response["success"] is True
        assert response["key_type"] == "full access"
        assert "Successfully added" in response["message"]

        print(f"Successfully added full access key: {response}")

        # Now add a function call key
        public_key = "00" + secrets.token_hex(32)  # New key

        result = self.instance.call_as(
            account=self.alice,
            method_name="add_access_key",
            args={
                "account_id": self.contract.account_id,
                "public_key": public_key,
                "is_full_access": False,
                "allowance": 10**25,  # 10 NEAR
                "receiver_id": self.alice.account_id,
                "method_names": ["get_value", "set_value"],
            },
            gas=300 * 10**12,
        )

        # Parse the JSON result
        response = json.loads(result)

        # Verify the function call key was added
        assert response["success"] is True
        assert response["key_type"] == "function call"
        assert "Successfully added" in response["message"]

        print(f"Successfully added function call key: {response}")

    def test_multi_operation_sequence(self):
        """
        Example: Execute a complex sequence of operations.

        This demonstrates how to chain multiple batches and promises
        to perform a complex sequence of operations.

        Promise API used:
        - Chaining multiple batch operations
        - Creating, funding, and initializing an account
        """
        # Generate a key pair for the new account
        public_key = "00" + secrets.token_hex(32)
        subaccount_name = "complex"

        # Execute a multi-operation sequence
        result = self.instance.call_as(
            account=self.alice,
            method_name="multi_operation_sequence",
            args={
                "subaccount_name": subaccount_name,
                "public_key": public_key,
                "deploy_and_init": False,  # No contract deployment in this test
            },
            gas=300 * 10**12,
        )

        # Parse the JSON result
        response = json.loads(result)

        # Verify the sequence completed successfully
        assert response["success"] is True
        assert f"{subaccount_name}.{self.contract.account_id}" in response["account_id"]
        assert "account creation" in response["operations_completed"]

        print(f"Successfully completed multi-operation sequence: {response}")

        # Verify the account exists on chain
        account_info = self._client.view_account(response["account_id"])
        assert int(account_info["amount"]) == 5 * 10**24  # 5 NEAR
