from collections.abc import MutableSet
from typing import Generic, Iterator, TypeVar

from ..storage import Storage

T = TypeVar('T')

class UnorderedSet(MutableSet[T], Generic[T]):
    """
    A set implementation that allows O(1) removals using swap-remove strategy.
    Maintains indices for fast lookups while allowing quick removals.
    """
    
    def __init__(self, prefix: str):
        self.prefix = prefix
        self._elements_prefix = f"{prefix}:elements"
        self._indices_prefix = f"{prefix}:indices"
        
        if not Storage.has(self._elements_prefix):
            Storage.set_json(self._elements_prefix, [])
            Storage.set_json(self._indices_prefix, {})
    
    def add(self, element: T) -> None:
        indices = Storage.get_json(self._indices_prefix) or {}
        str_element = str(element)
        
        if str_element not in indices:
            elements = Storage.get_json(self._elements_prefix) or []
            index = len(elements)
            indices[str_element] = index
            elements.append(str_element)
            
            Storage.set_json(self._indices_prefix, indices)
            Storage.set_json(self._elements_prefix, elements)
    
    def discard(self, element: T) -> None:
        indices = Storage.get_json(self._indices_prefix) or {}
        str_element = str(element)
        
        if str_element in indices:
            index = indices[str_element]
            elements = Storage.get_json(self._elements_prefix)
            
            # Swap with last element if not last
            last_idx = len(elements) - 1
            if index != last_idx:
                last_element = elements[last_idx]
                elements[index] = last_element
                indices[last_element] = index
            
            # Remove last element
            elements.pop()
            del indices[str_element]
            
            Storage.set_json(self._indices_prefix, indices)
            Storage.set_json(self._elements_prefix, elements)
    
    def __contains__(self, element: T) -> bool:
        indices = Storage.get_json(self._indices_prefix) or {}
        return str(element) in indices
    
    def __iter__(self) -> Iterator[T]:
        elements = Storage.get_json(self._elements_prefix) or []
        return iter(elements)
    
    def __len__(self) -> int:
        elements = Storage.get_json(self._elements_prefix) or []
        return len(elements)