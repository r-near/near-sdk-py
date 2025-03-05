# Managing Storage Prefixes

Storage prefixes are a critical concept in NEAR smart contracts. Each collection needs a unique prefix to avoid storage collisions, and managing these prefixes properly is essential for building maintainable contracts.

## Understanding Prefixes

### What is a Prefix?

A storage prefix is a string that gets prepended to all keys when storing data in blockchain storage. For example, if you have a collection with the prefix `"users"`, and store data with key `"alice"`, it will be stored with the composite key `"users:alice"` in the contract's storage.

### Why Prefixes Matter

1. **Avoid Collisions**: Different collections must use different prefixes to prevent them from overwriting each other's data.

2. **Organized Storage**: Prefixes help organize contract storage into logical sections.

3. **Contract Upgrades**: Consistent prefix usage makes contract upgrades safer.

4. **Nested Collections**: For complex contracts, prefixes can be structured hierarchically.

## Basic Prefix Usage

Every collection requires a prefix when instantiated:

```python
from near_sdk_py.collections import Vector, UnorderedMap, LookupSet

# Simple string prefixes
tokens = Vector("tokens")
balances = UnorderedMap("balances")
users = LookupSet("users")
```

## Common Prefix Patterns

### 1. String Constants

Define prefix strings as constants to avoid typos and ensure consistency:

```python
# Define prefixes as constants
TOKEN_PREFIX = "token"
USER_PREFIX = "user"
BALANCE_PREFIX = "balance"

# Use constants for collections
self.tokens = Vector(TOKEN_PREFIX)
self.users = UnorderedSet(USER_PREFIX)
self.balances = UnorderedMap(BALANCE_PREFIX)
```

### 2. Enum-Based Prefixes

Using enums for prefixes provides both type safety and organization:

```python
from enum import Enum
from near_sdk_py.collections import Vector, UnorderedMap, create_enum_prefix

class StorageKey(Enum):
    TOKENS = 1
    USERS = 2
    BALANCES = 3

# Create collections with enum prefixes
self.tokens = Vector(create_enum_prefix(StorageKey, StorageKey.TOKENS))
self.users = Vector(create_enum_prefix(StorageKey, StorageKey.USERS))
self.balances = UnorderedMap(create_enum_prefix(StorageKey, StorageKey.BALANCES))
```

The `create_enum_prefix` function generates a string like `"StorageKey:TOKENS"` from an enum value.

### 3. Nested Prefixes

For more complex contracts, you might need nested prefixes:

```python
from near_sdk_py.collections import UnorderedMap, Vector, create_prefix_guard

# Base prefix for a contract
CONTRACT_PREFIX = "contract_v1"

# Create a prefix guard function
prefix = create_prefix_guard(CONTRACT_PREFIX)

# Create collections with nested prefixes
self.users = UnorderedMap(prefix("users"))
self.tokens = Vector(prefix("tokens"))

# Further nesting for per-user data
user_id = "alice.near"
user_prefix = prefix(f"user:{user_id}")

# Create prefix guard for user data
user_prefix_guard = create_prefix_guard(user_prefix)

# Collections for specific user
self.user_tokens = Vector(user_prefix_guard("tokens"))
self.user_balances = UnorderedMap(user_prefix_guard("balances"))
```

The `create_prefix_guard` function returns a function that prepends a base prefix to any string you pass to it.

## Advanced Techniques

### Versioned Prefixes

Include a version in your prefixes to facilitate clean contract upgrades:

```python
# With version in the prefix
CONTRACT_VERSION = "1"
token_prefix = f"token_v{CONTRACT_VERSION}"
self.tokens = Vector(token_prefix)

# When upgrading to v2, use:
# CONTRACT_VERSION = "2"
# This creates a completely separate storage space
```

### Dynamic Prefixes

Generate prefixes dynamically based on contract state:

```python
def get_data_prefix(self):
    # Get current schema version from contract state
    schema_version = self.settings.get("schema_version", "1")
    return f"data_v{schema_version}"

# Use the dynamic prefix
data_prefix = self.get_data_prefix()
self.data = UnorderedMap(data_prefix)
```

### Prefix Trees

For sophisticated contracts, organize prefixes in a tree-like structure:

```python
class PrefixTree:
    def __init__(self, base_prefix):
        self.base = base_prefix
    
    def __call__(self, key):
        return f"{self.base}:{key}"
    
    def branch(self, key):
        """Create a new PrefixTree with an extended base"""
        return PrefixTree(f"{self.base}:{key}")

# Usage
prefixes = PrefixTree("contract_v1")

# Main collections
tokens = Vector(prefixes("tokens"))
users = UnorderedMap(prefixes("users"))

# Branch for a specific user
user_branch = prefixes.branch(f"user:{user_id}")
user_tokens = Vector(user_branch("tokens"))
```

## Prefix Naming Conventions

Follow these conventions for consistent and maintainable prefix naming:

1. **Use Descriptive Names**: Prefer `"user_profiles"` over `"up"`.

2. **Use Underscores**: Separate words with underscores: `"token_metadata"`.

3. **Include Versions**: When appropriate, include version: `"users_v2"`.

4. **Avoid Reserved Characters**: Avoid characters that might interfere with prefix parsing, such as `:` (which is used internally).

5. **Be Consistent**: Use the same naming pattern throughout your contract.

## Common Prefix Mistake: Collisions

The most common mistake is prefix collision, where two collections accidentally use the same prefix:

```python
# BAD: Same prefix for two collections
self.tokens = Vector("tokens")
self.token_metadata = UnorderedMap("tokens")  # COLLISION!

# GOOD: Different prefixes
self.tokens = Vector("tokens")
self.token_metadata = UnorderedMap("token_metadata")
```

## Prefix Patterns for Common Use Cases

### NFT Contract

```python
class NFTContract:
    def __init__(self):
        # Create prefix guard
        prefix = create_prefix_guard("nft_v1")
        
        # Main collections
        self.tokens = UnorderedSet(prefix("tokens"))
        self.token_metadata = UnorderedMap(prefix("metadata"))
        self.owners = UnorderedMap(prefix("owners"))
        
        # Per-owner collections
        def owner_prefix(owner_id):
            return prefix(f"owner:{owner_id}")
        
        # Example usage:
        # owner_id = "alice.near"
        # owner_tokens = Vector(owner_prefix(owner_id))
```

### Fungible Token Contract

```python
class FTContract:
    def __init__(self):
        # Create prefix guard with enum
        class StorageKey(Enum):
            BALANCES = 1
            ALLOWANCES = 2
            METADATA = 3
        
        # Create collections
        self.balances = UnorderedMap(create_enum_prefix(StorageKey, StorageKey.BALANCES))
        self.allowances = UnorderedMap(create_enum_prefix(StorageKey, StorageKey.ALLOWANCES))
        self.metadata = UnorderedMap(create_enum_prefix(StorageKey, StorageKey.METADATA))
```

### DAO Contract

```python
class DAOContract:
    def __init__(self):
        base_prefix = "dao_v1"
        prefix = create_prefix_guard(base_prefix)
        
        # Member management
        self.members = UnorderedSet(prefix("members"))
        
        # Proposal management
        self.proposals = UnorderedMap(prefix("proposals"))
        self.votes = UnorderedMap(prefix("votes"))
        
        # For each proposal
        def proposal_prefix(proposal_id):
            return prefix(f"proposal:{proposal_id}")
        
        # Example usage:
        # proposal_id = "proposal-1"
        # proposal_votes = UnorderedMap(proposal_prefix(proposal_id))
```

## Conclusion

Proper prefix management is essential for building maintainable and upgradable NEAR smart contracts. By following the patterns and practices outlined in this guide, you can avoid storage collisions and create well-organized contract storage structures.