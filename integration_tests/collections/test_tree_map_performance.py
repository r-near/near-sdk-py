import base64
import json
import os
from datetime import datetime

from near_pytest.testing import NearTestCase
from rich.console import Console
from rich.table import Table


class TestTreeMapBulkPerformance(NearTestCase):
    @classmethod
    def setup_class(cls):
        # Call parent setup method first
        super().setup_class()

        # Compile the contract
        cls.wasm_path = cls.compile_contract(
            "integration_tests/contracts/collections/tree_map.py", single_file=True
        )

        # Create account for contract
        cls.tree_map_account = cls.create_account("tree_map_bulk")

        # Deploy contract
        cls.tree_map_contract = cls.deploy_contract(cls.tree_map_account, cls.wasm_path)

        # Save initial state for future resets
        cls.save_state()

    def setup_method(self):
        # Reset to initial state before each test method
        self.reset_state()

    def patch_tree_map_storage(self, num_elements):
        """
        Directly patch the contract storage to create a tree map with specified number of elements
        using the sandbox_patch_state RPC call.
        """
        account_id = self.tree_map_account.account_id

        # Create records array
        records = []

        # Add the metadata record with collection type
        metadata = {"version": "1.0.0", "type": "t", "length": num_elements}
        metadata_key = base64.b64encode(b"items:meta").decode("utf-8")
        metadata_value = base64.b64encode(json.dumps(metadata).encode("utf-8")).decode(
            "utf-8"
        )

        records.append(
            {
                "Data": {
                    "account_id": account_id,
                    "data_key": metadata_key,
                    "value": metadata_value,
                }
            }
        )

        # Note: We don't need a separate length record since it's already in metadata

        # Add the keys vector metadata
        keys_vector_metadata = {"version": "1.0.0", "type": "v", "length": num_elements}
        keys_metadata_key = base64.b64encode(b"items:keys:meta").decode("utf-8")
        keys_metadata_value = base64.b64encode(
            json.dumps(keys_vector_metadata).encode("utf-8")
        ).decode("utf-8")

        records.append(
            {
                "Data": {
                    "account_id": account_id,
                    "data_key": keys_metadata_key,
                    "value": keys_metadata_value,
                }
            }
        )

        # Note: We don't need a separate keys length record since it's already in metadata

        # Create records for all elements
        for i in range(num_elements):
            # Create the key string (making sure keys are sorted)
            key_str = f"key{i:06d}"  # Use padding to ensure lexicographic order

            # Add to keys vector (index -> key)
            keys_element_key = f"items:keys:{i}"
            encoded_keys_key = base64.b64encode(
                keys_element_key.encode("utf-8")
            ).decode("utf-8")
            encoded_key_value = base64.b64encode(
                json.dumps(key_str).encode("utf-8")
            ).decode("utf-8")

            records.append(
                {
                    "Data": {
                        "account_id": account_id,
                        "data_key": encoded_keys_key,
                        "value": encoded_key_value,
                    }
                }
            )

            # Add key-value pair
            value = f"value{i}"
            tree_map_key = f"items:{key_str}"
            encoded_tree_map_key = base64.b64encode(
                tree_map_key.encode("utf-8")
            ).decode("utf-8")
            encoded_value = base64.b64encode(json.dumps(value).encode("utf-8")).decode(
                "utf-8"
            )

            records.append(
                {
                    "Data": {
                        "account_id": account_id,
                        "data_key": encoded_tree_map_key,
                        "value": encoded_value,
                    }
                }
            )

        # Submit the patch state request
        print(f"Patching state with {num_elements} tree map elements...")
        self.__class__._client._run_async(
            self.__class__._client._master_account.provider.json_rpc(
                "sandbox_patch_state", {"records": records}
            )
        )

    def test_tree_map_bulk_operations(self):
        """Test operations on a tree map with 10k elements."""
        # Patch storage to create a tree map with 10k elements
        num_elements = 10000
        self.patch_tree_map_storage(num_elements)
        self._sandbox.dump_state()

        # For storing performance data
        performance_data = []

        # Get baseline gas usage from calling hello world
        response, tx_result = self.tree_map_contract.call(
            method_name="hello", return_full_result=True
        )
        hello_world_gas_usage = tx_result.receipt_outcome[0].gas_burnt / 10**12
        print(f"Hello world gas usage: {hello_world_gas_usage} TGas")

        # Add hello world to performance data
        performance_data.append(
            {
                "operation": "hello world (baseline)",
                "gas_tgas": hello_world_gas_usage,
                "ratio": 1.0,
                "details": "Basic function call",
            }
        )

        # # Test contains operation for existing key
        # print("\nTesting contains for existing key...")
        # keys_to_test = [f"key{i:06d}" for i in [0, 1, 100, 999, 5000, 9999]]
        # contains_gas = []

        # for key in keys_to_test:
        #     result, tx_result = self.tree_map_contract.call(
        #         "contains_key", {"key": key}, return_full_result=True
        #     )
        #     gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        #     contains_gas.append(gas_burn_tgas)

        #     contains = result.json().get("contains", False)
        #     assert contains, f"Key {key} should exist in the tree map"
        #     print(f"  Contains key {key}: {gas_burn_tgas} TGas")

        # # Add contains to performance data
        # avg_contains_gas = sum(contains_gas) / len(contains_gas)
        # performance_data.append(
        #     {
        #         "operation": "contains_key (existing)",
        #         "gas_tgas": avg_contains_gas,
        #         "ratio": avg_contains_gas / hello_world_gas_usage,
        #         "details": f"Average of {len(keys_to_test)} keys",
        #     }
        # )

        # # Test contains operation for non-existing key
        # print("\nTesting contains for non-existing key...")
        # result, tx_result = self.tree_map_contract.call(
        #     "contains_key", {"key": "nonexistent_key"}, return_full_result=True
        # )
        # gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        # print(f"  Contains non-existing key: {gas_burn_tgas} TGas")

        # performance_data.append(
        #     {
        #         "operation": "contains_key (non-existing)",
        #         "gas_tgas": gas_burn_tgas,
        #         "ratio": gas_burn_tgas / hello_world_gas_usage,
        #         "details": "Check for a key that doesn't exist",
        #     }
        # )

        # # Test get operation
        # print("\nTesting get operation...")
        # get_gas = []

        # for key in keys_to_test:
        #     result, tx_result = self.tree_map_contract.call(
        #         "get", {"key": key}, return_full_result=True
        #     )
        #     gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        #     get_gas.append(gas_burn_tgas)

        #     value = result.json().get("value")
        #     expected = f"value{int(key[3:])}"  # Extract the number part from key000001
        #     assert value == expected, (
        #         f"Value for key {key} should be {expected}, got {value}"
        #     )
        #     print(f"  Get key {key}: {gas_burn_tgas} TGas")

        # # Add get to performance data
        # avg_get_gas = sum(get_gas) / len(get_gas)
        # performance_data.append(
        #     {
        #         "operation": "get",
        #         "gas_tgas": avg_get_gas,
        #         "ratio": avg_get_gas / hello_world_gas_usage,
        #         "details": f"Average of {len(keys_to_test)} keys",
        #     }
        # )

        # # Test set operation (update existing)
        # print("\nTesting set operation (update existing)...")
        # result, tx_result = self.tree_map_contract.call(
        #     "set",
        #     {"key": "key000100", "value": "updated_value"},
        #     return_full_result=True,
        # )
        # gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        # print(f"  Update existing key: {gas_burn_tgas} TGas")

        # performance_data.append(
        #     {
        #         "operation": "set (update existing)",
        #         "gas_tgas": gas_burn_tgas,
        #         "ratio": gas_burn_tgas / hello_world_gas_usage,
        #         "details": "Update value for an existing key",
        #     }
        # )

        # Test set operation (add new)
        print("\nTesting set operation (add new)...")
        result, tx_result = self.tree_map_contract.call(
            "set", {"key": "key1000001", "value": "new_value"}, return_full_result=True
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        print(f"  Add new key: {gas_burn_tgas} TGas")

        performance_data.append(
            {
                "operation": "set (add new)",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": "Add value with a new key",
            }
        )

        # Test remove operation
        print("\nTesting remove operation...")
        result, tx_result = self.tree_map_contract.call(
            "remove", {"key": "key005000"}, return_full_result=True
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        print(f"  Remove key: {gas_burn_tgas} TGas")

        performance_data.append(
            {
                "operation": "remove",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": "Remove an existing key-value pair",
            }
        )

        # Test floor_key operation
        print("\nTesting floor_key operation...")
        # Test with key that has a floor
        result, tx_result = self.tree_map_contract.call(
            "floor_key", {"key": "key000100"}, return_full_result=True
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        floor_key = result.json().get("key")
        print(f"  Floor key for key000100: {floor_key}, gas: {gas_burn_tgas} TGas")

        performance_data.append(
            {
                "operation": "floor_key",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": "Get the greatest key less than or equal to a given key",
            }
        )

        # Test ceiling_key operation
        print("\nTesting ceiling_key operation...")
        result, tx_result = self.tree_map_contract.call(
            "ceiling_key", {"key": "key000100"}, return_full_result=True
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        ceiling_key = result.json().get("key")
        print(f"  Ceiling key for key000100: {ceiling_key}, gas: {gas_burn_tgas} TGas")

        performance_data.append(
            {
                "operation": "ceiling_key",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": "Get the least key greater than or equal to a given key",
            }
        )

        # Test min_key operation
        print("\nTesting min_key operation...")
        result, tx_result = self.tree_map_contract.call(
            "min_key", return_full_result=True
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        min_key = result.json().get("key")
        print(f"  Min key: {min_key}, gas: {gas_burn_tgas} TGas")

        performance_data.append(
            {
                "operation": "min_key",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": "Get the minimum key in the map",
            }
        )

        # Test max_key operation
        print("\nTesting max_key operation...")
        result, tx_result = self.tree_map_contract.call(
            "max_key", return_full_result=True
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        max_key = result.json().get("key")
        print(f"  Max key: {max_key}, gas: {gas_burn_tgas} TGas")

        performance_data.append(
            {
                "operation": "max_key",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": "Get the maximum key in the map",
            }
        )

        # Test paginated operations
        print("\nTesting keys with pagination...")
        result, tx_result = self.tree_map_contract.call(
            "keys", {"start_index": 0, "limit": 5}, return_full_result=True
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        keys = result.json().get("keys")
        print(f"  First 5 keys: {keys}, gas: {gas_burn_tgas} TGas")
        assert len(keys) == 5, "Should return exactly 5 keys"

        performance_data.append(
            {
                "operation": "keys (paginated, 5 items)",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": "Get the first 5 keys with pagination",
            }
        )

        # Test values with pagination
        print("\nTesting values with pagination...")
        result, tx_result = self.tree_map_contract.call(
            "values", {"start_index": 0, "limit": 5}, return_full_result=True
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        values = result.json().get("values")
        print(f"  First 5 values: {values}, gas: {gas_burn_tgas} TGas")
        assert len(values) == 5, "Should return exactly 5 values"

        performance_data.append(
            {
                "operation": "values (paginated, 5 items)",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": "Get the first 5 values with pagination",
            }
        )

        # Test items with pagination
        print("\nTesting items with pagination...")
        result, tx_result = self.tree_map_contract.call(
            "items_list", {"start_index": 0, "limit": 5}, return_full_result=True
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        items = result.json().get("items")
        print(f"  First 5 items: {items}, gas: {gas_burn_tgas} TGas")
        assert len(items) == 5, "Should return exactly 5 items"

        performance_data.append(
            {
                "operation": "items_list (paginated, 5 items)",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": "Get the first 5 key-value pairs with pagination",
            }
        )

        # Test range with pagination
        print("\nTesting range with pagination...")
        result, tx_result = self.tree_map_contract.call(
            "range",
            {
                "from_key": "key001000",
                "to_key": "key002000",
                "start_index": 0,
                "limit": 5,
            },
            return_full_result=True,
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        range_keys = result.json().get("keys")
        print(
            f"  Range (paginated, first 5 items): {range_keys}, gas: {gas_burn_tgas} TGas"
        )
        assert len(range_keys) == 5, "Should return exactly 5 keys in range"

        performance_data.append(
            {
                "operation": "range (paginated, 5 items)",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": "Get 5 keys in specified range with pagination",
            }
        )

        # Test range_paginated (convenience method)
        print("\nTesting range_paginated...")
        result, tx_result = self.tree_map_contract.call(
            "range_paginated",
            {
                "from_key": "key001000",
                "to_key": "key002000",
                "page_size": 5,
                "page_number": 0,
            },
            return_full_result=True,
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        range_keys = result.json().get("keys")
        print(
            f"  Range paginated (page 0, size 5): {range_keys}, gas: {gas_burn_tgas} TGas"
        )
        assert len(range_keys) == 5, "Should return exactly 5 keys in range"

        performance_data.append(
            {
                "operation": "range_paginated",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": "Get first page of 5 keys in specified range",
            }
        )

        # Test clear_paginated
        print("\nTesting clear_paginated...")
        result, tx_result = self.tree_map_contract.call(
            "clear_paginated", {"batch_size": 5}, return_full_result=True
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        removed_count = result.json().get("removed_count")
        print(
            f"  Removed {removed_count} items with batch size 5, gas: {gas_burn_tgas} TGas"
        )
        assert removed_count == 5, "Should remove exactly 5 items"

        performance_data.append(
            {
                "operation": "clear_paginated (batch size 5)",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": "Remove 5 items in a batch",
            }
        )

        # Generate performance comparison table
        console = Console()

        table = Table(title=f"TreeMap Performance (Size: {num_elements} elements)")

        table.add_column("Operation", style="cyan")
        table.add_column("Gas (TGas)", justify="right", style="green")
        table.add_column("vs. Baseline", justify="right", style="magenta")
        table.add_column("Details", style="yellow")

        # Also prepare data for Markdown export
        md_content = "# TreeMap Performance Test Results\n\n"
        md_content += f"TreeMap size: {num_elements} elements\n\n"
        md_content += "| Operation | Gas (TGas) | vs. Baseline | Details |\n"
        md_content += "|-----------|------------|--------------|----------|\n"

        for entry in performance_data:
            # Format the ratio to be more readable
            ratio_str = f"{entry['ratio']:.2f}x"

            # Format TGas to 4 decimal places
            tgas_str = f"{entry['gas_tgas']:.4f}"

            table.add_row(entry["operation"], tgas_str, ratio_str, entry["details"])

            # Add to Markdown content
            md_content += f"| {entry['operation']} | {tgas_str} | {ratio_str} | {entry['details']} |\n"

        # Print to console
        console.print(table)

        # Save results to Markdown file
        md_content += "\n\n## Test Information\n\n"
        md_content += f"- Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

        # Create results directory if it doesn't exist
        results_dir = "performance_results"
        os.makedirs(results_dir, exist_ok=True)

        # Save to file
        with open(f"{results_dir}/tree_map_performance_{num_elements}.md", "w") as f:
            f.write(md_content)

        print(
            f"\nResults saved to: {results_dir}/tree_map_performance_{num_elements}.md"
        )
