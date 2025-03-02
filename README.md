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
# Install using pip & uv
uv pip install near-sdk-py

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

Use `near-py-tool` to build and deploy your contract:

```bash
# Create a new project
near-py-tool new greeting-contract

# Copy your contract code into the project directory
cp my_contract.py greeting-contract/

# Build the contract
cd greeting-contract
near-py-tool build

# Deploy to testnet
near-py-tool deploy testnet
```

### 3️⃣ Interact with your Contract

```bash
# Call view methods (free)
near view greeting-contract.testnet get_greeting

# Call methods that change state (costs gas)
near call greeting-contract.testnet set_greeting '{"message":"Hello from CLI"}' --accountId your-account.testnet
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

```python
# Call another contract
promise = CrossContract.call(
    "nft.example.near",      # Contract account
    "nft_transfer",          # Method name
    {                        # Arguments
        "receiver_id": "bob.near", 
        "token_id": "token-123"
    },
    1,                       # Attached deposit (1 yoctoNEAR)
    10 * ONE_TGAS            # Gas to attach (10 TGas)
)

# Add a callback for when the call completes
callback = CrossContract.then(
    promise,                         # Previous promise
    Context.current_account_id(),    # This contract
    "on_transfer_complete",          # Callback method
    {"user": "alice.near"},          # Arguments
    0,                               # No deposit
    5 * ONE_TGAS                     # Gas (5 TGas)
)

# Return the result from the callback
CrossContract.return_value(callback)
```

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