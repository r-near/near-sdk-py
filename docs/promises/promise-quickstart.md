# Promise API Quick Start Guide

This guide will help you get started with the Promise API for cross-contract calls in NEAR Python smart contracts.

## Installation

The Promise API is included with the NEAR Python SDK. No additional installation is required.

## Basic Concepts

Before we dive in, let's understand the core concepts:

- **Contract**: A reference to another NEAR contract
- **Promise**: Represents the result of an asynchronous operation
- **Callback**: A method that processes the result of a promise

## Simple Cross-Contract Call

Let's start with a basic example - calling another contract and processing the result:

```python
from near_sdk_py import call
from near_sdk_py.promises import Contract, callback

class TokenPortfolio:
    @call
    def get_token_name(self, token_id):
        # Create a reference to the token contract
        token = Contract(f"token.{token_id}.near")
        
        # Call the ft_metadata method
        promise = token.call("ft_metadata")
        
        # Add a callback to process the result
        promise = promise.then("on_metadata_received")
        
        # Return the promise value
        return promise.value()
    
    @callback
    def on_metadata_received(self, metadata):
        # metadata is automatically parsed from JSON
        return {
            "name": metadata.get("name", "Unknown Token"),
            "symbol": metadata.get("symbol", "???")
        }
```

That's it! The Promise API handles all the complexity of cross-contract calls behind the scenes.

## Passing Arguments

You can pass arguments to contract methods directly as keyword arguments:

```python
# Pass arguments directly
promise = token.call("ft_balance_of", account_id="alice.near")
```

This is equivalent to the more verbose traditional approach:

```python
# Traditional approach
promise = CrossContract.call(
    "token.near", 
    "ft_balance_of", 
    {"account_id": "alice.near"}
)
```

## Passing Context to Callbacks

Often, you'll want to pass additional context to your callback methods:

```python
@call
def get_token_data(self, token_id):
    token = Contract(f"token.{token_id}.near")
    
    # Pass context to the callback
    promise = token.call("ft_metadata").then(
        "on_metadata_received", 
        token_id=token_id,
        timestamp=near.block_timestamp()
    )
    
    return promise.value()

@callback
def on_metadata_received(self, metadata, token_id=None, timestamp=None):
    # Access context variables alongside the parsed result
    return {
        "token_id": token_id,
        "name": metadata.get("name"),
        "timestamp": timestamp
    }
```

## Setting Gas and Deposit

You can specify gas and deposit amounts:

```python
# Set gas for a contract
token = Contract("token.near").gas(10 * ONE_TGAS)

# Set deposit for a specific call
promise = token.deposit(ONE_NEAR).call("storage_deposit")

# Combine and chain
promise = Contract("token.near").gas(5 * ONE_TGAS).call("ft_metadata")
```

## Chaining Multiple Calls

You can chain multiple calls together:

```python
# Call sequence: get metadata -> get price -> format result
promise = token.call("ft_metadata").then("get_price").then("format_result")
```

## Calling Other Contracts in a Chain

Call another contract after processing a result:

```python
@callback
def on_balance_received(self, balance_data, token_id=None):
    balance = int(balance_data.get("balance", "0"))
    
    # Continue by calling another contract
    oracle = Contract("price.oracle.near")
    return oracle.call("get_price", token_id=token_id).then(
        "on_price_received", 
        token_id=token_id,
        balance=balance
    )
```

## Next Steps

Now that you've learned the basics, check out:

- [API Reference](./promise-reference.md) for detailed documentation
- [Advanced Patterns](./promise-advanced-patterns.md) for complex use cases
- [Examples](./promise-examples.md) for real-world applications
