from near_sdk_py import call, view
from near_sdk_py.collections import LookupMap
from near_sdk_py.contract import Contract


class LookupMapContract(Contract):
    items: LookupMap

    def __init__(self):
        super().__init__()
        self.items = LookupMap("items")

    @call
    def hello(self):
        """Basic check to get a baseline gas usage"""
        return {"Hello": "World"}

    @call
    def set(self, key: str, value: str):
        """Set a key-value pair in the lookup map"""
        self.items[key] = value
        return {"success": True}

    @view
    def get(self, key: str):
        """Get a value by key from the lookup map"""
        return {"value": self.items.get(key)}

    @view
    def contains_key(self, key: str):
        """Check if the lookup map contains the given key"""
        return {"contains": key in self.items}

    @call
    def remove(self, key: str):
        """Remove a key-value pair from the lookup map"""
        if key in self.items:
            del self.items[key]
            return {"success": True}
        return {"success": False}

    @call
    def clear(self):
        """Remove all items from the lookup map"""
        self.items.clear()
        return {"success": True}
