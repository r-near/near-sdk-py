import base64
import json
import os
from datetime import datetime

from near_pytest.testing import NearTestCase
from rich.console import Console
from rich.table import Table


class TestUnorderedSetBulkPerformance(NearTestCase):
    @classmethod
    def setup_class(cls):
        # Call parent setup method first
        super().setup_class()

        # Compile the contract
        cls.wasm_path = cls.compile_contract(
            "integration_tests/contracts/collections/unordered_set.py", single_file=True
        )

        # Create account for contract
        cls.set_account = cls.create_account("set_bulk")

        # Deploy contract
        cls.set_contract = cls.deploy_contract(cls.set_account, cls.wasm_path)

        # Save initial state for future resets
        cls.save_state()

    def setup_method(self):
        # Reset to initial state before each test method
        self.reset_state()

    def patch_set_storage(self, num_elements):
        """
        Generates the records array for patching the contract storage to create an UnorderedSet.
        """
        records = []

        # 1. Metadata record
        metadata = {
            "version": "1.0.0",
            "length": num_elements,
            "type": "o",
        }
        metadata_key = base64.b64encode(b"items:meta").decode("utf-8")
        metadata_value = base64.b64encode(json.dumps(metadata).encode("utf-8")).decode(
            "utf-8"
        )
        records.append(
            {
                "Data": {
                    "account_id": self.set_contract.account_id,
                    "data_key": metadata_key,
                    "value": metadata_value,
                }
            }
        )

        # 2. Values vector metadata
        values_metadata = {"version": "1.0.0", "type": "v", "length": num_elements}
        values_metadata_key = base64.b64encode(b"items:values:meta").decode("utf-8")
        values_metadata_value = base64.b64encode(
            json.dumps(values_metadata).encode("utf-8")
        ).decode("utf-8")
        records.append(
            {
                "Data": {
                    "account_id": self.set_contract.account_id,
                    "data_key": values_metadata_key,
                    "value": values_metadata_value,
                }
            }
        )

        # 3. Elements (both marker and vector entry)
        for i in range(num_elements):
            value = f"bulk_item_{i}"  # Simpler value naming for clarity

            # 3a. Presence marker (LookupSet part)
            marker_key = base64.b64encode(f"items:{value}".encode("utf-8")).decode(
                "utf-8"
            )
            marker_value = base64.b64encode(json.dumps(True).encode("utf-8")).decode(
                "utf-8"
            )  # True indicates presence
            records.append(
                {
                    "Data": {
                        "account_id": self.set_contract.account_id,
                        "data_key": marker_key,
                        "value": marker_value,
                    }
                }
            )

            # 3b. Values vector entry
            vector_key = base64.b64encode(f"items:values:{i}".encode("utf-8")).decode(
                "utf-8"
            )
            vector_value = base64.b64encode(json.dumps(value).encode("utf-8")).decode(
                "utf-8"
            )
            records.append(
                {
                    "Data": {
                        "account_id": self.set_contract.account_id,
                        "data_key": vector_key,
                        "value": vector_value,
                    }
                }
            )

            # 4. Create the indices mapping (value -> index in vector)
            # This is the critical addition for efficient removal
            index_storage_key = f"items:indices:{value}"
            encoded_index_key = base64.b64encode(
                index_storage_key.encode("utf-8")
            ).decode("utf-8")
            encoded_index_value = base64.b64encode(
                json.dumps(i).encode("utf-8")
            ).decode("utf-8")

            records.append(
                {
                    "Data": {
                        "account_id": self.set_contract.account_id,
                        "data_key": encoded_index_key,
                        "value": encoded_index_value,
                    }
                }
            )

        # Submit the patch state request
        print(
            f"Patching state with {num_elements} map elements. Records: {len(records)}"
        )
        self.__class__._client._run_async(
            self.__class__._client._master_account.provider.json_rpc(
                "sandbox_patch_state", {"records": records}
            )
        )

    def test_unordered_set_bulk_operations(self):
        """Test operations on an unordered set with 10k elements."""
        num_elements = 10000
        self.patch_set_storage(num_elements)
        self._sandbox.dump_state()  # return

        # For storing performance data
        performance_data = []

        # Get baseline gas usage from calling hello world
        response, tx_result = self.set_contract.call(
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
        print("\nVerifying set length...")
        length, tx_result = self.set_contract.call(
            "get_length", {}, return_full_result=True
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        print(f"Length check gas usage: {gas_burn_tgas} TGas")
        assert gas_burn_tgas < 10, "Length check uses too much gas"
        assert length.json()["length"] == num_elements
        print(f"Confirmed set length: {num_elements}")

        # Add length to performance data
        performance_data.append(
            {
                "operation": "get_length",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": f"Set size: {num_elements}",
            }
        )

        # Test item lookup performance
        print("\nTesting item lookup performance...")
        # We'll test items at different positions
        items_to_test = [
            "bulk_item_0",
            "bulk_item_1",
            "bulk_item_100",
            "bulk_item_999",
            "bulk_item_5000",
            "bulk_item_9999",
        ]
        item_lookup_gas = []

        for item in items_to_test:
            result, tx_result = self.set_contract.call(
                "contains_value", {"value": item}, return_full_result=True
            )
            gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
            item_lookup_gas.append(gas_burn_tgas)

            contains = result.json()["contains"]
            assert contains is True, f"Item {item} should be in the set"
            print(f"  Get value for item {item}: {gas_burn_tgas} TGas")
            assert gas_burn_tgas < 10, f"Item lookup for {item} uses too much gas"

        # Add average item lookup to performance data
        avg_item_lookup = sum(item_lookup_gas) / len(item_lookup_gas)
        performance_data.append(
            {
                "operation": "contains_value (item lookup)",
                "gas_tgas": avg_item_lookup,
                "ratio": avg_item_lookup / hello_world_gas_usage,
                "details": f"Average of {len(items_to_test)} items",
            }
        )

        # Also add individual keys for detailed comparison
        for i, item in enumerate(items_to_test):
            performance_data.append(
                {
                    "operation": f"  - contains_value for item {item}",
                    "gas_tgas": item_lookup_gas[i],
                    "ratio": item_lookup_gas[i] / hello_world_gas_usage,
                    "details": f"Direct lookup of item {item}",
                }
            )

        # Test remove_item performance
        print("\nTesting remove_item performance...")
        item_to_remove = "bulk_item_5000"
        result, tx_result = self.set_contract.call(
            "remove_item", {"value": item_to_remove}, return_full_result=True
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        removed = result.json()["removed"]
        print(
            f"Removed item with value {item_to_remove}: {removed}, gas usage: {gas_burn_tgas} TGas"
        )
        assert gas_burn_tgas < 15, "Remove operation uses too much gas"

        # Add remove_item to performance data
        performance_data.append(
            {
                "operation": "remove_item",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": f"Removes item with value {item_to_remove}",
            }
        )

        # Verify length after remove
        length, tx_result = self.set_contract.call(
            "get_length", {}, return_full_result=True
        )
        assert length.json()["length"] == num_elements - 1

        # Test insert performance (insert new)
        print("\nTesting insert performance (insert new)...")
        new_value = "new_value"
        result, tx_result = self.set_contract.call(
            "add_item", {"value": new_value}, return_full_result=True
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        print(
            f"Inserted new item with value {new_value}, gas usage: {gas_burn_tgas} TGas"
        )
        assert gas_burn_tgas < 10, "Insert operation uses too much gas"

        # Add add_item (insert) to performance data
        performance_data.append(
            {
                "operation": "add_item (insert new)",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": f"Inserts new item with value {new_value}",
            }
        )

        # Test pagination (first 5 items)
        print("\nTesting pagination (first 5 items)...")
        result, tx_result = self.set_contract.call(
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
                "operation": "get_paginated_items (pagination)",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": "Retrieves first 5 items",
            }
        )

        # Generate performance comparison table
        console = Console()

        table = Table(title=f"UnorderedSet Performance (Size: {num_elements} elements)")

        table.add_column("Operation", style="cyan")
        table.add_column("Gas (TGas)", justify="right", style="green")
        table.add_column("vs. Baseline", justify="right", style="magenta")
        table.add_column("Details", style="yellow")

        # Also prepare data for Markdown export
        md_content = "# UnorderedSet Performance Test Results\n\n"
        md_content += f"UnorderedSet size: {num_elements} elements\n\n"
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
