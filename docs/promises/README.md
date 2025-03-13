# NEAR Python SDK Promises API

The NEAR Python SDK provides a high-level, idiomatic interface for making cross-contract calls on the NEAR blockchain through its Promises API. This document serves as an overview of the API and provides links to more detailed documentation.

## Understanding Cross-Contract Calls in NEAR

Cross-contract calls in NEAR have two important characteristics that make them different from other blockchains:

1. **Asynchronous**: There is a delay between the call and the callback execution, usually of 1 or 2 blocks.
2. **Independent**: Cross-contract calls require two independent functions: one to make the call, and another to receive the result.

When you make a cross-contract call in NEAR, the execution happens over multiple transactions:

1. Your initial function creates a promise to call another contract
2. The promise is executed in a subsequent block
3. If you specified a callback, it's executed after the promise completes

This asynchronous nature means you need to handle both outgoing calls and incoming results as separate functions.

## Core Components

The Promises API consists of several key components:

- **Promise**: A fluent interface for creating and chaining cross-contract calls
- **Contract**: A convenient wrapper for interacting with deployed contracts
- **PromiseBatch**: Allows multiple operations on a contract in a single transaction
- **PromiseResult**: Wraps results from cross-contract calls
- **Callback Decorators**: Simplify the creation of callback functions

A key feature of the API is its chainable method design. This allows for concise, readable code when building complex promise chains:

```python
# Methods can be chained together in a fluent interface
Contract("token.near")
    .gas(30 * ONE_TGAS)
    .deposit(ONE_NEAR)
    .call("transfer", to="recipient.near", amount="100")
    .then("on_transfer_complete", transfer_id="123")
    .value()
```

This chainable design makes it easy to build sophisticated cross-contract interactions while keeping your code elegant and understandable.

## Documentation Sections

Explore the following sections to learn more about the Promises API:

- [Basic Usage](basic-usage.md): Getting started with cross-contract calls
- [Callbacks](callbacks.md): Processing results from other contracts
- [Advanced Patterns](advanced-patterns.md): Chaining, batching, and parallel execution
- [Account Operations](account-operations.md): Creating accounts and managing access keys
- [Token and Gas Management](token-gas.md): Handling NEAR tokens and gas allocation
- [Error Handling](error-handling.md): Strategies for robust cross-contract interactions
- [Security Considerations](security.md): Important security aspects of cross-contract calls
- [API Reference](api-reference.md): Complete reference for all Promises API components

## Quick Example

Here's a simple example of a cross-contract call with a callback:

```python
from near_sdk_py import call, callback, Contract, PromiseResult

class MyContract:
    @call
    def get_data_from_other_contract(self, contract_id: str, data_key: str):
        # Create a contract instance
        other_contract = Contract(contract_id)
        
        # Call a method on the other contract
        promise = other_contract.call("get_data", key=data_key)
        
        # Add a callback to process the result
        promise = promise.then("process_data", original_key=data_key)
        
        # Return the promise result
        return promise.value()
    
    @callback
    def process_data(self, result: PromiseResult, original_key: str):
        if result.success:
            # Process the data from the other contract
            return {
                "success": True,
                "key": original_key,
                "data": result.data,
                "processed": True
            }
        else:
            return {
                "success": False,
                "key": original_key,
                "error": "Failed to retrieve data"
            }
```

This example demonstrates the basic pattern for cross-contract calls in NEAR using the Python SDK's Promises API.