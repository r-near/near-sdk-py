"""
Tests for handling bytes objects in the collections.
"""

from near_sdk_py.collections.vector import Vector
from near_sdk_py.collections.lookup_map import LookupMap
from near_sdk_py.collections.unordered_map import UnorderedMap


def test_bytes_in_vector(setup_storage_mocks, dump_storage):
    """Test handling of bytes objects in Vector"""
    test_vec = Vector("test_vec")

    # Simple bytes
    simple_bytes = b"hello world"
    test_vec.append(simple_bytes)
    assert test_vec[0] == simple_bytes

    # Complex structure with bytes
    complex_obj = {
        "name": "test",
        "data": b"binary data",
        "nested": {"more_data": b"more binary data"},
    }
    test_vec.append(complex_obj)

    # Check that the complex object was recovered correctly
    retrieved = test_vec[1]
    assert retrieved["name"] == "test"
    assert retrieved["data"] == b"binary data"
    assert retrieved["nested"]["more_data"] == b"more binary data"


def test_bytes_as_keys(setup_storage_mocks, dump_storage):
    """Test using bytes as keys in maps"""
    test_map = LookupMap("test_map")

    # Use bytes as keys
    key1 = b"key1"
    key2 = b"key2"

    test_map[key1] = "value1"
    test_map[key2] = "value2"

    # Check that we can retrieve using bytes keys
    assert test_map[key1] == "value1"
    assert test_map[key2] == "value2"

    # Check membership
    assert key1 in test_map
    assert b"nonexistent" not in test_map


def test_bytes_as_values(setup_storage_mocks, dump_storage):
    """Test using bytes as values in maps"""
    test_map = UnorderedMap("test_map")

    # Use bytes as values
    test_map["key1"] = b"value1"
    test_map["key2"] = b"value2"

    # Check retrieval
    assert test_map["key1"] == b"value1"
    assert test_map["key2"] == b"value2"

    # Check values method
    values = test_map.values()
    assert b"value1" in values
    assert b"value2" in values


def test_complex_bytes_structures(setup_storage_mocks, dump_storage):
    """Test complex structures with bytes"""
    test_map = UnorderedMap("test_map")

    # Create a complex structure with bytes at various levels
    complex_structure = {
        "simple_bytes": b"simple value",
        "list_with_bytes": [b"item1", b"item2", "text_item"],
        "dict_with_bytes": {
            "key1": b"nested_value1",
            "key2": {"deeply_nested": b"deep value"},
        },
    }

    test_map["complex"] = complex_structure

    # Retrieve and verify
    retrieved = test_map["complex"]

    assert retrieved["simple_bytes"] == b"simple value"
    assert retrieved["list_with_bytes"][0] == b"item1"
    assert retrieved["list_with_bytes"][2] == "text_item"
    assert retrieved["dict_with_bytes"]["key1"] == b"nested_value1"
    assert retrieved["dict_with_bytes"]["key2"]["deeply_nested"] == b"deep value"

    # Dump storage for debugging if needed
    # dump_storage()
