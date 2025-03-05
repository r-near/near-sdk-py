"""
Utility functions for working with collection prefixes.
"""

from typing import Any, Callable


def create_enum_prefix(enum_type: type, enum_value: Any) -> str:
    """
    Create a prefix from an enum value.
    This is useful for ensuring each collection has a unique prefix.

    Example:
    ```python
    class StorageKey(Enum):
        TOKENS = 1
        BALANCES = 2
        APPROVALS = 3

    tokens = Vector(create_enum_prefix(StorageKey, StorageKey.TOKENS))
    balances = UnorderedMap(create_enum_prefix(StorageKey, StorageKey.BALANCES))
    ```

    Args:
        enum_type: The enum class
        enum_value: The enum value

    Returns:
        A string prefix
    """
    return f"{enum_type.__name__}:{enum_value.name}"


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
