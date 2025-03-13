# Working with Callbacks in the Promises API

Callbacks are an essential part of cross-contract calls in NEAR. Because cross-contract calls are asynchronous and independent, you need a callback function to process the results that come back from other contracts.

## The Callback Decorator

The NEAR Python SDK provides the `@callback` decorator to simplify working with callbacks:

```python
from near_sdk_py import call, callback, Contract, PromiseResult

class MyContract:
    @call
    def get_data(self, contract_id: str, data_id: str):
        contract = Contract(contract_id)
        
        # Make the call to the other contract
        promise = contract.call("retrieve_data", id=data_id)
        
        # Add a callback to process the result
        promise = promise.then("on_data_retrieved", original_id=data_id)
        
        return promise.value()
    
    @callback
    def on_data_retrieved(self, result: PromiseResult, original_id: str):
        """Process the data retrieved from the other contract."""
        if not result.success:
            return {
                "success": False,
                "error": f"Failed to retrieve data for ID: {original_id}"
            }
        
        # Process the successful result
        data = result.data
        
        # You can perform additional processing on the data here
        processed_data = self._process_data(data)
        
        return {
            "success": True,
            "id": original_id,
            "data": processed_data
        }
    
    def _process_data(self, data):
        # Internal method to process the data
        return data
```

The `@callback` decorator:

1. Accesses the promise result automatically
2. Parses JSON data if possible
3. Passes the result as a `PromiseResult` object
4. Handles serialization of the return value

## Passing Data to Callbacks

You can pass additional data to your callback function using keyword arguments:

```python
from near_sdk_py import call, callback, Contract, PromiseResult

class MyContract:
    @call
    def get_user_profile(self, user_id: str, fields: list):
        profiles_contract = Contract("profiles.near")
        
        # Make the call to the other contract
        promise = profiles_contract.call("get_profile", user_id=user_id)
        
        # Pass additional data to the callback
        promise = promise.then(
            "process_profile",
            user_id=user_id,
            requested_fields=fields,
            timestamp=Context.block_timestamp()
        )
        
        return promise.value()
    
    @callback
    def process_profile(
        self, 
        result: PromiseResult, 
        user_id: str, 
        requested_fields: list,
        timestamp: int
    ):
        """Process the profile with the additional context."""
        if not result.success:
            return {"success": False, "error": "Failed to retrieve profile"}
        
        # Get the full profile
        full_profile = result.data
        
        # Filter to just the requested fields
        filtered_profile = {
            field: full_profile.get(field) 
            for field in requested_fields 
            if field in full_profile
        }
        
        return {
            "success": True,
            "user_id": user_id,
            "profile": filtered_profile,
            "retrieved_at": timestamp
        }
```

The additional keyword arguments you provide to `.then()` will be passed to your callback function.

## The Multi-Callback Decorator

When working with multiple promises joined together, use the `@multi_callback` decorator to process all the results:

```python
from near_sdk_py import call, multi_callback, Contract, PromiseResult
from typing import List

class MyContract:
    @call
    def get_data_from_multiple_sources(self, contract_ids: List[str], data_id: str):
        # Create first promise
        contract1 = Contract(contract_ids[0])
        promise1 = contract1.call("get_data", id=data_id)
        
        # Create second promise
        contract2 = Contract(contract_ids[1])
        promise2 = contract2.call("get_data", id=data_id)
        
        # Join the promises and add a callback
        combined_promise = promise1.join(
            [promise2],
            "process_multiple_results",
            data_id=data_id
        )
        
        return combined_promise.value()
    
    @multi_callback
    def process_multiple_results(self, results: List[PromiseResult], data_id: str):
        """Process results from multiple contracts."""
        # Check if all promises succeeded
        if not all(result.success for result in results):
            return {
                "success": False,
                "error": "One or more data sources failed to respond"
            }
        
        # Combine the data from both sources
        combined_data = {}
        
        for i, result in enumerate(results):
            source_data = result.data
            combined_data[f"source_{i+1}"] = source_data
        
        return {
            "success": True,
            "data_id": data_id,
            "combined_data": combined_data
        }
```

The `@multi_callback` decorator:

1. Collects all promise results
2. Parses JSON data for each result if possible
3. Passes them as a list of `PromiseResult` objects
4. Handles serialization of the return value

## Security Considerations for Callbacks

Callbacks need special security considerations:

1. **Always mark callbacks with the decorator**: The `@callback` decorator ensures the function can only be called as a callback, not directly by users.

2. **Validate input data**: Even though callbacks are internal, validate the data coming from other contracts.

3. **Handle failures gracefully**: Always check if the promise succeeded before processing the result.

4. **Manage state carefully**: Remember that there's a delay between the initial call and the callback, during which other transactions may execute.

```python
from near_sdk_py import call, callback, Storage, Context, PromiseResult

class SecureCallback:
    @call
    def secure_operation(self, contract_id: str, data_id: str):
        # Record the operation in progress
        Storage.set("pending_operation", data_id)
        Storage.set("operation_caller", Context.predecessor_account_id())
        
        # Make the external call
        contract = Contract(contract_id)
        promise = contract.call("get_data", id=data_id)
        
        # Add callback
        promise = promise.then("on_operation_complete", data_id=data_id)
        
        return promise.value()
    
    @callback
    def on_operation_complete(self, result: PromiseResult, data_id: str):
        # Check that this matches our pending operation
        pending_id = Storage.get_string("pending_operation")
        
        if pending_id != data_id:
            return {"success": False, "error": "Operation mismatch"}
        
        # Get the original caller
        caller = Storage.get_string("operation_caller")
        
        # Clear the pending operation state
        Storage.remove("pending_operation")
        Storage.remove("operation_caller")
        
        # Process the result
        if not result.success:
            return {"success": False, "error": "Operation failed"}
        
        # Return the result with the caller information
        return {
            "success": True,
            "data": result.data,
            "caller": caller
        }
```

## Next Steps

Now that you understand callbacks, you might want to explore:

- [Advanced Promise Patterns](advanced-patterns.md) for more complex interactions
- [Error Handling](error-handling.md) for robust callback implementations
- [Security Considerations](security.md) for secure cross-contract communication
