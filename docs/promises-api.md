# Promises API for Cross-Contract Calls

NEAR's smart contracts can interact with each other through asynchronous cross-contract calls. The NEAR Python SDK provides an enhanced Promises API to make working with these asynchronous workflows easier and more reliable.

## Table of Contents

- [Overview](#overview)
- [Basic Cross-Contract Calls](#basic-cross-contract-calls)
- [Using Callbacks](#using-callbacks)
- [The `@callback` Decorator](#the-callback-decorator)
- [Promise Chaining](#promise-chaining)
- [Error Handling](#error-handling)
- [Advanced Usage](#advanced-usage)
- [Best Practices](#best-practices)

## Overview

In NEAR, when one contract calls another, the call returns a *Promise*. Promises are NEAR's way of handling asynchronous operations between contracts. The NEAR Python SDK provides a clean API for working with these promises through the `CrossContract` class and the `@callback` decorator.

## Basic Cross-Contract Calls

Making a simple cross-contract call:

```python
from near_sdk_py import call, ONE_TGAS, CrossContract

@call
def get_token_info(self, token_account_id: str) -> int:
    """Call another contract and return the promise directly"""
    promise = CrossContract.call(
        account_id=token_account_id,      # Contract to call 
        method_name="ft_metadata",        # Method to call
        args={},                          # Arguments (empty in this case)
        amount=0,                         # Attached deposit in yoctoNEAR
        gas=5 * ONE_TGAS                  # Gas to attach
    )
    
    # The return value of the called contract will be returned to the caller
    return CrossContract.return_value(promise)
```

## Using Callbacks

Often, you'll want to process the result of a cross-contract call before returning it to the user. This is where callbacks come in:

```python
from near_sdk_py import call, callback, ONE_TGAS, CrossContract, Log

class TokenAggregator:
    @call
    def get_token_price_in_usd(self, token_account_id: str) -> int:
        """Get token price and convert it to USD"""
        
        # Using the simplified call_with_callback method
        promise = CrossContract.call_with_callback(
            account_id=token_account_id,   # Contract to call
            method_name="get_price",       # Method to call
            args={},                       # Arguments
            gas=5 * ONE_TGAS,              # Gas for the call
            callback_method="on_price_received"  # Our callback method
        )
        
        # This will execute the callback and return its result
        return CrossContract.return_value(promise)
    
    @callback
    def on_price_received(self, promise_result: dict) -> float:
        """Process the token price result"""
        if promise_result["status"] != "Successful":
            # Handle the error case
            Log.error(f"Failed to get token price: {promise_result['status']}")
            return 0.0
            
        # Parse the result (assuming it's a JSON string)
        import json
        price_data = json.loads(promise_result["data"].decode("utf-8"))
        
        # Convert to USD using our exchange rate
        usd_price = price_data["price"] * 1.25  # Example conversion
        
        return usd_price
```

## The `@callback` Decorator

The `@callback` decorator is specifically designed for handling promise results. When you use this decorator:

1. Your method will automatically receive a `promise_result` parameter with:
   - `status`: A string representing the promise status ('Successful', 'Failed', or 'NotReady')
   - `status_code`: The numeric status code (1 for success, 2 for failure, 0 for not ready)
   - `data`: The raw bytes returned by the promise (if successful)

2. Your return value will be properly serialized to be returned to the caller

Example:

```python
@callback
def on_data_received(self, promise_result: dict) -> dict:
    """Process data from another contract"""
    if promise_result["status"] != "Successful":
        return {"error": f"Call failed with status: {promise_result['status']}"}
        
    # Process the data
    data = promise_result["data"].decode("utf-8")
    parsed_data = json.loads(data)
    
    # Transform or enhance the data
    processed_data = {
        "original": parsed_data,
        "processed_at": Context.block_timestamp(),
        "processor": Context.current_account_id()
    }
    
    return processed_data
```

## Promise Chaining

You can chain multiple promises together to create more complex workflows:

```python
@call
def process_data_pipeline(self, data_source: str, processor: str) -> int:
    """
    Create a data processing pipeline across multiple contracts:
    1. Get data from data_source contract
    2. Process it with the processor contract
    3. Handle the final result in our callback
    """
    # First promise: get data
    promise1 = CrossContract.call(
        data_source, 
        "get_data",
        {},
        0,
        10 * ONE_TGAS
    )
    
    # Second promise: process data
    promise2 = CrossContract.then(
        promise1,
        processor,
        "process_data",
        {},
        0,
        10 * ONE_TGAS
    )
    
    # Final callback: handle the processed data
    final_promise = CrossContract.then(
        promise2,
        Context.current_account_id(),
        "on_processing_complete",
        {},
        0,
        10 * ONE_TGAS
    )
    
    return CrossContract.return_value(final_promise)
```

## Error Handling

Always check the status of promises in your callbacks:

```python
@callback
def on_result(self, promise_result: dict):
    if promise_result["status"] == "NotReady":
        return {"error": "Promise not ready yet"}
    elif promise_result["status"] == "Failed":
        return {"error": "The cross-contract call failed"}
    
    # Process the successful result
    # ...
```

## Advanced Usage

### Parallel Promises

You can execute multiple promises in parallel and then combine their results:

```python
@call
def aggregate_data(self, source1: str, source2: str) -> int:
    """Call multiple contracts and aggregate their results"""
    
    # Create multiple promises
    promise1 = CrossContract.call(source1, "get_data", {}, 0, 5 * ONE_TGAS)
    promise2 = CrossContract.call(source2, "get_data", {}, 0, 5 * ONE_TGAS)
    
    # Combine promises and add a callback
    combined_promise = CrossContract.and_then(
        [promise1, promise2],
        Context.current_account_id(),
        "on_combined_data",
        {},
        0,
        10 * ONE_TGAS
    )
    
    return CrossContract.return_value(combined_promise)

@callback
def on_combined_data(self, promise_result: dict):
    # Here you'd need to handle multiple promise results
    # This is a simplified example
    # ...
```

### Manual Promise Management

For more control, you can use the lower-level API:

```python
@call
def execute_complex_workflow(self, target: str, data: dict) -> int:
    # Initial call
    promise = CrossContract.call(target, "process", data, 0, 15 * ONE_TGAS)
    
    # Callback with specific gas allocation
    callback = CrossContract.then(
        promise,
        Context.current_account_id(),
        "on_process_complete",
        {"original_data": data},  # Pass additional context to callback
        0,
        15 * ONE_TGAS
    )
    
    return CrossContract.return_value(callback)
```

## Best Practices

1. **Gas Management**: Always allocate enough gas for both the cross-contract call and your callback.

2. **Error Handling**: Always check the promise status in callbacks.

3. **Data Serialization**: Be careful with data formats. Remember that promise results are returned as raw bytes.

4. **Testing**: Test cross-contract calls thoroughly, including error cases.

5. **Callback Structure**: Keep callbacks focused on processing the specific promise result they're designed for.

6. **Documentation**: Document the expected callback behavior for complex promise chains.

7. **Security**: Be cautious about which contracts you call and validate their responses.