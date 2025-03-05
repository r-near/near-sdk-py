"""
Unit tests for LookupSet collection.
"""

import pytest

# Import the collection we want to test
from near_sdk_py.collections.lookup_set import LookupSet
from near_sdk_py.collections.adapter import CollectionStorageAdapter


def test_lookup_set_basics(setup_storage_mocks):
    """Test basic LookupSet operations"""
    # Create a new LookupSet
    test_set = LookupSet("test_set")

    # Initially the set should be empty
    assert len(test_set) == 0
    assert test_set.is_empty()

    # Add some elements
    test_set.add("item1")
    test_set.add("item2")
    test_set.add("item3")

    # Check length
    assert len(test_set) == 3
    assert not test_set.is_empty()

    # Check membership
    assert "item1" in test_set
    assert "item2" in test_set
    assert "item3" in test_set
    assert "item4" not in test_set

    # Remove an element
    test_set.remove("item2")
    assert "item2" not in test_set
    assert len(test_set) == 2

    # Discard an element that exists
    test_set.discard("item3")
    assert "item3" not in test_set
    assert len(test_set) == 1

    # Discard an element that doesn't exist (should not raise an error)
    test_set.discard("item4")
    assert len(test_set) == 1

    # Clear the set
    test_set.clear()
    assert len(test_set) == 0
    assert test_set.is_empty()


def test_lookup_set_errors(setup_storage_mocks):
    """Test error handling in LookupSet"""
    test_set = LookupSet("test_set")

    # Add an item
    test_set.add("item1")

    # Try to remove a non-existent item
    with pytest.raises(KeyError):
        test_set.remove("item2")

    # Add the same item again (should not change the length)
    test_set.add("item1")
    assert len(test_set) == 1


def test_lookup_set_with_different_types(setup_storage_mocks):
    """Test LookupSet with different types of values"""
    test_set = LookupSet("test_set")

    # Add different types of values
    test_set.add(42)
    test_set.add(3.14)
    test_set.add(True)
    test_set.add("string")

    # Check they all exist
    assert 42 in test_set
    assert 3.14 in test_set
    assert True in test_set
    assert "string" in test_set

    # Verify total count
    assert len(test_set) == 4

    # Check serialization by inspecting the mock storage
    mock_storage = setup_storage_mocks
    for key, value in mock_storage.items():
        if ":meta" not in key:  # Skip metadata
            # For LookupSet, values are just True
            assert CollectionStorageAdapter.deserialize_value(value) is True


def test_lookup_set_with_complex_types(setup_storage_mocks):
    """Test LookupSet with more complex types (dicts, lists)"""
    test_set = LookupSet("test_set")

    # Dictionaries need to be converted to strings for storage keys
    dict1 = {"name": "Alice", "age": 30}
    dict2 = {"name": "Bob", "age": 25}

    # Add dictionaries
    test_set.add(str(dict1))
    test_set.add(str(dict2))

    # Check membership
    assert str(dict1) in test_set
    assert str(dict2) in test_set
    assert str({"name": "Charlie", "age": 35}) not in test_set

    # Verify length
    assert len(test_set) == 2


def test_multiple_lookup_sets(setup_storage_mocks):
    """Test multiple LookupSets with different prefixes"""
    set1 = LookupSet("set1")
    set2 = LookupSet("set2")

    # Add elements to both sets
    set1.add("shared")
    set1.add("only_in_set1")

    set2.add("shared")
    set2.add("only_in_set2")

    # Verify the sets are independent
    assert len(set1) == 2
    assert len(set2) == 2

    assert "shared" in set1
    assert "shared" in set2

    assert "only_in_set1" in set1
    assert "only_in_set1" not in set2

    assert "only_in_set2" not in set1
    assert "only_in_set2" in set2

    # Removing from one set should not affect the other
    set1.remove("shared")
    assert "shared" not in set1
    assert "shared" in set2
