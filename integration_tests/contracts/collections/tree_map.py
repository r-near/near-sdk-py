from typing import List, Optional

from near_sdk_py import call, view
from near_sdk_py.collections import TreeMap
from near_sdk_py.contract import Contract


class TreeMapContract(Contract):
    items: TreeMap

    def __init__(self):
        super().__init__()
        self.items = TreeMap("items")

    @call
    def hello(self):
        """Basic check to get a baseline gas usage"""
        return {"Hello": "World"}

    @call
    def set(self, key: str, value: str):
        """Set a key-value pair in the tree map"""
        self.items[key] = value
        return {"success": True}

    @view
    def get(self, key: str):
        """Get a value by key from the tree map"""
        return {"value": self.items.get(key)}

    @view
    def contains_key(self, key: str):
        """Check if the tree map contains the given key"""
        return {"contains": key in self.items}

    @call
    def remove(self, key: str):
        """Remove a key-value pair from the tree map"""
        value = self.items.remove(key)
        return {"success": value is not None, "value": value}

    @call
    def clear(self):
        """Remove all items from the tree map (WARNING: may exceed gas limits)"""
        self.items.clear()
        return {"success": True}

    @call
    def clear_paginated(self, batch_size: int = 100):
        """Remove items from the tree map in batches to avoid gas limits"""
        count = self.items.clear_paginated(batch_size)
        return {"removed_count": count, "success": True}

    @view
    def keys(self, start_index: int = 0, limit: Optional[int] = None):
        """Get keys from the tree map with pagination support"""
        return {"keys": self.items.keys(start_index, limit)}

    @view
    def values(self, start_index: int = 0, limit: Optional[int] = None):
        """Get values from the tree map with pagination support"""
        return {"values": self.items.values(start_index, limit)}

    @view
    def items_list(self, start_index: int = 0, limit: Optional[int] = None):
        """Get key-value pairs from the tree map with pagination support"""
        return {"items": self.items.items(start_index, limit)}

    @view
    def floor_key(self, key: str) -> Optional[str]:
        """Get the greatest key less than or equal to the given key"""
        return {"key": self.items.floor_key(key)}

    @view
    def ceiling_key(self, key: str) -> Optional[str]:
        """Get the least key greater than or equal to the given key"""
        return {"key": self.items.ceiling_key(key)}

    @view
    def min_key(self) -> Optional[str]:
        """Get the minimum key in the tree map"""
        return {"key": self.items.min_key()}

    @view
    def max_key(self) -> Optional[str]:
        """Get the maximum key in the tree map"""
        return {"key": self.items.max_key()}

    @view
    def range(
        self,
        from_key: Optional[str] = None,
        to_key: Optional[str] = None,
        start_index: int = 0,
        limit: Optional[int] = None,
    ) -> List[str]:
        """Get keys in the given range with pagination support"""
        return {"keys": self.items.range(from_key, to_key, start_index, limit)}

    @view
    def range_paginated(
        self,
        from_key: Optional[str] = None,
        to_key: Optional[str] = None,
        page_size: int = 10,
        page_number: int = 0,
    ) -> List[str]:
        """Get a page of keys in the given range"""
        return {
            "keys": self.items.range_paginated(from_key, to_key, page_size, page_number)
        }
