# Promise API Reference

This document provides a comprehensive reference for the Promise API classes and methods.

## Contract Class

The `Contract` class represents a NEAR smart contract with methods you can call.

### Constructor

```python
Contract(account_id: str, gas: int = 5 * ONE_TGAS, deposit: int = 0)
```

Creates a reference to a NEAR contract.

**Parameters:**
- `account_id`: The contract's account ID
- `gas`: Default gas to use for calls (default: 5 TGas)
- `deposit`: Default deposit amount in yoctoNEAR (default: 0)

**Example:**
```python
token = Contract("token.near")
token_with_gas = Contract("token.near", gas=10 * ONE_TGAS)
```

### Methods

#### gas

```python
gas(amount: int) -> Contract
```

Sets the default gas amount for calls to this contract.

**Parameters:**
- `amount`: Gas amount in gas units

**Returns:**
A new `Contract` instance with updated gas setting

**Example:**
```python
token = Contract("token.near").gas(10 * ONE_TGAS)
```

#### deposit

```python
deposit(amount: int) -> Contract
```

Sets the default deposit amount for calls to this contract.

**Parameters:**
- `amount`: Deposit amount in yoctoNEAR

**Returns:**
A new `Contract` instance with updated deposit setting

**Example:**
```python
token = Contract("token.near").deposit(ONE_NEAR)
```

#### call

```python
call(method: str, **kwargs) -> Promise
```

Calls a method on this contract with keyword arguments.

**Parameters:**
- `method`: The method name to call
- `**kwargs`: Keyword arguments to pass to the method

**Returns:**
A `Promise` object representing the call

**Example:**
```python
promise = token.call("ft_metadata")
promise = token.call("ft_transfer", receiver_id="bob.near", amount="1000")
```

## Promise Class

The `Promise` class represents the result of an asynchronous contract call.

### Methods

#### gas

```python
gas(amount: int) -> Promise
```

Sets the gas amount for the next operation in the chain.

**Parameters:**
- `amount`: Gas amount in gas units

**Returns:**
A new `Promise` with updated gas setting

**Example:**
```python
promise = token.call("ft_metadata").gas(10 * ONE_TGAS)
```

#### deposit

```python
deposit(amount: int) -> Promise
```

Sets the deposit amount for the next operation in the chain.

**Parameters:**
- `amount`: Deposit amount in yoctoNEAR

**Returns:**
A new `Promise` with updated deposit setting

**Example:**
```python
promise = token.call("ft_metadata").deposit(ONE_NEAR)
```

#### then

```python
then(method: str, **kwargs) -> Promise
```

Chains a callback to the current contract after this promise.

**Parameters:**
- `method`: Method name in the current contract to call as callback
- `**kwargs`: Keyword arguments to pass to the callback

**Returns:**
A new `Promise` representing the chained operation

**Example:**
```python
promise = token.call("ft_metadata").then("on_metadata_received", token_id="near")
```

#### then_call

```python
then_call(contract_id: str, method: str, **kwargs) -> Promise
```

Chains a call to another contract after this promise.

**Parameters:**
- `contract_id`: Account ID of the contract to call
- `method`: Method name to call on the target contract
- `**kwargs`: Keyword arguments to pass to the method

**Returns:**
A new `Promise` representing the chained call

**Example:**
```python
promise = token.call("ft_metadata").then_call("price.oracle.near", "get_price", token_id="near")
```

#### join

```python
join(other_promises: List[Promise], callback: str, **kwargs) -> Promise
```

Joins this promise with others and adds a callback.

**Parameters:**
- `other_promises`: List of other `Promise` objects to join with
- `callback`: Method name to call as callback
- `**kwargs`: Keyword arguments to pass to the callback

**Returns:**
A new `Promise` representing the joined operation

**Example:**
```python
promise1 = token_a.call("ft_metadata")
promise2 = token_b.call("ft_metadata")
combined = promise1.join([promise2], "on_both_received")
```

#### value

```python
value()
```

Returns this promise's result to the caller. This should be the final operation in your promise chain.

**Example:**
```python
return promise.value()
```

## Decorators

### callback

```python
@callback
def handler(self, data, **context):
    # Process data
```

Decorator for promise result handlers.

This decorator:
1. Registers the function as a callback
2. Parses the promise result and handles errors
3. Passes the parsed data directly to your function

**Parameters passed to the decorated function:**
- `self`: The contract instance
- `data`: The parsed data from the promise result
- `**context`: Any context variables passed from the previous call

**Example:**
```python
@callback
def on_metadata_received(self, metadata, token_id=None):
    return {
        "name": metadata.get("name"),
        "token_id": token_id
    }
```

## PromiseResult Class

The `PromiseResult` class is used internally to wrap promise results, providing helper methods for error handling and data access.

### Properties

#### is_success

```python
@property
def is_success(self) -> bool
```

Whether the promise completed successfully.

#### is_error

```python
@property
def is_error(self) -> bool
```

Whether the promise completed with an error.

#### data

```python
@property
def data(self) -> Any
```

Gets deserialized data from the result.

### Methods

#### unwrap

```python
unwrap(self) -> Any
```

Gets the data or raises an exception if failed.

#### unwrap_or

```python
unwrap_or(self, default: T) -> Union[Any, T]
```

Gets the data or returns a default value if failed.
