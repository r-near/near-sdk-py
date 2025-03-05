"""
Storage adapter for serialization and deserialization of collection values using MessagePack.
"""

import pickle
from typing import Any, Optional

import near


class CollectionStorageAdapter:
    """
    Base adapter for handling storage operations with MessagePack serialization.
    """

    @staticmethod
    def serialize_key(key: Any) -> str:
        """
        Serializes a key for storage.
        Simple types are converted to strings.
        Complex types are not supported as keys.
        """
        if isinstance(key, (int, float, bool, str, bytes)):
            return str(key)
        # For other types, try to convert to string
        return str(key)

    @staticmethod
    def serialize_value(value: Any) -> bytes:
        """
        Serializes a value for storage using MessagePack.
        MessagePack automatically handles primitive types, lists, dicts,
        and bytes objects natively.
        """
        # Use Pickle to serialize the value
        return pickle.dumps(value)

    @staticmethod
    def deserialize_value(value: bytes) -> Any:
        """
        Deserializes a value from storage using MessagePack.
        """
        # Decode as Pickle
        return pickle.loads(value)

    @staticmethod
    def write(key: str, value: Any) -> None:
        """Writes a value to storage with serialization"""
        serialized = CollectionStorageAdapter.serialize_value(value)
        near.storage_write(key, serialized)

    @staticmethod
    def read(key: str) -> Optional[Any]:
        """Reads and deserializes a value from storage"""
        value = near.storage_read(key)
        if value is None:
            return None
        return CollectionStorageAdapter.deserialize_value(value)

    @staticmethod
    def remove(key: str) -> bool:
        """Removes a key from storage, returns True if it existed"""
        prev_value = near.storage_remove(key)
        return prev_value is not None

    @staticmethod
    def has(key: str) -> bool:
        """Checks if a key exists in storage"""
        return near.storage_has_key(key)
