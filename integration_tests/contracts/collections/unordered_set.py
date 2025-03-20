from near_sdk_py import call, view
from near_sdk_py.collections import UnorderedSet
from near_sdk_py.contract import Contract


class UnorderedSetContract(Contract):
    unordered_set: UnorderedSet

    def __init__(self):
        super().__init__()
        self.unordered_set = UnorderedSet("items")

    @call
    def hello(self):
        """Basic check to get a baseline gas usage"""
        return {"Hello": "World"}

    @call
    def add_item(self, value: str):
        """Add an item to the set"""
        self.unordered_set.add(value)
        return {"length": len(self.unordered_set)}

    @view
    def get_all_items(self):
        """Get all items in the map (keys and values)"""
        return {"items": [value for value in self.unordered_set.values()]}

    @view
    def get_length(self):
        """Get the length of the map"""
        return {"length": len(self.unordered_set)}

    @call
    def clear_items(self):
        """Clear all items in the map"""
        self.unordered_set.clear()
        return {"length": len(self.unordered_set)}

    @call
    def remove_item(self, value: str):
        """Remove an item by value"""
        if value in self.unordered_set:
            self.unordered_set.remove(value)
            return {"removed": value}
        return {"removed": None}

    @view
    def contains_value(self, value: str):
        """Check if the map contains a value"""
        return {"contains": value in self.unordered_set}

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
        total_items = len(self.unordered_set)
        items = list(self.unordered_set.values(start_index, limit))

        return {
            "items": items,
            "total": total_items,
            "start_index": start_index,
            "limit": limit,
            "page_count": len(items),
        }
