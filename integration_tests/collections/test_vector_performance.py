import base64
import json
import os
from datetime import datetime

from near_pytest.testing import NearTestCase
from rich.console import Console
from rich.table import Table


class TestVectorBulkPerformance(NearTestCase):
    @classmethod
    def setup_class(cls):
        # Call parent setup method first
        super().setup_class()

        # Compile the contract
        cls.wasm_path = cls.compile_contract(
            "integration_tests/contracts/collections/vector.py", single_file=True
        )

        # Create account for contract
        cls.vector_account = cls.create_account("vector_bulk")

        # Deploy contract
        cls.vector_contract = cls.deploy_contract(cls.vector_account, cls.wasm_path)

        # Save initial state for future resets
        cls.save_state()

    def setup_method(self):
        # Reset to initial state before each test method
        self.reset_state()

    def patch_vector_storage(self, num_elements):
        """
        Directly patch the contract storage to create a vector with specified number of elements
        using the sandbox_patch_state RPC call.
        """
        account_id = self.vector_account.account_id

        # Create records array
        records = []

        # First, add the metadata record with length information
        metadata = {"version": "1.0.0", "type": "v", "length": num_elements}
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

        # Create records for all elements
        for i in range(num_elements):
            # Create the key for this element
            element_key = f"items:{i}"
            encoded_key = base64.b64encode(element_key.encode("utf-8")).decode("utf-8")

            # Create the value (JSON serialized string)
            value = f"bulk_item_{i}"
            encoded_value = base64.b64encode(json.dumps(value).encode("utf-8")).decode(
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
        print(f"Patching state with {num_elements} vector elements...")
        self.__class__._client._run_async(
            self.__class__._client._master_account.provider.json_rpc(
                "sandbox_patch_state", {"records": records}
            )
        )

    def test_vector_bulk_operations(self):
        """Test operations on a vector with 10k elements."""
        # Patch storage to create a vector with 10k elements
        num_elements = 10000
        self.patch_vector_storage(num_elements)
        self._sandbox.dump_state()

        # For storing performance data
        performance_data = []

        # Get baseline gas usage from calling hello world
        response, tx_result = self.vector_contract.call(
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
        print("\nVerifying vector length...")
        length, tx_result = self.vector_contract.call(
            "get_length", {}, return_full_result=True
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        print(f"Length check gas usage: {gas_burn_tgas} TGas")
        assert gas_burn_tgas < 10, "Length check uses too much gas"
        assert length.json()["length"] == num_elements
        print(f"Confirmed vector length: {num_elements}")

        # Add length to performance data
        performance_data.append(
            {
                "operation": "get_length",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": f"Vector size: {num_elements}",
            }
        )

        # Test random access to verify data integrity and measure gas
        print("\nTesting random access...")
        # We'll store all random access operations to average them later
        random_access_gas = []

        indices_to_test = [0, 1, 100, 999, 5000, 9999]
        for idx in indices_to_test:
            result, tx_result = self.vector_contract.call(
                "get_item", {"index": idx}, return_full_result=True
            )
            gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
            random_access_gas.append(gas_burn_tgas)

            item = result.json()["item"]
            expected = f"bulk_item_{idx}"
            assert item == expected, (
                f"Item at index {idx} doesn't match: {item} vs {expected}"
            )
            print(f"  Get item at index {idx}: {gas_burn_tgas} TGas")
            assert gas_burn_tgas < 10, (
                f"Random access at position {idx} uses too much gas"
            )

        # Add average random access to performance data
        avg_random_access = sum(random_access_gas) / len(random_access_gas)
        performance_data.append(
            {
                "operation": "get_item (random access)",
                "gas_tgas": avg_random_access,
                "ratio": avg_random_access / hello_world_gas_usage,
                "details": f"Average of {len(indices_to_test)} positions",
            }
        )

        # Also add individual indices for detailed comparison
        for i, idx in enumerate(indices_to_test):
            performance_data.append(
                {
                    "operation": f"  - get_item at index {idx}",
                    "gas_tgas": random_access_gas[i],
                    "ratio": random_access_gas[i] / hello_world_gas_usage,
                    "details": f"Direct access at position {idx}",
                }
            )

        # Benchmark pop operations
        print("\nBenchmarking pop operations...")
        result, tx_result = self.vector_contract.call(
            method_name="pop_item",
            args={},  # Default pops the last item
            return_full_result=True,
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        popped = result.json()["item"]
        print(f"Popped last item: {popped}, gas usage: {gas_burn_tgas} TGas")
        assert gas_burn_tgas < 10, "Pop operation uses too much gas"

        # Add pop to performance data
        performance_data.append(
            {
                "operation": "pop_item",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": "Removes last element",
            }
        )

        # Verify length after pop
        length, tx_result = self.vector_contract.call(
            "get_length", {}, return_full_result=True
        )
        assert length.json()["length"] == num_elements - 1

        # Benchmark swap_remove operations
        print("\nBenchmarking swap_remove operations...")
        result, tx_result = self.vector_contract.call(
            method_name="swap_remove_item",
            args={"index": 5000},
            return_full_result=True,
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        removed = result.json()["item"]
        print(
            f"Swap removed item at index 5000: {removed}, gas usage: {gas_burn_tgas} TGas"
        )
        assert gas_burn_tgas < 10, "Swap remove operation uses too much gas"

        # Add swap_remove to performance data
        performance_data.append(
            {
                "operation": "swap_remove_item",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": "Swaps with last element and removes",
            }
        )

        # Verify length after swap_remove
        length, tx_result = self.vector_contract.call(
            "get_length", {}, return_full_result=True
        )
        assert length.json()["length"] == num_elements - 2

        # Test add item operation
        print("\nTesting add item operation...")
        result, tx_result = self.vector_contract.call(
            method_name="add_item",
            args={"item": "new_test_item"},
            return_full_result=True,
        )
        gas_burn_tgas = tx_result.receipt_outcome[0].gas_burnt / 10**12
        print(f"Add item gas usage: {gas_burn_tgas} TGas")
        assert gas_burn_tgas < 10, "Add item operation uses too much gas"

        # Add add_item to performance data
        performance_data.append(
            {
                "operation": "add_item",
                "gas_tgas": gas_burn_tgas,
                "ratio": gas_burn_tgas / hello_world_gas_usage,
                "details": "Appends item to vector",
            }
        )

        # Note: We're skipping full iteration test as it would exceed gas limits with 10k elements
        print(
            "\nNote: Skipping full iteration test (get_all_items) as it would exceed gas limits with 10k elements"
        )

        # Generate performance comparison table
        console = Console()

        table = Table(title=f"Vector Performance (Size: {num_elements} elements)")

        table.add_column("Operation", style="cyan")
        table.add_column("Gas (TGas)", justify="right", style="green")
        table.add_column("vs. Baseline", justify="right", style="magenta")
        table.add_column("Details", style="yellow")

        # Also prepare data for Markdown export
        md_content = "# Vector Performance Test Results\n\n"
        md_content += f"Vector size: {num_elements} elements\n\n"
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
        with open(f"{results_dir}/vector_performance_{num_elements}.md", "w") as f:
            f.write(md_content)

        print(f"\nResults saved to: {results_dir}/vector_performance_{num_elements}.md")
