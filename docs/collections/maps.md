# Maps: LookupMap and UnorderedMap

The Collections API provides two map implementations that offer different tradeoffs between functionality, gas efficiency, and storage usage:

1. **LookupMap**: A non-iterable key-value store optimized for lookups
2. **UnorderedMap**: An iterable key-value store that provides full map functionality

## Comparison

| Feature | LookupMap | UnorderedMap |
|---------|-----------|--------------|
| Key-value lookup | ✅ O(1) | ✅ O(1) |
| Iteration support | ❌ No | ✅ Yes |
| Memory overhead | ✅ Low | ⚠️ Medium |
| Gas efficiency | ✅ Most efficient | ⚠️ Less efficient |
| Get all keys | ❌ No | ✅ Yes |
| Get all values | ❌ No | ✅ Yes |

## LookupMap

`LookupMap` is a key-value store optimized for lookups. It does not support iteration, making it more gas-efficient for cases where you only need to access values by their keys.

### When to Use LookupMap

Use `LookupMap` when:
- You only need to access values by their keys
- You don't need to iterate through all entries
- Gas efficiency is a priority
- You want the lowest storage overhead

### Import

```python
from near_sdk_py.collections import LookupMap
# OR
from near_sdk_py.collections.lookup_map import LookupMap
```

### Creation

```python
# Create a new lookup map with a unique storage prefix
my_map = LookupMap("prefix")

# With type hints (recommended)
from typing import Dict
user_balances: LookupMap[str, int] = LookupMap("balances")
```

### Basic Operations

```python
# Set values
my_map["key1"] = "value1"
my_map["key2"] = 42

# Alternative syntax
my_map.set("key3", [1, 2, 3])

# Get values
value1 = my_map["key1"]  # "value1"

# Get with default (won't raise KeyError if key doesn't exist)
value4 = my_map.get("key4", "default")  # "default"

# Check if key exists
has_key = "key1" in my_map  # True

# Remove a key
del my_map["key1"]
# OR
removed_value = my_map.remove("key2")  # 42

# Get length
length = len(my_map)  # 1

# Check if empty
is_empty = my_map.is_empty()  # False
```

### Storage Limitations

Since `LookupMap` doesn't track keys, the `clear()` method will reset the length counter but won't actually remove entries from storage (creating "orphaned" storage entries). If you need to frequently clear the entire map, consider using `UnorderedMap` instead.

## UnorderedMap

`UnorderedMap` is a full-featured map implementation that supports both key-value lookups and iteration. It maintains an internal list of keys to enable iteration.

### When to Use UnorderedMap

Use `UnorderedMap` when:
- You need to iterate through keys, values, or entries
- You need to get all keys or values
- You need to clear the map completely
- Storage efficiency is more important than gas efficiency

### Import

```python
from near_sdk_py.collections import UnorderedMap
# OR
from near_sdk_py.collections.unordered_map import UnorderedMap
```

### Creation

```python
# Create a new unordered map with a unique storage prefix
my_map = UnorderedMap("prefix")

# With type hints (recommended)
user_data: UnorderedMap[str, Dict] = UnorderedMap("user_data")
```

### Basic Operations

```python
# Set values (same as LookupMap)
my_map["key1"] = "value1"
my_map["key2"] = 42

# Get values (same as LookupMap)
value1 = my_map["key1"]  # "value1"
value3 = my_map.get("key3", "default")  # "default"

# Check if key exists (same as LookupMap)
has_key = "key1" in my_map  # True

# Remove a key (same as LookupMap)
del my_map["key1"]
# OR
removed_value = my_map.remove("key2")  # 42

# Get length (same as LookupMap)
length = len(my_map)  # 0

# Check if empty (same as LookupMap)
is_empty = my_map.is_empty()  # True
```

### Iteration and Collection Operations

```python
# Add some data
my_map["a"] = 1
my_map["b"] = 2
my_map["c"] = 3

# Iterate through keys
for key in my_map:
    print(key)  # Prints "a", "b", "c"

# Get all keys as a list
all_keys = my_map.keys()  # ["a", "b", "c"]

# Get all values as a list
all_values = my_map.values()  # [1, 2, 3]

# Get all key-value pairs as a list of tuples
all_items = my_map.items()  # [("a", 1), ("b", 2), ("c", 3)]

# Clear all entries
my_map.clear()  # Properly removes all entries from storage
```

## Performance Characteristics

| Operation | LookupMap | UnorderedMap |
|-----------|-----------|--------------|
| Get (`map[key]`) | O(1) | O(1) |
| Set (`map[key] = value`) | O(1) | O(1)* |
| Delete (`del map[key]`) | O(1) | O(n)** |
| Contains (`key in map`) | O(1) | O(1) |
| Length (`len(map)`) | O(1) | O(1) |
| Iteration | N/A | O(n) |
| Clear | O(1)*** | O(n) |

\* *Amortized O(1), but requires tracking the key in the keys vector*  
\** *Requires finding the key in the keys vector*  
\*** *Doesn't actually remove entries, only resets the counter*

## Storage Structure

Both map types store values in the contract's storage using keys derived from the map's prefix and the serialized key:

- `LookupMap` with prefix `"mymap"` and key `"user1"` would store at `"mymap:user1"`
- `UnorderedMap` does the same but also maintains an internal `Vector` to track all keys

## IterableMap

For compatibility with the Rust SDK naming, the API also provides `IterableMap` as an alias for `UnorderedMap`:

```python
from near_sdk_py.collections import IterableMap

# IterableMap and UnorderedMap are the same type
my_map = IterableMap("prefix")
```

## Examples

### User Profiles with LookupMap

```python
from near_sdk_py import call, view
from near_sdk_py.collections import LookupMap
from typing import Dict, Optional

class ProfileContract:
    def __init__(self):
        self.profiles = LookupMap("profiles")
    
    @call
    def set_profile(self, profile_data: Dict) -> bool:
        caller = Context.predecessor_account_id()
        self.profiles[caller] = profile_data
        return True
    
    @view
    def get_profile(self, account_id: str) -> Optional[Dict]:
        return self.profiles.get(account_id)
```

### Token Balances with UnorderedMap

```python
from near_sdk_py import call, view
from near_sdk_py.collections import UnorderedMap
from typing import List, Dict

class TokenContract:
    def __init__(self):
        self.balances = UnorderedMap("balances")
        self.total_supply = 0
    
    @call
    def transfer(self, to: str, amount: int) -> bool:
        sender = Context.predecessor_account_id()
        sender_balance = self.balances.get(sender, 0)
        
        assert sender_balance >= amount, "Insufficient balance"
        
        # Update sender balance
        self.balances[sender] = sender_balance - amount
        
        # Update receiver balance
        receiver_balance = self.balances.get(to, 0)
        self.balances[to] = receiver_balance + amount
        
        return True
    
    @view
    def get_balance(self, account_id: str) -> int:
        return self.balances.get(account_id, 0)
    
    @view
    def get_accounts_with_balance(self) -> List[Dict]:
        """Returns all accounts that have a non-zero balance"""
        result = []
        for account_id in self.balances:
            balance = self.balances[account_id]
            if balance > 0:
                result.append({"account_id": account_id, "balance": balance})
        return result
```

### Pagination with UnorderedMap

```python
@view
def get_accounts_paginated(self, from_index: int = 0, limit: int = 50) -> List[Dict]:
    """Returns accounts in paginated form"""
    accounts = self.balances.keys()
    
    # Apply pagination
    start = min(from_index, len(accounts))
    end = min(start + limit, len(accounts))
    
    # Get the page of account IDs
    page_account_ids = accounts[start:end]
    
    # Fetch data for each account ID
    result = []
    for account_id in page_account_ids:
        balance = self.balances[account_id]
        result.append({"account_id": account_id, "balance": balance})
    
    return result
```

## Best Practices

1. **Choose the right map type**:
   - Use `LookupMap` when you only need key-based access and never need to iterate
   - Use `UnorderedMap` when you need to iterate or get all keys/values

2. **Use type hints** for better IDE support and code clarity:
   ```python
   from near_sdk_py.collections import LookupMap, UnorderedMap
   
   balances: LookupMap[str, int] = LookupMap("balances")
   metadata: UnorderedMap[str, Dict] = UnorderedMap("metadata")
   ```

3. **Implement pagination** for methods that return potentially large lists:
   ```python
   @view
   def get_keys(self, from_index: int = 0, limit: int = 50) -> list:
       all_keys = self.my_map.keys()
       return all_keys[from_index:from_index + limit]
   ```

4. **Consider storage management** when choosing between map types:
   - If you frequently need to clear all entries, use `UnorderedMap`
   - If you only add/update/remove individual entries, `LookupMap` may be more efficient

5. **Handle key existence safely**:
   ```python
   # Safer than direct access which might raise KeyError
   value = my_map.get(key, default_value)
   
   # For conditional logic
   if key in my_map:
       # Do something with my_map[key]
   ```

6. **Be careful with complex keys**:
   - Simple keys (strings, numbers) are most efficient
   - Complex keys will be serialized to JSON, which adds overhead
   - Consider using string concatenation for composite keys:
     ```python
     # Instead of using a tuple as key: (user_id, token_id)
     key = f"{user_id}:{token_id}"
     my_map[key] = value
     ```

7. **For large maps, consider implementing cleanup routines**:
   ```python
   @call
   def cleanup_inactive_users(self, days_inactive: int) -> int:
       threshold = Context.block_timestamp() - (days_inactive * 86400 * 10^9)
       removed_count = 0
       
       # We can only do this with UnorderedMap
       inactive_users = []
       for user_id in self.last_active:
           if self.last_active[user_id] < threshold:
               inactive_users.append(user_id)
       
       # Remove inactive users
       for user_id in inactive_users:
           del self.last_active[user_id]
           del self.user_data[user_id]
           removed_count += 1
       
       return removed_count
   ```

## Common Patterns

### Composite Keys

When you need to index data by multiple fields, you can create composite keys:

```python
# Store token approvals by combining token_id and approved_account_id
approval_key = f"{token_id}:{approved_account_id}"
self.approvals[approval_key] = approval_id

# Retrieve later
approval_id = self.approvals.get(f"{token_id}:{approved_account_id}")
```

### Multi-Index Data

When you need to access the same data through multiple indices, store references:

```python
# Store token by ID
self.tokens[token_id] = token_data

# Also index by owner for quick lookup
owner_tokens = self.tokens_by_owner.get(owner_id, [])
owner_tokens.append(token_id)
self.tokens_by_owner[owner_id] = owner_tokens
```

### LookupMap with Tracked Keys

If you need both the efficiency of `LookupMap` and the ability to iterate or clear all entries:

```python
class TrackedLookupMap:
    def __init__(self, prefix):
        self.data = LookupMap(f"{prefix}:data")
        self.keys = Vector(f"{prefix}:keys")
    
    def __setitem__(self, key, value):
        exists = key in self.data
        self.data[key] = value
        if not exists:
            self.keys.append(key)
    
    def __getitem__(self, key):
        return self.data[key]
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def keys(self):
        return list(self.keys)
    
    def clear(self):
        for key in self.keys:
            del self.data[key]
        self.keys.clear()
```

## Migration Considerations

When upgrading your contract, be aware that:

1. `LookupMap` and `UnorderedMap` use different storage structures
2. Converting between them requires migrating the data
3. Always use the same prefix when upgrading to maintain data integrity

Migration example:

```python
@call
def migrate_to_unordered_map(self):
    """Migrate from LookupMap to UnorderedMap"""
    old_map = LookupMap("my_data")
    new_map = UnorderedMap("my_data_v2")
    
    # We need to know the keys in advance for LookupMap
    # This would come from another source or be hardcoded
    known_keys = ["key1", "key2", "key3", ...]
    
    for key in known_keys:
        if key in old_map:
            new_map[key] = old_map[key]
    
    return len(new_map)
```