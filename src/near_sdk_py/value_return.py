"""
Utilities for returning values from contract methods.
"""

import json
from typing import Any

import near


class ValueReturn:
    """
    Utilities for returning values from contract methods
    """

    @staticmethod
    def bytes(value: bytes):
        """Returns raw bytes"""
        near.value_return(value)

    @staticmethod
    def string(value: str):
        """Returns a UTF-8 string"""
        near.value_return(value.encode("utf-8"))

    @staticmethod
    def json(value: Any):
        """Returns a JSON value"""
        json_str = json.dumps(value)
        near.value_return(json_str.encode("utf-8"))
