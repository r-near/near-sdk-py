"""
Base collection class for NEAR persistent collections.
"""

from typing import Any, Dict

import near
from near_sdk_py.contract import StorageError

from .adapter import CollectionStorageAdapter


# Replace Enum with string constants
class PrefixType:
    """Constants for collection prefix types"""

    VECTOR = "v"
    LOOKUP_MAP = "m"
    UNORDERED_MAP = "u"
    LOOKUP_SET = "s"
    UNORDERED_SET = "o"
    TREE_MAP = "t"


class Collection:
    """Base class for all persistent collections"""

    def __init__(self, prefix: str, collection_type: str):
        """
        Initialize a collection with a unique prefix.

        Args:
            prefix: A unique string prefix for this collection
            collection_type: The type of collection (for metadata)
        """
        if not prefix:
            raise ValueError("Collection prefix cannot be empty")

        self._prefix = prefix
        self._collection_type = collection_type

        # Create metadata key
        self._metadata_key = f"{self._prefix}:meta"

        # Initialize metadata if it doesn't exist
        if not near.storage_has_key(self._metadata_key):
            metadata = {"type": collection_type, "length": 0, "version": "1.0.0"}
            CollectionStorageAdapter.write(self._metadata_key, metadata)

    def _get_metadata(self) -> Dict[str, Any]:
        """Gets the collection metadata"""
        result = CollectionStorageAdapter.read(self._metadata_key)
        if result is None:
            raise StorageError(f"Metadata missing for collection {self._prefix}")
        return result

    def _update_metadata(self, updates: Dict[str, Any]) -> None:
        """Updates the collection metadata"""
        metadata = self._get_metadata()
        metadata.update(updates)
        CollectionStorageAdapter.write(self._metadata_key, metadata)

    def _get_length(self) -> int:
        """Gets the collection length from metadata"""
        metadata = self._get_metadata()
        return int(metadata.get("length", 0))

    def _set_length(self, length: int) -> None:
        """Updates the collection length in metadata"""
        self._update_metadata({"length": length})

    def _make_key(self, key: Any) -> str:
        """Creates a storage key from a collection key"""
        serialized = CollectionStorageAdapter.serialize_key(key)
        return f"{self._prefix}:{serialized}"

    def _make_index_key(self, index: int) -> str:
        """Creates a storage key for an index"""
        return f"{self._prefix}:{index}"

    def __len__(self) -> int:
        """Returns the number of elements in the collection"""
        return self._get_length()

    def is_empty(self) -> bool:
        """Returns True if the collection is empty"""
        return len(self) == 0

    def clear(self) -> None:
        """Removes all elements from the collection"""
        raise NotImplementedError("Must be implemented by subclasses")
