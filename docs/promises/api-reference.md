# Promises API Reference

This document provides a comprehensive reference for all classes, methods, and decorators in the NEAR Python SDK's Promises API.

## Table of Contents

- [Promise Class](#promise-class)
- [Contract Class](#contract-class)
- [PromiseBatch Class](#promisebatch-class)
- [PromiseResult Class](#promiseresult-class)
- [Decorators](#decorators)
- [CrossContract Utility](#crosscontract-utility)
- [Constants](#constants)

## Promise Class

The `Promise` class is the core of the Promises API, providing a fluent interface for creating and chaining cross-contract calls.

### Constructors

```python
Promise(promise_id: int, gas: int = 5 * ONE_TGAS, deposit: int = 0)
```

Creates a new Promise wrapper around a low-level promise ID.

- `promise_id`: The NEAR promise ID to wrap
- `gas`: Gas to use for subsequent operations (default: 5 TGas)
- `deposit`: Deposit amount for subsequent operations (default: 0)

### Class Methods

```python
@classmethod
def create_batch(cls, account_id: str) -> PromiseBatch
```

Creates a new promise batch for the given account.

- `account_id`: The account to create the batch for
- Returns: A new `PromiseBatch` instance

```python
@staticmethod
def all(promises: List[Promise]) -> int
```

Creates a promise that resolves when all input promises resolve.

- `promises`: List of promises to join
- Returns: A promise ID for the combined promise

### Instance Methods

```python
gas(amount: int) -> Promise
```

Sets the gas amount for the next operation.

- `amount`: Gas amount in gas units
- Returns: A new Promise with updated gas setting

```python
deposit(amount: int) -> Promise
```

Sets the deposit amount for the next operation.

- `amount`: Deposit amount in yoctoNEAR
- Returns: A new Promise with updated deposit setting

```python
then(method: str, **kwargs) -> Promise
```

Chains a callback to the current contract after this promise.

- `method`: Method name in the current contract to call as callback
- `**kwargs`: Keyword arguments to pass to the callback
- Returns: A new Promise representing the chained operation

```python
then_call(contract_id: str, method: str, **kwargs) -> Promise
```

Chains a call to another contract after this promise.

- `contract_id`: Account ID of the contract to call
- `method`: Method name to call on the target contract
- `**kwargs`: Keyword arguments to pass to the method
- Returns: A new Promise representing the chained call

```python
then_batch(account_id: str) -> PromiseBatch
```

Chains a batch of actions to be executed after this promise completes.

- `account_id`: Account ID to execute the batch on
- Returns: A new PromiseBatch for adding actions

```python
join(other_promises: List[Promise], callback: str, **kwargs) -> Promise
```

Joins this promise with others and adds a callback.

- `other_promises`: List of other Promise objects to join with
- `callback`: Method name to call as callback
- `**kwargs`: Keyword arguments to pass to the callback
- Returns: A new Promise representing the joined operation

```python
value()
```

Returns this promise's result to the caller. This should be the final operation in your promise chain.

## Contract Class

The `Contract` class provides a convenient interface for interacting with deployed contracts.

### Constructor

```python
Contract(account_id: str, gas: int = 10 * ONE_TGAS, deposit: int = 0)
```

Initializes a contract proxy.

- `account_id`: The contract's account ID
- `gas`: Default gas to use for calls (default: 10 TGas)
- `deposit`: Default deposit amount (default: 0)

### Instance Methods

```python
gas(amount: int) -> Contract
```

Sets the default gas amount for calls to this contract.

- `amount`: Gas amount in gas units
- Returns: A new Contract with updated gas setting

```python
deposit(amount: int) -> Contract
```

Sets the default deposit amount for calls to this contract.

- `amount`: Deposit amount in yoctoNEAR
- Returns: A new Contract with updated deposit setting

```python
call(method: str, **kwargs) -> Promise
```

Calls a method on this contract with keyword arguments.

- `method`: The method name to call
- `**kwargs`: Keyword arguments to pass to the method
- Returns: A Promise object representing the call

```python
batch() -> PromiseBatch
```

Creates a batch of actions to execute on this contract.

- Returns: A new PromiseBatch for adding actions

## PromiseBatch Class

The `PromiseBatch` class allows you to perform multiple actions on a NEAR account in a single transaction.

### Constructor

```python
PromiseBatch(promise_id: int, gas: int = 5 * ONE_TGAS)
```

Initializes a promise batch.

- `promise_id`: The NEAR promise ID to wrap
- `gas`: Gas to use for subsequent operations (default: 5 TGas)

### Instance Methods

```python
create_account() -> PromiseBatch
```

Adds a CreateAccount action to this batch.

- Returns: Self for method chaining

```python
deploy_contract(code: bytes) -> PromiseBatch
```

Adds a DeployContract action to this batch.

- `code`: The Wasm binary of the contract
- Returns: Self for method chaining

```python
function_call(method: str, args: Any = None, amount: int = 0, gas: Optional[int] = None) -> PromiseBatch
```

Adds a FunctionCall action to this batch.

- `method`: Name of the method to call
- `args`: Arguments to pass to the method (dict, will be serialized to JSON)
- `amount`: Amount of NEAR tokens to attach (in yoctoNEAR)
- `gas`: Gas to attach (if None, uses the batch's gas setting)
- Returns: Self for method chaining

```python
transfer(amount: int) -> PromiseBatch
```

Adds a Transfer action to this batch.

- `amount`: Amount of NEAR tokens to transfer (in yoctoNEAR)
- Returns: Self for method chaining

```python
stake(amount: int, public_key: bytes) -> PromiseBatch
```

Adds a Stake action to this batch.

- `amount`: Amount of NEAR tokens to stake (in yoctoNEAR)
- `public_key`: Validator key to stake with
- Returns: Self for method chaining

```python
add_full_access_key(public_key: bytes, nonce: int = 0) -> PromiseBatch
```

Adds a full access key to the account.

- `public_key`: The public key to add
- `nonce`: Nonce for the access key
- Returns: Self for method chaining

```python
add_access_key(public_key: bytes, allowance: Optional[int], receiver_id: str, method_names: List[str], nonce: int = 0) -> PromiseBatch
```

Adds an access key with function call permission.

- `public_key`: The public key to add
- `allowance`: Allowance for the key (None means unlimited)
- `receiver_id`: Which account the key is allowed to call
- `method_names`: Which methods the key is allowed to call
- `nonce`: Nonce for the access key
- Returns: Self for method chaining

```python
delete_key(public_key: bytes) -> PromiseBatch
```

Deletes an access key.

- `public_key`: The public key to delete
- Returns: Self for method chaining

```python
delete_account(beneficiary_id: str) -> PromiseBatch
```

Deletes the account and sends remaining funds to beneficiary.

- `beneficiary_id`: Account to receive remaining funds
- Returns: Self for method chaining

```python
then(account_id: str) -> PromiseBatch
```

Creates a promise batch that will execute after this one completes.

- `account_id`: Account ID to execute the next batch on
- Returns: A new PromiseBatch for the next execution

```python
value()
```

Returns this batch's result to the caller. This should be the final operation in your batch chain.

## PromiseResult Class

The `PromiseResult` class wraps results from cross-contract calls.

### Constructor

```python
PromiseResult(status_code, data)
```

Initializes a minimal wrapper for cross-contract call results.

- `status_code`: The status code of the result
- `data`: The result data

### Properties

- `status_code`: The result status code (1 = success, other values = failure)
- `data`: The result data
- `success`: Boolean indicating if the call succeeded

### Methods

```python
unwrap()
```

Gets data or raises exception if failed.

```python
unwrap_or(default)
```

Gets data or returns default if failed.

## Decorators

### @callback

```python
@callback
def my_callback(self, result: PromiseResult, **kwargs):
    # Process the result
    pass
```

Decorator for promise result handlers with automatic unpacking. It:
1. Registers the function as a callback
2. Parses the promise result and handles errors
3. Passes the parsed data directly to your function

### @multi_callback

```python
@multi_callback
def my_multi_callback(self, results: List[PromiseResult], **kwargs):
    # Process the multiple results
    pass
```

Decorator for handling multiple promise results when using Promise.join or Promise.all. It:
1. Registers the function as a multi-promise callback
2. Collects all available promise results
3. Passes them to your function as a list of PromiseResult objects

## CrossContract Utility

The `CrossContract` class provides utility methods for working with promises.

### Class Methods

```python
@staticmethod
def call(account_id: str, method_name: str, args: Any = None, amount: int = 0, gas: int = MAX_GAS // 3) -> int
```

Makes a cross-contract call. Returns the promise index.

```python
@staticmethod
def call_with_callback(account_id: str, method_name: str, args: Any = None, amount: int = 0, gas: int = MAX_GAS // 3, callback_gas: Optional[int] = None, callback_method: Optional[str] = None, callback_args: Any = None) -> int
```

Makes a cross-contract call with an automatic callback to the current contract. Returns the final promise index.

```python
@staticmethod
def then(promise_idx: int, account_id: str, method_name: str, args: Any = None, amount: int = 0, gas: int = MAX_GAS // 3) -> int
```

Chains a callback to a promise. Returns the new promise index.

```python
@staticmethod
def get_result(promise_idx: int = 0) -> Dict[str, Any]
```

Gets the result of a promise for callback processing.

```python
@staticmethod
def and_then(promise_indices: List[int], account_id: str, method_name: str, args: Any = None, amount: int = 0, gas: int = MAX_GAS // 3) -> int
```

Combines multiple promises and chains a callback.

```python
@staticmethod
def return_value(promise_idx: int)
```

Returns the value of a promise.

## Constants

- `ONE_NEAR = 10**24`: 1 NEAR in yoctoNEAR
- `ONE_TGAS = 10**12`: 1 TeraGas
- `MAX_GAS = 300 * ONE_TGAS`: 300 TGas (maximum gas)

## Usage Example

Here's a comprehensive example showing how to use multiple components of the Promises API together:

```python
from near_sdk_py import call, callback, multi_callback, Context, Contract, PromiseResult, Storage, ONE_TGAS, ONE_NEAR
from near_sdk_py.promises import Promise
from typing import List

class ComplexExample:
    @call
    def multi_step_operation(self, contract_ids: List[str], data_id: str):
        # Store operation data
        Storage.set("operation:data_id", data_id)
        Storage.set("operation:initiator", Context.predecessor_account_id())
        
        # Create first contract call
        if not contract_ids:
            return {"success": False, "error": "No contract IDs provided"}
        
        primary_contract = Contract(contract_ids[0], gas=30 * ONE_TGAS)
        promise1 = primary_contract.call("get_data", id=data_id)
        
        # Create remaining calls
        other_promises = []
        for contract_id in contract_ids[1:]:
            contract = Contract(contract_id, gas=20 * ONE_TGAS)
            promise = contract.call("get_data", id=data_id)
            other_promises.append(promise)
        
        # Join all the promises with a callback
        combined_promise = promise1.join(
            other_promises,
            "process_data_results",
            contract_count=len(contract_ids)
        )
        
        return combined_promise.value()
    
    @multi_callback
    def process_data_results(self, results: List[PromiseResult], contract_count: int):
        data_id = Storage.get_string("operation:data_id")
        initiator = Storage.get_string("operation:initiator")
        
        # Process successful results
        successful_data = []
        for result in results:
            if result.success:
                successful_data.append(result.data)
        
        # If we have data, process it further
        if successful_data:
            # Create a batch to transfer tokens to the initiator
            batch = Promise.create_batch(initiator)
            batch.transfer(ONE_NEAR)
            
            # Add callback to confirm completion
            final_promise = batch.then(Context.current_account_id()).function_call(
                "operation_complete", 
                {
                    "data_id": data_id, 
                    "result_count": len(successful_data)
                },
                gas=10 * ONE_TGAS
            )
            
            return final_promise.value()
        else:
            return {
                "success": False,
                "error": "No successful data retrievals",
                "data_id": data_id
            }
    
    @callback
    def operation_complete(self, result: PromiseResult, data_id: str, result_count: int):
        # Clean up storage
        Storage.remove("operation:data_id")
        Storage.remove("operation:initiator")
        
        return {
            "success": result.success,
            "data_id": data_id,
            "result_count": result_count,
            "complete": True
        }
```

This example demonstrates:

1. Making multiple contract calls in parallel
2. Using the `@multi_callback` decorator to process multiple results
3. Chaining another promise batch (token transfer) based on the results
4. Adding a final callback to confirm completion and clean up
