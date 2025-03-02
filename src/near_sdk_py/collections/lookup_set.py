from collections.abc import MutableSet
from typing import Generic, Iterator, TypeVar

from ..storage import Storage

T = TypeVar('T')

class LookupSet(MutableSet[T], Generic[T]):
    """
    A persistent set-like collection that implements the MutableSet interface.
    Elements are stored with a prefix to provide namespace separation for different collections.
    """
    
    def __init__(self, prefix: str):
        self.prefix = prefix
        self._elements_prefix = f"{prefix}:elements"
        
        # Initialize elements set if it doesn't exist
        if not Storage.has(self._elements_prefix):
            Storage.set_json(self._elements_prefix, [])
    
    def _get_key(self, element: T) -> str:
        """Convert an element into its storage representation"""
        return f"{self.prefix}:{str(element)}"
    
    def add(self, element: T) -> None:
        storage_key = self._get_key(element)
        if not Storage.has(storage_key):
            elements = Storage.get_json(self._elements_prefix) or []
            elements.append(str(element))
            Storage.set_json(self._elements_prefix, elements)
            Storage.set_json(storage_key, True)
    
    def discard(self, element: T) -> None:
        storage_key = self._get_key(element)
        if Storage.has(storage_key):
            Storage.remove(storage_key)
            elements = Storage.get_json(self._elements_prefix) or []
            elements.remove(str(element))
            Storage.set_json(self._elements_prefix, elements)
    
    def __contains__(self, element: T) -> bool:
        storage_key = self._get_key(element)
        return Storage.has(storage_key)
    
    def __iter__(self) -> Iterator[T]:
        elements = Storage.get_json(self._elements_prefix) or []
        return iter(elements)
    
    def __len__(self) -> int:
        elements = Storage.get_json(self._elements_prefix) or []
        return len(elements)