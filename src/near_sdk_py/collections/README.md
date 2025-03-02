# NEAR SDK Python Collections

This module provides persistent collection types for NEAR smart contracts. These collections are designed to work with NEAR's storage and provide familiar Python interfaces.

## Available Collections

- **LookupMap**: A dictionary-like collection that implements the `MutableMapping` interface
- **LookupSet**: A set-like collection that implements the `MutableSet` interface
- **UnorderedMap**: A dictionary with O(1) operations that maintains iteration order
- **UnorderedSet**: A set with O(1) operations that maintains iteration order
- **Vector**: A list-like collection that implements the `MutableSequence` interface

## Usage Examples

### LookupMap

```python
from near_sdk_py.collections import LookupMap

# Initialize a map with a unique storage prefix
scores = LookupMap("scores")

# Use like a regular dictionary
scores["alice"] = 42
scores["bob"] = 99

# Check if a key exists
if "alice" in scores:
    print(f"Alice's score: {scores['alice']}")

# Iterate through keys
for player in scores:
    print(f"Player: {player}")

# Get the number of entries
print(f"Number of players: {len(scores)}")

# Remove an entry
del scores["bob"]
```

### LookupSet

```python
from near_sdk_py.collections import LookupSet

# Initialize a set with a unique storage prefix
active_users = LookupSet("active_users")

# Add elements
active_users.add("alice")
active_users.add("bob")

# Check membership
if "alice" in active_users:
    print("Alice is active")

# Iterate through elements
for user in active_users:
    print(f"Active user: {user}")

# Get the number of elements
print(f"Number of active users: {len(active_users)}")

# Remove an element
active_users.discard("bob")
```

### UnorderedMap

```python
from near_sdk_py.collections import UnorderedMap

# Initialize with a unique storage prefix
balances = UnorderedMap("balances")

# Use like a regular dictionary
balances["alice"] = 100
balances["bob"] = 200

# Efficient removal (O(1) operation)
del balances["alice"]

# Iterate through keys (maintains insertion order)
for account in balances:
    print(f"Account: {account}, Balance: {balances[account]}")
```

### UnorderedSet

```python
from near_sdk_py.collections import UnorderedSet

# Initialize with a unique storage prefix
validators = UnorderedSet("validators")

# Add elements
validators.add("validator1")
validators.add("validator2")

# Efficient removal (O(1) operation)
validators.discard("validator1")

# Iterate through elements (maintains insertion order)
for validator in validators:
    print(f"Active validator: {validator}")
```

### Vector

```python
from near_sdk_py.collections import Vector

# Initialize with a unique storage prefix
messages = Vector("messages")

# Use like a regular list
messages.append("Hello")
messages.append("World")

# Access by index
first_message = messages[0]  # "Hello"

# Insert at position
messages.insert(1, "Beautiful")  # ["Hello", "Beautiful", "World"]

# Efficient removal with swap_remove (O(1) operation)
# Swaps with the last element and removes
messages.swap_remove(1)  # ["Hello", "World"]

# Standard removal (shifts elements)
del messages[0]  # ["World"]

# Get length
print(f"Number of messages: {len(messages)}")
```

## Storage Considerations

Each collection uses a unique prefix to separate its data in storage. Make sure to use different prefixes for different collections to avoid data collisions.

For example:
```python
users = LookupSet("users")
user_scores = LookupMap("user_scores")
```

## Performance Notes

- **LookupMap** and **LookupSet** provide O(1) access but may have higher storage costs
- **UnorderedMap** and **UnorderedSet** provide O(1) operations and maintain iteration order
- **Vector** provides O(1) access by index and O(n) insertion/deletion, with a special O(1) `swap_remove` method

Choose the appropriate collection based on your specific use case and performance requirements.
