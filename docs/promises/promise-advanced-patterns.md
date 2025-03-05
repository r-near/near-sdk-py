# Promise API Advanced Patterns

This guide explores advanced patterns and techniques for using the Promise API in complex scenarios.

## Table of Contents

- [Multi-Step Promise Chains](#multi-step-promise-chains)
- [Parallel Promises](#parallel-promises)
- [State Management Between Callbacks](#state-management-between-callbacks)
- [Error Handling Strategies](#error-handling-strategies)
- [Gas Management](#gas-management)
- [Timeouts and Fallbacks](#timeouts-and-fallbacks)

## Multi-Step Promise Chains

Complex workflows often require multiple steps that depend on previous results. The Promise API makes these chains readable and maintainable.

### Example: Token Swap

```python
@call
def swap_tokens(self, token_in, token_out, amount):
    """
    Multi-step token swap process:
    1. Check balance
    2. Get exchange rate
    3. Approve DEX to spend tokens
    4. Execute swap
    5. Verify result
    """
    # Step 1: Check balance
    token = Contract(token_in)
    promise = token.call("ft_balance_of", account_id=near.current_account_id())
    
    # Chain the rest of the steps
    promise = promise.then("verify_balance_for_swap", 
                           token_in=token_in,
                           token_out=token_out,
                           amount=amount)
    
    return promise.value()

@callback
def verify_balance_for_swap(self, balance_data, token_in, token_out, amount):
    # Process balance and continue if sufficient
    balance = int(balance_data.get("balance", "0"))
    if balance < amount:
        return {"error": "Insufficient balance", "available": balance, "required": amount}
    
    # Step 2: Get exchange rate
    dex = Contract("dex.near")
    return dex.call("get_rate", token_in=token_in, token_out=token_out) \
              .then("prepare_swap", token_in=token_in, token_out=token_out, amount=amount)

@callback
def prepare_swap(self, rate_data, token_in, token_out, amount):
    # Process rate and prepare swap parameters
    rate = float(rate_data.get("rate", "0"))
    min_out = int(amount * rate * 0.98)  # 2% slippage tolerance
    
    # Step 3: Approve DEX to spend tokens
    token = Contract(token_in)
    return token.call("ft_approve", spender="dex.near", amount=str(amount)) \
                .then("execute_swap", 
                       token_in=token_in,
                       token_out=token_out,
                       amount=amount,
                       min_out=min_out)

@callback
def execute_swap(self, approve_result, token_in, token_out, amount, min_out):
    # Step 4: Execute the swap
    dex = Contract("dex.near")
    return dex.call("swap", 
                    token_in=token_in,
                    token_out=token_out,
                    amount_in=str(amount),
                    min_amount_out=str(min_out)) \
              .then("verify_swap_result")

@callback
def verify_swap_result(self, swap_result):
    # Step 5: Verify and format the result
    if "error" in swap_result:
        return {"success": False, "error": swap_result["error"]}
    
    return {
        "success": True,
        "amount_in": swap_result.get("amount_in"),
        "amount_out": swap_result.get("amount_out"),
        "rate": float(swap_result.get("amount_out")) / float(swap_result.get("amount_in"))
    }
```

## Parallel Promises

For operations that can run independently, you can execute multiple promises in parallel and join their results.

### Example: Multi-Token Portfolio

```python
@call
def get_portfolio_value(self, account_id, token_ids):
    """Get balances and values for multiple tokens in parallel."""
    promises = []
    
    # Create a promise for each token balance
    for token_id in token_ids:
        token = Contract(f"token.{token_id}.near")
        promise = token.call("ft_balance_of", account_id=account_id)
        promises.append(promise)
    
    # Join all promises with a callback
    if not promises:
        return {"error": "No tokens specified"}
        
    combined = promises[0].join(promises[1:], "calculate_portfolio", 
                                account_id=account_id, 
                                token_ids=token_ids)
    
    return combined.value()

@callback
def calculate_portfolio(self, balance_results, account_id, token_ids):
    """Process multiple token balances in parallel."""
    portfolio = []
    
    # Process each token's balance
    for i, token_id in enumerate(token_ids):
        if i < len(balance_results):
            balance_data = balance_results[i]
            balance = int(balance_data.get("balance", "0"))
            
            # In a real application, you would get the token price here
            # or make another batch of parallel calls to a price oracle
            price = self._get_token_price(token_id)
            
            portfolio.append({
                "token_id": token_id,
                "balance": balance,
                "value_usd": balance * price / 1_000_000  # Assuming 6 decimals
            })
    
    # Calculate total value
    total_value = sum(item["value_usd"] for item in portfolio)
    
    return {
        "account_id": account_id,
        "total_value_usd": total_value,
        "tokens": portfolio
    }

def _get_token_price(self, token_id):
    """Helper to get token price (mock implementation)."""
    # In a real application, you would call a price oracle
    mock_prices = {"near": 5.20, "eth": 3500.00, "usdc": 1.00}
    return mock_prices.get(token_id, 0.00)
```

## State Management Between Callbacks

When you need to pass complex state between multiple callbacks, you can either:

1. Pass state through the callback arguments
2. Store state in contract storage (for very large data)

### Example: Auction Process with State Passing

```python
@call
def start_auction_process(self, token_id, min_bid):
    """Start a multi-step auction process."""
    # Step 1: Get token metadata
    token = Contract(f"token.{token_id}.near")
    
    # Initialize auction state
    auction_state = {
        "token_id": token_id,
        "min_bid": min_bid,
        "start_time": near.block_timestamp(),
        "participants": []
    }
    
    # Start the process by getting token metadata
    promise = token.call("nft_metadata", token_id=token_id)
    
    # Pass the entire auction state to the next step
    promise = promise.then("prepare_auction", state=auction_state)
    
    return promise.value()

@callback
def prepare_auction(self, metadata, state):
    """Process token metadata and prepare the auction."""
    # Update state with token metadata
    state["metadata"] = {
        "title": metadata.get("title", "Unknown Item"),
        "description": metadata.get("description", ""),
        "media": metadata.get("media", None)
    }
    
    # Next step: get previous auction data
    auctions = Contract("auction.near")
    return auctions.call("get_previous_sales", token_id=state["token_id"]) \
                   .then("finalize_auction_setup", state=state)

@callback
def finalize_auction_setup(self, previous_sales, state):
    """Finalize auction setup with historical data."""
    # Add historical data to state
    state["previous_sales"] = previous_sales
    
    # Calculate suggested price based on history
    if previous_sales and len(previous_sales) > 0:
        avg_price = sum(sale["price"] for sale in previous_sales) / len(previous_sales)
        state["suggested_price"] = max(avg_price, state["min_bid"])
    else:
        state["suggested_price"] = state["min_bid"]
    
    # Now create the actual auction
    auctions = Contract("auction.near")
    return auctions.call("create_auction", 
                       token_id=state["token_id"],
                       min_bid=state["min_bid"],
                       suggested_price=state["suggested_price"],
                       metadata=state["metadata"]) \
                 .then("on_auction_created", state=state)

@callback
def on_auction_created(self, auction_data, state):
    """Handle the auction creation result."""
    # Final step - format and return complete auction info
    return {
        "auction_id": auction_data.get("auction_id"),
        "token_id": state["token_id"],
        "metadata": state["metadata"],
        "min_bid": state["min_bid"],
        "suggested_price": state["suggested_price"],
        "start_time": state["start_time"],
        "previous_sales_count": len(state["previous_sales"])
    }
```

## Error Handling Strategies

The `@callback` decorator provides basic error handling, but you can implement more sophisticated strategies.

### Example: Retry Pattern

```python
@call
def retry_critical_operation(self, operation_id):
    """Execute a critical operation with retry capability."""
    # Create a reference to the operation contract
    ops = Contract("operations.near")
    
    # Set up retry state
    retry_state = {
        "operation_id": operation_id,
        "attempts": 0,
        "max_attempts": 3,
        "last_error": None
    }
    
    # Start operation
    promise = ops.call("execute", operation_id=operation_id)
    promise = promise.then("handle_operation_result", state=retry_state)
    
    return promise.value()

@callback
def handle_operation_result(self, result, state):
    """Process operation result with retry logic."""
    # Check if operation succeeded
    if "error" not in result:
        return {
            "success": True,
            "operation_id": state["operation_id"],
            "attempts": state["attempts"] + 1,
            "result": result
        }
    
    # Update retry state
    state["attempts"] += 1
    state["last_error"] = result["error"]
    
    # Check if we should retry
    if state["attempts"] < state["max_attempts"]:
        # Log the retry
        self._log_retry(state["operation_id"], state["attempts"], result["error"])
        
        # Retry with exponential backoff (simulated by increasing gas)
        ops = Contract("operations.near")
        retry_gas = 5 * ONE_TGAS * (2 ** state["attempts"])
        
        return ops.gas(retry_gas).call("execute", operation_id=state["operation_id"]) \
                 .then("handle_operation_result", state=state)
    
    # Max retries exceeded
    return {
        "success": False,
        "operation_id": state["operation_id"],
        "attempts": state["attempts"],
        "error": f"Operation failed after {state['attempts']} attempts. Last error: {state['last_error']}"
    }

def _log_retry(self, operation_id, attempt, error):
    """Helper to log retry information."""
    from .log import Log
    Log.warning(f"Retrying operation {operation_id} (attempt {attempt}) after error: {error}")
```

## Gas Management

Proper gas management is crucial for complex cross-contract calls.

### Example: Adaptive Gas Allocation

```python
@call
def process_large_dataset(self, data_id):
    """Process a dataset with adaptive gas allocation."""
    # Get information about the dataset first
    data_service = Contract("data.near")
    
    # Use a small amount of gas for the initial info query
    promise = data_service.gas(2 * ONE_TGAS).call("get_dataset_info", id=data_id)
    
    # Chain with the processing step
    promise = promise.then("allocate_processing_gas", data_id=data_id)
    
    return promise.value()

@callback
def allocate_processing_gas(self, dataset_info, data_id):
    """Allocate appropriate gas based on dataset size."""
    # Calculate gas needed based on dataset size
    size = dataset_info.get("size", 0)
    
    if size <= 0:
        return {"error": "Invalid dataset size"}
    
    # Adaptive gas allocation formula (example)
    # Base gas (10 TGas) + 1 TGas per MB of data, up to a maximum
    gas_needed = min(
        10 * ONE_TGAS + (size / 1_000_000) * ONE_TGAS,  # 1 TGas per MB
        100 * ONE_TGAS  # Cap at 100 TGas
    )
    
    # Log the gas allocation
    from .log import Log
    Log.info(f"Allocating {gas_needed / ONE_TGAS} TGas for processing {size} bytes")
    
    # Proceed with processing using the calculated gas
    data_service = Contract("data.near")
    return data_service.gas(gas_needed).call("process_dataset", id=data_id) \
                      .then("on_processing_complete")

@callback
def on_processing_complete(self, processing_result):
    """Handle the result of the data processing."""
    return {
        "status": "complete",
        "result": processing_result
    }
```

## Timeouts and Fallbacks

NEAR doesn't have native timeout mechanisms for promises, but you can implement logical timeouts and fallbacks.

### Example: Data Provider with Fallback

```python
@call
def get_price_with_fallback(self, token_id):
    """Get token price with fallback providers if the primary fails."""
    # Try the primary price provider first
    primary = Contract("primary-oracle.near")
    
    promise = primary.call("get_price", token_id=token_id)
    
    # Chain with fallback logic
    promise = promise.then("handle_price_result", 
                           token_id=token_id, 
                           provider="primary",
                           fallbacks=["backup1-oracle.near", "backup2-oracle.near"])
    
    return promise.value()

@callback
def handle_price_result(self, price_data, token_id, provider, fallbacks):
    """Handle price result with fallback logic."""
    # Check if we got a valid result
    if price_data and "error" not in price_data and price_data.get("price", 0) > 0:
        return {
            "token_id": token_id,
            "price": price_data.get("price"),
            "provider": provider,
            "timestamp": near.block_timestamp()
        }
    
    # If we have fallbacks available, try the next one
    if fallbacks and len(fallbacks) > 0:
        next_provider = fallbacks[0]
        remaining_fallbacks = fallbacks[1:]
        
        # Log the fallback
        from .log import Log
        Log.warning(f"Price from {provider} failed for {token_id}, trying {next_provider}")
        
        # Call the next provider
        oracle = Contract(next_provider)
        return oracle.call("get_price", token_id=token_id) \
                   .then("handle_price_result",
                         token_id=token_id,
                         provider=next_provider,
                         fallbacks=remaining_fallbacks)
    
    # All providers failed
    return {
        "token_id": token_id,
        "error": f"Failed to get price from all providers: {[provider] + fallbacks}",
        "timestamp": near.block_timestamp()
    }
```

These advanced patterns demonstrate the flexibility and power of the Promise API for complex cross-contract interactions.
