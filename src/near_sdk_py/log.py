"""
Logging utilities for NEAR smart contracts.
"""

import json
from typing import Any, Dict

import near


class Log:
    """Logging utilities for emitting log messages and events from NEAR smart contracts"""

    @staticmethod
    def info(message: str):
        """Logs an informational message"""
        near.log_utf8(f"INFO: {message}")

    @staticmethod
    def warning(message: str):
        """Logs a warning message"""
        near.log_utf8(f"WARNING: {message}")

    @staticmethod
    def error(message: str):
        """Logs an error message"""
        near.log_utf8(f"ERROR: {message}")

    @staticmethod
    def debug(message: str):
        """Logs a debug message"""
        near.log_utf8(f"DEBUG: {message}")

    @staticmethod
    def event(event_type: str, data: Dict[str, Any]):
        """
        Logs a structured event following the NEP standard for events
        https://nomicon.io/Standards/EventsFormat
        """
        event_data = {
            "standard": "nep171",
            "version": "1.0.0",
            "event": event_type,
            "data": data,
        }
        near.log_utf8(f"EVENT_JSON:{json.dumps(event_data)}")
