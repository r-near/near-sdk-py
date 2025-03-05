"""
Utility functions for working with collection prefixes.
"""

from typing import Any, Callable  # Keep typing for docs


def create_enum_prefix(enum_type: Any, enum_value: Any) -> str:
    """
    Create a prefix from an enum value.
    This is useful for ensuring each collection has a unique prefix.

    Adapted to work with MicroPython by accepting any type with name attributes.

    Example:
    ```python
    # Instead of using Enum, define a class with constants
    class StorageKey:
        TOKENS = 1
        BALANCES = 2
        APPROVALS = 3

        # Add names corresponding to values
        names = {
            TOKENS: "TOKENS",
            BALANCES: "BALANCES",
            APPROVALS: "APPROVALS"
        }

        @property
        def name(self):
            return self.names[self]

    # Create instances
    StorageKey.TOKENS = StorageKey()
    StorageKey.BALANCES = StorageKey()
    StorageKey.APPROVALS = StorageKey()

    tokens = Vector(create_enum_prefix(StorageKey, StorageKey.TOKENS))
    balances = UnorderedMap(create_enum_prefix(StorageKey, StorageKey.BALANCES))
    ```

    Args:
        enum_type: The class with name attributes
        enum_value: The value with a name property

    Returns:
        A string prefix
    """
    # Access name through a property or attribute
    name = enum_value.name if hasattr(enum_value, "name") else str(enum_value)
    type_name = enum_type.__name__ if hasattr(enum_type, "__name__") else str(enum_type)

    return f"{type_name}:{name}"


def create_prefix_guard(base_prefix: str) -> Callable[[str], str]:
    """
    Create a function that generates prefixes with a common base.
    This helps manage prefixes for nested collections.

    Example:
    ```python
    # In a contract class
    def __init__(self):
        self.prefix = create_prefix_guard("contract")
        self.accounts = UnorderedMap(self.prefix("accounts"))

        # For each account, we create nested collections
        account_id = "alice.near"
        account_prefix = self.prefix(f"account:{account_id}")

        tokens_prefix = create_prefix_guard(account_prefix)
        tokens = Vector(tokens_prefix("tokens"))
        approvals = UnorderedMap(tokens_prefix("approvals"))
    ```

    Args:
        base_prefix: The base prefix

    Returns:
        A function that generates prefixes with the base prefix
    """

    def prefix_fn(sub_prefix: str) -> str:
        return f"{base_prefix}:{sub_prefix}"

    return prefix_fn
