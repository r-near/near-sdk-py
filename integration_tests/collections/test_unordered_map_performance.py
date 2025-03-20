import base64
import json
import os
from datetime import datetime

from near_pytest.testing import NearTestCase
from rich.console import Console
from rich.table import Table


class TestUnorderedMapBulkPerformance(NearTestCase):
    @classmethod
    def setup_class(cls):
        # Call parent setup method first
        super().setup_class()

        # Compile the contract
        cls.wasm_path = cls.compile_contract(
            "integration_tests/contracts/collections/unordered_map.py", single_file=True
        )

        # Create account for contract
        cls.map_account = cls.create_account("map_bulk")

        # Deploy contract
        cls.map_contract = cls.deploy_contract(cls.map_account, cls.wasm_path)

        # Save initial state for future resets
        cls.save_state()

    def setup_method(self):
        # Reset to initial state before each test method
        self.reset_state()

    def patch_map_storage(self, num_elements):
        """
        Directly patch the contract storage to create an unordered map with specified number of elements
        using the sandbox_patch_state RPC call.

        This implementation uses indices to make key lookups and removals more efficient.
        """
        account_id = self.map_account.account_id

        # Create records array
        records = []

        # First, add the metadata record with length information and type
        metadata = {"version": "1.0.0", "type": "um", "length": num_elements}
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

        # Add the keys vector metadata
        keys_metadata = {"version": "1.0.0", "type": "v", "length": num_elements}
        keys_metadata_key = base64.b64encode(b"items:keys:meta").decode("utf-8")
        keys_metadata_value = base64.b64encode(
            json.dumps(keys_metadata).encode("utf-8")
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

        # Create records for all elements
        for i in range(num_elements):
            # Create the key string
            key = f"key_{i}"

            # 1. Create the values storage (LookupMap part)
            value = f"bulk_value_{i}"
            value_storage_key = f"items:{key}"
            encoded_value_key = base64.b64encode(
                value_storage_key.encode("utf-8")
            ).decode("utf-8")
            encoded_value = base64.b64encode(json.dumps(value).encode("utf-8")).decode(
                "utf-8"
            )

            records.append(
                {
                    "Data": {
                        "account_id": account_id,
                        "data_key": encoded_value_key,
                        "value": encoded_value,
                    }
                }
            )

            # 2. Create the keys vector storage (Vector part)
            key_vector_storage_key = f"items:keys:{i}"
            encoded_key_vector_key = base64.b64encode(
                key_vector_storage_key.encode("utf-8")
            ).decode("utf-8")
            encoded_key = base64.b64encode(json.dumps(key).encode("utf-8")).decode(
                "utf-8"
            )

            records.append(
                {
                    "Data": {
                        "account_id": account_id,
                        "data_key": encoded_key_vector_key,
                        "value": encoded_key,
                    }
                }
            )

            # 3. Create the indices mapping (key -> index in vector)
            # This is the critical addition for efficient removal
            index_storage_key = f"items:indices:{key}"
            encoded_index_key = base64.b64encode(
                index_storage_key.encode("utf-8")
            ).decode("utf-8")
            encoded_index_value = base64.b64encode(
                json.dumps(i).encode("utf-8")
            ).decode("utf-8")

            records.append(
                {
                    "Data": {
                        "account_id": account_id,
                        "data_key": encoded_index_key,
                        "value": encoded_index_value,
                    }
                }
            )

        # Submit the patch state request
        print(f"Patching state with {num_elements} map elements...")
        self.__class__._client._run_async(
            self.__class__._client._master_account.provider.json_rpc(
                "sandbox_patch_state", {"records": records}
            )
        )

    def test_unordered_map_bulk_operations(self):
        """Test operations on an unordered map with 10k elements."""
        # Patch storage to create an unordered map with 10k elements
        num_elements = 10000
        self.patch_map_storage(num_elements)
        self._sandbox.dump_state()

        # For storing performance data
        performance_data = []

        # Get baseline gas usage from calling hello world
        response, tx_result = self.map_contract.call(
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

        # Verify length
        print("\nVerifying map length...")
        length, tx_result = self.map_contract.call(
            "get_length", {}, return_full_result=True
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        print(f"Length check gas usage: {gas_burn_tgas} TGas")
        assert gas_burn_tgas < 10, "Length check uses too much gas"
        assert length.json()["length"] == num_elements
        print(f"Confirmed map length: {num_elements}")

        # Add length to performance data
        performance_data.append(
            {
                "operation": "get_length",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": f"Map size: {num_elements}",
            }
        )

        # Test key lookup performance
        print("\nTesting key lookup performance...")
        # We'll test keys at different positions
        keys_to_test = ["key_0", "key_1", "key_100", "key_999", "key_5000", "key_9999"]
        key_lookup_gas = []

        for key in keys_to_test:
            result, tx_result = self.map_contract.call(
                "get_item", {"key": key}, return_full_result=True
            )
            gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
            key_lookup_gas.append(gas_burn_tgas)

            value = result.json()["value"]
            expected = f"bulk_value_{key.split('_')[1]}"
            assert value == expected, (
                f"Value for key {key} doesn't match: {value} vs {expected}"
            )
            print(f"  Get value for key {key}: {gas_burn_tgas} TGas")
            assert gas_burn_tgas < 10, f"Key lookup for {key} uses too much gas"

        # Add average key lookup to performance data
        avg_key_lookup = sum(key_lookup_gas) / len(key_lookup_gas)
        performance_data.append(
            {
                "operation": "get_item (key lookup)",
                "gas_tgas": avg_key_lookup,
                "ratio": avg_key_lookup / hello_world_gas_usage,
                "details": f"Average of {len(keys_to_test)} keys",
            }
        )

        # Also add individual keys for detailed comparison
        for i, key in enumerate(keys_to_test):
            performance_data.append(
                {
                    "operation": f"  - get_item for key {key}",
                    "gas_tgas": key_lookup_gas[i],
                    "ratio": key_lookup_gas[i] / hello_world_gas_usage,
                    "details": f"Direct lookup of key {key}",
                }
            )

        # Test contains_key performance
        print("\nTesting contains_key performance...")
        contains_key_gas = []

        for key in keys_to_test:
            result, tx_result = self.map_contract.call(
                "contains_key", {"key": key}, return_full_result=True
            )
            gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
            contains_key_gas.append(gas_burn_tgas)

            contains = result.json()["contains"]
            assert contains is True, f"Key {key} should be in the map"
            print(f"  Contains key check for {key}: {gas_burn_tgas} TGas")
            assert gas_burn_tgas < 10, f"Contains key check for {key} uses too much gas"

        # Add average contains_key to performance data
        avg_contains_key = sum(contains_key_gas) / len(contains_key_gas)
        performance_data.append(
            {
                "operation": "contains_key",
                "gas_tgas": avg_contains_key,
                "ratio": avg_contains_key / hello_world_gas_usage,
                "details": f"Average of {len(keys_to_test)} keys",
            }
        )

        # Test remove_item performance
        print("\nTesting remove_item performance...")
        key_to_remove = "key_5000"
        result, tx_result = self.map_contract.call(
            "remove_item", {"key": key_to_remove}, return_full_result=True
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        removed = result.json()["removed"]
        print(
            f"Removed item with key {key_to_remove}: {removed}, gas usage: {gas_burn_tgas} TGas"
        )
        assert gas_burn_tgas < 15, "Remove operation uses too much gas"

        # Add remove_item to performance data
        performance_data.append(
            {
                "operation": "remove_item",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": f"Removes item with key {key_to_remove}",
            }
        )

        # Verify length after remove
        length, tx_result = self.map_contract.call(
            "get_length", {}, return_full_result=True
        )
        assert length.json()["length"] == num_elements - 1

        # Test set_item performance (update existing)
        print("\nTesting set_item performance (update existing)...")
        key_to_update = "key_1"
        result, tx_result = self.map_contract.call(
            "set_item",
            {"key": key_to_update, "value": "updated_value"},
            return_full_result=True,
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        print(f"Updated item with key {key_to_update}, gas usage: {gas_burn_tgas} TGas")
        assert gas_burn_tgas < 10, "Update operation uses too much gas"

        # Add set_item (update) to performance data
        performance_data.append(
            {
                "operation": "set_item (update existing)",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": f"Updates existing item with key {key_to_update}",
            }
        )

        # Test set_item performance (insert new)
        print("\nTesting set_item performance (insert new)...")
        new_key = "key_new"
        result, tx_result = self.map_contract.call(
            "set_item", {"key": new_key, "value": "new_value"}, return_full_result=True
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        print(f"Inserted new item with key {new_key}, gas usage: {gas_burn_tgas} TGas")
        assert gas_burn_tgas < 10, "Insert operation uses too much gas"

        # Add set_item (insert) to performance data
        performance_data.append(
            {
                "operation": "set_item (insert new)",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": f"Inserts new item with key {new_key}",
            }
        )

        # Test pagination (first 5 items)
        print("\nTesting pagination (first 5 items)...")
        result, tx_result = self.map_contract.call(
            "get_paginated_items",
            {"start_index": 0, "limit": 5},
            return_full_result=True,
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        items = result.json()["items"]
        print(f"Pagination (first 5 items) gas usage: {gas_burn_tgas} TGas")
        assert len(items) == 5, "Pagination should return 5 items"
        assert gas_burn_tgas < 15, "Pagination (5 items) uses too much gas"

        # Add pagination to performance data
        performance_data.append(
            {
                "operation": "get_items (pagination)",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": "Retrieves first 5 items",
            }
        )

        # Generate performance comparison table
        console = Console()

        table = Table(title=f"UnorderedMap Performance (Size: {num_elements} elements)")

        table.add_column("Operation", style="cyan")
        table.add_column("Gas (TGas)", justify="right", style="green")
        table.add_column("vs. Baseline", justify="right", style="magenta")
        table.add_column("Details", style="yellow")

        # Also prepare data for Markdown export
        md_content = "# UnorderedMap Performance Test Results\n\n"
        md_content += f"UnorderedMap size: {num_elements} elements\n\n"
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
        with open(
            f"{results_dir}/unordered_map_performance_{num_elements}.md", "w"
        ) as f:
            f.write(md_content)

        print(
            f"\nResults saved to: {results_dir}/unordered_map_performance_{num_elements}.md"
        )
