"""
Storage adapter for serialization and deserialization of collection values.
"""

import base64
import json
from typing import Any, Optional

import near


class CollectionStorageAdapter:
    """
    Base adapter for handling storage operations with proper serialization.
    """

    @staticmethod
    def serialize_key(key: Any) -> str:
        """
        Serializes a key for storage.
        For bytes keys, use base64 encoding.
        """
        if isinstance(key, bytes):
            # Encode bytes as base64 string
            return "bytes:" + base64.b64encode(key).decode("utf-8")
        elif isinstance(key, (int, float, bool, str)):
            return str(key)
        return json.dumps(key)

    @staticmethod
    def serialize_value(value: Any) -> bytes:
        """
        Serializes a value for storage.
        Handles bytes objects specially to avoid JSON serialization issues.
        """
        if isinstance(value, bytes):
            # For raw bytes, prefix with a marker and return as is
            # The prefix allows us to identify raw bytes when deserializing
            return b"bytes:" + value
        elif isinstance(value, str):
            return value.encode("utf-8")
        else:
            # For complex objects or other types, convert to JSON
            # Handle special types that aren't JSON serializable
            def json_serialize_handler(obj):
                if isinstance(obj, bytes):
                    # Use base64 for bytes objects inside complex structures
                    return {"__bytes__": base64.b64encode(obj).decode("utf-8")}
                # Let the JSON serializer handle the TypeError for other non-serializable types
                return obj.__dict__ if hasattr(obj, "__dict__") else str(obj)

            return json.dumps(value, default=json_serialize_handler).encode("utf-8")

    @staticmethod
    def deserialize_value(value: bytes) -> Any:
        """
        Deserializes a value from storage.
        Handles the special encoding for bytes objects.
        """
        # Check if it's a raw bytes value (with our prefix)
        if value.startswith(b"bytes:"):
            return value[6:]  # Return the raw bytes without the prefix

        # Otherwise, try to decode as JSON
        try:
            value_str = value.decode("utf-8")

            try:
                # Parse the JSON
                parsed = json.loads(value_str)

                # Check if we need to convert any base64 strings back to bytes
                if isinstance(parsed, dict) and "__bytes__" in parsed:
                    return base64.b64decode(parsed["__bytes__"])

                # Recursively check for any bytes objects in the parsed structure
                def restore_bytes(obj):
                    if isinstance(obj, dict):
                        if "__bytes__" in obj and len(obj) == 1:
                            return base64.b64decode(obj["__bytes__"])
                        else:
                            return {k: restore_bytes(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [restore_bytes(item) for item in obj]
                    else:
                        return obj

                return restore_bytes(parsed)
            except json.JSONDecodeError:
                # If it's not valid JSON, return the string
                return value_str
        except UnicodeDecodeError:
            # If it's not a valid UTF-8 string, return the raw bytes
            return value

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
