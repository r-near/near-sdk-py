from near_pytest.testing import NearTestCase


class TestBaseContract(NearTestCase):
    @classmethod
    def setup_class(cls):
        """Set up two contract instances and test accounts."""
        # Call parent setup method first
        super().setup_class()

        # Compile the contract
        wasm_path = cls.compile_contract(
            "integration_tests/contracts/base_ergonomics.py", single_file=True
        )

        cls.contract = cls.create_account("contract")

        cls.instance = cls.deploy_contract(cls.contract, wasm_path)

        # Create test user
        cls.alice = cls.create_account("alice")

        # Save initial state for future resets
        cls.save_state()

    def setup_method(self):
        """Reset state before each test method."""
        # Reset to initial state before each test method
        self.reset_state()  # Restores the snapshot, purely additive

    def test_get_greeting(self):
        """Test getting a greeting message."""
        message = "Hello, NEAR world!"
        result = self.instance.call_as(
            account=self.alice,
            method_name="get_greeting",
        )
        assert result == message
        print(f"Successfully retrieved greeting: {message}")

    def test_set_greeting(self):
        """Test setting a greeting message."""
        message = "My cool new greeting!"
        result = self.instance.call_as(
            account=self.alice,
            method_name="set_greeting",
            args={"message": message},
        )
        assert result == f"Greeting updated to: {message}"
        print(f"Successfully set greeting: {message}")
