# NEAR Python SDK

A Pythonic interface for building NEAR smart contracts.

[![PyPI version](https://img.shields.io/pypi/v/near-sdk-py)](https://pypi.org/project/near-sdk-py/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/badge/python-3.11%20|%203.12-blue)](https://pypi.org/project/near-sdk-py/)

## ✨ Highlights

- **Class-Based Contracts** - Clean, intuitive inheritance pattern
- **Pythonic Storage** - Dictionary-like interface for on-chain data
- **Elegant Promise API** - Intuitive chaining for cross-contract calls
- **Native Exception Handling** - Use try/except like regular Python
- **Ergonomic Context Access** - Properties instead of static methods

## 🚀 Getting Started

### 0️⃣ Install SDK

```bash
uv init your-contract
cd your-contract
uv add near-sdk-py
```

### 1️⃣ Create Your Contract

```python
from near_sdk_py import Contract, view, call, init

class GreetingContract(Contract):
    @init
    def initialize(self, default_message="Hello"):
        self.storage["greeting"] = default_message
        return {"success": True}
    
    @view
    def get_greeting(self):
        return self.storage.get("greeting", "Hello, world!")
    
    @call
    def set_greeting(self, message):
        self.storage["greeting"] = message
        return {"success": True}
```

### 2️⃣ Build and Deploy

```bash
uvx nearc build
near deploy your-contract.testnet greeting_contract.wasm
```

### 3️⃣ Interact With Your Contract

```bash
# Call a view method (free, no gas needed)
near view your-contract.testnet get_greeting

# Call a change method (requires gas)
near call your-contract.testnet set_greeting '{"message":"Hello, NEAR!"}' --accountId your-account.testnet
```

## 📚 SDK Components

### Contract Base Class

All contracts inherit from the `Contract` class, which provides:

```python
from near_sdk_py import Contract, call, view

class MyContract(Contract):
    @init
    def initialize(self):
        self.storage["owner"] = self.predecessor_account_id
        
    @view
    def get_status(self):
        # Access context properties directly
        return {
            "contract_id": self.current_account_id,
            "caller": self.predecessor_account_id,
            "owner": self.storage.get("owner"),
            "block_height": self.block_height,
            "timestamp": self.block_timestamp
        }
    
    @call
    def update_config(self, key, value):
        # Simple validation
        self.assert_owner()
        
        # Use dict-like storage access
        self.storage[key] = value
        
        # Easy logging
        self.log_event("config_updated", {"key": key})
        return {"success": True}
```

### Storage Interface

The storage interface is now more Pythonic with dictionary-like access:

```python
# Store values with dict syntax
self.storage["key"] = "value"                # String value
self.storage["config"] = {"active": True}    # Any JSON-serializable value

# Retrieve values with easy defaults 
value = self.storage.get("key", "default")   # With default
config = self.storage["config"]              # Direct access

# Check for keys
if "owner" in self.storage:
    # Do something
    
# Delete keys
del self.storage["old_key"]
```

### Context Properties

Access blockchain context directly as properties:

```python
# Account information
account_id = self.current_account_id      # This contract's account
caller = self.predecessor_account_id      # Who called this function
signer = self.signer_account_id           # Who signed the transaction

# Transaction details
deposit = self.attached_deposit           # NEAR tokens attached
gas = self.prepaid_gas                    # Gas allocated to this call

# Blockchain state 
height = self.block_height                # Current block height
timestamp = self.block_timestamp          # Current block timestamp
```

### Logging Helpers

```python
# Simple logging
self.log_info("Operation completed successfully")
self.log_warning("Approaching storage limit")
self.log_error("Transaction failed: insufficient deposit")

# NEP-standard event logging 
self.log_event("nft_mint", {
    "token_id": "token-123",
    "owner_id": "alice.near",
    "memo": "Happy birthday!"
})
```

## Exception Handling

Use native Python exceptions for error handling:

```python
from near_sdk_py import Contract, call, InvalidInput, AccessDenied

class MyContract(Contract):
    @call
    def restricted_method(self):
        if self.predecessor_account_id != self.storage.get("owner"):
            raise AccessDenied("Only the owner can call this method")
            
        if self.attached_deposit < self.storage.get("min_deposit", 0):
            raise InvalidInput("Insufficient deposit")
            
        try:
            # Do something that might fail
            result = some_operation()
        except Exception as e:
            raise ContractError(f"Operation failed: {e}")
```

## 🔄 Cross-Contract Calls

The SDK provides a powerful Promises API for making cross-contract calls with elegant method chaining:

```python
from near_sdk_py import call, callback, CrossContract, PromiseResult

class CrossContractExample(Contract):
    @call
    def get_token_balance(self, token_contract_id: str, account_id: str):
        # Create a contract instance and chain the operations
        promise = (
            CrossContract(token_contract_id)
            .call("ft_balance_of", account_id=account_id)
            .then("process_balance", account_id=account_id)
            .value()
        )
        return promise
    
    @callback
    def process_balance(self, result: PromiseResult, account_id: str):
        if result.success:
            return {
                "account_id": account_id,
                "balance": result.data
            }
        else:
            return {
                "account_id": account_id,
                "error": "Failed to retrieve balance"
            }
```

Key features of the Promises API:

- Fluent interface for chaining operations
- Automatic callback registration
- Promise result handling
- Support for batch operations

[Read the Promises documentation →](docs/promises/)

## 🔐 Security Best Practices

The `Contract` class provides built-in validation helpers:

```python
from near_sdk_py import call, ONE_NEAR

class SecureContract(Contract):
    @call
    def transfer_ownership(self, new_owner):
        self.assert_one_yocto()  # Ensures tx is signed (non-delegated)
        self.assert_owner()      # Verifies caller is the owner
        # Implementation...
    
    @call
    def place_bid(self, token_id):
        self.assert_min_deposit(ONE_NEAR)  # At least 1 NEAR required
        # Implementation...
```
## 🧪 Testing with near-pytest

The NEAR Python SDK works seamlessly with [near-pytest](https://github.com/r-near/near-pytest/), a pytest-native framework for testing NEAR smart contracts. Together, they provide a powerful toolchain for developing and testing contracts.

### Key Features of near-pytest

- **Zero-config setup** - Automatic sandbox management, contract compilation, and account creation
- **Lightning-fast tests** - State snapshots between tests make test suites run significantly faster
- **Intuitive API** - Simple, Pythonic interfaces for interacting with contracts and accounts

### Example Test Setup

```python
from near_pytest.testing import NearTestCase

class TestGreetingContract(NearTestCase):
    @classmethod
    def setup_class(cls):
        super().setup_class()
        
        # Compile the contract
        wasm_path = cls.compile_contract(
            "contracts/greeting.py", 
            single_file=True
        )
        
        # Deploy the contract
        cls.contract_account = cls.create_account("contract")
        cls.instance = cls.deploy_contract(cls.contract_account, wasm_path)
        
        # Create test user
        cls.user = cls.create_account("user")
        
        # Save state for future resets - this is crucial for performance
        cls.save_state()
    
    def setup_method(self):
        # Reset to initial state before each test method
        # This makes tests run much faster than re-deploying
        self.reset_state()
        
    def test_greeting(self):
        # Set greeting as user
        result = self.instance.call_as(
            account=self.user,
            method_name="set_greeting",
            args={"message": "Hello, tests!"}
        )
        result = json.loads(result)
        assert result["success"] == True
        
        # Get greeting
        greeting = self.instance.call_as(
            account=self.user,
            method_name="get_greeting"
        )
        assert greeting == "Hello, tests!"
```

### Running Tests

Simply run with pytest:

```bash
pytest test_greeting_contract.py -v
```

### State Management in Tests

The state management pattern (save_state/reset_state) is what makes near-pytest tests run significantly faster than traditional approaches. Rather than re-deploying contracts and recreating accounts for each test, it:

1. Sets up the full environment once in `setup_class` 
2. Takes a snapshot of the blockchain state
3. Quickly resets to this snapshot before each test

This approach can make test suites run orders of magnitude faster, especially as your test suite grows.


## 📊 Example Projects

The SDK includes starter templates for common contract types:

- **[Fungible Tokens](examples/ft-contract/)** - Create your own token
- **[Non-Fungible Tokens](examples/nft-contract/)** - Build an NFT collection
- **[DAO Governance](examples/dao-contract/)** - Decentralized organizations
- **[DeFi Contracts](examples/defi-contract/)** - Financial applications

## 📈 Performance Considerations

- Group related data in a single storage entry to reduce calls
- Implement pagination for methods that return large collections
- For collections, use the SDK's storage primitives which are optimized for gas efficiency

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to submit pull requests, report issues, and suggest improvements.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Made with ❤️ by r-near