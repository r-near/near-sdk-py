"""
Pytest configuration and shared fixtures for NEAR SDK tests.
"""

import json
from typing import Dict, Optional

import pytest

# Mock storage - this will simulate the blockchain storage
mock_storage: Dict[str, bytes] = {}


# Mock near module functions
def mock_storage_read(key: str) -> Optional[bytes]:
    """Mock implementation of near.storage_read"""
    return mock_storage.get(key)


def mock_storage_write(key: str, value: bytes) -> Optional[bytes]:
    """Mock implementation of near.storage_write"""
    previous = mock_storage.get(key)
    mock_storage[key] = value
    return previous


def mock_storage_remove(key: str) -> Optional[bytes]:
    """Mock implementation of near.storage_remove"""
    previous = mock_storage.get(key)
    if key in mock_storage:
        del mock_storage[key]
    return previous


def mock_storage_has_key(key: str) -> bool:
    """Mock implementation of near.storage_has_key"""
    return key in mock_storage


@pytest.fixture
def setup_storage_mocks(monkeypatch):
    """
    Fixture to set up mocks for near module functions.

    This fixture replaces NEAR storage functions with mock implementations
    that use an in-memory dictionary instead of blockchain storage.
    It also resets the mock storage before each test to ensure isolation.

    Usage:
        def test_something(setup_storage_mocks):
            # Test code that interacts with NEAR storage
            # The storage will be mocked in-memory

    Returns:
        The mock_storage dictionary for inspection in tests if needed
    """
    # Clear the mock storage before each test
    mock_storage.clear()

    # Patch the near module functions
    import near

    monkeypatch.setattr(near, "storage_read", mock_storage_read)
    monkeypatch.setattr(near, "storage_write", mock_storage_write)
    monkeypatch.setattr(near, "storage_remove", mock_storage_remove)
    monkeypatch.setattr(near, "storage_has_key", mock_storage_has_key)

    # Return the mock_storage for inspection in tests if needed
    return mock_storage


@pytest.fixture
def dump_storage():
    """
    Fixture to print the contents of the mock storage for debugging.

    Usage:
        def test_something(setup_storage_mocks, dump_storage):
            # Test code
            dump_storage()  # Will print storage contents
    """

    def _dump_storage():
        print("\n--- Mock Storage Contents ---")
        for key, value_bytes in mock_storage.items():
            try:
                # Try to decode as JSON
                value_str = value_bytes.decode("utf-8")
                try:
                    value = json.loads(value_str)
                    print(f"{key}: {value}")
                except json.JSONDecodeError:
                    print(f"{key}: {value_str}")
            except UnicodeDecodeError:
                print(f"{key}: {value_bytes}")
        print("----------------------------")

    return _dump_storage
