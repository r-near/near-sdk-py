# Error Handling in Promises API

Proper error handling is crucial when working with cross-contract calls in NEAR. Because of NEAR's asynchronous execution model, errors need special handling. This guide covers error handling patterns for the NEAR Python SDK's Promises API.

## Understanding Promise Failures

When a promise fails, it can be due to several reasons:

1. The target contract doesn't exist
2. The method doesn't exist on the target contract
3. The method executed but panicked
4. Insufficient gas was provided
5. Deserialization errors with arguments

The `PromiseResult` object provides information about success or failure:

```python
@callback
def handle_result(self, result: PromiseResult):
    # The status_code will be 1 for success, other values for failure
    if result.status_code != 1:
        # This promise failed
        return {"success": False, "error": f"Failed with status code: {result.status_code}"}
    
    # Success case
    return {"success": True, "data": result.data}
```

## Basic Error Handling Pattern

Here's a basic pattern for handling errors in cross-contract calls:

```python
from near_sdk_py import call, callback, Contract, PromiseResult

class ErrorHandling:
    @call
    def call_with_error_handling(self, contract_id: str):
        contract = Contract(contract_id)
        
        # Make the call (which might fail)
        promise = contract.call("potentially_failing_method")
        
        # Add a callback to handle success or failure
        promise = promise.then("handle_result")
        
        return promise.value()
    
    @callback
    def handle_result(self, result: PromiseResult):
        if not result.success:
            # Handle the error case
            status_message = f"Call failed with status code: {result.status_code}"
            
            # Perform any necessary recovery or fallback logic
            return {
                "success": False,
                "error": status_message,
                "handled": True
            }
        
        # Handle the success case
        return {
            "success": True,
            "data": result.data
        }
```

## Using PromiseResult Properties

The `PromiseResult` object provides several helpful properties:

```python
@callback
def process_result(self, result: PromiseResult):
    # .success is a boolean (true if status_code == 1)
    if not result.success:
        # Handle failure
        pass
    
    # .status_code gives the numerical status
    # 1 = Success
    # 2 = Failure
    # 0 = NotReady (should not happen in callbacks)
    status_code = result.status_code
    
    # .data contains the returned data (if successful)
    data = result.data
```

## Fallback Strategy Pattern

When one contract might fail, you can implement a fallback strategy:

```python
from near_sdk_py import call, callback, Contract, PromiseResult

class FallbackStrategy:
    @call
    def call_with_fallback(
        self, primary_contract_id: str, fallback_contract_id: str, key: str
    ):
        """Try to call a primary contract, but fall back to another if it fails."""
        # Try the primary contract first
        contract = Contract(primary_contract_id)
        promise = contract.call("get_value", key=key)
        
        # Add callback that will check the result and potentially use the fallback
        final_promise = promise.then(
            "process_with_fallback", fallback_contract_id=fallback_contract_id, key=key
        )
        
        return final_promise.value()
    
    @callback
    def process_with_fallback(
        self, result: PromiseResult, fallback_contract_id: str, key: str
    ):
        # If primary call succeeded, just return the result
        if result.success:
            return {"success": True, "value": result.data, "source": "primary"}
        
        # Primary call failed, try the fallback
        fallback_contract = Contract(fallback_contract_id)
        fallback_promise = fallback_contract.call("get_value", key=key)
        
        # Add another callback to process the fallback result
        final_promise = fallback_promise.then("process_fallback_result")
        
        return final_promise.value()
    
    @callback
    def process_fallback_result(self, result: PromiseResult):
        if result.success:
            return {"success": True, "value": result.data, "source": "fallback"}
        else:
            # Both primary and fallback failed
            return {
                "success": False,
                "error": "Both primary and fallback calls failed"
            }
        }
```

## Conditional Processing Based on Results

Sometimes you want to only process results that meet certain criteria:

```python
from near_sdk_py import call, callback, Contract, PromiseResult

class ConditionalProcessing:
    @call
    def conditional_callback(self, contract_id: str, key: str, min_length: int):
        """Call another contract but only process result if value meets criteria."""
        contract = Contract(contract_id)
        promise = contract.call("get_value", key=key)
        
        # Chain a callback that will check the criteria
        final_promise = promise.then("check_result_criteria", min_length=min_length)
        
        return final_promise.value()
    
    @callback
    def check_result_criteria(self, result: PromiseResult, min_length: int):
        """Check if result meets criteria and process accordingly."""
        if not result.success:
            return {"success": False, "error": "Failed to retrieve value"}
        
        value = result.data
        # Strip quotes if the value is a JSON string
        if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
            value = value.strip('"')
        
        # Check if value meets criteria
        if len(value) >= min_length:
            # Process the value
            return {
                "success": True,
                "value": value,
                "meets_criteria": True,
                "length": len(value),
            }
        else:
            # Value doesn't meet criteria
            return {
                "success": True,
                "meets_criteria": False,
                "error": f"Value length {len(value)} is less than required {min_length}",
            }
```

## Handling Multiple Promise Results

When working with multiple promises joined together, you need to handle potential failures in any of them:

```python
from near_sdk_py import call, multi_callback, Contract
from near_sdk_py.promises import Promise, PromiseResult
from typing import List

class MultiPromiseErrorHandling:
    @call
    def join_multiple_calls(self, contract_ids: List[str], key: str):
        """Join calls to multiple contracts and handle errors from any of them."""
        if not contract_ids:
            return {"success": False, "error": "No contract IDs provided"}
        
        # Create first promise
        contract1 = Contract(contract_ids[0])
        promise1 = contract1.call("get_value", key=key)
        
        # Create rest of the promises
        other_promises = []
        for contract_id in contract_ids[1:]:
            contract = Contract(contract_id)
            promise = contract.call("get_value", key=key)
            other_promises.append(promise)
        
        # Join all promises and add a callback
        combined_promise = promise1.join(
            other_promises,
            "process_multiple_results",
            contract_ids=contract_ids
        )
        
        return combined_promise.value()
    
    @multi_callback
    def process_multiple_results(
        self, results: List[PromiseResult], contract_ids: List[str]
    ):
        """Process results from multiple contracts with error handling."""
        successful_results = []
        failures = []
        
        # Process each result and track successes and failures
        for i, result in enumerate(results):
            contract_id = contract_ids[i] if i < len(contract_ids) else f"Unknown-{i}"
            
            if result.success:
                successful_results.append({
                    "contract_id": contract_id,
                    "value": result.data
                })
            else:
                failures.append({
                    "contract_id": contract_id,
                    "status_code": result.status_code
                })
        
        # Return structured response with both successes and failures
        return {
            "success": len(successful_results) > 0,  # Consider successful if at least one worked
            "successful_results": successful_results,
            "failures": failures,
            "total_called": len(results),
            "successful_count": len(successful_results),
            "failure_count": len(failures)
        }
```

## Manual State Rollback

NEAR doesn't automatically roll back state changes if a cross-contract call fails. You need to handle this manually:

```python
from near_sdk_py import call, callback, Context, Contract, PromiseResult, Storage

class StateRollback:
    @call
    def update_with_verification(self, contract_id: str, key: str, new_value: str):
        """Update a value locally but verify with another contract first."""
        # Store the current value so we can rollback if needed
        current_value = Storage.get_string(key)
        Storage.set("pending_update_key", key)
        Storage.set("pending_update_old_value", current_value or "")
        Storage.set("pending_update_new_value", new_value)
        
        # Update the value optimistically
        Storage.set(key, new_value)
        
        # Make a call to verify the update is valid
        verifier = Contract(contract_id)
        promise = verifier.call("verify_update", key=key, value=new_value)
        
        # Add a callback to confirm or rollback
        final_promise = promise.then("handle_verification")
        
        return final_promise.value()
    
    @callback
    def handle_verification(self, result: PromiseResult):
        # Get the pending update data
        key = Storage.get_string("pending_update_key")
        old_value = Storage.get_string("pending_update_old_value")
        new_value = Storage.get_string("pending_update_new_value")
        
        # Clean up temporary storage regardless of outcome
        Storage.remove("pending_update_key")
        Storage.remove("pending_update_old_value")
        Storage.remove("pending_update_new_value")
        
        # If verification failed, roll back the change
        if not result.success or result.data == "false":
            # Roll back to the previous value
            if old_value:
                Storage.set(key, old_value)
            else:
                Storage.remove(key)
            
            return {
                "success": False,
                "error": "Verification failed",
                "rolled_back": True
            }
        
        # Verification succeeded
        return {
            "success": True,
            "key": key,
            "new_value": new_value
        }
```

## Handling Token Refunds on Failure

When a cross-contract call that attaches tokens fails, the tokens are returned to your contract (not the original caller). You need to handle refunds:

```python
from near_sdk_py import call, callback, Context, Contract, PromiseResult, Storage
from near_sdk_py.promises import Promise

class TokenRefund:
    @call
    def purchase_with_refund(self, contract_id: str, item_id: str):
        """Purchase an item with automatic refund on failure."""
        # Record the caller and deposit
        caller = Context.predecessor_account_id()
        deposit = Context.attached_deposit()
        
        Storage.set("purchase_caller", caller)
        Storage.set("purchase_deposit", str(deposit))
        Storage.set("purchase_item", item_id)
        
        # Make the purchase call
        shop = Contract(contract_id).deposit(deposit)
        promise = shop.call("buy_item", id=item_id)
        
        # Add a callback to handle the result
        final_promise = promise.then("handle_purchase_result")
        
        return final_promise.value()
    
    @callback
    def handle_purchase_result(self, result: PromiseResult):
        # Get the stored information
        caller = Storage.get_string("purchase_caller")
        deposit_str = Storage.get_string("purchase_deposit")
        item_id = Storage.get_string("purchase_item")
        deposit = int(deposit_str) if deposit_str else 0
        
        # Clean up storage
        Storage.remove("purchase_caller")
        Storage.remove("purchase_deposit")
        Storage.remove("purchase_item")
        
        # If the purchase failed, refund the caller
        if not result.success:
            # Create a transfer batch
            batch = Promise.create_batch(caller)
            batch.transfer(deposit)
            
            return {
                "success": False,
                "error": "Purchase failed",
                "refunded": True,
                "amount": deposit
            }
        
        # Purchase succeeded
        return {
            "success": True,
            "item_id": item_id,
            "message": "Purchase successful"
        }
```

## Best Practices for Error Handling

1. **Always Check Result Status**: Never assume a promise succeeded.

2. **Plan for Failures**: Consider what should happen when a call fails and implement appropriate recovery.

3. **Store State for Rollback**: Store enough information to roll back changes if necessary.

4. **Handle Token Refunds**: Implement refund logic when cross-contract calls involving tokens fail.

5. **Use Fallback Strategies**: When critical operations are involved, have fallback options.

6. **Provide Detailed Error Information**: Return structured error information to help diagnose issues.

7. **Log Important Errors**: Use `Log.error()` to record significant failures for later analysis.

## Next Steps

Now that you understand error handling, you might want to explore:

- [Security Considerations](security.md) for secure cross-contract interactions
- [Advanced Promise Patterns](advanced-patterns.md) for complex workflows
- [Token and Gas Management](token-gas.md) for handling tokens correctly
