# Promise API for Cross-Contract Calls

NEAR's smart contracts can interact with each other through asynchronous cross-contract calls. This Promise API provides a clean, Pythonic interface for working with these asynchronous workflows.

## Overview

Cross-contract calls in NEAR are inherently asynchronous, returning "promises" that represent future results. The Promise API makes working with these asynchronous operations more intuitive through method chaining and modern Python syntax.

## Key Features

- **Fluent Interface**: Chain method calls for cleaner, more readable code
- **Pythonic Design**: Uses keyword arguments and other Python idioms
- **Simplified Error Handling**: Automatic error handling for promise results
- **Context Passing**: Easily pass context data between promise steps
- **Promise Joining**: Combine multiple promises with a single callback

## Components

The Promise API consists of three main components:

1. **Contract**: Represents a NEAR contract with methods you can call
2. **Promise**: Represents the result of a contract call, with methods for chaining operations
3. **@callback**: Decorator for methods that process promise results

## Basic Usage

```python
from near_sdk_py import call
from near_sdk_py.promises import Contract, callback

class MyContract:
    @call
    def get_token_info(self, token_id):
        # Create a Contract reference
        token = Contract(f"token.{token_id}.near")
        
        # Call a method and chain a callback
        promise = token.call("ft_metadata").then("on_token_info")
        
        # Return the promise value
        return promise.value()
    
    @callback
    def on_token_info(self, token_info):
        # token_info is already parsed from JSON
        return {
            "name": token_info.get("name"),
            "symbol": token_info.get("symbol"),
            "decimals": token_info.get("decimals")
        }
```

## Compared to Traditional Approach

| Traditional Approach | Promise API |
|----------------------|-------------|
| `CrossContract.call("contract.near", "method", {"arg": "value"})` | `Contract("contract.near").call("method", arg="value")` |
| Manual promise result handling | Automatic parsing with `@callback` |
| Manual error handling | Built-in error handling |
| Explicit callback chaining | Fluent method chaining with `.then()` |

## Next Steps

- Check the [Quick Start Guide](./promise-quickstart.md) for a step-by-step introduction
- See [API Reference](./promise-reference.md) for detailed method documentation
- Explore [Advanced Patterns](./promise-advanced-patterns.md) for complex workflows
- See the [Examples](./promise-examples.md) for real-world examples
