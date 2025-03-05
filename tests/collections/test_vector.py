"""
Unit tests for Vector collection.
"""

import pytest

# Import the collection we want to test
from near_sdk_py.collections.vector import Vector


def test_vector_basics(setup_storage_mocks):
    """Test basic Vector operations"""
    # Create a new Vector
    test_vec = Vector("test_vec")

    # Initially the vector should be empty
    assert len(test_vec) == 0
    assert test_vec.is_empty()

    # Append some elements
    test_vec.append("item1")
    test_vec.append("item2")
    test_vec.append("item3")

    # Check length
    assert len(test_vec) == 3
    assert not test_vec.is_empty()

    # Access elements by index
    assert test_vec[0] == "item1"
    assert test_vec[1] == "item2"
    assert test_vec[2] == "item3"

    # Test negative indexing
    assert test_vec[-1] == "item3"
    assert test_vec[-2] == "item2"
    assert test_vec[-3] == "item1"

    # Test slicing
    assert test_vec[0:2] == ["item1", "item2"]
    assert test_vec[1:] == ["item2", "item3"]
    assert test_vec[:2] == ["item1", "item2"]

    # Modify an element
    test_vec[1] = "modified"
    assert test_vec[1] == "modified"

    # Use get with default value
    assert test_vec.get(1) == "modified"
    assert test_vec.get(10, "default") == "default"


def test_vector_pop_and_swap(setup_storage_mocks):
    """Test Vector pop and swap_remove operations"""
    test_vec = Vector("test_vec")

    # Add some elements
    test_vec.append("item1")
    test_vec.append("item2")
    test_vec.append("item3")
    test_vec.append("item4")

    # Test pop from end
    assert test_vec.pop() == "item4"
    assert len(test_vec) == 3

    # Test pop from index
    assert test_vec.pop(0) == "item1"
    assert len(test_vec) == 2
    assert test_vec[0] == "item2"  # item2 shifted to index 0

    # Test swap_remove (should swap with last element)
    test_vec.append("item5")  # Now we have ["item2", "item3", "item5"]
    assert test_vec.swap_remove(0) == "item2"
    assert len(test_vec) == 2
    assert test_vec[0] == "item5"  # item5 swapped to index 0
    assert test_vec[1] == "item3"  # item3 stayed at index 1


def test_vector_errors(setup_storage_mocks):
    """Test Vector error handling"""
    test_vec = Vector("test_vec")

    # Test index out of bounds
    with pytest.raises(IndexError):
        _ = test_vec[0]

    test_vec.append("item1")

    # Test negative index out of bounds
    with pytest.raises(IndexError):
        _ = test_vec[-2]

    # Test pop from empty vector
    test_vec.pop()  # Remove the only item
    with pytest.raises(IndexError):
        test_vec.pop()


def test_vector_iteration(setup_storage_mocks):
    """Test Vector iteration"""
    test_vec = Vector("test_vec")

    # Add some elements
    items = [b"item1", b"item2", b"item3"]
    for item in items:
        test_vec.append(item)

    # Test iteration
    for i, item in enumerate(test_vec):
        assert item == items[i]

    # Test list conversion
    assert list(test_vec) == items


def test_vector_extend(setup_storage_mocks):
    """Test Vector extend method"""
    test_vec = Vector("test_vec")

    # Add some initial elements
    test_vec.append("item1")

    # Extend with a list
    test_vec.extend(["item2", "item3", "item4"])

    # Check length and elements
    assert len(test_vec) == 4
    assert test_vec[0] == "item1"
    assert test_vec[1] == "item2"
    assert test_vec[2] == "item3"
    assert test_vec[3] == "item4"

    # Extend with another iterable (like a set)
    test_vec.extend({"item5", "item6"})

    # Check length
    assert len(test_vec) == 6

    # Since sets are unordered, just check that the items are in the vector
    items = set(test_vec[4:])
    assert "item5" in items
    assert "item6" in items


def test_vector_clear(setup_storage_mocks):
    """Test Vector clear method"""
    test_vec = Vector("test_vec")

    # Add some elements
    test_vec.extend(["item1", "item2", "item3"])
    assert len(test_vec) == 3

    # Clear the vector
    test_vec.clear()
    assert len(test_vec) == 0
    assert test_vec.is_empty()

    # Should be able to add new elements after clearing
    test_vec.append("new_item")
    assert len(test_vec) == 1
    assert test_vec[0] == "new_item"
