"""
Access to blockchain context information for NEAR smart contracts.
"""

import near


class Context:
    """Access to blockchain context information"""

    @staticmethod
    def current_account_id() -> str:
        """Gets the current contract account ID"""
        return near.current_account_id()

    @staticmethod
    def predecessor_account_id() -> str:
        """Gets the account ID that called this contract"""
        return near.predecessor_account_id()

    @staticmethod
    def signer_account_id() -> str:
        """Gets the account ID that signed the transaction"""
        return near.signer_account_id()

    @staticmethod
    def attached_deposit() -> int:
        """Gets the attached deposit in yoctoNEAR"""
        return near.attached_deposit()

    @staticmethod
    def prepaid_gas() -> int:
        """Gets the prepaid gas"""
        return near.prepaid_gas()

    @staticmethod
    def used_gas() -> int:
        """Gets the used gas"""
        return near.used_gas()

    @staticmethod
    def block_height() -> int:
        """Gets the current block height"""
        return near.block_height()

    @staticmethod
    def block_timestamp() -> int:
        """Gets the current block timestamp in nanoseconds"""
        return near.block_timestamp()

    @staticmethod
    def epoch_height() -> int:
        """Gets the current epoch height"""
        return near.epoch_height()
