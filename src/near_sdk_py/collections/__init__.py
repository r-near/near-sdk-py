"""
NEAR SDK Collections API for Python.

This module provides persistent collections for NEAR smart contracts written in Python.
Collections efficiently store data on the blockchain by handling serialization,
lazy loading, and chunking of data.

It includes the following collection types:
- Vector: An ordered, indexable collection (similar to Python's list)
- LookupMap: A non-iterable key-value store (similar to Python's dict)
- UnorderedMap: A key-value store that supports iteration
- LookupSet: A non-iterable set of unique values
- UnorderedSet: A set of unique values that supports iteration
- TreeMap: An ordered key-value store (keys are ordered)

Example usage:

```python
from near_sdk_py import call, view, init, Storage
from near_sdk_py.collections import Vector, UnorderedMap, UnorderedSet

# In your contract class:
class TokenContract:
    def __init__(self):
        self.tokens = Vector("tokens")
        self.balances = UnorderedMap("balances")
        self.approvals = UnorderedMap("approvals")
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
"""

from .adapter import CollectionStorageAdapter
from .base import Collection, PrefixType
from .lookup_map import LookupMap
from .lookup_set import LookupSet
from .tree_map import TreeMap
from .unordered_map import IterableMap, UnorderedMap
from .unordered_set import IterableSet, UnorderedSet
from .utils import create_enum_prefix, create_prefix_guard
from .vector import Vector

# Export the collection classes
__all__ = [
    "Vector",
    "LookupMap",
    "UnorderedMap",
    "IterableMap",
    "LookupSet",
    "UnorderedSet",
    "IterableSet",
    "TreeMap",
    "Collection",
    "PrefixType",
    "CollectionStorageAdapter",
    "create_enum_prefix",
    "create_prefix_guard",
]
