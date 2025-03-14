from near_pytest import NearTestCase
import json


class TestStorageContract(NearTestCase):
    """Test the dictionary-like storage interface."""

    @classmethod
    def setup_class(cls):
        """Compile and deploy the storage test contract."""
        super().setup_class()

        # Compile the contract
        wasm_path = cls.compile_contract(
            "integration_tests/contracts/storage_contract.py", single_file=True
        )

        # Deploy the contract
        cls.contract_account = cls.create_account("contract-account")
        cls.alice = cls.create_account("alice")
        cls.instance = cls.deploy_contract(cls.contract_account, wasm_path)

        # Initialize the contract
        cls.instance.call_as(account=cls.contract_account, method_name="initialize")

        # Save state after deployment and initialization
        cls.save_state()

    def test_set_and_get(self):
        """Test basic set and get operations with the storage interface."""
        # Set a value
        self.instance.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": "test_key", "value": "test_value"},
        )

        # Get the value
        value = self.instance.call_as(
            account=self.alice, method_name="get_value", args={"key": "test_key"}
        )

        assert value == "test_value"

    def test_get_with_default(self):
        """Test getting a value with a default when key doesn't exist."""
        # Get a non-existent key with default
        value = self.instance.call_as(
            account=self.alice,
            method_name="get_value_with_default",
            args={"key": "nonexistent_key", "default": "default_value"},
        )

        assert value == "default_value"

    def test_delete_key(self):
        """Test deleting a key from storage."""
        # Set a value
        self.instance.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": "temp_key", "value": "temp_value"},
        )

        # Delete the key
        self.instance.call_as(
            account=self.alice, method_name="delete_value", args={"key": "temp_key"}
        )

        # Try to get the deleted key with default
        value = self.instance.call_as(
            account=self.alice,
            method_name="get_value_with_default",
            args={"key": "temp_key", "default": "was_deleted"},
        )

        assert value == "was_deleted"

    def test_contains_key(self):
        """Test checking if storage contains a key."""
        # Set a value
        self.instance.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": "exists_key", "value": "exists_value"},
        )

        # Check if key exists
        exists = self.instance.call_as(
            account=self.alice, method_name="has_key", args={"key": "exists_key"}
        )
        exists = json.loads(exists)

        assert exists is True

        # Check if non-existent key exists
        exists = self.instance.call_as(
            account=self.alice, method_name="has_key", args={"key": "nonexistent_key"}
        )
        exists = json.loads(exists)

        assert exists is False

    def test_complex_data(self):
        """Test storing and retrieving complex JSON data."""
        # Set a complex value
        complex_data = {
            "name": "Test User",
            "age": 30,
            "is_active": True,
            "scores": [95, 87, 92],
            "address": {"city": "Test City", "country": "Test Country"},
        }

        self.instance.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": "user_data", "value": complex_data},
        )

        # Get the complex value
        result = self.instance.call_as(
            account=self.alice, method_name="get_value", args={"key": "user_data"}
        )
        result = json.loads(result)

        assert result == complex_data
