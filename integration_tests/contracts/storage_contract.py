from near_sdk_py import Contract, view, call, init


class StorageContract(Contract):
    """
    A contract demonstrating the dictionary-like storage interface
    of the Contract base class.
    """

    @init
    def initialize(self):
        """Initialize the contract."""
        return {"success": True}

    @call
    def set_value(self, key, value):
        """
        Store a value in contract storage.

        Args:
            key: The storage key
            value: The value to store (can be any JSON-serializable data)

        Returns:
            Success status
        """
        self.storage[key] = value
        return {"success": True}

    @view
    def get_value(self, key):
        """
        Retrieve a value from contract storage.

        Args:
            key: The storage key to retrieve

        Returns:
            The stored value or raises KeyError if not found
        """
        return self.storage[key]

    @view
    def get_value_with_default(self, key, default=None):
        """
        Retrieve a value with a default if key doesn't exist.

        Args:
            key: The storage key to retrieve
            default: The default value to return if key doesn't exist

        Returns:
            The stored value or the default
        """
        return self.storage.get(key, default)

    @call
    def delete_value(self, key):
        """
        Delete a value from contract storage.

        Args:
            key: The storage key to delete

        Returns:
            Success status
        """
        if key in self.storage:
            del self.storage[key]
            return {"success": True}
        else:
            return {"success": False, "message": "Key not found"}

    @view
    def has_key(self, key):
        """
        Check if a key exists in contract storage.

        Args:
            key: The storage key to check

        Returns:
            True if the key exists, False otherwise
        """
        return key in self.storage
