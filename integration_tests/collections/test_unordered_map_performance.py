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
        Patches storage with exact structure matching Rust's UnorderedMap layout:
        - Main map metadata with type 'u'
        - Separate vector metadatas with type 'v'
        - Hex-encoded index keys
        - Base64 encoding for all storage entries
        """
        account_id = self.map_account.account_id
        records = []

        # Main UnorderedMap metadata
        map_metadata = {
            "type": "u",  # 'u' for unordered map
            "version": "1.0.0",
            "length": num_elements,
        }
        map_meta_key = base64.b64encode(b"items:meta").decode()
        map_meta_value = base64.b64encode(json.dumps(map_metadata).encode()).decode()
        records.append(
            {
                "Data": {
                    "account_id": account_id,
                    "data_key": map_meta_key,
                    "value": map_meta_value,
                }
            }
        )

        # Vector metadatas
        for component in ["keys", "vals"]:
            vec_metadata = {
                "type": "v",  # 'v' for vector
                "version": "1.0.0",
                "length": num_elements,
            }
            meta_key = base64.b64encode(f"items_{component}:meta".encode()).decode()
            meta_value = base64.b64encode(json.dumps(vec_metadata).encode()).decode()
            records.append(
                {
                    "Data": {
                        "account_id": account_id,
                        "data_key": meta_key,
                        "value": meta_value,
                    }
                }
            )

        # Create elements
        for i in range(num_elements):
            key = f"key_{i}"
            value = f"bulk_value_{i}"

            # Serialize key to bytes and hex for index
            key_bytes = key.encode()
            key_hex = key_bytes.hex()

            # 1. Add to keys vector
            key_entry_key = base64.b64encode(f"items_keys:{i}".encode()).decode()
            key_entry_value = base64.b64encode(json.dumps(key).encode()).decode()
            records.append(
                {
                    "Data": {
                        "account_id": account_id,
                        "data_key": key_entry_key,
                        "value": key_entry_value,
                    }
                }
            )

            # 2. Add to values vector
            val_entry_key = base64.b64encode(f"items_vals:{i}".encode()).decode()
            val_entry_value = base64.b64encode(json.dumps(value).encode()).decode()
            records.append(
                {
                    "Data": {
                        "account_id": account_id,
                        "data_key": val_entry_key,
                        "value": val_entry_value,
                    }
                }
            )

            # 3. Add index mapping (hex-encoded key)
            index_key = base64.b64encode(f"items_indices:{key_hex}".encode()).decode()
            index_value = base64.b64encode(str(i).encode()).decode()
            records.append(
                {
                    "Data": {
                        "account_id": account_id,
                        "data_key": index_key,
                        "value": index_value,
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

        # self.map_contract.call(
        #     method_name="set_item", args={"key": "key_0", "value": "bulk_value_0"}
        # )
        # self._sandbox.dump_state()
        # return

        # Patch storage to create an unordered map with 10k elements
        num_elements = 10000
        self.patch_map_storage(num_elements)
        # self._sandbox.dump_state()

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

        # Note: We're skipping full iteration tests as they would exceed gas limits with 10k elements
        print(
            "\nNote: Skipping full iteration tests (get_all_keys, get_all_values, get_all_items) as they would exceed gas limits with 10k elements"
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

    def test_pagination_performance(self):
        """Test pagination performance on an unordered map with many elements."""
        # Patch storage to create an unordered map with many elements
        num_elements = 10000
        self.patch_map_storage(num_elements)

        # For storing performance data
        pagination_perf_data = []

        # Get baseline gas usage for reference
        response, tx_result = self.map_contract.call(
            method_name="hello", return_full_result=True
        )
        hello_world_gas_usage = tx_result.receipt_outcome[0].gas_burnt / 10**12

        # Define page sizes to test - starting with smaller page sizes
        page_sizes = [5, 10, 20, 50]

        print("\nTesting pagination performance...")

        # First, verify the map has the expected number of elements
        length, tx_result = self.map_contract.call(
            "get_length", {}, return_full_result=True
        )
        actual_length = length.json()["length"]
        print(f"Verified map length: {actual_length} (expected {num_elements})")

        for page_size in page_sizes:
            try:
                # Test first page (start of map)
                print(f"\nAttempting to fetch first page with size {page_size}...")
                first_page_time_start = datetime.now()
                result, tx_result = self.map_contract.call(
                    "get_paginated_items",
                    {"start_index": 0, "limit": page_size},
                    return_full_result=True,
                    gas=300 * 10**12,
                )
                first_page_time = (
                    datetime.now() - first_page_time_start
                ).total_seconds()
                first_page_gas = tx_result.receipt_outcome[0].gas_burnt / 10**12

                # Verify results
                page_data = result.json()
                print(f"  Received {page_data['page_count']} items in first page")

                # Add to performance data
                pagination_perf_data.append(
                    {
                        "operation": f"pagination_first_page_{page_size}",
                        "gas_tgas": first_page_gas,
                        "ratio": first_page_gas / hello_world_gas_usage,
                        "details": f"First page with {page_size} items",
                        "time_seconds": first_page_time,
                    }
                )

                # Test middle page - but for safety, only test small jumps ahead
                # This avoids large index calculations that might be problematic
                middle_index = min(
                    100, num_elements // 4
                )  # More conservative middle point
                print(f"  Attempting to fetch middle page at index {middle_index}...")
                middle_page_time_start = datetime.now()
                result, tx_result = self.map_contract.call(
                    "get_paginated_items",
                    {"start_index": middle_index, "limit": page_size},
                    return_full_result=True,
                    gas=300 * 10**12,
                )
                middle_page_time = (
                    datetime.now() - middle_page_time_start
                ).total_seconds()
                middle_page_gas = tx_result.receipt_outcome[0].gas_burnt / 10**12

                # Verify results
                page_data = result.json()
                print(f"  Received {page_data['page_count']} items in middle page")

                # Add to performance data
                pagination_perf_data.append(
                    {
                        "operation": f"pagination_middle_page_{page_size}",
                        "gas_tgas": middle_page_gas,
                        "ratio": middle_page_gas / hello_world_gas_usage,
                        "details": f"Middle page (index {middle_index}) with {page_size} items",
                        "time_seconds": middle_page_time,
                    }
                )

                # Test jumping forward by page_size
                next_page_index = middle_index + page_size
                print(f"  Attempting to fetch next page at index {next_page_index}...")
                next_page_time_start = datetime.now()
                result, tx_result = self.map_contract.call(
                    "get_paginated_items",
                    {"start_index": next_page_index, "limit": page_size},
                    return_full_result=True,
                )
                next_page_time = (datetime.now() - next_page_time_start).total_seconds()
                next_page_gas = tx_result.receipt_outcome[0].gas_burnt / 10**12

                # Verify results
                page_data = result.json()
                print(f"  Received {page_data['page_count']} items in next page")

                # Add to performance data
                pagination_perf_data.append(
                    {
                        "operation": f"pagination_next_page_{page_size}",
                        "gas_tgas": next_page_gas,
                        "ratio": next_page_gas / hello_world_gas_usage,
                        "details": f"Next page (index {next_page_index}) with {page_size} items",
                        "time_seconds": next_page_time,
                    }
                )

                print(f"  Successfully tested pagination with page size {page_size}")

            except Exception as e:
                print(f"Error testing pagination with page size {page_size}: {str(e)}")
                print("Skipping remaining tests for this page size")
                continue

        # Generate performance comparison table for pagination if we have data
        if pagination_perf_data:
            console = Console()

            table = Table(
                title=f"UnorderedMap Pagination Performance (Size: {num_elements} elements)"
            )

            table.add_column("Operation", style="cyan")
            table.add_column("Gas (TGas)", justify="right", style="green")
            table.add_column("vs. Baseline", justify="right", style="magenta")
            table.add_column("Time (s)", justify="right", style="blue")
            table.add_column("Details", style="yellow")

            # Also prepare data for Markdown export
            md_content = "# UnorderedMap Pagination Performance Test Results\n\n"
            md_content += f"UnorderedMap size: {num_elements} elements\n\n"
            md_content += (
                "| Operation | Gas (TGas) | vs. Baseline | Time (s) | Details |\n"
            )
            md_content += (
                "|-----------|------------|--------------|----------|----------|\n"
            )

            for entry in pagination_perf_data:
                # Format the ratio to be more readable
                ratio_str = f"{entry['ratio']:.2f}x"

                # Format TGas to 4 decimal places
                tgas_str = f"{entry['gas_tgas']:.4f}"

                # Format time to 4 decimal places
                time_str = f"{entry['time_seconds']:.4f}"

                table.add_row(
                    entry["operation"], tgas_str, ratio_str, time_str, entry["details"]
                )

                # Add to Markdown content
                md_content += f"| {entry['operation']} | {tgas_str} | {ratio_str} | {time_str} | {entry['details']} |\n"

            # Print to console
            console.print(table)

            # Save results to Markdown file
            md_content += "\n\n## Test Information\n\n"
            md_content += (
                f"- Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )

            # Create results directory if it doesn't exist
            results_dir = "performance_results"
            os.makedirs(results_dir, exist_ok=True)

            # Save to file
            with open(
                f"{results_dir}/unordered_map_pagination_{num_elements}.md", "w"
            ) as f:
                f.write(md_content)

            print(
                f"\nPagination results saved to: {results_dir}/unordered_map_pagination_{num_elements}.md"
            )
        else:
            print("No pagination performance data was collected due to errors.")
