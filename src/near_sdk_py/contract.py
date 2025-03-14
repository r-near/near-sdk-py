"""
Base contract class and contract-related exceptions.
"""

from .log import Log


class ContractError(Exception):
    """Base exception for all contract errors"""

    pass


class ContractPanic(ContractError):
    """Exception that triggers a contract panic"""

    pass


class StorageError(ContractError):
    """Error related to contract storage operations"""

    pass


class AccessDenied(ContractError):
    """Error for unauthorized access attempts"""

    pass


class InvalidInput(ContractError):
    """Error for invalid function arguments"""

    pass


class ContractStorage:
    """A more intuitive interface for contract storage with dictionary-like access"""

    def __getitem__(self, key):
        """Allow dictionary-style access: contract.storage[key]"""
        from near_sdk_py.storage import Storage

        value = Storage.get_json(key)
        if value is None:
            raise KeyError(key)
        return value

    def __setitem__(self, key, value):
        """Allow dictionary-style assignment: contract.storage[key] = value"""
        from near_sdk_py.storage import Storage

        try:
            Storage.set_json(key, value)
        except Exception as e:
            raise StorageError(f"Failed to store value: {e}")

    def __delitem__(self, key):
        """Allow dictionary-style deletion: del contract.storage[key]"""
        from near_sdk_py.storage import Storage

        if not Storage.has(key):
            raise KeyError(key)
        Storage.remove(key)

    def __contains__(self, key):
        """Allow 'in' operator: key in contract.storage"""
        from near_sdk_py.storage import Storage

        return Storage.has(key)

    # Redis-like methods
    def get(self, key, default=None):
        """Get a value with optional default"""
        from near_sdk_py.storage import Storage

        value = Storage.get_json(key)
        return value if value is not None else default

    def set(self, key, value):
        """Set a value"""
        from near_sdk_py.storage import Storage

        try:
            Storage.set_json(key, value)
            return True
        except Exception as e:
            raise StorageError(f"Failed to store value: {e}")

    def delete(self, key):
        """Delete a key"""
        from near_sdk_py.storage import Storage

        if Storage.has(key):
            Storage.remove(key)
            return True
        return False


class Contract:
    """Base class for NEAR smart contracts."""

    def __init__(self):
        """Initialize the contract with storage"""
        self._storage = ContractStorage()

    @property
    def storage(self):
        """Access contract storage with dictionary-like interface"""
        return self._storage

    @property
    def current_account_id(self):
        """Get the current contract account ID"""
        from near_sdk_py.context import Context

        return Context.current_account_id()

    @property
    def predecessor_account_id(self):
        """Get the account ID of the immediate caller"""
        from near_sdk_py.context import Context

        return Context.predecessor_account_id()

    @property
    def signer_account_id(self):
        """Get the account ID that signed the transaction"""
        from near_sdk_py.context import Context

        return Context.signer_account_id()

    @property
    def attached_deposit(self):
        """Get the attached deposit in yoctoNEAR"""
        from near_sdk_py.context import Context

        return Context.attached_deposit()

    @property
    def prepaid_gas(self):
        """Get the prepaid gas"""
        from near_sdk_py.context import Context

        return Context.prepaid_gas()

    @property
    def used_gas(self):
        """Get the used gas"""
        from near_sdk_py.context import Context

        return Context.used_gas()

    @property
    def block_height(self):
        """Get the current block height"""
        from near_sdk_py.context import Context

        return Context.block_height()

    @property
    def block_timestamp(self):
        """Get the current block timestamp in nanoseconds"""
        from near_sdk_py.context import Context

        return Context.block_timestamp()

    # ----- Common validations -----

    def assert_one_yocto(self):
        """Assert exactly one yoctoNEAR was attached to the call"""
        if self.attached_deposit != 1:
            raise AccessDenied("Requires exactly 1 yoctoNEAR")

    def assert_min_deposit(self, amount):
        """Assert minimum deposit amount"""
        if self.attached_deposit < amount:
            raise InvalidInput(
                f"Requires at least {amount} yoctoNEAR (received {self.attached_deposit})"
            )

    def assert_owner(self, owner_key="owner"):
        """Assert the caller is the contract owner"""
        owner = self.storage.get(owner_key)
        if owner and self.predecessor_account_id != owner:
            raise AccessDenied("Only the owner can perform this action")

    # ----- Logging helpers -----

    def log_info(self, message):
        """Log an informational message"""
        Log.info(message)

    def log_warning(self, message):
        """Log a warning message"""
        Log.warning(message)

    def log_error(self, message):
        """Log an error message"""
        Log.error(message)

    def log_event(self, event_type, data):
        """Log a structured event"""
        Log.event(event_type, data)
