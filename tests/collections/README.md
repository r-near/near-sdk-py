# NEAR Python SDK Collections Tests

This directory contains unit tests for the NEAR Python SDK collections. The tests use pytest and mock the NEAR runtime functions to simulate blockchain storage.

## Test Structure

- `conftest.py`: Contains shared fixtures and helpers for mocking the NEAR runtime
- `test_lookup_set.py`: Tests for LookupSet collection
- `test_lookup_map.py`: Tests for LookupMap collection
- `test_unordered_set.py`: Tests for UnorderedSet (IterableSet) collection
- `test_unordered_map.py`: Tests for UnorderedMap (IterableMap) collection
- `test_vector.py`: Tests for Vector collection
- `test_tree_map.py`: Tests for TreeMap collection

## Running the Tests

To run all tests:

```
pytest
```

To run tests for a specific collection:

```
pytest test_vector.py
```

To run a specific test:

```
pytest test_vector.py::test_vector_basics
```

To run tests with verbose output:

```
pytest -v
```

## Test Approach

These tests use pytest's monkeypatching to replace the NEAR runtime functions with mock implementations that use an in-memory dictionary for storage. This allows testing the collections without requiring the actual NEAR blockchain.

The `setup_storage_mocks` fixture in `conftest.py` replaces the following functions:

- `near.storage_read`
- `near.storage_write`
- `near.storage_remove`
- `near.storage_has_key`

## Test Coverage

The tests cover the following aspects of each collection:

1. **Basic operations**: add/set, get, remove, contains, length
2. **Error handling**: accessing non-existent keys, removing non-existent items
3. **Collection-specific features**:
   - Vector: indexing, slicing, append, pop, swap_remove, extend
   - Maps: key-value storage, updates
   - Sets: uniqueness, membership
   - TreeMap: ordering, range queries, floor/ceiling keys, min/max
4. **Edge cases**: empty collections, mixed types
5. **Multiple instances**: verifying independence of collections with different prefixes

## Debugging

The `dump_storage` fixture can be used to print the contents of the mock storage for debugging:

```python
def test_something(setup_storage_mocks, dump_storage):
    # Test code
    dump_storage()  # Will print storage contents
```