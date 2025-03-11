from near_pytest.testing import NearTestCase
import json
import secrets


class TestPromisesBatch(NearTestCase):
    @classmethod
    def setup_class(cls):
        # Call parent setup method first
        super().setup_class()

        # Compile the contract
        wasm_path = cls.compile_contract(
            "integration_tests/contracts/batch.py", single_file=True
        )

        # Deploy two instances of the SimpleAccountCreator contract
        cls.creator1 = cls.create_account("creator1")
        cls.creator2 = cls.create_account("creator2")

        cls.contract1 = cls.deploy_contract(cls.creator1, wasm_path)
        cls.contract2 = cls.deploy_contract(cls.creator2, wasm_path)

        # Create test accounts
        cls.alice = cls.create_account("alice")
        cls.bob = cls.create_account("bob")

        # Save initial state for future resets
        cls.save_state()

    def setup_method(self):
        # Reset to initial state before each test method
        self.reset_state()

    def test_create_subaccount(self):
        # Call contract method

        public_key = secrets.token_hex(32)

        result = self.contract1.call_as(
            account=self.alice,
            method_name="create_subaccount",
            args={
                "name": "sub",
                "public_key": "00" + public_key,  # `00` prefix indicates an ED25519 key
            },
        )
        assert json.loads(result) == {
            "success": True,
            "account_id": "sub.creator1.test.near",
            "initial_balance": 4242424242,
        }

        # Check that the account was created, and has the correct balance
        assert self._client.view_account("sub.creator1.test.near")["amount"] == str(
            4242424242
        )

    def test_transfer_and_call(self):
        value, result = self.contract1.call_as(
            account=self.alice,
            method_name="transfer_and_call",
            args={
                "account_id": self.creator2.account_id,
                "amount": 100_000,
            },
            return_full_result=True,
        )
        assert "Received funds from" in "\n".join(result.logs)
