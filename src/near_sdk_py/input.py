"""
Input handling utilities for NEAR smart contracts.
"""

import json
from typing import Any
from .contract import InvalidInput

import near


class Input:
    """Higher-level input operations"""

    @staticmethod
    def bytes() -> bytes:
        """Gets the raw bytes input"""
        return near.input()

    @staticmethod
    def string() -> str:
        """Gets the input as UTF-8 string"""
        return near.input().decode("utf-8")

    @staticmethod
    def json() -> Any:
        """Gets the input as parsed JSON"""
        try:
            return json.loads(Input.string())
        except Exception as e:
            raise InvalidInput(f"Failed to decode JSON input: {e}")
