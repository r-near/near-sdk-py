# Import the collection we want to test
from near_sdk_py.collections.unordered_set import UnorderedSet


def test_unordered_set_basics(setup_storage_mocks, dump_storage):
    """Test basic UnorderedSet operations"""
    # Create a new UnorderedSet
    test_set = UnorderedSet("items")

    # Add 1 item
    test_set.add("bulk_item_0")

    # Check length
    assert len(test_set) == 1
    assert not test_set.is_empty()

    # Check membership
    assert "bulk_item_0" in test_set

    dump_storage()

    # Remove an item
    test_set.remove("bulk_item_0")
    assert "bulk_item_0" not in test_set
    assert len(test_set) == 0
