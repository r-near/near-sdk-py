# Security Considerations for Promises API

Cross-contract calls in NEAR present unique security challenges due to their asynchronous nature. This guide covers important security considerations when using the NEAR Python SDK's Promises API.

## The Asynchronous Gap Vulnerability

In NEAR, there's a delay between making a cross-contract call and receiving the callback. During this gap, other transactions can execute on your contract.

### Example Vulnerability

Consider this vulnerable implementation of a token transfer:

```python
from near_sdk_py import call, callback, Context, Contract, PromiseResult, Storage

class VulnerableContract:
    @call
    def transfer(self, token_id: str, recipient_id: str):
        # Check if the caller owns the token
        owner = Storage.get_string(f"owner:{token_id}")
        caller = Context.predecessor_account_id()
        
        if owner != caller:
            return {"success": False, "error": "Not the owner"}
        
        # Call the recipient's notification method
        recipient = Contract(recipient_id)
        promise = recipient.call("on_transfer", token_id=token_id, sender_id=caller)
        
        # VULNERABILITY: Owner is changed before callback confirmation
        Storage.set(f"owner:{token_id}", recipient_id)
        
        # Add callback to confirm receipt
        promise = promise.then("confirm_transfer")
        
        return promise.value()
    
    @callback
    def confirm_transfer(self, result: PromiseResult):
        # What if this fails? The token ownership is already changed!
        if not result.success:
            return {"success": False, "error": "Transfer notification failed"}
        
        return {"success": True}
```

In this vulnerable example, the token ownership is changed **before** confirming the recipient's notification was successful. If the notification fails, the token ownership has already been transferred.

### Secure Implementation

Here's a more secure implementation:

```python
from near_sdk_py import call, callback, Context, Contract, PromiseResult, Storage

class SecureContract:
    @call
    def transfer(self, token_id: str, recipient_id: str):
        # Check if the caller owns the token
        owner = Storage.get_string(f"owner:{token_id}")
        caller = Context.predecessor_account_id()
        
        if owner != caller:
            return {"success": False, "error": "Not the owner"}
        
        # Store pending transfer information
        Storage.set("pending_transfer:token", token_id)
        Storage.set("pending_transfer:from", caller)
        Storage.set("pending_transfer:to", recipient_id)
        
        # Call the recipient's notification method
        recipient = Contract(recipient_id)
        promise = recipient.call("on_transfer", token_id=token_id, sender_id=caller)
        
        # Add callback to confirm receipt and THEN change ownership
        promise = promise.then("complete_transfer")
        
        return promise.value()
    
    @callback
    def complete_transfer(self, result: PromiseResult):
        # Get the pending transfer information
        token_id = Storage.get_string("pending_transfer:token")
        from_id = Storage.get_string("pending_transfer:from")
        to_id = Storage.get_string("pending_transfer:to")
        
        # Clean up pending transfer data
        Storage.remove("pending_transfer:token")
        Storage.remove("pending_transfer:from")
        Storage.remove("pending_transfer:to")
        
        # Only change ownership if notification was successful
        if not result.success:
            return {
                "success": False,
                "error": "Transfer notification failed",
                "token_id": token_id,
                "ownership_unchanged": True
            }
        
        # Now it's safe to change ownership
        Storage.set(f"owner:{token_id}", to_id)
        
        return {
            "success": True,
            "token_id": token_id,
            "from": from_id,
            "to": to_id
        }
```

In this secure implementation, the ownership change only happens in the callback **after** confirming the notification was successful.

## Protecting Callbacks from Direct Calls

Callback functions should only be callable as callbacks, not directly by users. Always use the `@callback` decorator:

```python
from near_sdk_py import call, callback, Context, PromiseResult

class SecureCallbacks:
    @call
    def start_operation(self):
        # Start the operation
        # ...
        
        # Make cross-contract call
        promise = some_contract.call("some_method")
        
        # Add callback
        promise = promise.then("operation_callback")
        
        return promise.value()
    
    @callback  # This ensures the function can only be called as a callback
    def operation_callback(self, result: PromiseResult):
        # Process the result
        # ...
        
        return {"success": result.success}
```

The `@callback` decorator ensures the function can only be called as part of a cross-contract callback, not directly by external users.

## Manual State Rollback

NEAR doesn't automatically roll back state changes if a cross-contract call fails. Always implement manual rollback in your callbacks:

```python
from near_sdk_py import call, callback, Context, Contract, PromiseResult, Storage

class StateManagement:
    @call
    def execute_with_rollback(self, contract_id: str, item_id: str):
        # Store original state for potential rollback
        original_state = Storage.get_string(f"item:{item_id}:state")
        Storage.set("pending_item", item_id)
        Storage.set("pending_original_state", original_state or "")
        
        # Update state (optimistically)
        Storage.set(f"item:{item_id}:state", "processing")
        
        # Make cross-contract call
        contract = Contract(contract_id)
        promise = contract.call("process_item", id=item_id)
        
        # Add callback with rollback capability
        promise = promise.then("finalize_or_rollback")
        
        return promise.value()
    
    @callback
    def finalize_or_rollback(self, result: PromiseResult):
        # Get stored data
        item_id = Storage.get_string("pending_item")
        original_state = Storage.get_string("pending_original_state")
        
        # Clean up pending data
        Storage.remove("pending_item")
        Storage.remove("pending_original_state")
        
        if not result.success:
            # Roll back to original state
            if original_state:
                Storage.set(f"item:{item_id}:state", original_state)
            else:
                Storage.remove(f"item:{item_id}:state")
            
            return {
                "success": False,
                "error": "Processing failed",
                "rolled_back": True
            }
        
        # Update to completed state
        Storage.set(f"item:{item_id}:state", "completed")
        
        return {"success": True, "item_id": item_id}
```

## Handling Token Refunds

When your contract sends tokens in a cross-contract call and the call fails, the tokens are returned to your contract, not to the original caller:

```python
from near_sdk_py import call, callback, Context, Contract, PromiseResult, Storage
from near_sdk_py.promises import Promise

class TokenRefund:
    @call
    def purchase_with_deposit(self, market_id: str, item_id: str):
        # Store deposit and caller info
        deposit = Context.attached_deposit()
        caller = Context.predecessor_account_id()
        
        Storage.set("purchase_caller", caller)
        Storage.set("purchase_deposit", str(deposit))
        
        # Call marketplace with attached deposit
        market = Contract(market_id).deposit(deposit)
        promise = market.call("buy", id=item_id)
        
        # Add callback to handle result
        promise = promise.then("handle_purchase")
        
        return promise.value()
    
    @callback
    def handle_purchase(self, result: PromiseResult):
        # Get stored information
        caller = Storage.get_string("purchase_caller")
        deposit_str = Storage.get_string("purchase_deposit")
        deposit = int(deposit_str) if deposit_str else 0
        
        # Clean up storage
        Storage.remove("purchase_caller")
        Storage.remove("purchase_deposit")
        
        if not result.success:
            # Purchase failed, refund the caller
            if deposit > 0:
                batch = Promise.create_batch(caller)
                batch.transfer(deposit)
            
            return {
                "success": False,
                "error": "Purchase failed",
                "refunded": deposit > 0,
                "amount": deposit
            }
        
        # Purchase succeeded
        return {"success": True, "message": "Purchase completed"}
```

## Reentrant Call Protection

Reentrant attacks occur when a contract calls another contract, which then calls back into the original contract before the first operation completes. Protect against this:

```python
from near_sdk_py import call, callback, Context, Contract, PromiseResult, Storage

class ReentrantProtection:
    @call
    def secure_transfer(self, token_id: str, recipient_id: str):
        # Check if a transfer is already in progress
        if Storage.has("transfer_in_progress"):
            return {"success": False, "error": "Another transfer is already in progress"}
        
        # Check ownership
        owner = Storage.get_string(f"owner:{token_id}")
        caller = Context.predecessor_account_id()
        
        if owner != caller:
            return {"success": False, "error": "Not the owner"}
        
        # Set transfer in progress flag
        Storage.set("transfer_in_progress", "true")
        
        # Store pending transfer information
        Storage.set("pending_transfer:token", token_id)
        Storage.set("pending_transfer:from", caller)
        Storage.set("pending_transfer:to", recipient_id)
        
        # Call the recipient
        recipient = Contract(recipient_id)
        promise = recipient.call("on_transfer", token_id=token_id, sender_id=caller)
        
        # Add callback
        promise = promise.then("complete_transfer")
        
        return promise.value()
    
    @callback
    def complete_transfer(self, result: PromiseResult):
        # Always clear the transfer in progress flag at the end
        defer_flag_cleanup = False
        
        try:
            # Get the pending transfer information
            token_id = Storage.get_string("pending_transfer:token")
            from_id = Storage.get_string("pending_transfer:from")
            to_id = Storage.get_string("pending_transfer:to")
            
            # Process transfer result
            if not result.success:
                return {
                    "success": False,
                    "error": "Transfer notification failed"
                }
            
            # Complete the transfer
            Storage.set(f"owner:{token_id}", to_id)
            
            return {
                "success": True,
                "token_id": token_id,
                "from": from_id,
                "to": to_id
            }
        except Exception as e:
            # If an error occurs, prevent cleanup so we remain in a locked state
            # (this is a safety mechanism; in practice, add better error recovery)
            defer_flag_cleanup = True
            raise e
        finally:
            # Clean up pending transfer data
            Storage.remove("pending_transfer:token")
            Storage.remove("pending_transfer:from")
            Storage.remove("pending_transfer:to")
            
            # Clear the in-progress flag if no error occurred
            if not defer_flag_cleanup:
                Storage.remove("transfer_in_progress")
```

## One Yocto Pattern for Security

For sensitive operations, require a 1 yoctoNEAR deposit to ensure the transaction was actually signed by the user:

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

## Validating Contract IDs

Always validate contract IDs before making cross-contract calls:

```python
from near_sdk_py import call, Contract

class SecureContracts:
    @call
    def call_validated_contract(self, contract_id: str, method: str):
        # Basic validation
        if not contract_id or "." not in contract_id:
            return {"success": False, "error": "Invalid contract ID"}
        
        # Whitelist validation (for critical operations)
        allowed_contracts = ["trusted1.near", "trusted2.near"]
        if method in ["critical_method1", "critical_method2"]:
            if contract_id not in allowed_contracts:
                return {"success": False, "error": "Contract not authorized for this operation"}
        
        # Make the call
        contract = Contract(contract_id)
        promise = contract.call(method)
        
        # Handle result
        # ...
```

## Avoiding Common Vulnerabilities

### 1. Race Conditions

```python
# VULNERABLE - Race condition in counter increment
@call
def increment_counter(self, counter_id: str):
    current = int(Storage.get_string(counter_id) or "0")
    Storage.set(counter_id, str(current + 1))
    return current + 1

# SECURE - Using pending operation pattern
@call
def increment_counter_secure(self, counter_id: str):
    # Check if already pending
    pending_key = f"pending_increment:{counter_id}"
    if Storage.has(pending_key):
        return {"success": False, "error": "Operation already in progress"}
    
    # Mark as pending and store current value
    current = int(Storage.get_string(counter_id) or "0")
    Storage.set(pending_key, str(current))
    
    # We could make a cross-contract call here if needed
    # ...
    
    # Update the counter
    Storage.set(counter_id, str(current + 1))
    
    # Clear pending flag
    Storage.remove(pending_key)
    
    return {"success": True, "new_value": current + 1}
```

### 2. Confused Deputy

```python
# VULNERABLE - No validation of caller
@callback
def complete_operation(self, result: PromiseResult):
    operation_id = Storage.get_string("pending_operation")
    # Complete the operation without checking who started it
    
# SECURE - Tracking the original caller
@call
def start_operation(self, operation_id: str):
    caller = Context.predecessor_account_id()
    
    # Store who initiated this operation
    Storage.set(f"operation:{operation_id}:initiator", caller)
    
    # Make cross-contract call
    # ...

@callback
def complete_operation_secure(self, result: PromiseResult):
    operation_id = Storage.get_string("pending_operation")
    initiator = Storage.get_string(f"operation:{operation_id}:initiator")
    
    # Now we know who started this operation and can apply appropriate permissions
    # ...
```

## Security Checklist for Cross-Contract Calls

1. ✅ **Use the `@callback` decorator** for all callback functions
2. ✅ **Store state changes in callbacks**, not before receiving results
3. ✅ **Implement manual rollback** in callbacks if operations fail
4. ✅ **Handle token refunds** when operations involving deposits fail
5. ✅ **Use locks or flags** to prevent reentrant attacks
6. ✅ **Store caller information** for pending operations
7. ✅ **Validate contract IDs** before making calls
8. ✅ **Use the One Yocto pattern** for sensitive operations
9. ✅ **Clean up state** after operations complete (or fail)
10. ✅ **Use proper error handling** in all callbacks

## Next Steps

Now that you understand security considerations, you might want to explore:

- [API Reference](api-reference.md) for complete Promise API documentation
- [Advanced Promise Patterns](advanced-patterns.md) for complex secure workflows
- [Error Handling](error-handling.md) for robust cross-contract interactions
