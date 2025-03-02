from collections.abc import MutableSequence
from typing import Generic, Iterator, TypeVar, Optional

from ..storage import Storage

T = TypeVar('T')

class Vector(MutableSequence[T], Generic[T]):
    """
    A dynamic array implementation that supports standard list operations
    and provides additional helper methods like swap_remove.
    """
    
    def __init__(self, prefix: str):
        self.prefix = prefix
        self._length_prefix = f"{prefix}:len"
        self._elements_prefix = f"{prefix}:elements"
        
        if not Storage.has(self._length_prefix):
            Storage.set_json(self._length_prefix, 0)
            Storage.set_json(self._elements_prefix, [])
    
    def __getitem__(self, index: int) -> T:
        if isinstance(index, slice):
            elements = Storage.get_json(self._elements_prefix)
            return elements[index]
        
        if not 0 <= index < len(self):
            raise IndexError("Vector index out of range")
            
        elements = Storage.get_json(self._elements_prefix)
        return elements[index]
    
    def __setitem__(self, index: int, value: T) -> None:
        if isinstance(index, slice):
            elements = Storage.get_json(self._elements_prefix)
            elements[index] = value
            Storage.set_json(self._elements_prefix, elements)
            Storage.set_json(self._length_prefix, len(elements))
            return
            
        if not 0 <= index < len(self):
            raise IndexError("Vector index out of range")
            
        elements = Storage.get_json(self._elements_prefix)
        elements[index] = value
        Storage.set_json(self._elements_prefix, elements)
    
    def __delitem__(self, index: int) -> None:
        if isinstance(index, slice):
            elements = Storage.get_json(self._elements_prefix)
            del elements[index]
            Storage.set_json(self._elements_prefix, elements)
            Storage.set_json(self._length_prefix, len(elements))
            return
            
        if not 0 <= index < len(self):
            raise IndexError("Vector index out of range")
            
        elements = Storage.get_json(self._elements_prefix)
        del elements[index]
        Storage.set_json(self._elements_prefix, elements)
        Storage.set_json(self._length_prefix, len(elements))
    
    def __len__(self) -> int:
        return Storage.get_json(self._length_prefix) or 0
    
    def insert(self, index: int, value: T) -> None:
        if not 0 <= index <= len(self):
            raise IndexError("Vector index out of range")
            
        elements = Storage.get_json(self._elements_prefix) or []
        elements.insert(index, value)
        Storage.set_json(self._elements_prefix, elements)
        Storage.set_json(self._length_prefix, len(elements))
    
    def swap_remove(self, index: int) -> T:
        """
        Removes an element from the vector and returns it,
        replacing it with the last element of the vector.
        This operation is O(1).
        """
        if not 0 <= index < len(self):
            raise IndexError("Vector index out of range")
            
        elements = Storage.get_json(self._elements_prefix)
        last_idx = len(elements) - 1
        
        if index != last_idx:
            # Swap with last element
            elements[index] = elements[last_idx]
        
        # Remove and return the element
        value = elements.pop()
        Storage.set_json(self._elements_prefix, elements)
        Storage.set_json(self._length_prefix, len(elements))
        return value