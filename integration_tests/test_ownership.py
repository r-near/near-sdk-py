import json

from near_pytest.testing import NearTestCase


class TestOwnershipContract(NearTestCase):
    """Test contract ownership and access control features."""

    @classmethod
    def setup_class(cls):
        """Compile and deploy the ownership test contract."""
        super().setup_class()

        # Compile the contract
        wasm_path = cls.compile_contract(
            "integration_tests/contracts/ownership_contract.py", single_file=True
        )

        # Deploy the contract
        cls.contract_account = cls.create_account("contract-account")
        cls.instance = cls.deploy_contract(cls.contract_account, wasm_path)

        cls.alice = cls.create_account("alice")
        cls.bob = cls.create_account("bob")

        # Initialize the contract with owner
        cls.instance.call_as(
            account=cls.contract_account,
            method_name="initialize",
            args={"owner": cls.alice.account_id},
        )

        # Save state after deployment and initialization
        cls.save_state()

    def test_get_owner(self):
        """Test retrieving the contract owner."""
        owner = self.instance.call_as(account=self.bob, method_name="get_owner")

        assert owner == self.alice.account_id

    def test_owner_can_update_config(self):
        """Test that owner can update contract configuration."""
        result = self.instance.call_as(
            account=self.alice,
            method_name="update_config",
            args={"key": "max_users", "value": 100},
        )
        result = json.loads(result)
        assert result["success"] is True

        # Verify config was updated
        config = self.instance.call_as(
            account=self.alice, method_name="get_config", args={"key": "max_users"}
        )

        assert int(config) == 100

    def test_non_owner_cannot_update_config(self):
        """Test that non-owners cannot update contract configuration."""
        try:
            self.instance.call_as(
                account=self.bob,
                method_name="update_config",
                args={"key": "max_users", "value": 200},
            )
            assert False, "Non-owner should not be able to update config"
        except Exception as e:
            assert "AccessDenied" in str(e)

    def test_transfer_ownership(self):
        """Test transferring contract ownership."""
        # Alice (owner) transfers ownership to Bob
        result = self.instance.call_as(
            account=self.alice,
            method_name="transfer_ownership",
            args={"new_owner": self.bob.account_id},
        )
        result = json.loads(result)
        assert result["success"] is True

        # Verify Bob is now the owner
        owner = self.instance.call_as(account=self.bob, method_name="get_owner")

        assert owner == self.bob.account_id

        # Verify Bob can now update config
        result = self.instance.call_as(
            account=self.bob,
            method_name="update_config",
            args={"key": "max_users", "value": 200},
        )
        result = json.loads(result)
        assert result["success"] is True
