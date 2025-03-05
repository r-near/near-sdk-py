# NEAR Python SDK Collections API

The Collections API provides efficient, persistent data structures for NEAR smart contracts written in Python. These collections help you manage contract state with a familiar Pythonic interface while optimizing for blockchain storage efficiency.

## Overview

When developing smart contracts, choosing the right data structures is critical for both functionality and gas efficiency. The Collections API offers specialized data structures that are:

- **Storage-efficient**: Values are serialized and persisted to blockchain storage
- **Gas-optimized**: Data is lazy-loaded only when needed
- **Pythonic**: Uses familiar syntax and methods similar to standard Python collections 
- **Type-safe**: Provides proper typing for better IDE support and code quality

## Available Collections

| Collection | Description | Similar to | When to Use |
|------------|-------------|------------|-------------|
| `Vector` | Ordered, indexable collection | Python's `list` | When you need ordered data with index-based access |
| `LookupMap` | Non-iterable key-value store | Python's `dict` (without iteration) | When you only need fast key lookups and won't iterate |
| `UnorderedMap` | Iterable key-value store | Python's `dict` | When you need both key lookups and iteration |
| `LookupSet` | Non-iterable set of unique values | Python's `set` (without iteration) | When you only need to check for value existence |
| `UnorderedSet` | Iterable set of unique values | Python's `set` | When you need to check for existence and iterate |
| `TreeMap` | Ordered key-value store | Python's `SortedDict` | When you need keys in order or range queries |

## Quick Start

```python
from near_sdk_py import view, call, init
from near_sdk_py.collections import Vector, UnorderedMap, UnorderedSet

class TokenContract:
    def __init__(self):
        self.tokens = Vector("tokens")
        self.balances = UnorderedMap("balances")
        self.owners = UnorderedSet("owners")
    
    @call
    def mint(self, token_id, owner_id):
        self.tokens.append(token_id)
        self.balances[owner_id] = self.balances.get(owner_id, 0) + 1
        self.owners.add(owner_id)
    
    @view
    def get_tokens(self, from_index=0, limit=50):
        return self.tokens[from_index:from_index+limit]
    
    @view
    def get_balance(self, account_id):
        return self.balances.get(account_id, 0)
    
    @view
    def get_owners(self):
        return self.owners.values()
```

## Import Options

You can import all collections at once or import specific collections:

```python
# Import everything
from near_sdk_py.collections import Vector, LookupMap, UnorderedMap, LookupSet, UnorderedSet, TreeMap

# Import specific collections
from near_sdk_py.collections.vector import Vector
from near_sdk_py.collections.unordered_map import UnorderedMap
```

## Key Concepts

### Storage Prefixes

Each collection requires a unique prefix string to ensure data isn't accidentally overwritten. This prefix is used to create unique storage keys for each collection item.

```python
tokens = Vector("tokens")         # Uses prefix "tokens"
owners = UnorderedSet("owners")   # Uses prefix "owners"
```

For more sophisticated prefix management, see the [Prefixes Guide](prefixes.md).

### Storage Efficiency

Collections store data on the blockchain, which has a cost in NEAR tokens. The API is designed to be storage-efficient:

- Data is only loaded when accessed (lazy loading)
- Non-iterable collections (`LookupMap`, `LookupSet`) use less storage overhead
- Iterable collections add metadata to enable iteration

See the [Storage Management Guide](storage_management.md) for best practices.

### Choosing the Right Collection

Choosing the right collection type is important for both functionality and gas efficiency:

- Need ordered, indexable data? Use `Vector`
- Need key-value mapping without iteration? Use `LookupMap`
- Need key-value mapping with iteration? Use `UnorderedMap`
- Need to check for unique values without iteration? Use `LookupSet`
- Need to check for unique values with iteration? Use `UnorderedSet`
- Need ordered key-value mapping or range queries? Use `TreeMap`

For more details, see the [Choosing Collections Guide](choosing.md).

## Documentation

- [Vector Documentation](vector.md)
- [Maps Documentation](maps.md) (LookupMap and UnorderedMap)
- [Sets Documentation](sets.md) (LookupSet and UnorderedSet)
- [TreeMap Documentation](tree_map.md)
- [Storage Management Guide](storage_management.md)
- [Prefixes Guide](prefixes.md)
- [Examples](examples/)

## Reference

The Collections API is inspired by the [NEAR Rust SDK Collections](https://docs.near.org/build/smart-contracts/anatomy/collections) but adapted for Python's idioms and features.