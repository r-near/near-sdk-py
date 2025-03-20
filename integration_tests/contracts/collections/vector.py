from near_sdk_py import call, view
from near_sdk_py.collections import Vector
from near_sdk_py.contract import Contract


class VectorContract(Contract):
    vector: Vector

    def __init__(self):
        super().__init__()
        self.vector = Vector("items")

    @call
    def hello(self):
        """Basic check to get a baseline gas usage"""
        return {"Hello": "World"}

    @call
    def add_item(self, item: str):
        # Add an item to the vector
        self.vector.append(item)
        return {"length": len(self.vector)}

    @view
    def get_item(self, index: int):
        # Get an item at the specified index
        return {"item": self.vector[index]}

    @view
    def get_all_items(self):
        # Get all items in the vector
        return {"items": [item for item in self.vector]}

    @view
    def get_length(self):
        # Get the length of the vector
        return {"length": len(self.vector)}

    @call
    def clear_items(self):
        # Clear all items in the vector
        self.vector.clear()
        return {"length": len(self.vector)}

    @call
    def pop_item(self, index=-1):
        # Pop an item from the vector at the specified index
        # Default is to pop the last item
        return {"item": self.vector.pop(index)}

    @call
    def swap_remove_item(self, index: int):
        # Remove an item by swapping with the last item
        return {"item": self.vector.swap_remove(index)}

    @view
    def iterate_range(self, start: int, end: int):
        # Iterate through a range of elements
        count = 0
        for i, _ in enumerate(self.vector):
            if i >= start and i < end:
                count += 1
            if i >= end:
                break
        return {"count": count}
