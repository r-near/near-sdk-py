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

```python
@view
def get_all_verified_users(self) -> List[str]:
    """Get all verified users"""
    return self.verified_users.values()

@view
def get_verified_users_count(self) -> int:
    """Get count of verified users"""
    return len(self.verified_users)

@view
def search_verified_users(self, prefix: str) -> List[str]:
    """Search verified users by account prefix"""
    result = []
    for account_id in self.verified_users:
        if account_id.startswith(prefix):
            result.append(account_id)
    return result
```

### Removing from Set

```python
@call
def unverify_user(self, account_id: str) -> bool:
    """Remove a user from verified users set"""
    caller = Context.predecessor_account_id()
    assert caller == self.owner_id, "Only owner can unverify users"
    
    self.verified_users.remove(account_id)
    return True
```

### Paginated Access

```python
@view
def get_verified_users_paginated(self, from_index: int = 0, limit: int = 10) -> List[str]:
    """Get a page of verified users"""
    all_users = self.verified_users.values()
    
    # Calculate bounds
    start = min(from_index, len(all_users))
    end = min(start + limit, len(all_users))
    
    # Return the slice
    return all_users[start:end]
```

## TreeMap Examples

### Creating and Working with Ordered Maps

```python
from near_sdk_py import view, call, Context
from near_sdk_py.collections import TreeMap
from typing import List, Dict, Optional

# In your contract class
def __init__(self):
    # Map of timestamp -> event
    self.events_by_time = TreeMap("events_by_time")

@call
def add_event(self, title: str, description: str, event_time: int) -> Dict:
    """Add an event at the given timestamp"""
    event = {
        "title": title,
        "description": description,
        "event_time": event_time,
        "created_by": Context.predecessor_account_id(),
        "created_at": Context.block_timestamp()
    }
    
    self.events_by_time[event_time] = event
    return event
```

### Range Queries

```python
@view
def get_upcoming_events(self, from_time: Optional[int] = None) -> List[Dict]:
    """Get all events from a given time forward"""
    # If not specified, use current time
    start_time = from_time or Context.block_timestamp()
    
    # Get all events with timestamps >= start_time
    result = []
    for time in self.events_by_time.range(from_key=start_time):
        result.append(self.events_by_time[time])
    
    return result

@view
def get_events_in_range(self, start_time: int, end_time: int) -> List[Dict]:
    """Get all events in a specified time range"""
    result = []
    for time in self.events_by_time.range(from_key=start_time, to_key=end_time):
        result.append(self.events_by_time[time])
    
    return result
```

### Finding Nearest Entries

```python
@view
def get_nearest_event(self, target_time: int) -> Optional[Dict]:
    """Find the event closest to the target time"""
    # Try to find exact match first
    if target_time in self.events_by_time:
        return self.events_by_time[target_time]
    
    # Look for the nearest event after the target time
    ceiling_time = self.events_by_time.ceiling_key(target_time)
    if ceiling_time is not None:
        return self.events_by_time[ceiling_time]
    
    # If no events after, look for the latest event before
    floor_time = self.events_by_time.floor_key(target_time)
    if floor_time is not None:
        return self.events_by_time[floor_time]
    
    # No events found
    return None
```

### Min/Max Operations

```python
@view
def get_earliest_event(self) -> Optional[Dict]:
    """Get the earliest scheduled event"""
    if self.events_by_time.is_empty():
        return None
        
    earliest_time = self.events_by_time.min_key()
    return self.events_by_time[earliest_time]

@view
def get_latest_event(self) -> Optional[Dict]:
    """Get the latest scheduled event"""
    if self.events_by_time.is_empty():
        return None
        
    latest_time = self.events_by_time.max_key()
    return self.events_by_time[latest_time]
```

### Ordered Iteration

```python
@view
def get_all_events_ordered(self) -> List[Dict]:
    """Get all events in ascending time order"""
    result = []
    for time in self.events_by_time:
        result.append(self.events_by_time[time])
    return result

@view
def get_all_events_reverse_order(self) -> List[Dict]:
    """Get all events in descending time order"""
    result = []
    # Get all keys and reverse them
    times = self.events_by_time.keys()
    times.reverse()
    
    for time in times:
        result.append(self.events_by_time[time])
    return result
```

## Using Collections Together

Here's an example of using multiple collections together in a voting contract:

```python
from near_sdk_py import view, call, init, Context
from near_sdk_py.collections import (
    UnorderedMap, UnorderedSet, Vector, TreeMap, create_enum_prefix
)
from enum import Enum
from typing import List, Dict, Optional

class StorageKey(Enum):
    PROPOSALS = 1
    VOTES = 2
    VOTERS = 3
    PROPOSALS_BY_END_TIME = 4

class VotingContract:
    def __init__(self):
        # Proposal data
        self.proposals = UnorderedMap(create_enum_prefix(StorageKey, StorageKey.PROPOSALS))
        
        # Votes per proposal
        self.votes = UnorderedMap(create_enum_prefix(StorageKey, StorageKey.VOTES))
        
        # Who has voted for each proposal
        self.voters = UnorderedMap(create_enum_prefix(StorageKey, StorageKey.VOTERS))
        
        # Proposals ordered by end time
        self.proposals_by_end_time = TreeMap(create_enum_prefix(StorageKey, StorageKey.PROPOSALS_BY_END_TIME))
    
    @init
    def new(self) -> bool:
        """Initialize the contract"""
        return True
    
    @call
    def create_proposal(self, title: str, description: str, options: List[str], end_time: int) -> str:
        """Create a new proposal"""
        caller = Context.predecessor_account_id()
        
        # Create proposal ID
        proposal_id = f"{Context.block_timestamp()}:{caller}"
        
        # Create proposal
        proposal = {
            "id": proposal_id,
            "title": title,
            "description": description,
            "options": options,
            "creator": caller,
            "created_at": Context.block_timestamp(),
            "end_time": end_time
        }
        
        # Store proposal
        self.proposals[proposal_id] = proposal
        
        # Initialize vote counts for each option
        vote_counts = {option: 0 for option in options}
        self.votes[proposal_id] = vote_counts
        
        # Initialize voters set for this proposal
        self.voters[proposal_id] = []
        
        # Add to time index
        self.proposals_by_end_time[end_time] = proposal_id
        
        return proposal_id
    
    @call
    def vote(self, proposal_id: str, option: str) -> bool:
        """Vote on a proposal"""
        assert proposal_id in self.proposals, "Proposal not found"
        
        proposal = self.proposals[proposal_id]
        assert option in proposal["options"], "Invalid option"
        
        current_time = Context.block_timestamp()
        assert current_time < proposal["end_time"], "Voting period has ended"
        
        caller = Context.predecessor_account_id()
        
        # Check if already voted
        voters = self.voters[proposal_id]
        assert caller not in voters, "Already voted on this proposal"
        
        # Add voter to the voters list
        voters.append(caller)
        self.voters[proposal_id] = voters
        
        # Update vote count
        vote_counts = self.votes[proposal_id]
        vote_counts[option] += 1
        self.votes[proposal_id] = vote_counts
        
        return True
    
    @view
    def get_proposal(self, proposal_id: str) -> Optional[Dict]:
        """Get a proposal by ID"""
        if proposal_id not in self.proposals:
            return None
        
        proposal = self.proposals[proposal_id]
        result = dict(proposal)
        
        # Add vote counts
        if proposal_id in self.votes:
            result["votes"] = self.votes[proposal_id]
        
        return result
    
    @view
    def get_active_proposals(self) -> List[Dict]:
        """Get all active proposals"""
        current_time = Context.block_timestamp()
        
        active_proposals = []
        for time in self.proposals_by_end_time.range(from_key=current_time):
            proposal_id = self.proposals_by_end_time[time]
            proposal = self.get_proposal(proposal_id)
            active_proposals.append(proposal)
        
        return active_proposals
    
    @view
    def get_closed_proposals(self) -> List[Dict]:
        """Get all closed proposals"""
        current_time = Context.block_timestamp()
        
        closed_proposals = []
        for time in self.proposals_by_end_time.range(to_key=current_time):
            proposal_id = self.proposals_by_end_time[time]
            proposal = self.get_proposal(proposal_id)
            closed_proposals.append(proposal)
        
        return closed_proposals
    
    @view
    def has_voted(self, proposal_id: str, account_id: str) -> bool:
        """Check if an account has voted on a proposal"""
        if proposal_id not in self.voters:
            return False
        
        voters = self.voters[proposal_id]
        return account_id in voters
```

This voting contract demonstrates:

1. Using `UnorderedMap` for general key-value storage (proposals, votes)
2. Using `TreeMap` for time-ordered queries (active vs. closed proposals)
3. Tracking lists in storage (voters per proposal)
4. Using enum-based prefixes for clean storage organization
5. Combining data from multiple collections in view methods

## Common Patterns

Here are some common patterns you might find useful:

### Pagination

```python
@view
def get_items_paginated(self, from_index: int = 0, limit: int = 50) -> List:
    """Generic pagination pattern"""
    # Get the items (keys, values, or whatever)
    all_items = self.collection.values()  # or .keys() or list(self.collection)
    
    # Safety checks on bounds
    start = min(max(from_index, 0), len(all_items))
    end = min(start + max(limit, 1), len(all_items))
    
    # Return the slice
    return all_items[start:end]
```

### Index Tracking

```python
# Track both by ID and by owner
item = {
    "id": item_id,
    "owner": owner_id,
    # ... other fields
}

# Store by ID
self.items[item_id] = item

# Also track by owner
owner_items = self.items_by_owner.get(owner_id, [])
owner_items.append(item_id)
self.items_by_owner[owner_id] = owner_items
```

### Versioned Storage

```python
@view
def get_storage_version(self) -> int:
    """Get current storage schema version"""
    return self.settings.get("storage_version", 1)

@call
def migrate_storage(self) -> bool:
    """Migrate storage schema"""
    version = self.get_storage_version()
    
    if version == 1:
        # Migrate from v1 to v2
        # ... migration code ...
        self.settings["storage_version"] = 2
        return True
    
    return False
```

These examples should help you get started with using the Collections API effectively in your NEAR smart contracts.