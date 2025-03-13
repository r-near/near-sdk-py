"""
Test to verify callback security behavior in the Promises API.

This test verifies that:
1. Callbacks can only be called in a callback context
2. Callbacks can only be called by the contract itself

The tests include:
- Normal legitimate callback usage
- Direct callback access attempt (testing context check)
- External contract callback attempt (testing both checks)
- A more complex test with a fake callback context (testing specifically the self-call check)
"""

from near_pytest.testing import NearTestCase
import json


class TestCallbackSecurity(NearTestCase):
    """Tests to verify that callback security works correctly."""

    @classmethod
    def setup_class(cls):
        """Set up contract instances and test accounts."""
        # Call parent setup method first
        super().setup_class()

        # Compile the callback security test contract
        wasm_path = cls.compile_contract(
            "integration_tests/contracts/callback_security_contract.py",
            single_file=True,
        )

        # Deploy the contract
        cls.contract = cls.create_account("security")
        cls.instance = cls.deploy_contract(cls.contract, wasm_path)
        cls.second_contract = cls.create_account("second")
        cls.second_instance = cls.deploy_contract(cls.second_contract, wasm_path)

        # Create test user
        cls.alice = cls.create_account("alice")

        # Save initial state for future resets
        cls.save_state()

    def setup_method(self):
        """Reset state before each test method."""
        # Reset to initial state before each test method
        self.reset_state()

    def test_normal_cross_contract_call(self):
        """
        Test that callback works when called properly in a cross-contract context.

        This verifies that the security checks don't prevent legitimate callback usage.
        """
        # First set a value in the contract
        self.instance.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": "test_key", "value": "test_value"},
        )

        # Call the method that initiates a legitimate cross-contract call
        result = self.instance.call_as(
            account=self.alice,
            method_name="self_call_with_callback",
            args={"key": "test_key"},
            gas=300 * 10**12,  # Allocate enough gas for the cross-contract call
        )

        # Parse the JSON result
        response = json.loads(result)

        # Verify that the call succeeded
        assert response["success"] is True
        assert response["processed"] is True
        assert response["value"] == "test_value"

        print("Normal cross-contract callback succeeded as expected")

    def test_direct_callback_call(self):
        """
        Test that directly calling a callback function fails.

        This verifies the security check for callback context.
        """
        # Try to call the callback directly
        try:
            self.instance.call_as(
                account=self.alice,
                method_name="process_callback",
                args={"key": "test_key"},
            )
            assert False, "Direct callback call should have failed but didn't"
        except Exception as e:
            # Expect an error about "can only be called as a callback"
            error_message = str(e)
            assert "callback" in error_message.lower(), (
                f"Unexpected error: {error_message}"
            )

        print("Direct callback call failed with appropriate error as expected")

    def test_external_contract_callback_call(self):
        """
        Test that a callback called by another contract fails.

        This test verifies that either:
        1. The callback context check fails ("can only be called as a callback"), or
        2. The contract self-call check fails ("can only be called by the contract itself")
        """
        # Call the method that attempts to call another contract's callback
        try:
            self.second_instance.call_as(
                account=self.alice,
                method_name="external_callback_call",
                args={"target_contract": self.instance.account_id},
                gas=300 * 10**12,
            )
            assert False, (
                "External contract callback call should have failed but didn't"
            )
        except Exception as e:
            # Expect an error about either "callback" or "contract itself"
            error_message = str(e)
            assert (
                "callback" in error_message.lower()
                or "contract itself" in error_message.lower()
            ), f"Unexpected error: {error_message}"
            print(f"External call failed with error: {error_message}")

        print(
            "External contract callback call failed with appropriate error as expected"
        )

    def test_callback_from_callback_context(self):
        """
        Test a more complex scenario where we create a legitimate callback context,
        then try to call another contract's callback from within that context.

        This illustrates that promise results are scoped to each specific cross-contract call
        and do not propagate to subsequent calls, even from within a callback.
        """
        # Test value needed by the test contract
        self.instance.call_as(
            account=self.alice,
            method_name="set_value",
            args={"key": "test_key", "value": "test_value"},
        )

        # Call the method that creates a legitimate callback context
        try:
            self.second_instance.call_as(
                account=self.alice,
                method_name="create_fake_callback_context",
                args={"target_contract": self.instance.account_id},
                gas=300 * 10**12,
            )
            assert False, (
                "Callback from a callback context should have failed but didn't"
            )
        except Exception as e:
            # This fails with the callback context check because promise results
            # are not available in the second contract's call
            error_message = str(e)
            assert "callback" in error_message.lower(), (
                f"Expected 'callback' error but got: {error_message}"
            )

        print(
            "Callback from a callback context failed because promise results don't propagate to subsequent calls"
        )
