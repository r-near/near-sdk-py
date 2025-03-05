# Sets: LookupSet and UnorderedSet

The Collections API provides two set implementations that offer different tradeoffs between functionality, gas efficiency, and storage usage:

1. **LookupSet**: A non-iterable set optimized for membership testing
2. **UnorderedSet**: An iterable set that provides full set functionality

## Comparison

| Feature | LookupSet | UnorderedSet |
|---------|-----------|--------------|
| Membership testing | ✅ O(1) | ✅ O(1) |
| Iteration support | ❌ No | ✅ Yes |
| Memory overhead | ✅ Low | ⚠️ Medium |
| Gas efficiency | ✅ Most efficient | ⚠️ Less efficient |
| Get all values | ❌ No | ✅ Yes |

## LookupSet

`LookupSet` is a set implementation optimized for membership testing. It does not support iteration, making it more gas-efficient for cases where you only need to check if a value exists.

### When to Use LookupSet

Use `LookupSet` when:
- You only need to check if a value exists
- You don't need to iterate through all values
- Gas efficiency is a priority
- You want the lowest storage overhead

### Import

```python
from near_sdk_py.collections import LookupSet
# OR
from near_sdk_py.collections.lookup_set import LookupSet
```

### Creation

```python
# Create a new lookup set with a unique storage prefix
my_set = LookupSet("prefix")

# With type hints (recommended)
from typing import Set
whitelisted_accounts: LookupSet[str] = LookupSet("whitelist")
```

### Basic Operations

```python
# Add values
my_set.add("value1")
my_set.add("value2")

# Check if value exists
has_value = "value1" in my_set  # True

# Remove a value
my_set.remove("value1")
# OR safely remove (no error if not exists)
my_set.discard("value2")

# Get length
length = len(my_set)  # 0

# Check if empty
is_empty = my_set.is_empty()  # True
```

### Storage Limitations

Since `LookupSet` doesn't track values, the `clear()` method will reset the length counter but won't actually remove entries from storage (creating "orphaned" storage entries). If you need to frequently clear the entire set, consider using `UnorderedSet` instead.

## UnorderedSet

`UnorderedSet` is a full-featured set implementation that supports both membership testing and iteration. It maintains an internal list of values to enable iteration.

### When to Use UnorderedSet

Use `UnorderedSet` when:
- You need to iterate through all values
- You need to get all values as a list
- You need to clear the set completely
- Storage efficiency is more important than gas efficiency

### Import

```python
from near_sdk_py.collections import UnorderedSet
# OR
from near_sdk_py.collections.unordered_set import UnorderedSet
```

### Creation

```python
# Create a new unordered set with a unique storage prefix
my_set = UnorderedSet("prefix")

# With type hints (recommended)
active_users: UnorderedSet[str] = UnorderedSet("active_users")
```

### Basic Operations

```python
# Add values (same as LookupSet)
my_set.add("value1")
my_set.add("value2")

# Check if value exists (same as LookupSet)
has_value = "value1" in my_set  # True

# Remove a value (same as LookupSet)
my_set.remove("value1")
# OR safely remove (no error if not exists)
my_set.discard("value2")

# Get length (same as LookupSet)
length = len(my_set)  # 0

# Check if empty (same as LookupSet)
is_empty = my_set.is_empty()  # True
```

### Iteration and Collection Operations

```python
# Add some data
my_set.add("a")
my_set.add("b")
my_set.add("c")

# Iterate through values
for value in my_set:
    print(value)  # Prints "a", "b", "c"

# Get all values as a list
all_values = my_set.values()  # ["a", "b", "c"]

# Clear all entries
my_set.clear()  # Properly removes all entries from storage
```

## Performance Characteristics

| Operation | LookupSet | UnorderedSet |
|-----------|-----------|--------------|
| Add (`set.add(value)`) | O(1) | O(1)* |
| Remove (`set.remove(value)`) | O(1) | O(n)** |
| Contains (`value in set`) | O(1) | O(1) |
| Length (`len(set)`) | O(1) | O(1) |
| Iteration | N/A | O(n) |
| Clear | O(1)*** | O(n) |

\* *Amortized O(1), but requires tracking the value in the values vector*  
\** *Requires finding the value in the values vector*  
\*** *Doesn't actually remove entries, only resets the counter*

## Storage Structure

Both set types store markers in the contract's storage using keys derived from the set's prefix and the serialized value:

- `LookupSet` with prefix `"myset"` and value `"user1"` would store a marker at `"myset:user1"`
- `UnorderedSet` does the same but also maintains an internal `Vector` to track all values

## IterableSet

For compatibility with the Rust SDK naming, the API also provides `IterableSet` as an alias for `UnorderedSet`:

```python
from near_sdk_py.collections import IterableSet

# IterableSet and UnorderedSet are the same type
my_set = IterableSet("prefix")
```

## Examples

### Access Control with LookupSet

```python
from near_sdk_py import call, view, Context
from near_sdk_py.collections import LookupSet

class AccessControl:
    def __init__(self):
        self.admin = Context.predecessor_account_id()
        self.authorized = LookupSet("authorized")
        
        # Add admin to authorized set
        self.authorized.add(self.admin)
    
    @call
    def add_authorized(self, account_id: str) -> bool:
        """Add an account to the authorized set"""
        assert Context.predecessor_account_id() == self.admin, "Only admin can add authorized accounts"
        self.authorized.add(account_id)
        return True
    
    @call
    def remove_authorized(self, account_id: str) -> bool:
        """Remove an account from the authorized set"""
        assert Context.predecessor_account_id() == self.admin, "Only admin can remove authorized accounts"
        if account_id == self.admin:
            return False  # Can't remove admin
            
        if account_id in self.authorized:
            self.authorized.remove(account_id)
            return True
        return False
    
    @view
    def is_authorized(self, account_id: str) -> bool:
        """Check if an account is authorized"""
        return account_id in self.authorized
```

### Token Whitelist with UnorderedSet

```python
from near_sdk_py import call, view, Context
from near_sdk_py.collections import UnorderedSet
from typing import List

class TokenWhitelist:
    def __init__(self):
        self.owner = Context.predecessor_account_id()
        self.whitelisted_tokens = UnorderedSet("whitelist")
    
    @call
    def add_token(self, token_id: str) -> bool:
        """Add a token to the whitelist"""
        assert Context.predecessor_account_id() == self.owner, "Only owner can modify whitelist"
        self.whitelisted_tokens.add(token_id)
        return True
    
    @call
    def remove_token(self, token_id: str) -> bool:
        """Remove a token from the whitelist"""
        assert Context.predecessor_account_id() == self.owner, "Only owner can modify whitelist"
        if token_id in self.whitelisted_tokens:
            self.whitelisted_tokens.remove(token_id)
            return True
        return False
    
    @view
    def is_whitelisted(self, token_id: str) -> bool:
        """Check if a token is whitelisted"""
        return token_id in self.whitelisted_tokens
    
    @view
    def get_all_tokens(self) -> List[str]:
        """Get all whitelisted tokens"""
        return self.whitelisted_tokens.values()
```

### Paginated Token List

```python
@view
def get_tokens_paginated(self, from_index: int = 0, limit: int = 10) -> List[str]:
    """Get a paginated list of whitelisted tokens"""
    all_tokens = self.whitelisted_tokens.values()
    
    # Apply pagination
    start = min(from_index, len(all_tokens))
    end = min(start + limit, len(all_tokens))
    
    return all_tokens[start:end]
```

### Tracking User Activity

```python
from near_sdk_py import call, view, Context
from near_sdk_py.collections import UnorderedSet, UnorderedMap
from typing import List

class ActivityTracker:
    def __init__(self):
        # Track all users
        self.all_users = UnorderedSet("users")
        
        # Track active users (accessed in last N days)
        self.active_users = UnorderedSet("active")
        
        # Track last activity time
        self.last_activity = UnorderedMap("last_activity")
    
    @call
    def record_activity(self, account_id: str) -> bool:
        """Record activity for an account"""
        # Add to all users set
        self.all_users.add(account_id)
        
        # Add to active users set
        self.active_users.add(account_id)
        
        # Update last activity time
        self.last_activity[account_id] = Context.block_timestamp()
        
        return True
    
    @call
    def cleanup_inactive(self, days_threshold: int) -> int:
        """Remove users inactive for more than N days from active set"""
        current_time = Context.block_timestamp()
        inactive_threshold = current_time - (days_threshold * 86400 * 10**9)  # Convert days to nanoseconds
        
        inactive_users = []
        for user in self.active_users:
            last_active = self.last_activity.get(user, 0)
            if last_active < inactive_threshold:
                inactive_users.append(user)
        
        # Remove inactive users from active set
        for user in inactive_users:
            self.active_users.remove(user)
        
        return len(inactive_users)
    
    @view
    def get_active_count(self) -> int:
        """Get count of active users"""
        return len(self.active_users)
    
    @view
    def get_total_count(self) -> int:
        """Get count of all users"""
        return len(self.all_users)
```

## Best Practices

1. **Choose the right set type**:
   - Use `LookupSet` when you only need membership testing and never need to iterate
   - Use `UnorderedSet` when you need to iterate or get all values

2. **Use type hints** for better IDE support and code clarity:
   ```python
   from near_sdk_py.collections import LookupSet, UnorderedSet
   
   admins: LookupSet[str] = LookupSet("admins")
   users: UnorderedSet[str] = UnorderedSet("users")
   ```

3. **Implement pagination** for methods that return potentially large sets:
   ```python
   @view
   def get_values(self, from_index: int = 0, limit: int = 50) -> list:
       all_values = self.my_set.values()
       return all_values[from_index:from_index + limit]
   ```

4. **Consider storage management** when choosing between set types:
   - If you frequently need to clear all entries, use `UnorderedSet`
   - If you only add/remove individual entries, `LookupSet` may be more efficient

5. **Handle existence checks safely**:
   ```python
   # Check before removing to avoid errors
   if value in my_set:
       my_set.remove(value)
   
   # Or use discard which doesn't raise an error
   my_set.discard(value)
   ```

6. **Be careful with complex values**:
   - Simple values (strings, numbers) are most efficient
   - Complex values will be serialized to JSON, which adds overhead
   - Consider using string representations for composite values:
     ```python
     # Instead of using a tuple as value: (user_id, token_id)
     value = f"{user_id}:{token_id}"
     my_set.add(value)
     ```

## Common Patterns

### Intersection and Union

Since sets don't directly support set operations like union and intersection, you can implement them manually:

```python
@view
def get_intersection(self, set_a_prefix: str, set_b_prefix: str) -> List[str]:
    """Get the intersection of two sets"""
    set_a = UnorderedSet(set_a_prefix)
    set_b = UnorderedSet(set_b_prefix)
    
    # For better performance, iterate over the smaller set
    if len(set_a) > len(set_b):
        set_a, set_b = set_b, set_a
    
    # Find common elements
    result = []
    for value in set_a:
        if value in set_b:
            result.append(value)
    
    return result

@view
def get_union(self, set_a_prefix: str, set_b_prefix: str) -> List[str]:
    """Get the union of two sets"""
    set_a = UnorderedSet(set_a_prefix)
    set_b = UnorderedSet(set_b_prefix)
    
    # Add all values from set_a
    result = set_a.values()
    
    # Add values from set_b that aren't in set_a
    for value in set_b:
        if value not in set_a:
            result.append(value)
    
    return result
```

### Role-Based Access Control

Sets are perfect for implementing role-based access control:

```python
class RBAC:
    def __init__(self):
        # Create a set for each role
        self.admins = UnorderedSet("admins")
        self.moderators = UnorderedSet("moderators")
        self.users = UnorderedSet("users")
    
    def has_role(self, account_id: str, role: str) -> bool:
        """Check if an account has a specific role"""
        if role == "admin":
            return account_id in self.admins
        elif role == "moderator":
            return account_id in self.moderators
        elif role == "user":
            return account_id in self.users
        return False
    
    def require_role(self, account_id: str, role: str) -> None:
        """Assert that an account has a specific role"""
        assert self.has_role(account_id, role), f"Account {account_id} does not have {role} role"
```

### LookupSet with Tracked Values

If you need both the efficiency of `LookupSet` and the ability to iterate or clear all entries:

```python
class TrackedLookupSet:
    def __init__(self, prefix):
        self.data = LookupSet(f"{prefix}:data")
        self.values = Vector(f"{prefix}:values")
    
    def add(self, value):
        exists = value in self.data
        self.data.add(value)
        if not exists:
            self.values.append(value)
    
    def remove(self, value):
        if value in self.data:
            self.data.remove(value)
            # Find and remove from values
            for i, v in enumerate(self.values):
                if v == value:
                    self.values.swap_remove(i)
                    break
    
    def __contains__(self, value):
        return value in self.data
    
    def values(self):
        return list(self.values)
    
    def clear(self):
        for value in self.values:
            self.data.remove(value)
        self.values.clear()
```

## Migration Considerations

When upgrading your contract, be aware that:

1. `LookupSet` and `UnorderedSet` use different storage structures
2. Converting between them requires migrating the data
3. Always use the same prefix when upgrading to maintain data integrity

Migration example:

```python
@call
def migrate_to_unordered_set(self):
    """Migrate from LookupSet to UnorderedSet"""
    old_set = LookupSet("my_values")
    new_set = UnorderedSet("my_values_v2")
    
    # We need to know the values in advance for LookupSet
    # This would come from another source or be hardcoded
    known_values = ["value1", "value2", "value3", ...]
    
    for value in known_values:
        if value in old_set:
            new_set.add(value)
    
    return len(new_set)
```