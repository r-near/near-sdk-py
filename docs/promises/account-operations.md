# Account Operations with Promises API

The NEAR Python SDK's Promises API allows you to perform various account operations including creating subaccounts, managing access keys, and transferring tokens. This guide covers these operations in detail.

## Creating Subaccounts

You can create subaccounts (e.g., `subaccount.mycontract.near`) using Promise batches:

```python
from near_sdk_py import call, callback, Context, PromiseResult, ONE_TGAS, ONE_NEAR
from near_sdk_py.promises import Promise

class AccountOperations:
    @call
    def create_subaccount(self, name: str, public_key: str, initial_balance: int = ONE_NEAR):
        """
        Create a subaccount of the current contract account.
        
        Args:
            name: Name of the subaccount (name.currentaccount.near)
            public_key: Hex-encoded public key for the new account
            initial_balance: Initial balance for the new account (in yoctoNEAR)
        """
        # Get the current account ID
        current_account = Context.current_account_id()
        
        # Form the new account ID
        new_account_id = f"{name}.{current_account}"
        
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
        """Handle completion of subaccount creation."""
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
```

## Adding Access Keys

Access keys allow external accounts to call specific functions on your contract. You can add two types of access keys:

1. **Full Access Keys**: Grant complete control over an account
2. **Function Call Keys**: Grant limited permission to call specific contract functions

### Adding a Full Access Key

```python
from near_sdk_py import call, callback, Context, PromiseResult, ONE_TGAS
from near_sdk_py.promises import Promise

class AccountOperations:
    @call
    def add_full_access_key(self, account_id: str, public_key: str):
        """
        Add a full access key to an account.
        
        Args:
            account_id: Account to add the key to
            public_key: Hex-encoded public key to add
        """
        # Decode the public key
        key_bytes = bytes.fromhex(public_key)
        
        # Create a batch for the account
        batch = Promise.create_batch(account_id)
        
        # Add the full access key
        batch.add_full_access_key(key_bytes)
        
        # Add a callback to confirm key addition
        promise = batch.then(Context.current_account_id()).function_call(
            "key_added",
            {"account_id": account_id, "is_full_access": True},
            gas=10 * ONE_TGAS,
        )
        
        return promise.value()
    
    @callback
    def key_added(self, result: PromiseResult, account_id: str, is_full_access: bool):
        """Handle completion of key addition."""
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
```

### Adding a Function Call Key

```python
from near_sdk_py import call, callback, Context, PromiseResult, ONE_TGAS
from near_sdk_py.promises import Promise
from typing import Optional, List

class AccountOperations:
    @call
    def add_function_call_key(
        self,
        account_id: str,
        public_key: str,
        allowance: Optional[int] = None,
        receiver_id: str = None,
        method_names: Optional[List[str]] = None,
    ):
        """
        Add a function call access key to an account.
        
        Args:
            account_id: Account to add the key to
            public_key: Hex-encoded public key to add
            allowance: Token allowance for function call key (None for unlimited)
            receiver_id: Receiver contract for function call key
            method_names: Allowed methods for function call key
        """
        if not receiver_id:
            return {"success": False, "error": "receiver_id is required for function call keys"}
        
        # Decode the public key
        key_bytes = bytes.fromhex(public_key)
        
        # Create a batch for the account
        batch = Promise.create_batch(account_id)
        
        # Add the function call key
        batch.add_access_key(key_bytes, allowance, receiver_id, method_names or [])
        
        # Add a callback to confirm key addition
        promise = batch.then(Context.current_account_id()).function_call(
            "key_added",
            {"account_id": account_id, "is_full_access": False},
            gas=10 * ONE_TGAS,
        )
        
        return promise.value()
```

## Deleting Access Keys

Remove access keys when they're no longer needed:

```python
from near_sdk_py import call, callback, Context, PromiseResult, ONE_TGAS
from near_sdk_py.promises import Promise

class AccountOperations:
    @call
    def delete_access_key(self, account_id: str, public_key: str):
        """
        Delete an access key from an account.
        
        Args:
            account_id: Account to remove the key from
            public_key: Hex-encoded public key to remove
        """
        # Decode the public key
        key_bytes = bytes.fromhex(public_key)
        
        # Create a batch for the account
        batch = Promise.create_batch(account_id)
        
        # Add the delete key action
        batch.delete_key(key_bytes)
        
        # Add a callback to confirm key deletion
        promise = batch.then(Context.current_account_id()).function_call(
            "key_deleted",
            {"account_id": account_id, "public_key": public_key},
            gas=10 * ONE_TGAS,
        )
        
        return promise.value()
    
    @callback
    def key_deleted(self, result: PromiseResult, account_id: str, public_key: str):
        """Handle completion of key deletion."""
        if not result.success:
            return {
                "success": False,
                "error": f"Failed to delete key: {result.status_code}",
            }
        
        return {
            "success": True,
            "account_id": account_id,
            "public_key": public_key,
            "message": f"Successfully deleted key from {account_id}",
        }
```

## Deploying Contracts

Deploy a contract to an account:

```python
from near_sdk_py import call, callback, Context, PromiseResult, ONE_TGAS
from near_sdk_py.promises import Promise

class AccountOperations:
    @call
    def deploy_contract(self, account_id: str, contract_code: bytes):
        """
        Deploy a contract to an account.
        
        Args:
            account_id: Account to deploy the contract to
            contract_code: WASM contract code
        """
        # Create a batch for the account
        batch = Promise.create_batch(account_id)
        
        # Add the deploy contract action
        batch.deploy_contract(contract_code)
        
        # Add a callback to confirm deployment
        promise = batch.then(Context.current_account_id()).function_call(
            "contract_deployed",
            {"account_id": account_id},
            gas=10 * ONE_TGAS,
        )
        
        return promise.value()
    
    @callback
    def contract_deployed(self, result: PromiseResult, account_id: str):
        """Handle completion of contract deployment."""
        if not result.success:
            return {
                "success": False,
                "error": f"Failed to deploy contract: {result.status_code}",
            }
        
        return {
            "success": True,
            "account_id": account_id,
            "message": f"Successfully deployed contract to {account_id}",
        }
```

## Deleting Accounts

Delete an account and transfer remaining funds to a beneficiary:

```python
from near_sdk_py import call, callback, Context, PromiseResult, ONE_TGAS
from near_sdk_py.promises import Promise

class AccountOperations:
    @call
    def delete_account(self, account_id: str, beneficiary_id: str):
        """
        Delete an account and transfer its funds to a beneficiary.
        
        Args:
            account_id: Account to delete
            beneficiary_id: Account to receive remaining funds
        """
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
        """Handle completion of account deletion."""
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
```

## Complex Multi-Step Account Operations

Combine multiple account operations into a sequence:

```python
from near_sdk_py import call, callback, Context, PromiseResult, ONE_TGAS, ONE_NEAR
from near_sdk_py.promises import Promise
from typing import Optional

class AccountOperations:
    @call
    def create_account_and_deploy(
        self,
        name: str,
        public_key: str,
        contract_code: Optional[bytes] = None,
    ):
        """
        Create an account and deploy a contract to it.
        
        Args:
            name: Name for the subaccount
            public_key: Hex-encoded public key for the new account
            contract_code: WASM contract code to deploy
        """
        # Get the current account ID
        current_account = Context.current_account_id()
        
        # Form the new account ID
        new_account_id = f"{name}.{current_account}"
        
        # Decode the public key
        key_bytes = bytes.fromhex(public_key)
        
        # Create a batch for account creation
        batch = Promise.create_batch(new_account_id)
        
        # Add account creation actions
        batch.create_account().transfer(5 * ONE_NEAR).add_full_access_key(key_bytes)
        
        # Chain another batch for contract deployment if code is provided
        if contract_code:
            promise = batch.then(new_account_id).function_call(
                "deploy_contract_step",
                {"account_id": new_account_id, "contract_code": contract_code},
                gas=50 * ONE_TGAS,
            )
        else:
            # Just add a callback to confirm creation
            promise = batch.then(current_account).function_call(
                "operation_completed",
                {"account_id": new_account_id, "deployed": False},
                gas=10 * ONE_TGAS,
            )
        
        return promise.value()
    
    @call
    def deploy_contract_step(self, account_id: str, contract_code: bytes):
        """
        Deploy a contract as part of a multi-step operation.
        
        Args:
            account_id: Account to deploy to
            contract_code: WASM contract code
        """
        # Create a batch for the account
        batch = Promise.create_batch(account_id)
        
        # Add the deploy contract action
        batch.deploy_contract(contract_code)
        
        # Add a callback to confirm deployment
        promise = batch.then(Context.current_account_id()).function_call(
            "operation_completed",
            {"account_id": account_id, "deployed": True},
            gas=10 * ONE_TGAS,
        )
        
        return promise.value()
    
    @callback
    def operation_completed(
        self, result: PromiseResult, account_id: str, deployed: bool
    ):
        """Handle completion of the multi-step operation."""
        if not result.success:
            return {
                "success": False,
                "error": f"Operation failed: {result.status_code}",
            }
        
        operations = ["account creation"]
        if deployed:
            operations.append("contract deployment")
        
        return {
            "success": True,
            "account_id": account_id,
            "operations_completed": operations,
            "message": f"Successfully completed operations for {account_id}",
        }
```

## Next Steps

Now that you understand account operations, you might want to explore:

- [Token and Gas Management](token-gas.md) for handling tokens and gas
- [Error Handling](error-handling.md) for robust cross-contract interactions
- [Security Considerations](security.md) for secure account operations
