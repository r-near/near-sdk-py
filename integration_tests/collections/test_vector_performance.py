import base64
import json
import time

from near_pytest.testing import NearTestCase


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

        # Process elements in batches to avoid memory issues
        batch_size = 500

        print(f"Creating state patch records for {num_elements} elements...")
        start_time = time.time()

        for batch_start in range(0, num_elements, batch_size):
            batch_end = min(batch_start + batch_size, num_elements)
            batch_records = []

            # For each element in this batch
            for i in range(batch_start, batch_end):
                # Create the key for this element
                element_key = f"items:{i}"
                encoded_key = base64.b64encode(element_key.encode("utf-8")).decode(
                    "utf-8"
                )

                # Create the value (JSON serialized string)
                value = f"bulk_item_{i}"
                encoded_value = base64.b64encode(
                    json.dumps(value).encode("utf-8")
                ).decode("utf-8")

                # Add to records
                batch_records.append(
                    {
                        "Data": {
                            "account_id": account_id,
                            "data_key": encoded_key,
                            "value": encoded_value,
                        }
                    }
                )

            # Extend the main records list
            records.extend(batch_records)

            # Print progress
            print(f"  Created records for elements {batch_start} to {batch_end - 1}")

        # Submit the patch state request
        print(f"Submitting patch state request with {len(records)} records...")
        result = self.__class__._client._run_async(
            self.__class__._client._master_account.provider.json_rpc(
                "sandbox_patch_state", {"records": records}
            )
        )

        elapsed_time = time.time() - start_time
        print(f"Storage patching completed in {elapsed_time:.2f} seconds")

        # Verify the result
        if result.get("error"):
            raise Exception(f"Error patching state: {result['error']}")
        else:
            print("State patched successfully")

    def test_vector_bulk_operations(self):
        """Test operations on a vector with 10k elements."""
        # Patch storage to create a vector with 10k elements
        num_elements = 10000
        self.patch_vector_storage(num_elements)
        self._sandbox.dump_state()

        # Verify length
        print("\nVerifying vector length...")
        length = self.vector_contract.view("get_length", {})
        assert length.json()["length"] == num_elements
        print(f"Confirmed vector length: {num_elements}")

        # Test random access to verify data integrity
        print("\nTesting random access...")
        indices_to_test = [0, 1, 100, 999, 5000, 9999]
        for idx in indices_to_test:
            result = self.vector_contract.view("get_item", {"index": idx})
            item = result.json()["item"]
            expected = f"bulk_item_{idx}"
            assert item == expected, (
                f"Item at index {idx} doesn't match: {item} vs {expected}"
            )
            print(f"  Verified item at index {idx}: {item}")

        # Benchmark pop operations
        print("\nBenchmarking pop operations...")
        start_time = time.time()
        result = self.vector_contract.call(
            method_name="pop_item",
            args={},  # Default pops the last item
        )
        pop_time = time.time() - start_time
        popped = result.json()["item"]
        print(f"Popped last item: {popped} in {pop_time:.6f} seconds")

        # Verify length after pop
        length = self.vector_contract.view("get_length", {})
        assert length.json()["length"] == num_elements - 1

        # Benchmark swap_remove operations
        print("\nBenchmarking swap_remove operations...")
        start_time = time.time()
        result = self.vector_contract.call(
            method_name="swap_remove_item",
            args={"index": 5000},
        )
        swap_time = time.time() - start_time
        removed = result.json()["item"]
        print(f"Swap removed item at index 5000: {removed} in {swap_time:.6f} seconds")

        # Verify length after swap_remove
        length = self.vector_contract.view("get_length", {})
        assert length.json()["length"] == num_elements - 2
