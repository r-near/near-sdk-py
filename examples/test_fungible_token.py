from pathlib import Path

from near_pytest.testing import NearTestCase

# Constants for testing
TOTAL_SUPPLY = "1000000000000000000000000000"  # 1 billion tokens (with 24 decimals)
ONE_NEAR = "1000000000000000000000000"  # 1 NEAR in yoctoNEAR


class TestFungibleToken(NearTestCase):
    @classmethod
    def setup_class(cls):
        """Set up the test class"""
        # Call parent setup method first
        super().setup_class()

        # Compile the contract
        current_dir = Path(__file__).parent
        contract_path = (
            current_dir / "ft_contract.py"
        )  # Update this path to your converted file
        wasm_path = cls.compile_contract(contract_path, single_file=True)

        # Create contract account
        cls.token = cls.create_account("token")

        # Create test accounts
        cls.owner = cls.create_account("owner")
        cls.alice = cls.create_account("alice")
        cls.bob = cls.create_account("bob")

        # Deploy contract
        cls.token_contract = cls.deploy_contract(
            cls.token,
            wasm_path,
        )

        cls.token_contract.call(
            method_name="new",
            args={
                "owner_id": cls.owner.account_id,
                "total_supply": TOTAL_SUPPLY,
                "metadata": {
                    "spec": "ft-1.0.0",
                    "name": "Test Token",
                    "symbol": "TEST",
                    "decimals": 24,
                    "icon": None,
                },
            },
            gas=300 * 10**12,
        )

        # Register accounts for storage
        # Register Alice
        cls.token_contract.call_as(
            cls.alice,
            method_name="storage_deposit",
            args={"account_id": cls.alice.account_id},
            amount=int(ONE_NEAR),
        )

        # Register Bob
        cls.token_contract.call_as(
            cls.bob,
            method_name="storage_deposit",
            args={"account_id": cls.bob.account_id},
            amount=int(ONE_NEAR),
        )

        # Transfer some tokens to Alice
        cls.token_contract.call_as(
            cls.owner,
            method_name="ft_transfer",
            args={
                "receiver_id": cls.alice.account_id,
                "amount": "100000000000000000000000000",
                "memo": "init",
            },
            amount=1,
        )

        # Save state for tests
        cls.save_state()

    def setup_method(self):
        """Set up each test method by resetting to initial state"""
        # Reset to initial state
        self.reset_state()

    def test_init_state(self):
        """Test initial contract state"""
        # Check total supply
        result = self.token_contract.view("ft_total_supply", {})
        assert result.text == TOTAL_SUPPLY

        # Check owner balance
        owner_balance = self.token_contract.view(
            "ft_balance_of", {"account_id": self.owner.account_id}
        )
        owner_expected_balance = str(
            int(TOTAL_SUPPLY) - 100000000000000000000000000
        )  # Total supply minus Alice's tokens
        assert owner_balance.text == owner_expected_balance

        # Check Alice balance
        alice_balance = self.token_contract.view(
            "ft_balance_of", {"account_id": self.alice.account_id}
        )
        assert (
            alice_balance.text == "100000000000000000000000000"
        )  # 0.1 of total supply

        # Check metadata
        metadata = self.token_contract.view("ft_metadata", {})
        metadata_json = metadata.json()
        assert metadata_json["name"] == "Test Token"
        assert metadata_json["symbol"] == "TEST"
        assert metadata_json["decimals"] == 24

    def test_transfer(self):
        """Test token transfer between accounts"""
        # Alice transfers 10 tokens to Bob
        transfer_amount = "10000000000000000000000000"  # 10 tokens
        self.token_contract.call_as(
            self.alice,
            method_name="ft_transfer",
            args={
                "receiver_id": self.bob.account_id,
                "amount": transfer_amount,
                "memo": "test transfer",
            },
            amount=1,
        )

        # Check Alice's new balance
        alice_balance = self.token_contract.view(
            "ft_balance_of", {"account_id": self.alice.account_id}
        )
        expected_alice_balance = str(100000000000000000000000000 - int(transfer_amount))
        assert alice_balance.text == expected_alice_balance

        # Check Bob's new balance
        bob_balance = self.token_contract.view(
            "ft_balance_of", {"account_id": self.bob.account_id}
        )
        assert bob_balance.text == transfer_amount

    def test_transfer_error_insufficient_funds(self):
        """Test transfer with insufficient funds"""
        # Alice tries to transfer more tokens than she has
        transfer_amount = "200000000000000000000000000"  # More than Alice has

        try:
            self.token_contract.call_as(
                self.alice,
                method_name="ft_transfer",
                args={
                    "receiver_id": self.bob.account_id,
                    "amount": transfer_amount,
                    "memo": "should fail",
                },
                amount=1,
            )
            assert False, "Transfer should have failed"
        except Exception as e:
            # Verify an error occurred
            assert "Not enough balance" in str(e)

        # Verify balances didn't change
        alice_balance = self.token_contract.view(
            "ft_balance_of", {"account_id": self.alice.account_id}
        )
        assert alice_balance.text == "100000000000000000000000000"

        bob_balance = self.token_contract.view(
            "ft_balance_of", {"account_id": self.bob.account_id}
        )
        assert bob_balance.text == "0"

    def test_transfer_error_unregistered_receiver(self):
        """Test transfer to an unregistered account"""
        # Create a new unregistered account
        unregistered = self.create_account("unregistered")

        try:
            self.token_contract.call_as(
                self.alice,
                method_name="ft_transfer",
                args={
                    "receiver_id": unregistered.account_id,
                    "amount": "10000000000000000000000000",
                    "memo": "",
                },
                amount=1,
            )
            assert False, "Transfer should have failed"
        except Exception as e:
            # Verify the error is about unregistered account
            assert "not registered" in str(e).lower()

    def test_storage_registration(self):
        """Test storage registration and withdrawal"""
        # Create a new account
        new_user = self.create_account("new_user")

        # Register the account
        deposit_amount = int(ONE_NEAR)  # 1 NEAR
        register_result = self.token_contract.call_as(
            new_user,
            method_name="storage_deposit",
            args={"account_id": new_user.account_id},
            amount=deposit_amount,
        )

        # Check that registration worked
        balance_info = register_result.json()
        assert balance_info is not None
        assert "total" in balance_info

        # Now the account should have a storage balance
        result = self.token_contract.view(
            "storage_balance_of", {"account_id": new_user.account_id}
        )
        balance_data = result.json()
        assert balance_data is not None
        assert "total" in balance_data

        # Balance of tokens should still be 0
        token_balance = self.token_contract.view(
            "ft_balance_of", {"account_id": new_user.account_id}
        )
        assert token_balance.text == "0"

    def test_storage_unregister(self):
        """Test storage unregistration"""
        # Create a new account and register it
        temp_user = self.create_account("temp_user")
        self.token_contract.call_as(
            temp_user,
            method_name="storage_deposit",
            args={"account_id": temp_user.account_id},
            amount=int(ONE_NEAR),
        )

        # Unregister the account
        unregister_result = self.token_contract.call_as(
            temp_user,
            method_name="storage_unregister",
            args={"force": True},
            amount=1,
        )

        # Check that unregistration worked
        assert unregister_result.text == "true"
