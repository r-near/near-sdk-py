import json

from near_pytest.testing import NearTestCase


class TestSimpleGreetingContract(NearTestCase):
    """Test the basics of the Contract class with a simple greeting contract."""

    @classmethod
    def setup_class(cls):
        """Compile and deploy the greeting contract."""
        super().setup_class()

        cls.contract_account = cls.create_account("contract-account")
        cls.alice = cls.create_account("alice")

        # Compile the contract
        wasm_path = cls.compile_contract(
            "integration_tests/contracts/greeting_contract.py", single_file=True
        )

        # Deploy the contract
        cls.instance = cls.deploy_contract(cls.contract_account, wasm_path)

        # Initialize the contract
        cls.instance.call_as(
            account=cls.contract_account,
            method_name="initialize",
            args={"default_message": "Initial greeting"},
        )

        # Save state after deployment and initialization
        cls.save_state()

    def setup_method(self):
        """Reset state before each test method."""
        self.reset_state()

    def test_get_greeting_default(self):
        """Test retrieving the default greeting."""
        greeting = self.instance.call_as(account=self.alice, method_name="get_greeting")

        assert greeting == "Initial greeting"

    def test_set_greeting(self):
        """Test setting a new greeting."""
        new_greeting = "Hello from Alice!"

        result = self.instance.call_as(
            account=self.alice,
            method_name="set_greeting",
            args={"message": new_greeting},
        )

        result = json.loads(result)

        assert result["success"] is True

        # Verify the greeting was updated
        greeting = self.instance.call_as(account=self.alice, method_name="get_greeting")

        assert greeting == new_greeting

    def test_get_greeting_with_args(self):
        """Test greeting with language parameter."""
        # First make sure we have a greeting set
        self.instance.call_as(
            account=self.alice,
            method_name="set_greeting",
            args={"message": "Hello world!"},
        )

        # Get greeting in different languages
        english = self.instance.call_as(
            account=self.alice,
            method_name="get_greeting_with_language",
            args={"language": "english"},
        )

        spanish = self.instance.call_as(
            account=self.alice,
            method_name="get_greeting_with_language",
            args={"language": "spanish"},
        )

        assert english == "Hello world!"
        assert spanish == "¡Hola mundo!"
