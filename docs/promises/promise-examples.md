# Promise API Examples

This document provides practical examples of common use cases for the Promise API.

## Table of Contents

- [Token Operations](#token-operations)
- [DeFi Applications](#defi-applications)
- [NFT Marketplace Integration](#nft-marketplace-integration)
- [Oracle Integrations](#oracle-integrations)
- [Storage Management](#storage-management)

## Token Operations

### Get Token Metadata

```python
@call
def get_token_info(self, token_id):
    """Get token metadata from a fungible token contract."""
    token = Contract(f"token.{token_id}.near")
    
    promise = token.call("ft_metadata").then("on_metadata_received")
    
    return promise.value()

@callback
def on_metadata_received(self, metadata):
    """Process token metadata."""
    return {
        "name": metadata.get("name", "Unknown Token"),
        "symbol": metadata.get("symbol", "???"),
        "decimals": metadata.get("decimals", 0),
        "icon": metadata.get("icon", None) is not None
    }
```

### Transfer Tokens with Confirmation

```python
@call
def transfer_with_confirmation(self, token_id, receiver_id, amount):
    """Transfer tokens and confirm the receiver's balance after."""
    token = Contract(f"token.{token_id}.near")
    
    # First check our own balance
    promise = token.call("ft_balance_of", account_id=near.current_account_id())
    
    # Chain the transfer and confirmation steps
    promise = promise.then("process_transfer", 
                          token_id=token_id,
                          receiver_id=receiver_id,
                          amount=amount)
    
    return promise.value()

@callback
def process_transfer(self, balance_data, token_id, receiver_id, amount):
    """Verify balance and process the transfer."""
    # Check if we have enough balance
    balance = int(balance_data.get("balance", "0"))
    amount_int = int(amount)
    
    if balance < amount_int:
        return {
            "success": False,
            "error": "Insufficient balance",
            "balance": balance,
            "amount": amount_int
        }
    
    # Proceed with the transfer
    token = Contract(f"token.{token_id}.near")
    
    # Call ft_transfer and check receiver's balance after
    return token.call("ft_transfer", 
                    receiver_id=receiver_id,
                    amount=amount,
                    memo="Transfer with confirmation") \
               .then("verify_transfer", 
                    token_id=token_id,
                    receiver_id=receiver_id,
                    amount=amount_int)

@callback
def verify_transfer(self, transfer_result, token_id, receiver_id, amount):
    """Verify the transfer by checking receiver's balance."""
    token = Contract(f"token.{token_id}.near")
    
    # Check receiver's balance after transfer
    return token.call("ft_balance_of", account_id=receiver_id) \
                .then("finalize_transfer", 
                      receiver_id=receiver_id, 
                      amount=amount)

@callback
def finalize_transfer(self, balance_data, receiver_id, amount):
    """Finalize the transfer with balance confirmation."""
    # Get the receiver's balance
    balance = int(balance_data.get("balance", "0"))
    
    return {
        "success": True,
        "receiver_id": receiver_id,
        "confirmed_balance": balance,
        "transfer_amount": amount,
        "timestamp": near.block_timestamp()
    }
```

## DeFi Applications

### Automated Liquidity Provision

```python
@call
def provide_liquidity(self, token_a, token_b, amount_a):
    """Provide liquidity to a DEX with optimal amounts."""
    # First get the current pool exchange rate
    dex = Contract("dex.near")
    
    promise = dex.call("get_pool_info", 
                     token_a=token_a,
                     token_b=token_b)
    
    # Chain with the calculation step
    promise = promise.then("calculate_optimal_amounts", 
                          token_a=token_a,
                          token_b=token_b,
                          amount_a=amount_a)
    
    return promise.value()

@callback
def calculate_optimal_amounts(self, pool_info, token_a, token_b, amount_a):
    """Calculate the optimal amount of token B to provide based on the pool ratio."""
    reserves_a = int(pool_info.get("reserves_a", "0"))
    reserves_b = int(pool_info.get("reserves_b", "0"))
    amount_a_int = int(amount_a)
    
    # Cannot calculate if pool is empty
    if reserves_a == 0 or reserves_b == 0:
        return {"error": "Pool has no liquidity yet, cannot calculate optimal amounts"}
    
    # Calculate optimal amount of token B based on current pool ratio
    # formula: amount_b = amount_a * (reserves_b / reserves_a)
    amount_b = (amount_a_int * reserves_b) // reserves_a
    
    # Get our balance of token B to ensure we have enough
    token_b_contract = Contract(token_b)
    return token_b_contract.call("ft_balance_of", 
                               account_id=near.current_account_id()) \
                          .then("execute_liquidity_provision", 
                               token_a=token_a,
                               token_b=token_b,
                               amount_a=amount_a_int,
                               amount_b=amount_b)

@callback
def execute_liquidity_provision(self, balance_data, token_a, token_b, amount_a, amount_b):
    """Execute the liquidity provision if we have enough of token B."""
    balance_b = int(balance_data.get("balance", "0"))
    
    if balance_b < amount_b:
        return {
            "success": False,
            "error": "Insufficient balance of token B",
            "required": amount_b,
            "available": balance_b
        }
    
    # Approve the DEX to use our tokens
    token_a_contract = Contract(token_a)
    
    # Approve token A, then token B, then add liquidity
    return token_a_contract.call("ft_approve", 
                               spender="dex.near", 
                               amount=str(amount_a)) \
                          .then("approve_token_b", 
                               token_b=token_b,
                               amount_b=amount_b,
                               token_a=token_a,
                               amount_a=amount_a)

@callback
def approve_token_b(self, approve_result, token_b, amount_b, token_a, amount_a):
    """Approve token B after approving token A."""
    token_b_contract = Contract(token_b)
    
    return token_b_contract.call("ft_approve", 
                               spender="dex.near", 
                               amount=str(amount_b)) \
                          .then("add_liquidity", 
                               token_a=token_a,
                               token_b=token_b,
                               amount_a=amount_a,
                               amount_b=amount_b)

@callback
def add_liquidity(self, approve_result, token_a, token_b, amount_a, amount_b):
    """Add liquidity to the DEX."""
    dex = Contract("dex.near")
    
    return dex.call("add_liquidity", 
                  token_a=token_a,
                  token_b=token_b,
                  amount_a=str(amount_a),
                  amount_b=str(amount_b)) \
                .then("on_liquidity_added")

@callback
def on_liquidity_added(self, result):
    """Process the result of adding liquidity."""
    return {
        "success": True,
        "lp_tokens_received": result.get("lp_tokens", "0"),
        "timestamp": near.block_timestamp()
    }
```

## NFT Marketplace Integration

### List NFT for Sale

```python
@call
def list_nft_for_sale(self, nft_contract_id, token_id, price):
    """List an NFT for sale on a marketplace with verification."""
    # First verify ownership
    nft = Contract(nft_contract_id)
    
    promise = nft.call("nft_token", token_id=token_id)
    
    # Chain with ownership check and listing
    promise = promise.then("verify_ownership_and_list", 
                          nft_contract_id=nft_contract_id,
                          token_id=token_id,
                          price=price)
    
    return promise.value()

@callback
def verify_ownership_and_list(self, token_data, nft_contract_id, token_id, price):
    """Verify NFT ownership and proceed with listing."""
    # Check if we own the token
    if not token_data:
        return {"error": "Token not found"}
        
    owner_id = token_data.get("owner_id")
    current_account = near.current_account_id()
    
    if owner_id != current_account:
        return {
            "success": False,
            "error": "You don't own this NFT",
            "owner_id": owner_id,
            "your_account": current_account
        }
    
    # Approve the marketplace to transfer the NFT
    nft = Contract(nft_contract_id)
    
    market_id = "marketplace.near"
    
    return nft.call("nft_approve", 
                   token_id=token_id,
                   account_id=market_id,
                   msg=json.dumps({"price": price})) \
                  .then("on_nft_approved", 
                       nft_contract_id=nft_contract_id,
                       token_id=token_id,
                       price=price,
                       market_id=market_id)

@callback
def on_nft_approved(self, approve_result, nft_contract_id, token_id, price, market_id):
    """Create the actual listing after approval."""
    marketplace = Contract(market_id)
    
    return marketplace.call("list_token", 
                          nft_contract_id=nft_contract_id,
                          token_id=token_id,
                          price=price) \
                     .then("on_nft_listed", 
                          nft_contract_id=nft_contract_id,
                          token_id=token_id,
                          price=price)

@callback
def on_nft_listed(self, listing_result, nft_contract_id, token_id, price):
    """Process the listing result."""
    return {
        "success": True,
        "nft_contract_id": nft_contract_id,
        "token_id": token_id,
        "price": price,
        "listing_id": listing_result.get("listing_id"),
        "market_url": f"https://marketplace.near/token/{nft_contract_id}/{token_id}"
    }
```

## Oracle Integrations

### Get Validated Price Feed

```python
@call
def get_validated_price(self, asset_id):
    """Get a validated price from multiple oracle sources."""
    # Get prices from three different oracle providers
    oracle1 = Contract("oracle1.near")
    oracle2 = Contract("oracle2.near")
    oracle3 = Contract("oracle3.near")
    
    # Create promises for each oracle call
    promise1 = oracle1.call("get_price", asset_id=asset_id)
    promise2 = oracle2.call("get_price", asset_id=asset_id)
    promise3 = oracle3.call("get_price", asset_id=asset_id)
    
    # Join all promises and process the results together
    combined = promise1.join([promise2, promise3], "aggregate_prices", asset_id=asset_id)
    
    return combined.value()

@callback
def aggregate_prices(self, price_results, asset_id):
    """Aggregate and validate prices from multiple sources."""
    valid_prices = []
    timestamps = []
    
    # Process each price source
    for i, result in enumerate(price_results):
        source_name = f"oracle{i+1}"
        
        if result and "error" not in result:
            price = float(result.get("price", 0))
            timestamp = int(result.get("timestamp", 0))
            
            if price > 0:
                valid_prices.append(price)
                timestamps.append(timestamp)
                
    # Require at least 2 valid price sources
    if len(valid_prices) < 2:
        return {
            "success": False,
            "error": "Could not get enough valid price feeds",
            "valid_feeds": len(valid_prices),
            "required": 2
        }
    
    # Calculate median price (more robust against outliers)
    median_price = sorted(valid_prices)[len(valid_prices) // 2]
    
    # Find max deviation from median
    max_deviation = 0
    for price in valid_prices:
        deviation = abs(price - median_price) / median_price * 100
        max_deviation = max(max_deviation, deviation)
    
    # Use most recent timestamp
    latest_timestamp = max(timestamps) if timestamps else near.block_timestamp()
    
    return {
        "success": True,
        "asset_id": asset_id,
        "price": median_price,
        "timestamp": latest_timestamp,
        "sources": len(valid_prices),
        "max_deviation_percent": max_deviation,
        "is_reliable": max_deviation < 5.0  # Consider reliable if less than 5% deviation
    }
```

## Storage Management

### Batch Storage Operations

```python
@call
def batch_store_data(self, data_items):
    """Store multiple data items in parallel."""
    if not data_items or len(data_items) == 0:
        return {"error": "No data items provided"}
    
    # Get storage size info first
    storage = Contract("storage.near")
    
    promise = storage.call("get_storage_usage").then(
        "process_storage_requirements", 
        data_items=data_items
    )
    
    return promise.value()

@callback
def process_storage_requirements(self, storage_info, data_items):
    """Check if we have enough storage and proceed with batch operations."""
    available_storage = int(storage_info.get("available_bytes", "0"))
    
    # Estimate required storage (simple estimation)
    required_storage = sum(len(json.dumps(item)) for item in data_items)
    
    if required_storage > available_storage:
        # Not enough storage - need to pay for more
        storage = Contract("storage.near")
        
        # Calculate required deposit
        price_per_byte = float(storage_info.get("price_per_byte", "0"))
        required_deposit = math.ceil((required_storage - available_storage) * price_per_byte)
        
        # Pay for storage first, then continue
        return storage.deposit(required_deposit).call("buy_storage", bytes=required_storage) \
                     .then("execute_batch_store", data_items=data_items)
    
    # We have enough storage - proceed directly
    return self._create_store_promises(data_items)

@callback
def execute_batch_store(self, storage_result, data_items):
    """Execute the batch store operations after ensuring storage."""
    return self._create_store_promises(data_items)

def _create_store_promises(self, data_items):
    """Helper to create parallel store promises."""
    storage = Contract("storage.near")
    promises = []
    
    # Create a promise for each data item
    for item in data_items:
        promise = storage.call("store_data", 
                             key=item.get("key"),
                             value=item.get("value"),
                             metadata=item.get("metadata", {}))
        promises.append(promise)
    
    # Join all promises
    combined = promises[0].join(promises[1:], "on_batch_store_complete")
    
    return combined.value()

@callback
def on_batch_store_complete(self, results):
    """Process the results of the batch store operations."""
    succeeded = 0
    failed = 0
    
    # Count successes and failures
    for result in results:
        if result and "error" not in result:
            succeeded += 1
        else:
            failed += 1
    
    return {
        "success": failed == 0,
        "total": len(results),
        "succeeded": succeeded,
        "failed": failed,
        "results": results
    }
```

These examples demonstrate how the Promise API can be applied to real-world scenarios, making complex cross-contract interactions more readable and maintainable.
