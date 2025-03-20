import base64
import json
import os
from datetime import datetime

from near_pytest.testing import NearTestCase
from rich.console import Console
from rich.table import Table


class TestLookupSetBulkPerformance(NearTestCase):
    @classmethod
    def setup_class(cls):
        # Call parent setup method first
        super().setup_class()

        # Compile the contract
        cls.wasm_path = cls.compile_contract(
            "integration_tests/contracts/collections/lookup_set.py", single_file=True
        )

        # Create account for contract
        cls.lookup_set_account = cls.create_account("lookup_set_bulk")

        # Deploy contract
        cls.lookup_set_contract = cls.deploy_contract(
            cls.lookup_set_account, cls.wasm_path
        )

        # Save initial state for future resets
        cls.save_state()

    def setup_method(self):
        # Reset to initial state before each test method
        self.reset_state()

    def patch_lookup_set_storage(self, num_elements):
        """
        Directly patch the contract storage to create a lookup set with specified number of elements
        using the sandbox_patch_state RPC call.
        """
        account_id = self.lookup_set_account.account_id

        # Create records array
        records = []

        # Add the metadata record with collection type
        metadata = {"version": "1.0.0", "type": "s"}
        metadata_key = base64.b64encode(b"items:metadata").decode("utf-8")
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

        # Add the length record (number of elements)
        length_key = base64.b64encode(b"items:len").decode("utf-8")
        length_value = base64.b64encode(
            json.dumps(num_elements).encode("utf-8")
        ).decode("utf-8")

        records.append(
            {
                "Data": {
                    "account_id": account_id,
                    "data_key": length_key,
                    "value": length_value,
                }
            }
        )

        # Create records for all elements
        for i in range(num_elements):
            # Create the value string
            value_str = f"value{i}"

            # Apply the _make_key logic: prefix:serialized_value
            element_key = f"items:{value_str}"
            encoded_key = base64.b64encode(element_key.encode("utf-8")).decode("utf-8")

            # For sets, we just store a marker value (True)
            encoded_value = base64.b64encode(json.dumps(True).encode("utf-8")).decode(
                "utf-8"
            )

            # Add to records
            records.append(
                {
                    "Data": {
                        "account_id": account_id,
                        "data_key": encoded_key,
                        "value": encoded_value,
                    }
                }
            )

        # Submit the patch state request
        print(f"Patching state with {num_elements} lookup set elements...")
        self.__class__._client._run_async(
            self.__class__._client._master_account.provider.json_rpc(
                "sandbox_patch_state", {"records": records}
            )
        )

    def test_lookup_set_bulk_operations(self):
        """Test operations on a lookup set with 10k elements."""
        # Patch storage to create a lookup set with 10k elements
        num_elements = 10000
        self.patch_lookup_set_storage(num_elements)
        self._sandbox.dump_state()

        # For storing performance data
        performance_data = []

        # Get baseline gas usage from calling hello world
        response, tx_result = self.lookup_set_contract.call(
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

        # Test contains operation for existing value
        print("\nTesting contains for existing value...")
        values_to_test = [f"value{i}" for i in [0, 1, 100, 999, 5000, 9999]]
        contains_gas = []

        for value in values_to_test:
            result, tx_result = self.lookup_set_contract.call(
                "contains", {"value": value}, return_full_result=True
            )
            gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
            contains_gas.append(gas_burn_tgas)

            contains = result.json().get("contains", False)
            assert contains, f"Value {value} should exist in the lookup set"
            print(f"  Contains value {value}: {gas_burn_tgas} TGas")

        # Add contains to performance data
        avg_contains_gas = sum(contains_gas) / len(contains_gas)
        performance_data.append(
            {
                "operation": "contains (existing)",
                "gas_tgas": avg_contains_gas,
                "ratio": avg_contains_gas / hello_world_gas_usage,
                "details": f"Average of {len(values_to_test)} values",
            }
        )

        # Test contains operation for non-existing value
        print("\nTesting contains for non-existing value...")
        result, tx_result = self.lookup_set_contract.call(
            "contains", {"value": "nonexistent_value"}, return_full_result=True
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        print(f"  Contains non-existing value: {gas_burn_tgas} TGas")

        performance_data.append(
            {
                "operation": "contains (non-existing)",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": "Check for a value that doesn't exist",
            }
        )

        # Test add operation (add new)
        print("\nTesting add operation (add new)...")
        result, tx_result = self.lookup_set_contract.call(
            "add", {"value": "new_value"}, return_full_result=True
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        print(f"  Add new value: {gas_burn_tgas} TGas")

        performance_data.append(
            {
                "operation": "add (new value)",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": "Add a new value to the set",
            }
        )

        # Test add operation (existing value - should be efficient)
        print("\nTesting add operation (existing value)...")
        result, tx_result = self.lookup_set_contract.call(
            "add", {"value": "value100"}, return_full_result=True
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        print(f"  Add existing value: {gas_burn_tgas} TGas")

        performance_data.append(
            {
                "operation": "add (existing value)",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": "Add a value that already exists (no-op)",
            }
        )

        # Test remove operation
        print("\nTesting remove operation...")
        result, tx_result = self.lookup_set_contract.call(
            "remove", {"value": "value5000"}, return_full_result=True
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        print(f"  Remove value: {gas_burn_tgas} TGas")

        performance_data.append(
            {
                "operation": "remove",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": "Remove an existing value",
            }
        )

        # Test discard operation (existing)
        print("\nTesting discard operation (existing value)...")
        result, tx_result = self.lookup_set_contract.call(
            "discard", {"value": "value9999"}, return_full_result=True
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        print(f"  Discard existing value: {gas_burn_tgas} TGas")

        performance_data.append(
            {
                "operation": "discard (existing)",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": "Discard an existing value",
            }
        )

        # Test discard operation (non-existing)
        print("\nTesting discard operation (non-existing value)...")
        result, tx_result = self.lookup_set_contract.call(
            "discard", {"value": "nonexistent_value"}, return_full_result=True
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        print(f"  Discard non-existing value: {gas_burn_tgas} TGas")

        performance_data.append(
            {
                "operation": "discard (non-existing)",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": "Discard a value that doesn't exist",
            }
        )

        # Generate performance comparison table
        console = Console()

        table = Table(title=f"LookupSet Performance (Size: {num_elements} elements)")

        table.add_column("Operation", style="cyan")
        table.add_column("Gas (TGas)", justify="right", style="green")
        table.add_column("vs. Baseline", justify="right", style="magenta")
        table.add_column("Details", style="yellow")

        # Also prepare data for Markdown export
        md_content = "# LookupSet Performance Test Results\n\n"
        md_content += f"LookupSet size: {num_elements} elements\n\n"
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
        with open(f"{results_dir}/lookup_set_performance_{num_elements}.md", "w") as f:
            f.write(md_content)

        print(
            f"\nResults saved to: {results_dir}/lookup_set_performance_{num_elements}.md"
        )
