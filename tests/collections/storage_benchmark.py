"""
Benchmark storage usage for NEAR SDK Python collections.

This script measures storage units used by different collection operations,
which directly corresponds to gas costs in NEAR smart contracts.
"""

from rich.console import Console
from rich.table import Table
from typing import Dict, Tuple

# Import collections
from near_sdk_py.collections.vector import Vector
from near_sdk_py.collections.lookup_map import LookupMap
from near_sdk_py.collections.lookup_set import LookupSet
from near_sdk_py.collections.unordered_map import UnorderedMap
from near_sdk_py.collections.tree_map import TreeMap


def calculate_storage_size(storage_dict: Dict[str, bytes]) -> int:
    """Calculate the total storage size in bytes."""
    total_size = 0
    for key, value in storage_dict.items():
        # Add size of key (in bytes) and value
        total_size += len(key.encode("utf-8")) + len(value)
    return total_size


def measure_storage_operation(
    operation_func,
    mock_storage: Dict[str, bytes],
    item_count: int = 1,
    clear_storage: bool = True,
) -> Tuple[int, int]:
    """
    Measure the storage before and after an operation.

    Args:
        operation_func: Function to execute
        mock_storage: Dictionary used for storage mocking
        item_count: Number of items being processed
        clear_storage: Whether to clear storage before running

    Returns:
        Tuple of (initial_size, final_size)
    """
    if clear_storage:
        mock_storage.clear()

    # Measure storage before operation
    initial_size = calculate_storage_size(mock_storage)

    # Run the operation
    operation_func()

    # Measure storage after operation
    final_size = calculate_storage_size(mock_storage)

    return initial_size, final_size


def test_vector_storage_usage(setup_storage_mocks):
    """Benchmark storage usage for Vector operations with different amounts of data."""

    mock_storage = setup_storage_mocks
    console = Console()

    # Create a table for Vector results
    table = Table(title="Vector Storage Usage")
    table.add_column("Operation")
    table.add_column("Items")
    table.add_column("Initial Size (bytes)")
    table.add_column("Final Size (bytes)")
    table.add_column("Difference (bytes)")
    table.add_column("Bytes per Item")

    # Test vector creation and initialization
    initial, final = measure_storage_operation(
        lambda: Vector("test_vector"), mock_storage
    )
    table.add_row(
        "Creation", "0", str(initial), str(final), str(final - initial), "N/A"
    )

    # Test adding items (small strings)
    item_counts = [10, 100, 1000, 10000]

    for count in item_counts:

        def add_items():
            vec = Vector("test_vector")
            for i in range(count):
                vec.append(f"item{i}")

        initial, final = measure_storage_operation(add_items, mock_storage)
        bytes_per_item = (final - initial) / count if count > 0 else 0
        table.add_row(
            f"Append {count} small strings",
            str(count),
            str(initial),
            str(final),
            str(final - initial),
            f"{bytes_per_item:.2f}",
        )

    # Test adding items (large strings)
    for count in [10, 100, 1000]:

        def add_large_items():
            vec = Vector("test_vector")
            for i in range(count):
                vec.append("x" * 1000)  # 1KB string

        initial, final = measure_storage_operation(add_large_items, mock_storage)
        bytes_per_item = (final - initial) / count if count > 0 else 0
        table.add_row(
            f"Append {count} large strings (1KB)",
            str(count),
            str(initial),
            str(final),
            str(final - initial),
            f"{bytes_per_item:.2f}",
        )

    # Display the results
    console.print(table)


def test_lookup_map_storage_usage(setup_storage_mocks):
    """Benchmark storage usage for LookupMap operations with different amounts of data."""

    mock_storage = setup_storage_mocks
    console = Console()

    # Create a table for LookupMap results
    table = Table(title="LookupMap Storage Usage")
    table.add_column("Operation")
    table.add_column("Items")
    table.add_column("Initial Size (bytes)")
    table.add_column("Final Size (bytes)")
    table.add_column("Difference (bytes)")
    table.add_column("Bytes per Item")

    # Test map creation
    initial, final = measure_storage_operation(
        lambda: LookupMap("test_map"), mock_storage
    )
    table.add_row(
        "Creation", "0", str(initial), str(final), str(final - initial), "N/A"
    )

    # Test adding key-value pairs
    item_counts = [10, 100, 1000, 10000]

    for count in item_counts:

        def add_items():
            m = LookupMap("test_map")
            for i in range(count):
                m[f"key{i}"] = f"value{i}"

        initial, final = measure_storage_operation(add_items, mock_storage)
        bytes_per_item = (final - initial) / count if count > 0 else 0
        table.add_row(
            f"Set {count} small key-values",
            str(count),
            str(initial),
            str(final),
            str(final - initial),
            f"{bytes_per_item:.2f}",
        )

    # Display the results
    console.print(table)


def test_lookup_set_storage_usage(setup_storage_mocks):
    """Benchmark storage usage for LookupSet operations with different amounts of data."""

    mock_storage = setup_storage_mocks
    console = Console()

    # Create a table for LookupSet results
    table = Table(title="LookupSet Storage Usage")
    table.add_column("Operation")
    table.add_column("Items")
    table.add_column("Initial Size (bytes)")
    table.add_column("Final Size (bytes)")
    table.add_column("Difference (bytes)")
    table.add_column("Bytes per Item")

    # Test set creation
    initial, final = measure_storage_operation(
        lambda: LookupSet("test_set"), mock_storage
    )
    table.add_row(
        "Creation", "0", str(initial), str(final), str(final - initial), "N/A"
    )

    # Test adding items
    item_counts = [10, 100, 1000, 10000]

    for count in item_counts:

        def add_items():
            s = LookupSet("test_set")
            for i in range(count):
                s.add(f"item{i}")

        initial, final = measure_storage_operation(add_items, mock_storage)
        bytes_per_item = (final - initial) / count if count > 0 else 0
        table.add_row(
            f"Add {count} items",
            str(count),
            str(initial),
            str(final),
            str(final - initial),
            f"{bytes_per_item:.2f}",
        )

    # Display the results
    console.print(table)


def test_unordered_map_storage_usage(setup_storage_mocks):
    """Benchmark storage usage for UnorderedMap operations with different amounts of data."""

    mock_storage = setup_storage_mocks
    console = Console()

    # Create a table for UnorderedMap results
    table = Table(title="UnorderedMap Storage Usage")
    table.add_column("Operation")
    table.add_column("Items")
    table.add_column("Initial Size (bytes)")
    table.add_column("Final Size (bytes)")
    table.add_column("Difference (bytes)")
    table.add_column("Bytes per Item")

    # Test map creation
    initial, final = measure_storage_operation(
        lambda: UnorderedMap("test_map"), mock_storage
    )
    table.add_row(
        "Creation", "0", str(initial), str(final), str(final - initial), "N/A"
    )

    # Test adding key-value pairs
    item_counts = [10, 100, 1000, 10000]

    for count in item_counts:

        def add_items():
            m = UnorderedMap("test_map")
            for i in range(count):
                m[f"key{i}"] = f"value{i}"

        initial, final = measure_storage_operation(add_items, mock_storage)
        bytes_per_item = (final - initial) / count if count > 0 else 0
        table.add_row(
            f"Set {count} small key-values",
            str(count),
            str(initial),
            str(final),
            str(final - initial),
            f"{bytes_per_item:.2f}",
        )

    # Display the results
    console.print(table)


def test_tree_map_storage_usage(setup_storage_mocks):
    """Benchmark storage usage for TreeMap operations with different amounts of data."""

    mock_storage = setup_storage_mocks
    console = Console()

    # Create a table for TreeMap results
    table = Table(title="TreeMap Storage Usage")
    table.add_column("Operation")
    table.add_column("Items")
    table.add_column("Initial Size (bytes)")
    table.add_column("Final Size (bytes)")
    table.add_column("Difference (bytes)")
    table.add_column("Bytes per Item")

    # Test map creation
    initial, final = measure_storage_operation(
        lambda: TreeMap("test_map"), mock_storage
    )
    table.add_row(
        "Creation", "0", str(initial), str(final), str(final - initial), "N/A"
    )

    # Test adding key-value pairs
    item_counts = [10, 100, 1000, 10000]

    for count in item_counts:

        def add_items():
            m = TreeMap("test_map")
            for i in range(count):
                m[i] = f"value{i}"

        initial, final = measure_storage_operation(add_items, mock_storage)
        bytes_per_item = (final - initial) / count if count > 0 else 0
        table.add_row(
            f"Set {count} items",
            str(count),
            str(initial),
            str(final),
            str(final - initial),
            f"{bytes_per_item:.2f}",
        )

    # Display the results
    console.print(table)


def run_all_benchmarks():
    """Run all storage benchmarks and display a summary."""
    console = Console()
    console.print("[bold]Running Storage Usage Benchmarks for NEAR Collections[/bold]")

    # The actual test runs will be triggered by pytest
    pass


if __name__ == "__main__":
    run_all_benchmarks()
