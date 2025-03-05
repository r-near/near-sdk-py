"""
Unit tests for LookupMap collection.
"""

import pytest

# Import the collection we want to test
from near_sdk_py.collections.lookup_map import LookupMap


def test_lookup_map_basics(setup_storage_mocks):
    """Test basic LookupMap operations"""
    # Create a new LookupMap
    test_map = LookupMap("test_map")

    # Initially the map should be empty
    assert len(test_map) == 0
    assert test_map.is_empty()

    # Add some key-value pairs
    test_map["key1"] = "value1"
    test_map["key2"] = "value2"
    test_map["key3"] = "value3"

    # Check length
    assert len(test_map) == 3
    assert not test_map.is_empty()

    # Check membership
    assert "key1" in test_map
    assert "key2" in test_map
    assert "key3" in test_map
    assert "key4" not in test_map

    # Get values
    assert test_map["key1"] == "value1"
    assert test_map["key2"] == "value2"
    assert test_map["key3"] == "value3"

    # Use get method with default
    assert test_map.get("key1") == "value1"
    assert test_map.get("key4") is None
    assert test_map.get("key4", "default") == "default"

    # Use set method
    test_map.set("key4", "value4")
    assert test_map["key4"] == "value4"
    assert len(test_map) == 4

    # Update existing keys
    test_map["key1"] = "updated1"
    assert test_map["key1"] == "updated1"
    assert len(test_map) == 4  # Length should not change

    # Remove a key-value pair
    del test_map["key2"]
    assert "key2" not in test_map
    assert len(test_map) == 3

    # Remove using remove method
    removed_value = test_map.remove("key3")
    assert removed_value == "value3"
    assert "key3" not in test_map
    assert len(test_map) == 2

    # Remove non-existent key
    removed_value = test_map.remove("nonexistent")
    assert removed_value is None
    assert len(test_map) == 2

    # Clear the map
    test_map.clear()
    assert len(test_map) == 0
    assert test_map.is_empty()


def test_lookup_map_errors(setup_storage_mocks):
    """Test error handling in LookupMap"""
    test_map = LookupMap("test_map")

    # Add a key-value pair
    test_map["key1"] = "value1"

    # Try to get a non-existent key
    with pytest.raises(KeyError):
        _ = test_map["nonexistent"]

    # Try to delete a non-existent key
    with pytest.raises(KeyError):
        del test_map["nonexistent"]


def test_lookup_map_with_different_types(setup_storage_mocks):
    """Test LookupMap with different types of keys and values"""
    test_map = LookupMap("test_map")

    # Test with different key types
    test_map[42] = "int_key"
    test_map[3.14] = "float_key"
    test_map[True] = "bool_key"
    test_map["string"] = "string_key"

    # Check they all exist
    assert 42 in test_map
    assert 3.14 in test_map
    assert True in test_map
    assert "string" in test_map

    # Test with different value types
    test_map["int_value"] = 42
    test_map["float_value"] = 3.14
    test_map["bool_value"] = True
    test_map["string_value"] = "string"
    test_map["list_value"] = [1, 2, 3]
    test_map["dict_value"] = {"a": 1, "b": 2}

    # Check values
    assert test_map["int_value"] == 42
    assert test_map["float_value"] == 3.14
    assert test_map["bool_value"] is True
    assert test_map["string_value"] == "string"
    assert test_map["list_value"] == [1, 2, 3]
    assert test_map["dict_value"] == {"a": 1, "b": 2}


def test_multiple_lookup_maps(setup_storage_mocks):
    """Test multiple LookupMaps with different prefixes"""
    map1 = LookupMap("map1")
    map2 = LookupMap("map2")

    # Add key-value pairs to both maps
    map1["shared_key"] = "value1"
    map1["only_in_map1"] = "value_map1"

    map2["shared_key"] = "value2"
    map2["only_in_map2"] = "value_map2"

    # Verify the maps are independent
    assert len(map1) == 2
    assert len(map2) == 2

    assert "shared_key" in map1
    assert "shared_key" in map2
    assert map1["shared_key"] == "value1"
    assert map2["shared_key"] == "value2"

    assert "only_in_map1" in map1
    assert "only_in_map1" not in map2

    assert "only_in_map2" not in map1
    assert "only_in_map2" in map2

    # Removing from one map should not affect the other
    del map1["shared_key"]
    assert "shared_key" not in map1
    assert "shared_key" in map2
