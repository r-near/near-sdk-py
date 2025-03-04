"""
Base contract class and contract-related exceptions.
"""

import near


class ContractError(Exception):
    """Base class for contract-related errors"""

    pass


class StorageError(ContractError):
    """Error related to storage operations"""

    pass


class InputError(ContractError):
    """Error related to input serialization/deserialization"""

    pass


class Contract:
    """Base class for NEAR smart contracts with higher-level API"""

    @staticmethod
    def assert_one_yocto():
        """
        Ensures exactly one yoctoNEAR was attached to the call.
        Commonly used to ensure the user has authorized the transaction.
        """
        attached = near.attached_deposit()
        if attached != 1:
            near.panic_utf8(f"Requires exactly 1 yoctoNEAR (received {attached})")

    @staticmethod
    def assert_min_deposit(amount: int):
        """Ensures at least the specified amount was attached"""
        attached = near.attached_deposit()
        if attached < amount:
            near.panic_utf8(
                f"Requires at least {amount} yoctoNEAR (received {attached})"
            )
