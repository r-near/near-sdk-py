"""
Higher-level storage operations for NEAR smart contracts.
"""

import json
from typing import Any, List, Optional, Union

import near
from .contract import StorageError


class Storage:
    """Higher-level storage operations"""

    @staticmethod
    def get(key: str) -> Optional[bytes]:
        """Gets a value from storage by key"""
        return near.storage_read(key)

    @staticmethod
    def get_string(key: str) -> Optional[str]:
        """Gets a UTF-8 string from storage by key"""
        value = near.storage_read(key)
        if value is not None:
            return value.decode("utf-8")
        return None

    @staticmethod
    def get_json(key: str) -> Optional[Any]:
        """Gets a JSON value from storage by key"""
        value = Storage.get_string(key)
        if value is not None:
            try:
                return json.loads(value)
            except Exception as e:
                raise StorageError(f"Failed to decode JSON for key {key}: {e}")
        return None

    @staticmethod
    def set(key: str, value: Union[str, bytes]) -> Optional[bytes]:
        """Sets a value in storage"""
        if isinstance(value, str):
            value = value.encode("utf-8")
        return near.storage_write(key, value)

    @staticmethod
    def set_json(key: str, value: Any) -> Optional[bytes]:
        """Sets a JSON value in storage"""
        json_str = json.dumps(value)
        return Storage.set(key, json_str)

    @staticmethod
    def remove(key: str) -> Optional[bytes]:
        """Removes a value from storage"""
        return near.storage_remove(key)

    @staticmethod
    def has(key: str) -> bool:
        """Checks if a key exists in storage"""
        return near.storage_has_key(key)

    @staticmethod
    def prefix_range(prefix: str) -> List[bytes]:
        """
        Returns a list of keys with the given prefix.
        This is a simplified version as the near-sdk-rs has range and iterator methods
        which would require more complex implementation to replicate in Python.
        """
        # This would need a lower-level implementation to be efficient
        # Just a placeholder to show the API design
        raise NotImplementedError("Storage iteration is not implemented yet")
