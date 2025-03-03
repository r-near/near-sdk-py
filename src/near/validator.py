"""
NEAR Validator API functions.

This module provides functions for interacting with the NEAR validator system.
"""


def validator_stake(account_id: str) -> int:
    """
    Get the stake of the validator with the given account ID.

    Args:
        account_id: The account ID of the validator

    Returns:
        The stake of the validator in yoctoNEAR (10^-24 NEAR)

    Note:
        This is a mock function in the local environment and will return 0.
    """
    return 0


def validator_total_stake() -> int:
    """
    Get the total stake of all validators.

    Returns:
        The total stake in yoctoNEAR (10^-24 NEAR)

    Note:
        This is a mock function in the local environment and will return 0.
    """
    return 0
