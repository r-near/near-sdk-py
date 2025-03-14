# Improved NEAR Python SDK

A more ergonomic, Pythonic interface for building NEAR smart contracts.

## Key Improvements

This improved version of the NEAR Python SDK enhances the developer experience with:

1. **Class-Based Contracts** - Clean, intuitive inheritance pattern
2. **Storage Collections** - Pythonic storage for on-chain data
3. **Native Exception Handling** - Use try/except like regular Python
4. **Ergonomic Context Access** - Properties instead of static methods
5. **Validation Helpers** - Common security assertions built-in

## Quick Start

### 1. Install the SDK

```bash
pip install near-sdk-py
```

### 2. Define Your Contract

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

### 3. Build and Deploy

```bash
nearc build greeting_contract.py
near deploy your-contract.testnet greeting_contract.wasm
```

## Contract Base Class

All contracts now inherit from the `Contract` class, which provides:

- Automatic method exporting
- Convenient property access to context
- Storage interface
- Collection management
- Validation helpers

### Defining a Contract

```python
from near_sdk_py import Contract, view, call

class MyContract(Contract):
    # Contract methods...
```

The `Contract` class automatically handles the export of methods
decorated with `@view`, `@call`, or `@init`. You no longer need to
manually assign methods to global variables.

### Accessing Context

```python
@call
def my_method(self):
    # Previously:
    # account_id = Context.predecessor_account_id()
    
    # Now:
    account_id = self.predecessor_account_id
    
    # Also available:
    contract_id = self.current_account_id
    deposit = self.attached_deposit
    gas = self.prepaid_gas
```

## Storage Interface

The storage interface is now more Pythonic with dictionary-like access:

```python
@call
def update_config(self, key, value):
    # Dictionary-style access
    self.storage[key] = value
    
    # Check if a key exists
    if "owner" in self.storage:
        # ...
    
    # Delete a key
    del self.storage["old_key"]
    
    # Get with default
    owner = self.storage.get("owner", "default_owner")
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

## Validation Helpers

The Contract class includes built-in validation methods:

```python
@call
def owner_only_method(self):
    # Verify caller is the owner
    self.assert_owner()
    
    # ... rest of the method ...

@call
def premium_feature(self):
    # Verify attached deposit meets minimum
    self.assert_min_deposit(ONE_NEAR)
    
    # ... rest of the method ...

@call
def withdraw_funds(self):
    # Verify this is signed by the owner (not a delegate)
    self.assert_one_yocto()
    self.assert_owner()
    
    # ... rest of the method ...
```

## Promise API Integration

The improved SDK maintains compatibility with the existing Promise API:

```python
from near_sdk_py import Contract, call, callback, PromiseResult

class CrossContractExample(Contract):
    @call
    def call_other_contract(self, contract_id, message):
        from near_sdk_py import CrossContract
        
        other_contract = CrossContract(contract_id)
        promise = other_contract.call("some_method", message=message)
        
        return promise.then("handle_result").value()
    
    @callback
    def handle_result(self, result: PromiseResult):
        if result.success:
            return {"success": True, "data": result.data}
        else:
            return {"success": False, "error": "Call failed"}
```

## License

This SDK is licensed under the MIT License.