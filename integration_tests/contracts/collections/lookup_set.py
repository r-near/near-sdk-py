from near_sdk_py import call, view
from near_sdk_py.collections import LookupSet
from near_sdk_py.contract import Contract


class LookupSetContract(Contract):
    items: LookupSet

    def __init__(self):
        super().__init__()
        self.items = LookupSet("items")

    @call
    def hello(self):
        """Basic check to get a baseline gas usage"""
        return {"Hello": "World"}

    @call
    def add(self, value: str):
        """Add a value to the lookup set"""
        self.items.add(value)
        return {"success": True}

    @view
    def contains(self, value: str):
        """Check if the lookup set contains the given value"""
        return {"contains": value in self.items}

    @call
    def remove(self, value: str):
        """Remove a value from the lookup set"""
        try:
            self.items.remove(value)
            return {"success": True}
        except KeyError:
            return {"success": False}

    @call
    def discard(self, value: str):
        """Discard a value from the lookup set"""
        self.items.discard(value)
        return {"success": True}

    @call
    def clear(self):
        """Remove all items from the lookup set"""
        self.items.clear()
        return {"success": True}
