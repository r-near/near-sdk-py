from near_sdk_py import call, view
from near_sdk_py.collections import UnorderedMap
from near_sdk_py.contract import Contract


class UnorderedMapContract(Contract):
    unordered_map: UnorderedMap

    def __init__(self):
        super().__init__()
        self.unordered_map = UnorderedMap("items")

    @call
    def hello(self):
        """Basic check to get a baseline gas usage"""
        return {"Hello": "World"}

    @call
    def set_item(self, key: str, value: str):
        """Add or update an item in the map"""
        self.unordered_map[key] = value
        return {"length": len(self.unordered_map)}

    @view
    def get_item(self, key: str):
        """Get an item by key"""
        return {"value": self.unordered_map[key] if key in self.unordered_map else None}

    @view
    def get_all_items(self):
        """Get all items in the map (keys and values)"""
        return {"items": [(key, value) for key, value in self.unordered_map.items()]}

    @view
    def get_all_keys(self):
        """Get all keys in the map"""
        return {"keys": list(self.unordered_map.keys())}

    @view
    def get_all_values(self):
        """Get all values in the map"""
        return {"values": list(self.unordered_map.values())}

    @view
    def get_length(self):
        """Get the length of the map"""
        return {"length": len(self.unordered_map)}

    @call
    def clear_items(self):
        """Clear all items in the map"""
        self.unordered_map.clear()
        return {"length": len(self.unordered_map)}

    @call
    def remove_item(self, key: str):
        """Remove an item by key"""
        if key in self.unordered_map:
            value = self.unordered_map[key]
            del self.unordered_map[key]
            return {"removed": value}
        return {"removed": None}

    @view
    def contains_key(self, key: str):
        """Check if the map contains a key"""
        return {"contains": key in self.unordered_map}

    @view
    def get_paginated_items(self, start_index: int, limit: int):
        """
        Get a paginated subset of items from the map
        Args:
            start_index: The index to start from (0-based)
            limit: Maximum number of items to return
        Returns:
            Dictionary with paginated items and total count
        """
        total_items = len(self.unordered_map)
        items = list(self.unordered_map.items(start_index, limit))

        return {
            "items": items,
            "total": total_items,
            "start_index": start_index,
            "limit": limit,
            "page_count": len(items),
        }
