# Token and Gas Management with Promises API

The NEAR Python SDK's Promises API provides several ways to manage NEAR tokens and gas allocation when making cross-contract calls. This guide covers these aspects in detail.

## Attaching Tokens to Function Calls

You can attach NEAR tokens to function calls using the `deposit` method:

```python
from near_sdk_py import call, callback, Contract, PromiseResult, ONE_NEAR

class TokenExample:
    @call
    def call_with_tokens(self, contract_id: str, method: str, amount: int = ONE_NEAR):
        """
        Call a contract method with attached tokens.
        
        Args:
            contract_id: Target contract ID
            method: Method to call on the target contract
            amount: Amount of yoctoNEAR to attach
        """
        # Create contract with the specified deposit
        contract = Contract(contract_id).deposit(amount)
        
        # Make the call with attached tokens
        promise = contract.call(method)
        
        # Add a callback to process the result
        final_promise = promise.then("process_token_call")
        
        return final_promise.value()
    
    @callback
    def process_token_call(self, result: PromiseResult):
        """Process the result of a call with attached tokens."""
        if not result.success:
            return {"success": False, "error": "Token call failed"}
        
        return {"success": True, "result": result.data, "tokens_attached": True}
```

### Receiving Attached Tokens

On the receiving end, you can access the attached tokens using `Context.attached_deposit()`:

```python
from near_sdk_py import call, Context

class TokenReceiver:
    @call
    def receive_funds(self):
        """Method that can be called when receiving funds."""
        deposit = Context.attached_deposit()
        sender = Context.predecessor_account_id()
        
        return {
            "success": True,
            "message": f"Received {deposit} yoctoNEAR from {sender}",
            "deposit": deposit,
            "sender": sender,
        }
```

## Transferring Tokens

You can transfer NEAR tokens to an account using a promise batch:

```python
from near_sdk_py import call, callback, Context, PromiseResult, ONE_TGAS
from near_sdk_py.promises import Promise

class TokenTransfer:
    @call
    def transfer_funds(self, recipient_id: str, amount: int):
        """
        Transfer NEAR tokens to a recipient.
        
        Args:
            recipient_id: Account to receive tokens
            amount: Amount of yoctoNEAR to transfer
        """
        # Create a batch for the recipient account
        batch = Promise.create_batch(recipient_id)
        
        # Add transfer action
        batch.transfer(amount)
        
        # Add callback to handle the result
        promise = batch.then(Context.current_account_id()).function_call(
            "transfer_callback",
            {"recipient_id": recipient_id, "amount": amount},
            gas=10 * ONE_TGAS,
        )
        
        return promise.value()
    
    @callback
    def transfer_callback(self, result: PromiseResult, recipient_id: str, amount: int):
        """Handle completion of a token transfer."""
        if not result.success:
            return {"success": False, "error": f"Transfer failed: {result.status_code}"}
        
        return {
            "success": True,
            "recipient_id": recipient_id,
            "amount": amount,
            "message": f"Successfully transferred {amount} yoctoNEAR",
        }
```

## Transferring Tokens and Calling a Method

You can combine token transfer with a function call in a single operation:

```python
from near_sdk_py import call, callback, Context, PromiseResult, ONE_TGAS
from near_sdk_py.promises import Promise
from typing import Optional, Dict

class TokenTransferCall:
    @call
    def transfer_and_call(
        self,
        recipient_id: str,
        amount: int,
        method: Optional[str] = None,
        args: Optional[Dict] = None,
    ):
        """
        Transfer NEAR tokens and optionally call a method on the recipient.
        
        Args:
            recipient_id: Account to receive tokens
            amount: Amount of yoctoNEAR to transfer
            method: Optional method to call after transfer
            args: Arguments for the method call
        """
        # Create a batch for operations on the recipient account
        batch = Promise.create_batch(recipient_id)
        
        # Add transfer action
        batch.transfer(amount)
        
        # Add function call if specified
        if method is not None:
            batch.function_call(method, args or {}, gas=10 * ONE_TGAS)
        
        # Add callback to handle the result
        promise = batch.then(Context.current_account_id()).function_call(
            "transfer_callback",
            {"recipient_id": recipient_id, "amount": amount},
            gas=10 * ONE_TGAS,
        )
        
        return promise.value()
```

## Setting a Fixed Gas Amount

You can set a specific gas amount for a contract call:

```python
from near_sdk_py import call, callback, Contract, PromiseResult, ONE_TGAS

class GasExample:
    @call
    def call_with_fixed_gas(
        self, contract_id: str, method: str, args: dict, gas_amount: int = 20 * ONE_TGAS
    ):
        """
        Call a contract method with a fixed gas amount.
        
        Args:
            contract_id: Target contract ID
            method: Method to call on the target contract
            args: Arguments to pass to the method
            gas_amount: Gas to attach (in gas units)
        """
        # Create contract with specified gas
        contract = Contract(contract_id, gas=gas_amount)
        
        # Make the call with fixed gas
        promise = contract.call(method, **args)
        
        # Add a callback with some gas reserved for it
        callback_gas = 5 * ONE_TGAS
        final_promise = promise.then("process_fixed_gas_call").gas(callback_gas)
        
        return final_promise.value()
    
    @callback
    def process_fixed_gas_call(self, result: PromiseResult):
        """Process the result of a call with fixed gas."""
        if not result.success:
            return {"success": False, "error": "Fixed gas call failed"}
        
        return {"success": True, "result": result.data, "fixed_gas_used": True}
```

## Proportional Gas Allocation

You can allocate gas proportionally based on available gas:

```python
from near_sdk_py import call, callback, Context, Contract, PromiseResult, ONE_TGAS

class GasExample:
    @call
    def call_with_proportional_gas(
        self, contract_id: str, method: str, args: dict, gas_fraction: int = 2
    ):
        """
        Call a contract method with proportional gas allocation.
        
        Args:
            contract_id: Target contract ID
            method: Method to call on the target contract
            args: Arguments to pass to the method
            gas_fraction: Denominator for gas fraction (e.g., 2 means 1/2 of available gas)
        """
        # Calculate available gas
        available_gas = Context.prepaid_gas() - Context.used_gas() - 5 * ONE_TGAS
        
        # Calculate proportional gas amount
        if gas_fraction <= 0:
            gas_fraction = 1  # Default to all available gas
        
        gas_to_use = available_gas // gas_fraction
        
        # Create contract with calculated gas
        contract = Contract(contract_id, gas=gas_to_use)
        
        # Make the call
        promise = contract.call(method, **args)
        
        # Add a callback with remaining gas
        remaining_gas = available_gas - gas_to_use
        final_promise = promise.then("process_proportional_call").gas(remaining_gas)
        
        return final_promise.value()
    
    @callback
    def process_proportional_call(self, result: PromiseResult):
        """Process the result of a call with proportional gas."""
        if not result.success:
            return {"success": False, "error": "Proportional gas call failed"}
        
        return {"success": True, "result": result.data, "proportional_gas_used": True}
```

## Gas for Callbacks

Always make sure to reserve enough gas for your callbacks. If your callback runs out of gas, it won't be able to process the results correctly:

```python
from near_sdk_py import call, callback, Contract, PromiseResult, ONE_TGAS

class GasExample:
    @call
    def call_with_callback_gas(self, contract_id: str, method: str):
        # Calculate gas distribution
        total_gas = Context.prepaid_gas() - Context.used_gas() - ONE_TGAS
        
        # Allocate 2/3 to the external call and 1/3 to the callback
        external_gas = (total_gas * 2) // 3
        callback_gas = total_gas - external_gas
        
        # Create contract with external gas
        contract = Contract(contract_id, gas=external_gas)
        
        # Make the call
        promise = contract.call(method)
        
        # Add a callback with explicit gas
        final_promise = promise.then("process_result").gas(callback_gas)
        
        return final_promise.value()
    
    @callback
    def process_result(self, result: PromiseResult):
        # Complex processing that requires sufficient gas
        # ...
        
        return {"success": result.success, "data": result.data}
```

## Handling Token Refunds

When your contract sends tokens in a cross-contract call and the call fails, the tokens are returned to your contract, not to the original caller. You need to handle refunds explicitly:

```python
from near_sdk_py import call, callback, Context, Contract, PromiseResult, Storage, ONE_TGAS

class TokenRefund:
    @call
    def purchase_item(self, marketplace_id: str, item_id: str):
        # Store the caller and deposit for potential refund
        caller = Context.predecessor_account_id()
        deposit = Context.attached_deposit()
        
        # Store information for the callback
        Storage.set("purchase_caller", caller)
        Storage.set("purchase_deposit", str(deposit))
        
        # Create contract with deposit
        marketplace = Contract(marketplace_id).deposit(deposit)
        
        # Make the purchase call
        promise = marketplace.call("buy_item", id=item_id)
        
        # Add a callback to handle the result
        final_promise = promise.then("handle_purchase_result")
        
        return final_promise.value()
    
    @callback
    def handle_purchase_result(self, result: PromiseResult):
        # Get stored information
        caller = Storage.get_string("purchase_caller")
        deposit = int(Storage.get_string("purchase_deposit"))
        
        # Clear storage
        Storage.remove("purchase_caller")
        Storage.remove("purchase_deposit")
        
        # If the purchase failed, refund the caller
        if not result.success:
            # Create a batch for refund
            batch = Promise.create_batch(caller)
            batch.transfer(deposit)
            
            # Return failure with refund information
            return {
                "success": False,
                "error": "Purchase failed",
                "refunded": True,
                "amount": deposit
            }
        
        # Purchase succeeded
        return {"success": True, "message": "Purchase successful"}
```

## Best Practices for Token and Gas Management

1. **Reserve Gas for Callbacks**: Always ensure your callbacks have enough gas to execute.

2. **Handle Token Refunds**: Implement refund logic when cross-contract calls involving tokens fail.

3. **Balance Gas Distribution**: Distribute gas properly between the main call and callback.

4. **Store Context Information**: Store information about deposits and callers for use in callbacks.

5. **Use Proportional Gas Allocation**: For complex operations, calculate gas proportionally based on available gas.

6. **One Yocto for Security**: For sensitive operations, require a 1 yoctoNEAR deposit to ensure the call was signed by the user:

```python
from near_sdk_py import call, BaseContract

class SecureOperations:
    @call
    def sensitive_operation(self):
        # Require exactly 1 yoctoNEAR to ensure the user signed the transaction
        BaseContract.assert_one_yocto()
        
        # Perform sensitive operation
        # ...
        
        return {"success": True}
```

## Next Steps

Now that you understand token and gas management, you might want to explore:

- [Error Handling](error-handling.md) for robust cross-contract interactions
- [Security Considerations](security.md) for secure token operations
- [Advanced Promise Patterns](advanced-patterns.md) for complex workflows
