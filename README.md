# NEAR Python SDK

A higher-level API for building NEAR smart contracts in Python.

[![PyPI version](https://img.shields.io/badge/pypi-0.1.0-blue.svg)](https://pypi.org/project/near-sdk-py/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/badge/python-3.11%20|%203.12-blue)](https://pypi.org/project/near-sdk-py/)

## Introduction

NEAR Python SDK provides a structured abstraction layer over the low-level NEAR blockchain API. This library streamlines the development of smart contracts by offering type-safe interfaces, standardized patterns, and utility functions that handle common blockchain operations. Built on top of the near-py-tool project, it enables developers to write maintainable and secure contract code with reduced complexity.

```python
from near_sdk_py import view, Storage

@view
def get_greeting():
    return Storage.get_string("greeting") or "Hello, NEAR world!"
```

## 🔥 Key Features

- 📦 **Simple Storage API** - Store/retrieve data with intuitive methods
- 🔄 **Smart Contract Lifecycle** - Easily manage initialization and upgrades
- 🔍 **Decorators** - Clearly mark functions as `@view`, `@call`, or `@init`
- 🌐 **Cross-Contract Calls** - Seamlessly interact with other contracts
- 📝 **Structured Logging** - NEP-standard event logging made simple
- 🛡️ **Built-in Security** - Validation helpers for common security patterns
- 🧩 **Modular Design** - Well-organized codebase for maximum maintainability

## 📋 Installation

```bash
# Install using uv
uv add near-sdk-py

# Traditional pip install
pip install near-sdk-py
```

## 🚦 Getting Started

### 1️⃣ Create Your Contract

```python
from near_sdk_py import view, call, init, Context, Storage, Log

class GreetingContract:
    @init
    def new(self, owner_id=None):
        """Initialize the contract with optional owner"""
        owner = owner_id or Context.predecessor_account_id()
        Storage.set("owner", owner)
        Log.info(f"Contract initialized by {owner}")
        return True
    
    @call
    def set_greeting(self, message):
        """Store a greeting message (requires gas)"""
        Storage.set("greeting", message)
        return f"Greeting updated to: {message}"
    
    @view
    def get_greeting(self):
        """Retrieve the greeting message (free, no gas needed)"""
        return Storage.get_string("greeting") or "Hello, NEAR world!"

# Export the contract methods
contract = GreetingContract()

# These exports make functions available to the NEAR runtime
new = contract.new
set_greeting = contract.set_greeting
get_greeting = contract.get_greeting
```

### 2️⃣ Build and Deploy

Use [nearc](https://github.com/r-near/nearc) to compile your contract:

```bash
# Create a new project
uv init greeting-contract
cd greeting-contract

# Install the SDK
uv add near-sdk-py

# Create your contract file
# (Copy your contract code into contract.py)

# Compile the contract
uvx nearc contract.py
```

This will generate a WebAssembly (`.wasm`) file that can be deployed to the NEAR blockchain.

### 3️⃣ Deploy to NEAR

After compiling your contract, use the NEAR CLI to deploy it:

```bash
# Deploy to testnet
near deploy your-contract.testnet contract.wasm --networkId testnet
```

### 4️⃣ Interact with your Contract

```bash
# Call view methods (free)
near view your-contract.testnet get_greeting

# Call methods that change state (costs gas)
near call your-contract.testnet set_greeting '{"message":"Hello from CLI"}' --accountId your-account.testnet
```

## 📚 SDK Components

### Storage API

```python
# Store values in different formats
Storage.set("key", "value")                  # String value
Storage.set_json("config", {"active": True}) # Any JSON-serializable value

# Retrieve stored values 
value = Storage.get_string("key")           # As string
config = Storage.get_json("config")         # As Python object

# Manage storage
exists = Storage.has("key")                 # Check if key exists
Storage.remove("key")                       # Delete a key
```

### Context Information

```python
# Account information
account_id = Context.current_account_id()    # This contract's account
caller = Context.predecessor_account_id()    # Who called this function
signer = Context.signer_account_id()         # Who signed the transaction

# Transaction details
deposit = Context.attached_deposit()         # NEAR tokens attached
gas = Context.prepaid_gas()                  # Gas allocated to this call

# Blockchain state 
height = Context.block_height()              # Current block height
timestamp = Context.block_timestamp()        # Current block timestamp
```

### Logging

```python
# Simple logging
Log.info("Operation completed successfully")
Log.warning("Approaching storage limit")
Log.error("Transaction failed: insufficient deposit")

# NEP-standard event logging 
Log.event("nft_mint", {
    "token_id": "token-123",
    "owner_id": "alice.near",
    "memo": "Happy birthday!"
})
```

### Cross-Contract Calls

Work with NEAR's asynchronous cross-contract calls using the Promises API:

```python
from near_sdk_py import call, callback, CrossContract, ONE_TGAS

class MyContract:
    @call
    def update_profile(self, username: str):
        return CrossContract.call_with_callback(
            "profile.near",               # Target contract
            "set_username",               # Method to call
            {"username": username},       # Arguments
            gas=5 * ONE_TGAS,             # Gas for the call
            callback_method="on_update_complete"  # Our callback
        )

    @callback
    def on_update_complete(self, promise_result: dict):
        if promise_result["status"] == "Successful":
            return "Profile updated successfully!"
        else:
            return "Update failed!"
```

The `@callback` decorator helps process responses from other contracts, while `CrossContract.call_with_callback()` streamlines the common pattern of making a call and handling its result.

For advanced use cases, you can also build promise chains manually:

```python
# Make initial call
promise = CrossContract.call("token.near", "get_balance", {"account_id": "alice.near"})

# Chain a callback to process the result
callback = CrossContract.then(
    promise,
    CrossContract.current_account_id(),
    "on_balance_received"
)

# Return the final result
return CrossContract.return_value(callback)
```

See the [Promises API documentation](docs/promises-api.md) for more detailed examples.

## 🔐 Security Best Practices

```python
# Require exactly 1 yoctoNEAR to prove key ownership
@call
def transfer_ownership(self, new_owner):
    Contract.assert_one_yocto()  # Ensures tx is signed (non-delegated)
    # Implementation...

# Require minimum deposit for a function
@call
def place_bid(self, token_id):
    Contract.assert_min_deposit(ONE_NEAR)  # At least 1 NEAR required
    # Implementation...
```

## 📊 Example Projects

The SDK includes starter templates for common contract types:

- **[Fungible Tokens](examples/ft-contract/)** - Create your own token
- **[Non-Fungible Tokens](examples/nft-contract/)** - Build an NFT collection
- **[DAO Governance](examples/dao-contract/)** - Decentralized organizations
- **[DeFi Contracts](examples/defi-contract/)** - Financial applications

## 📈 Performance Considerations

- Use `Storage.get_json()` for complex data instead of parsing manually
- Group related data in a single storage entry to reduce calls
- Implement pagination for methods that return large collections

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to submit pull requests, report issues, and suggest improvements.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Made with ❤️ by r-near