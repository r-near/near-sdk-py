# Choosing the Right Collection

Selecting the appropriate collection type for your NEAR smart contract is crucial for both functionality and gas efficiency. This guide will help you understand the tradeoffs between different collection types.

## Collection Types Overview

| Collection | Iterable? | Ordered? | Unique Keys? | Memory Overhead | Use Case |
|------------|-----------|----------|--------------|----------------|----------|
| `Vector` | ✅ | ✅ (by insertion) | ❌ | Low | Ordered list of items |
| `LookupMap` | ❌ | ❌ | ✅ | Lowest | Fast key-value lookups |
| `UnorderedMap` | ✅ | ❌ | ✅ | Medium | Key-value with iteration |
| `LookupSet` | ❌ | ❌ | ✅ | Lowest | Fast unique value lookups |
| `UnorderedSet` | ✅ | ❌ | ✅ | Medium | Unique values with iteration |
| `TreeMap` | ✅ | ✅ (by key) | ✅ | Highest | Ordered key-value pairs |

## Decision Flowchart

```
Do you need to store key-value pairs?
├── Yes → Do you need to iterate over all entries?
│         ├── Yes → Do you need keys to be ordered?
│         │         ├── Yes → Use TreeMap
│         │         └── No → Use UnorderedMap
│         └── No → Use LookupMap
└── No → Do you need to store unique values?
          ├── Yes → Do you need to iterate over all values?
          │         ├── Yes → Use UnorderedSet
          │         └── No → Use LookupSet
          └── No → Do you need indexed access or ordered items?
                    ├── Yes → Use Vector
                    └── No → Use Vector (still the best choice)
```

## When to Use Each Collection

### Use `Vector` when you need:

- An ordered list of items
- Index-based access (e.g., `my_vector[5]`)
- To frequently add items to the end of a list
- To maintain insertion order

### Use `LookupMap` when you need:

- Fast key-value lookups
- Gas efficiency (lowest overhead)
- Only key-based access, never iteration
- To check if a key exists

### Use `UnorderedMap` when you need:

- Both key-value lookups and iteration
- To get all keys, values, or key-value pairs
- A classic dictionary/map with full functionality

### Use `LookupSet` when you need:

- To check if a value exists (membership)
- Gas efficiency (lowest overhead)
- Only membership testing, never iteration

### Use `UnorderedSet` when you need:

- Both membership testing and iteration
- To get all unique values in the set
- A classic set with full functionality

### Use `TreeMap` when you need:

- Keys to be kept in sorted order
- Range queries (get all keys between X and Y)
- To find the nearest key (floor/ceiling operations)
- Ordered iteration through keys

## Gas and Storage Considerations

Collections have different storage and gas cost profiles:

- **Non-iterable collections** (`LookupMap`, `LookupSet`) have the lowest storage overhead but cannot be iterated over
- **Iterable collections** (`UnorderedMap`, `UnorderedSet`) require additional storage to track keys/values for iteration
- **Ordered collections** (`Vector`, `TreeMap`) have additional overhead to maintain order

## Collection Size Recommendations

| Collection Size | Recommended Collection Type |
|-----------------|---------------------------|
| Small (< 100 items) | Any collection type is fine |
| Medium (100-1,000 items) | Consider gas efficiency more carefully |
| Large (> 1,000 items) | Use non-iterable collections when possible and implement pagination |

## Examples

### Tokens in an NFT Contract

```python
# Store a list of all token IDs
token_ids = Vector("token_ids")

# Store token metadata by token ID
token_metadata = UnorderedMap("token_metadata")

# Track which tokens are owned by which accounts
tokens_by_owner = UnorderedMap("tokens_by_owner")
```

### Voting System

```python
# Track valid voters
eligible_voters = LookupSet("eligible_voters")

# Track who has already voted
voted = LookupSet("voted")

# Store votes by proposal ID
votes_by_proposal = UnorderedMap("votes_by_proposal")

# Store proposals in order by closing time
proposals_by_end_time = TreeMap("proposals_by_end_time")
```

### User Profiles

```python
# Store user profiles by account ID
profiles = LookupMap("profiles")

# Track verified users
verified_users = LookupSet("verified_users")

# Featured profiles in priority order
featured_profiles = Vector("featured_profiles")
```

## Hybrid Approaches

Sometimes you might need multiple collections to achieve your goals efficiently:

```python
# For a system needing both fast lookups and ordered access:

# Fast lookup by ID
items_by_id = LookupMap("items_by_id")

# Ordered listing of IDs
ordered_item_ids = Vector("ordered_item_ids")

# Usage:
def get_item(item_id):
    return items_by_id.get(item_id)

def get_items_paginated(from_index, limit):
    # Get IDs in order
    ids = ordered_item_ids[from_index:from_index + limit]
    # Retrieve each item by ID
    return [items_by_id[id] for id in ids]
```

## Summary

1. For simple ordered lists, use `Vector`
2. For key-value lookups without iteration, use `LookupMap`
3. For key-value with iteration, use `UnorderedMap`
4. For unique value checking without iteration, use `LookupSet`
5. For unique values with iteration, use `UnorderedSet`
6. For ordered key-value data, use `TreeMap`

Choose the most restrictive collection that meets your needs to maximize gas efficiency.