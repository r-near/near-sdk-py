from near_pytest.testing import NearTestCase


class TestVectorContract(NearTestCase):
    @classmethod
    def setup_class(cls):
        # Call parent setup method first
        super().setup_class()

        # Compile the contract
        cls.wasm_path = cls.compile_contract(
            "integration_tests/contracts/collections/vector.py", single_file=True
        )

        # Create account for contract
        cls.vector_account = cls.create_account("vector")

        # Deploy contract
        cls.vector_contract = cls.deploy_contract(cls.vector_account, cls.wasm_path)

        # Save initial state for future resets
        cls.save_state()

    def setup_method(self):
        # Reset to initial state before each test method
        self.reset_state()

    def test_vector_basics(self):
        """Test basic Vector operations."""
        # Add items to the vector
        result = self.vector_contract.call(
            method_name="add_item",
            args={"item": "first"},
        )
        assert result.json()["length"] == 1

        result = self.vector_contract.call(
            method_name="add_item",
            args={"item": "second"},
        )
        assert result.json()["length"] == 2

        result = self.vector_contract.call(
            method_name="add_item",
            args={"item": "third"},
        )
        assert result.json()["length"] == 3

        # Get length
        length = self.vector_contract.view("get_length", {})
        assert length.json()["length"] == 3

        # Get item at index
        item = self.vector_contract.view("get_item", {"index": 0})
        assert item.json()["item"] == "first"

        item = self.vector_contract.view("get_item", {"index": 1})
        assert item.json()["item"] == "second"

        # Clear items
        result = self.vector_contract.call(
            method_name="clear_items",
            args={},
        )
        assert result.json()["length"] == 0

        # Verify length is 0 after clearing
        length = self.vector_contract.view("get_length", {})
        assert length.json()["length"] == 0

    def test_vector_pop(self):
        """Test Vector pop operations."""
        # Add items to the vector
        self.vector_contract.call(
            method_name="add_item",
            args={"item": "item1"},
        )
        self.vector_contract.call(
            method_name="add_item",
            args={"item": "item2"},
        )
        self.vector_contract.call(
            method_name="add_item",
            args={"item": "item3"},
        )

        # Pop the last item
        popped = self.vector_contract.call(
            method_name="pop_item",
            args={},
        )
        assert popped.json()["item"] == "item3"

        # Check length after pop
        length = self.vector_contract.view("get_length", {})
        assert length.json()["length"] == 2

        # Get all items after pop
        items = self.vector_contract.view("get_all_items", {})
        assert items.json()["items"] == ["item1", "item2"]

        # Pop at specific index
        popped = self.vector_contract.call(
            method_name="pop_item",
            args={"index": 0},
        )
        assert popped.json()["item"] == "item1"

        # Check items after specific index pop
        items = self.vector_contract.view("get_all_items", {})
        assert items.json()["items"] == ["item2"]

    def test_vector_swap_remove(self):
        """Test Vector swap_remove operations."""

        self.vector_contract.call(method_name="clear_items")
        # Add items to the vector
        for i in range(5):
            self.vector_contract.call(
                method_name="add_item",
                args={"item": f"item{i}"},
            )

        # Check initial state
        items = self.vector_contract.view("get_all_items", {})
        assert items.json()["items"] == ["item0", "item1", "item2", "item3", "item4"]

        # Swap remove at index 1
        removed = self.vector_contract.call(
            method_name="swap_remove_item",
            args={"index": 1},
        )
        assert removed.json()["item"] == "item1"

        # Check items after swap_remove
        # The last item should be moved to position 1
        items = self.vector_contract.view("get_all_items", {})
        assert items.json()["items"] == ["item0", "item4", "item2", "item3"]

        # Check length after swap_remove
        length = self.vector_contract.view("get_length", {})
        assert length.json()["length"] == 4
