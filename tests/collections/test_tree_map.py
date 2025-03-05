"""
Unit tests for TreeMap collection.
"""

import pytest

# Import the collection we want to test
from near_sdk_py.collections.tree_map import TreeMap


def test_tree_map_basics(setup_storage_mocks):
    """Test basic TreeMap operations"""
    # Create a new TreeMap
    test_map = TreeMap("test_map")

    # Initially the map should be empty
    assert len(test_map) == 0
    assert test_map.is_empty()

    # Add some key-value pairs
    test_map[5] = "value5"
    test_map[3] = "value3"
    test_map[7] = "value7"

    # Check length
    assert len(test_map) == 3
    assert not test_map.is_empty()

    # Check membership
    assert 3 in test_map
    assert 5 in test_map
    assert 7 in test_map
    assert 4 not in test_map

    # Get values
    assert test_map[3] == "value3"
    assert test_map[5] == "value5"
    assert test_map[7] == "value7"

    # Use get method with default
    assert test_map.get(3) == "value3"
    assert test_map.get(4) is None
    assert test_map.get(4, "default") == "default"

    # Update existing keys
    test_map[5] = "updated5"
    assert test_map[5] == "updated5"
    assert len(test_map) == 3  # Length should not change

    # Remove a key-value pair
    del test_map[3]
    assert 3 not in test_map
    assert len(test_map) == 2

    # Remove using remove method
    removed_value = test_map.remove(7)
    assert removed_value == "value7"
    assert 7 not in test_map
    assert len(test_map) == 1

    # Clear the map
    test_map.clear()
    assert len(test_map) == 0
    assert test_map.is_empty()


def test_tree_map_iteration(setup_storage_mocks, dump_storage):
    """Test TreeMap iteration capabilities and ordering"""
    test_map = TreeMap("test_map")

    # Add some key-value pairs in random order
    test_map[5] = "value5"
    test_map[2] = "value2"
    test_map[8] = "value8"
    test_map[1] = "value1"
    test_map[3] = "value3"
    test_map[7] = "value7"

    # Test iteration over keys (should be in sorted order)
    keys = list(test_map)
    assert keys == [1, 2, 3, 5, 7, 8]

    # Test keys() method
    keys_list = test_map.keys()
    assert keys_list == [1, 2, 3, 5, 7, 8]

    # Test values() method (should be in key-sorted order)
    values_list = test_map.values()
    assert values_list == ["value1", "value2", "value3", "value5", "value7", "value8"]

    # Test items() method
    items_list = test_map.items()
    expected_items = [
        (1, "value1"),
        (2, "value2"),
        (3, "value3"),
        (5, "value5"),
        (7, "value7"),
        (8, "value8"),
    ]
    assert items_list == expected_items


def test_tree_map_range_queries(setup_storage_mocks):
    """Test TreeMap range query capabilities"""
    test_map = TreeMap("test_map")

    # Add some key-value pairs
    for i in range(1, 11):
        test_map[i] = f"value{i}"

    # Test range queries
    assert test_map.range(3, 7) == [3, 4, 5, 6]  # inclusive start, exclusive end
    assert test_map.range(None, 5) == [1, 2, 3, 4]  # from beginning to exclusive end
    assert test_map.range(8, None) == [8, 9, 10]  # from inclusive start to end
    assert test_map.range() == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # entire range


def test_tree_map_floor_ceiling(setup_storage_mocks):
    """Test TreeMap floor and ceiling key operations"""
    test_map = TreeMap("test_map")

    # Initially empty
    assert test_map.floor_key(5) is None
    assert test_map.ceiling_key(5) is None

    # Add some key-value pairs
    for i in [1, 3, 5, 7, 9]:
        test_map[i] = f"value{i}"

    # Test floor_key (greatest key ≤ target)
    assert test_map.floor_key(0) is None
    assert test_map.floor_key(1) == 1
    assert test_map.floor_key(2) == 1
    assert test_map.floor_key(3) == 3
    assert test_map.floor_key(4) == 3
    assert test_map.floor_key(5) == 5
    assert test_map.floor_key(6) == 5
    assert test_map.floor_key(10) == 9

    # Test ceiling_key (smallest key ≥ target)
    assert test_map.ceiling_key(0) == 1
    assert test_map.ceiling_key(1) == 1
    assert test_map.ceiling_key(2) == 3
    assert test_map.ceiling_key(3) == 3
    assert test_map.ceiling_key(4) == 5
    assert test_map.ceiling_key(5) == 5
    assert test_map.ceiling_key(8) == 9
    assert test_map.ceiling_key(9) == 9
    assert test_map.ceiling_key(10) is None


def test_tree_map_min_max(setup_storage_mocks):
    """Test TreeMap min_key and max_key operations"""
    test_map = TreeMap("test_map")

    # Initially empty
    assert test_map.min_key() is None
    assert test_map.max_key() is None

    # Add some key-value pairs in random order
    test_map[5] = "value5"
    assert test_map.min_key() == 5
    assert test_map.max_key() == 5

    test_map[3] = "value3"
    assert test_map.min_key() == 3
    assert test_map.max_key() == 5

    test_map[7] = "value7"
    assert test_map.min_key() == 3
    assert test_map.max_key() == 7

    test_map[1] = "value1"
    assert test_map.min_key() == 1
    assert test_map.max_key() == 7

    # Remove min and max
    del test_map[1]
    assert test_map.min_key() == 3

    del test_map[7]
    assert test_map.max_key() == 5


def test_tree_map_errors(setup_storage_mocks):
    """Test error handling in TreeMap"""
    test_map = TreeMap("test_map")

    # Add a key-value pair
    test_map[1] = "value1"

    # Try to get a non-existent key
    with pytest.raises(KeyError):
        _ = test_map[2]

    # Try to delete a non-existent key
    with pytest.raises(KeyError):
        del test_map[2]


def test_tree_map_string_keys(setup_storage_mocks):
    """Test TreeMap with string keys"""
    test_map = TreeMap("test_map")

    # Add key-value pairs with string keys
    test_map["apple"] = "red"
    test_map["banana"] = "yellow"
    test_map["cherry"] = "red"
    test_map["date"] = "brown"

    # Check iteration order (alphabetical)
    assert list(test_map) == ["apple", "banana", "cherry", "date"]

    # Check range queries
    assert test_map.range("banana", "date") == ["banana", "cherry"]

    # Check floor and ceiling
    assert test_map.floor_key("blueberry") == "banana"
    assert test_map.ceiling_key("blueberry") == "cherry"


def test_multiple_tree_maps(setup_storage_mocks):
    """Test multiple TreeMaps with different prefixes"""
    map1 = TreeMap("map1")
    map2 = TreeMap("map2")

    # Add key-value pairs to both maps
    map1[1] = "value1_1"
    map1[3] = "value1_3"

    map2[1] = "value2_1"
    map2[2] = "value2_2"

    # Verify the maps are independent
    assert len(map1) == 2
    assert len(map2) == 2

    assert 1 in map1
    assert 1 in map2
    assert map1[1] == "value1_1"
    assert map2[1] == "value2_1"

    assert 3 in map1
    assert 3 not in map2

    assert 2 not in map1
    assert 2 in map2

    # Verify iterations are independent
    assert set(map1.keys()) == {1, 3}
    assert set(map2.keys()) == {1, 2}


def test_tree_map_edge_cases(setup_storage_mocks):
    """Test TreeMap edge cases"""
    test_map = TreeMap("test_map")

    # Test with negative keys
    test_map[-5] = "negative"
    test_map[0] = "zero"
    test_map[5] = "positive"

    assert list(test_map.keys()) == [-5, 0, 5]

    # Test with very large keys
    test_map[1000000] = "large"
    assert test_map[1000000] == "large"

    # Test with string keys in a separate TreeMap
    # (TreeMap requires all keys to be comparable with each other)
    string_map = TreeMap("string_map")
    string_map["apple"] = "fruit"
    string_map["banana"] = "fruit"
    string_map["string"] = "string_value"

    assert "string" in string_map
    assert string_map["string"] == "string_value"
    assert list(string_map.keys()) == ["apple", "banana", "string"]

    # Test find operations with non-existent keys
    assert test_map.get(999) is None
    assert test_map.floor_key(999) == 5
    assert test_map.ceiling_key(6) == 1000000
