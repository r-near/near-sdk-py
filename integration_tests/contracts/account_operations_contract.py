"""
Account Operations Contract for testing Promise batch actions.

This contract demonstrates complex Promise patterns with batch operations:
- Creating subaccounts
- Adding/removing access keys
- Deploying contracts to accounts
- Executing complex multi-operation sequences
"""

from typing import Optional

from near_sdk_py import ONE_NEAR, ONE_TGAS, Context, Log, Storage, call, view
from near_sdk_py.promises import Promise, PromiseResult, callback


class AccountOperationsContract:
    """Contract demonstrating account operations with Promise batches"""

    @view
    def get_value(self, key: str):
        """Get a value from storage or return default."""
        return Storage.get_string(key) or "default_value"

    @call
    def set_value(self, key: str, value: str):
        """Set a value in storage."""
        Storage.set(key, value)
        return {"success": True, "key": key, "value": value}

    @call
    def create_subaccount(
        self, name: str, public_key: str, initial_balance: int = ONE_NEAR
    ):
        """Create a subaccount of the current contract account.

        This demonstrates using Promise batch operations to create an account.

        Args:
            name: Name of the subaccount (name.currentaccount.near)
            public_key: Hex-encoded public key for the new account
            initial_balance: Initial balance for the new account (in yoctoNEAR)
        """
        # Get the current account ID
        current_account = Context.current_account_id()

        # Form the new account ID
        new_account_id = f"{name}.{current_account}"
        Log.info(f"Creating subaccount: {new_account_id}")

        # Decode the public key
        key_bytes = bytes.fromhex(public_key)

        # Create a batch of actions
        batch = Promise.create_batch(new_account_id)

        # Add account creation actions to the batch
        batch.create_account().transfer(initial_balance).add_full_access_key(key_bytes)

        # Add a callback to confirm creation
        promise = batch.then(Context.current_account_id()).function_call(
            "subaccount_created",
            {"subaccount_id": new_account_id, "initial_balance": initial_balance},
            gas=10 * ONE_TGAS,
        )

        return promise.value()

    @callback
    def subaccount_created(
        self, result: PromiseResult, subaccount_id: str, initial_balance: int
    ):
        """Handle completion of subaccount creation.

        Args:
            result: Result of the creation operation
            subaccount_id: The newly created account ID
            initial_balance: Initial balance provided
        """
        if not result.success:
            return {
                "success": False,
                "error": f"Failed to create subaccount: {result.status_code}",
            }

        return {
            "success": True,
            "subaccount_id": subaccount_id,
            "initial_balance": initial_balance,
            "message": f"Successfully created subaccount {subaccount_id}",
        }

    @call
    def add_access_key(
        self,
        account_id: str,
        public_key: str,
        is_full_access: bool = True,
        allowance: Optional[int] = None,
        receiver_id: Optional[str] = None,
        method_names: Optional[list] = None,
    ):
        """Add an access key to an account.

        This demonstrates adding different types of access keys.

        Args:
            account_id: Account to add the key to
            public_key: Hex-encoded public key to add
            is_full_access: If True, add as full access key; otherwise as function call key
            allowance: Token allowance for function call key (None for unlimited)
            receiver_id: Receiver contract for function call key
            method_names: Allowed methods for function call key
        """
        # Decode the public key
        key_bytes = bytes.fromhex(public_key)

        # Create a batch for the account
        batch = Promise.create_batch(account_id)

        # Add the appropriate key
        if is_full_access:
            Log.info(f"Adding full access key to {account_id}")
            batch.add_full_access_key(key_bytes)
        else:
            if not receiver_id:
                raise ValueError("receiver_id is required for function call keys")

            Log.info(f"Adding function call key to {account_id} for {receiver_id}")
            batch.add_access_key(key_bytes, allowance, receiver_id, method_names or [])

        # Add a callback to confirm key addition
        promise = batch.then(Context.current_account_id()).function_call(
            "key_added",
            {"account_id": account_id, "is_full_access": is_full_access},
            gas=10 * ONE_TGAS,
        )

        return promise.value()

    @callback
    def key_added(self, result: PromiseResult, account_id: str, is_full_access: bool):
        """Handle completion of key addition.

        Args:
            result: Result of the key addition operation
            account_id: Account that received the key
            is_full_access: Whether the key was full access
        """
        if not result.success:
            return {
                "success": False,
                "error": f"Failed to add key: {result.status_code}",
            }

        key_type = "full access" if is_full_access else "function call"
        return {
            "success": True,
            "account_id": account_id,
            "key_type": key_type,
            "message": f"Successfully added {key_type} key to {account_id}",
        }

    @call
    def delete_account(self, account_id: str, beneficiary_id: str):
        """Delete an account and transfer its funds to a beneficiary.

        This demonstrates the account deletion operation.

        Args:
            account_id: Account to delete
            beneficiary_id: Account to receive remaining funds
        """
        Log.info(f"Deleting account {account_id}, beneficiary: {beneficiary_id}")

        # Create a batch for the account
        batch = Promise.create_batch(account_id)

        # Add delete action
        batch.delete_account(beneficiary_id)

        # Add a callback to confirm deletion
        promise = batch.then(Context.current_account_id()).function_call(
            "account_deleted",
            {"account_id": account_id, "beneficiary_id": beneficiary_id},
            gas=10 * ONE_TGAS,
        )

        return promise.value()

    @callback
    def account_deleted(
        self, result: PromiseResult, account_id: str, beneficiary_id: str
    ):
        """Handle completion of account deletion.

        Args:
            result: Result of the deletion operation
            account_id: Account that was deleted
            beneficiary_id: Account that received the funds
        """
        if not result.success:
            return {
                "success": False,
                "error": f"Failed to delete account: {result.status_code}",
            }

        return {
            "success": True,
            "account_id": account_id,
            "beneficiary_id": beneficiary_id,
            "message": f"Successfully deleted account {account_id}",
        }

    @call
    def multi_operation_sequence(
        self,
        subaccount_name: str,
        public_key: str,
        deploy_and_init: bool = False,
        contract_code: Optional[bytes] = None,
    ):
        """Execute a complex sequence of operations.

        This demonstrates chaining multiple batches of operations.

        Args:
            subaccount_name: Name for the new subaccount
            public_key: Hex-encoded public key for the new account
            deploy_and_init: Whether to deploy a contract to the new account
            contract_code: WASM contract code to deploy (if deploy_and_init is True)
        """
        # Get the current account ID
        current_account = Context.current_account_id()

        # Form the new account ID
        new_account_id = f"{subaccount_name}.{current_account}"
        Log.info(f"Starting multi-operation sequence for: {new_account_id}")

        # Decode the public key
        key_bytes = bytes.fromhex(public_key)

        # Create a batch for account creation
        batch = Promise.create_batch(new_account_id)

        # Add account creation actions
        batch.create_account().transfer(ONE_NEAR * 5).add_full_access_key(key_bytes)

        # If deploying a contract, chain another batch
        if deploy_and_init and contract_code:
            Log.info("Will deploy contract after account creation")

            # Chain a batch for contract deployment
            promise = batch.then(new_account_id).function_call(
                "deploy_and_init",
                {"account_id": new_account_id, "contract_code": contract_code},
                gas=50 * ONE_TGAS,
            )
        else:
            # Just add a callback to confirm creation
            promise = batch.then(current_account).function_call(
                "multi_sequence_completed",
                {"account_id": new_account_id, "deployed": False},
                gas=10 * ONE_TGAS,
            )

        return promise.value()

    @callback
    def multi_sequence_completed(
        self, result: PromiseResult, account_id: str, deployed: bool
    ):
        """Handle completion of the multi-operation sequence.

        Args:
            result: Result of the operation sequence
            account_id: The account that was created/modified
            deployed: Whether a contract was deployed
        """
        if not result.success:
            return {
                "success": False,
                "error": f"Multi-operation sequence failed: {result.status_code}",
            }

        operations = ["account creation"]
        if deployed:
            operations.append("contract deployment")

        return {
            "success": True,
            "account_id": account_id,
            "operations_completed": operations,
            "message": f"Successfully completed multi-operation sequence for {account_id}",
        }


# Create an instance and export the methods
contract = AccountOperationsContract()

# Export contract methods
get_value = contract.get_value
set_value = contract.set_value
create_subaccount = contract.create_subaccount
subaccount_created = contract.subaccount_created
add_access_key = contract.add_access_key
key_added = contract.key_added
delete_account = contract.delete_account
account_deleted = contract.account_deleted
multi_operation_sequence = contract.multi_operation_sequence
multi_sequence_completed = contract.multi_sequence_completed
