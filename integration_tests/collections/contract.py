"""
NEAR Python SDK Collections Test Contract

This contract implements various operations on all collection types
to test their functionality and measure gas usage on-chain.
"""

from near_sdk_py import call
from near_sdk_py.collections.vector import Vector
from near_sdk_py.collections.lookup_map import LookupMap
from near_sdk_py.collections.lookup_set import LookupSet
from near_sdk_py.collections.unordered_map import UnorderedMap
from near_sdk_py.collections.tree_map import TreeMap
import json


class Insertable:
    """A class for items to be inserted into collections."""

    def __init__(self, index=0, data="", is_valid=True):
        self.index = index
        self.data = data
        self.is_valid = is_valid


class Collection:
    """Enum-like class for collection types."""

    ITERABLE_MAP = "IterableMap"
    LOOKUP_MAP = "LookupMap"
    LOOKUP_SET = "LookupSet"
    TREE_MAP = "TreeMap"
    VECTOR = "Vector"
    UNORDERED_MAP = "UnorderedMap"


class CollectionsTestContract:
    """Test contract for NEAR Python SDK collections."""

    def __init__(self):
        self.vector = Vector("vec")
        self.lookup_map = LookupMap("lookup_map")
        self.lookup_set = LookupSet("lookup_set")
        self.unordered_map = UnorderedMap("unordered_map")
        self.tree_map = TreeMap("tree_map")

    def _create_insertable(self) -> dict:
        """Create a sample item to insert into collections."""
        return {
            "index": 0,
            "data": "scatter cinnamon wheel useless please rough situate iron eager noise try evolve runway neglect onion",
            "is_valid": True,
        }

    @call
    def new(self) -> bool:
        """Initialize the contract."""
        return True

    @call
    def insert(self, col: str, index_offset: int, iterations: int) -> int:
        """Insert elements into a collection."""
        insertable = self._create_insertable()
        count = 0

        for i in range(iterations + 1):
            insertable["index"] = i + index_offset
            self._insert_op(col, insertable.copy())
            count += 1

        return count

    @call
    def remove(self, col: str, iterations: int) -> int:
        """Remove elements from a collection."""
        insertable = self._create_insertable()
        count = 0

        for i in range(iterations + 1):
            insertable["index"] = i
            self._remove_op(col, insertable)
            count += 1

        return count

    @call
    def contains(self, col: str, repeat: int, iterations: int) -> bool:
        """Test contains operations."""
        insertable = self._create_insertable()

        for i in range(iterations + 1):
            insertable["index"] = i
            for _ in range(repeat):
                self._contains_op(col, insertable)

        return True

    @call
    def iter(self, col: str, repeat: int, iterations: int) -> int:
        """Test iteration operations."""
        count = 0

        for _ in range(iterations + 1):
            for _ in range(repeat):
                count += self._iter_op(col, iterations)

        return count

    @call
    def nth(self, col: str, repeat: int, iterations: int) -> bool:
        """Test nth element access operations."""
        for i in range(iterations + 1):
            for _ in range(repeat):
                self._nth_op(col, i % max(1, iterations))

        return True

    def _insert_op(self, col: str, val: dict) -> None:
        """Insert operation for a specific collection type."""
        if col == Collection.VECTOR:
            self.vector.append(val)
        elif col == Collection.LOOKUP_MAP:
            self.lookup_map[val["index"]] = val
        elif col == Collection.LOOKUP_SET:
            self.lookup_set.add(json.dumps(val))
        elif col == Collection.UNORDERED_MAP:
            self.unordered_map[val["index"]] = val
        elif col == Collection.TREE_MAP:
            self.tree_map[val["index"]] = val

    def _remove_op(self, col: str, val: dict) -> None:
        """Remove operation for a specific collection type."""
        if col == Collection.VECTOR:
            if not self.vector.is_empty():
                self.vector.swap_remove(self.vector.len() - 1)
        elif col == Collection.LOOKUP_MAP:
            if val["index"] in self.lookup_map:
                self.lookup_map.remove(val["index"])
        elif col == Collection.LOOKUP_SET:
            val_str = json.dumps(val)
            if val_str in self.lookup_set:
                self.lookup_set.remove(val_str)
        elif col == Collection.UNORDERED_MAP:
            if val["index"] in self.unordered_map:
                del self.unordered_map[val["index"]]
        elif col == Collection.TREE_MAP:
            if val["index"] in self.tree_map:
                del self.tree_map[val["index"]]

    def _contains_op(self, col: str, val: dict) -> bool:
        """Contains operation for a specific collection type."""
        if col == Collection.LOOKUP_MAP:
            return val["index"] in self.lookup_map
        elif col == Collection.LOOKUP_SET:
            return json.dumps(val) in self.lookup_set
        elif col == Collection.UNORDERED_MAP:
            return val["index"] in self.unordered_map
        elif col == Collection.TREE_MAP:
            return val["index"] in self.tree_map
        # Vector doesn't have a standard contains method
        return False

    def _iter_op(self, col: str, take: int) -> int:
        """Iteration operation for a specific collection type."""
        count = 0

        # Only iterable collections
        if col == Collection.VECTOR:
            for _, _ in enumerate(self.vector):
                if count >= take:
                    break
                count += 1
        elif col == Collection.UNORDERED_MAP:
            for _, _ in enumerate(self.unordered_map):
                if count >= take:
                    break
                count += 1
        elif col == Collection.TREE_MAP:
            for _, _ in enumerate(self.tree_map):
                if count >= take:
                    break
                count += 1

        return count

    def _nth_op(self, col: str, element_idx: int) -> bool:
        """Nth element access operation for a specific collection type."""
        # Only iterable collections
        if col == Collection.VECTOR:
            if element_idx < len(self.vector):
                _ = self.vector[element_idx]
                return True
        elif col == Collection.UNORDERED_MAP:
            keys = list(self.unordered_map.keys())
            if element_idx < len(keys):
                _ = self.unordered_map[keys[element_idx]]
                return True
        elif col == Collection.TREE_MAP:
            keys = list(self.tree_map.keys())
            if element_idx < len(keys):
                _ = self.tree_map[keys[element_idx]]
                return True

        return False


# Export contract methods
contract = CollectionsTestContract()
new = contract.new
insert = contract.insert
remove = contract.remove
contains = contract.contains
iter = contract.iter
nth = contract.nth
