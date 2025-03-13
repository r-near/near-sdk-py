# Basic Usage of the Promises API

This guide covers the fundamental usage patterns for the NEAR Python SDK's Promises API.

## Making Simple Cross-Contract Calls

The most basic cross-contract call involves calling a method on another contract and returning the result directly:

```python
from near_sdk_py import call, Contract

class MyContract:
    @call
    def direct_call(self, contract_id: str, key: str):
        """
        Call a method on another contract and return the result directly.
        This is the simplest possible cross-contract call pattern.
        """
        # Create a Contract object
        contract = Contract(contract_id)
        
        # Call the get_value method on the other contract
        # and return the Promise result directly
        return contract.call("get_value", key=key).value()
```

When you use `.value()` at the end of a promise chain, the result of the promise is returned to the caller. This approach is suitable for simple calls where you don't need to process the result.

## Customizing Gas and Deposit

You can customize the gas and deposit amounts for a cross-contract call:

```python
from near_sdk_py import call, Contract, ONE_TGAS, ONE_NEAR

class MyContract:
    @call
    def customized_call(self, contract_id: str, method: str):
        # Create a Contract object with custom gas allocation
        contract = Contract(contract_id, gas=30 * ONE_TGAS)
        
        # Attach tokens to the call
        contract = contract.deposit(ONE_NEAR)
        
        # Make the call
        promise = contract.call(method)
        
        # Return the promise result
        return promise.value()
```

Alternatively, you can use method chaining to set gas and deposit amounts:

```python
from near_sdk_py import call, Contract, ONE_TGAS, ONE_NEAR

class MyContract:
    @call
    def chained_customization(self, contract_id: str, method: str):
        # Use method chaining to set gas and deposit
        promise = Contract(contract_id)
            .gas(30 * ONE_TGAS)
            .deposit(ONE_NEAR)
            .call(method)
        
        return promise.value()
```

The chainable design is one of the most powerful features of the Promises API, allowing you to create complex interaction patterns with clean, readable code.

## Using the Contract Wrapper

The `Contract` class provides a convenient wrapper for interacting with deployed contracts:

```python
from near_sdk_py import call, Contract

class MyContract:
    @call
    def interact_with_contract(self, contract_id: str, user_id: str, item_id: str):
        # Create a Contract object
        token_contract = Contract(contract_id)
        
        # Call methods with keyword arguments
        promise = token_contract.call(
            "transfer_item",
            from_id=user_id,
            item_id=item_id,
            memo="Transferred via MyContract"
        )
        
        return promise.value()
```

The `call` method accepts keyword arguments that are automatically serialized to JSON and sent to the target contract.

## Basic Cross-Contract Call with a Callback

When you need to process the result of a cross-contract call before returning it, use a callback:

```python
from near_sdk_py import call, callback, Contract, PromiseResult

class MyContract:
    @call
    def call_with_callback(self, contract_id: str, key: str):
        # Create a Contract object
        contract = Contract(contract_id)
        
        # Call a method on the contract
        promise = contract.call("get_value", key=key)
        
        # Add a callback to process the result
        promise = promise.then("process_callback", key=key)
        
        # Return the final promise result
        return promise.value()
    
    @callback
    def process_callback(self, result: PromiseResult, key: str):
        """Process the result of the cross-contract call."""
        if result.success:
            return {
                "success": True,
                "key": key,
                "value": result.data,
                "processed": True
            }
        else:
            return {
                "success": False,
                "key": key,
                "error": "Failed to retrieve value"
            }
```

The `@callback` decorator handles the boilerplate of accessing and processing the promise result. Your callback function receives a `PromiseResult` object that contains:

- `status_code`: The raw status code (1 = success)
- `data`: The data returned by the called contract
- `success`: A boolean indicating success or failure

## Next Steps

Once you're comfortable with the basics, explore these more advanced topics:

- [Working with Callbacks](callbacks.md)
- [Advanced Promise Patterns](advanced-patterns.md)
- [Token and Gas Management](token-gas.md)