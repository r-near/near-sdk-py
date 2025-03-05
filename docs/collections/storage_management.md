# Storage Management Guide

Efficient storage management is essential when developing NEAR smart contracts. This guide explains how the Collections API interacts with blockchain storage and provides best practices for optimizing storage usage.

## Understanding NEAR Storage

On NEAR, contract storage works as follows:

1. **Storage Staking**: Contracts must lock NEAR tokens proportional to the amount of data they store (approximately 1 NEAR per 100KB of data).

2. **Storage Refunds**: When data is removed from storage, the locked NEAR tokens become available again.

3. **Per-Key Storage**: Data is stored as key-value pairs. Each key and its associated value count toward storage usage.

4. **Serialization**: All data is serialized before storage. Complex data structures like dictionaries and objects are typically serialized to JSON.

## How Collections Use Storage

The Collections API manages storage with the following strategies:

1. **Prefix-Based Keys**: Each collection uses a unique prefix to avoid storage collisions.

2. **Lazy Loading**: Data is only loaded from storage when accessed, not when the collection is created.

3. **Serialization**: The `CollectionStorageAdapter` handles serialization and deserialization automatically.

4. **Metadata**: Collections store metadata about themselves (like length) for efficient operations.

## Storage Layout by Collection Type

### Vector

- **Metadata**: Stored at `{prefix}:meta`
- **Elements**: Stored at `{prefix}:0`, `{prefix}:1`, `{prefix}:2`, etc.

### LookupMap and LookupSet

- **Metadata**: Stored at `{prefix}:meta`
- **Entries**: Stored at `{prefix}:{serialized_key}`

### UnorderedMap and UnorderedSet

- **Metadata**: Stored at `{prefix}:meta`
- **Entries**: Stored at `{prefix}:{serialized_key}`
- **Keys/Values**: Additional Vector at `{prefix}:keys` or `{prefix}:values`

### TreeMap

- **Metadata**: Stored at `{prefix}:meta`
- **Entries**: Stored at `{prefix}:{serialized_key}`
- **Ordered Keys**: Additional Vector at `{prefix}:keys`

## Storage Efficiency by Collection Type

From most to least storage-efficient:

1. **LookupMap/LookupSet**: Minimal overhead, just the stored values and metadata
2. **Vector**: Slightly more overhead due to indexed keys
3. **UnorderedMap/UnorderedSet**: Additional overhead for tracking keys/values
4. **TreeMap**: Most overhead due to key ordering and tracking

## Storage Pitfalls and Solutions

### Orphaned Storage Entries

**Problem**: Some operations can leave "orphaned" storage entries that still consume space.

**Common Causes**:
- Using `clear()` on `LookupMap` or `LookupSet` (resets length but doesn't remove entries)
- Overwriting collections without proper cleanup

**Solutions**:
1. Use iterable collections when you need to clear everything
2. Implement versioned prefixes for complete storage replacement
3. Explicitly track and remove known keys

```python
# Option 1: Use UnorderedMap instead
my_map = UnorderedMap("prefix")
my_map.clear()  # Properly removes all entries

# Option 2: Versioned prefixes
def get_current_prefix(self):
    version = self.storage.get("version", 0)
    return f"data_v{version}"

def clear_data(self):
    # Increment version instead of clearing entries
    version = self.storage.get("version", 0)
    self.storage.set("version", version + 1)
    # Creates a new collection with a new prefix
    self.data = LookupMap(self.get_current_prefix())
```

### Excessive Storage Growth

**Problem**: Collections can grow too large, increasing storage costs and potentially hitting gas limits.

**Solutions**:
1. Implement data expiration and cleanup
2. Use pagination for data access
3. Split large collections into smaller ones
4. Implement storage limits per user

```python
# Implement data expiration
@call
def cleanup_old_data(self, days_to_keep: int) -> int:
    current_time = Context.block_timestamp()
    expiration = current_time - (days_to_keep * 86400 * 10**9)  # Convert days to nanoseconds
    
    expired_keys = []
    for key in self.data_timestamps:
        if self.data_timestamps[key] < expiration:
            expired_keys.append(key)
    
    for key in expired_keys:
        del self.data_timestamps[key]
        del self.data[key]
    
    return len(expired_keys)
```

### Storage Refunds

**Problem**: Not removing data when it's no longer needed wastes locked NEAR tokens.

**Solutions**:
1. Explicitly clear collections when done with them
2. Remove individual entries when they're no longer needed
3. Implement cleanup routines that run periodically

```python
# Claim a storage refund by clearing temporary data
@call
def finalize_operation(self):
    # Process the temporary data
    result = self._process_temp_data()
    
    # Clear the temporary data to get a storage refund
    self.temp_data.clear()
    
    return result
```

## Storage Monitoring

Tracking storage usage can help you optimize your contract:

```python
@view
def get_storage_usage(self) -> dict:
    """Get storage usage statistics for the contract"""
    return {
        "total_storage_usage": near.storage_usage(),
        "collection_stats": {
            "users": len(self.users),
            "tokens": len(self.tokens),
            "balances": len(self.balances)
        }
    }
```

## Storage Quota Management

For contracts that allow users to store data, consider implementing storage quotas:

```python
@call
def store_data(self, key: str, value: str):
    """Store data with per-user storage limits"""
    caller = Context.predecessor_account_id()
    
    # Check if user has storage allocation
    user_storage = self.storage_used.get(caller, 0)
    storage_limit = self.storage_limits.get(caller, DEFAULT_STORAGE_LIMIT)
    
    # Calculate new storage requirements
    new_key_size = len(key.encode('utf-8'))
    new_value_size = len(value.encode('utf-8'))
    new_storage = user_storage + new_key_size + new_value_size
    
    assert new_storage <= storage_limit, f"Storage limit exceeded: {new_storage} > {storage_limit}"
    
    # Store the data
    self.user_data.set(f"{caller}:{key}", value)
    
    # Update user's storage usage
    self.storage_used[caller] = new_storage
```

## Best Practices

1. **Choose the Right Collection Type**:
   - For temporary data that will be cleared, use iterable collections
   - For permanent data with rare deletions, non-iterable collections are more efficient

2. **Explicit Cleanup**:
   - Always call `clear()` on collections you no longer need
   - Implement cleanup routines for long-running contracts

3. **Efficient Key Design**:
   - Keep keys as short as possible
   - Use simple types (strings, numbers) rather than complex objects

4. **Storage Limits**:
   - Implement per-user storage limits for contracts where users can store data
   - Consider charging users for storage (e.g., requiring storage deposits)

5. **Versioning Strategy**:
   - For major storage changes, use versioned prefixes rather than migrating data
   - Include a contract version in prefixes for easy upgradeability

6. **Pagination**:
   - Always implement pagination for methods that return data from collections
   - Keep page sizes reasonable (20-50 items per page)

7. **Monitor Storage Growth**:
   - Implement methods to track storage usage
   - Set up alerts or automatic cleanup for excessive growth

## Conclusion

Proper storage management is crucial for building efficient and cost-effective NEAR contracts. By understanding how the Collections API interacts with NEAR's storage system, you can optimize your contract's storage usage and avoid common pitfalls.