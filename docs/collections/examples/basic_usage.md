# Basic Usage Examples

This guide provides practical examples for working with the Collections API. We'll cover basic operations for each collection type and show how they can be used together.

## Vector Examples

### Creating and Adding Elements

```python
from near_sdk_py import view, call
from near_sdk_py.collections import Vector

# In your contract class
def __init__(self):
    self.messages = Vector("messages")

@call
def add_message(self, text: str) -> int:
    """Add a message and return its index"""
    self.messages.append(text)
    return len(self.messages) - 1

@view
def get_message(self, index: int) -> str:
    """Get a message by index"""
    return self.messages[index]
```

### Updating Elements

```python
@call
def update_message(self, index: int, new_text: str) -> bool:
    """Update a message at the given index"""
    if 0 <= index < len(self.messages):
        self.messages[index] = new_text
        return True
    return False
```

### Removing Elements

```python
@call
def remove_last_message(self) -> str:
    """Remove and return the last message"""
    if len(self.messages) > 0:
        return self.messages.pop()
    raise IndexError("No messages to remove")

@call
def remove_message(self, index: int) -> str:
    """Remove a message by index, replacing it with the last one"""
    if 0 <= index < len(self.messages):
        return self.messages.swap_remove(index)
    raise IndexError("Invalid message index")
```

### Paginated Access

```python
@view
def get_messages(self, from_index: int = 0, limit: int = 10) -> list:
    """Get a page of messages"""
    end = min(from_index + limit, len(self.messages))
    return self.messages[from_index:end]
```

## LookupMap Examples

### Creating and Setting Values

```python
from near_sdk_py import view, call, Context
from near_sdk_py.collections import LookupMap

# In your contract class
def __init__(self):
    self.scores = LookupMap("scores")

@call
def set_score(self, score: int) -> int:
    """Set score for the caller"""
    account_id = Context.predecessor_account_id()
    self.scores[account_id] = score
    return score
```

### Getting Values

```python
@view
def get_score(self, account_id: str) -> int:
    """Get score for an account, returns 0 if not found"""
    return self.scores.get(account_id, 0)

@view
def get_my_score(self) -> int:
    """Get score for the caller"""
    account_id = Context.predecessor_account_id()
    return self.scores.get(account_id, 0)
```

### Removing Values

```python
@call
def reset_score(self, account_id: str) -> bool:
    """Reset score for an account"""
    if account_id in self.scores:
        del self.scores[account_id]
        return True
    return False
```

## UnorderedMap Examples

### Creating and Working with Entries

```python
from near_sdk_py import view, call, Context
from near_sdk_py.collections import UnorderedMap
from typing import List, Dict

# In your contract class
def __init__(self):
    self.profiles = UnorderedMap("profiles")

@call
def set_profile(self, name: str, avatar: str) -> Dict:
    """Set profile for the caller"""
    account_id = Context.predecessor_account_id()
    profile = {
        "name": name,
        "avatar": avatar,
        "updated_at": Context.block_timestamp()
    }
    self.profiles[account_id] = profile
    return profile
```

### Iterating and Listing

```python
@view
def get_all_profiles(self) -> List[Dict]:
    """Get all profiles with account info"""
    result = []
    for account_id in self.profiles:
        profile = self.profiles[account_id]
        # Add account_id to each profile
        profile_with_id = dict(profile)
        profile_with_id["account_id"] = account_id
        result.append(profile_with_id)
    return result

@view
def search_profiles(self, name_prefix: str) -> List[Dict]:
    """Search profiles by name prefix"""
    result = []
    for account_id in self.profiles:
        profile = self.profiles[account_id]
        if profile["name"].startswith(name_prefix):
            # Add account_id to each profile
            profile_with_id = dict(profile)
            profile_with_id["account_id"] = account_id
            result.append(profile_with_id)
    return result
```

### Getting Keys and Values

```python
@view
def get_profile_accounts(self) -> List[str]:
    """Get all account IDs with profiles"""
    return self.profiles.keys()

@view
def get_profile_data(self) -> List[Dict]:
    """Get all profile data without account IDs"""
    return self.profiles.values()
```

### Paginated Access

```python
@view
def get_profiles_paginated(self, from_index: int = 0, limit: int = 10) -> List[Dict]:
    """Get a page of profiles"""
    accounts = self.profiles.keys()
    
    # Calculate bounds
    start = min(from_index, len(accounts))
    end = min(start + limit, len(accounts))
    
    # Get accounts for this page
    page_accounts = accounts[start:end]
    
    # Get profiles for these accounts
    result = []
    for account_id in page_accounts:
        profile = self.profiles[account_id]
        profile_with_id = dict(profile)
        profile_with_id["account_id"] = account_id
        result.append(profile_with_id)
    
    return result
```

## LookupSet Examples

### Creating and Working with Sets

```python
from near_sdk_py import view, call, Context
from near_sdk_py.collections import LookupSet

# In your contract class
def __init__(self):
    self.admins = LookupSet("admins")
    
    # Add contract owner as the first admin
    owner_id = Context.predecessor_account_id()
    self.admins.add(owner_id)

@call
def add_admin(self, account_id: str) -> bool:
    """Add a new admin (only current admin can call)"""
    caller = Context.predecessor_account_id()
    assert caller in self.admins, "Only admins can add new admins"
    
    self.admins.add(account_id)
    return True
```

### Checking Membership

```python
@view
def is_admin(self, account_id: str) -> bool:
    """Check if an account is an admin"""
    return account_id in self.admins

@view
def can_i_admin(self) -> bool:
    """Check if caller is an admin"""
    account_id = Context.predecessor_account_id()
    return account_id in self.admins
```

### Removing from Set

```python
@call
def remove_admin(self, account_id: str) -> bool:
    """Remove an admin (only current admin can call)"""
    caller = Context.predecessor_account_id()
    assert caller in self.admins, "Only admins can remove admins"
    
    # Prevent removing yourself
    assert caller != account_id, "Cannot remove yourself"
    
    # Remove admin if exists
    if account_id in self.admins:
        self.admins.remove(account_id)
        return True
    return False
```

## UnorderedSet Examples

### Creating and Working with Sets

```python
from near_sdk_py import view, call, Context
from near_sdk_py.collections import UnorderedSet
from typing import List

# In your contract class
def __init__(self):
    self.verified_users = UnorderedSet("verified")

@call
def verify_user(self, account_id: str) -> bool:
    """Add a user to verified users set"""
    caller = Context.predecessor_account_id()
    assert caller == self.owner_id, "Only owner can verify users"
    
    self.verified_users.add(account_id)
    return True
```

### Listing and Iterating