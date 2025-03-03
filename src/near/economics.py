"""
NEAR Economics API functions.

This module provides functions for working with NEAR token economics, including
account balances, deposits, and gas metering.
"""


def account_balance() -> int:
    """
    Get the balance of the current account.

    Returns:
        The account balance in yoctoNEAR (10^-24 NEAR)

    Note:
        This is a mock function in the local environment and will return 0.
    """
    return 0


def account_locked_balance() -> int:
    """
    Get the locked balance of the current account.

    Returns:
        The locked balance in yoctoNEAR (10^-24 NEAR)

    Note:
        This is a mock function in the local environment and will return 0.
    """
    return 0


def attached_deposit() -> int:
    """
    Get the amount of NEAR attached to the current function call.

    Returns:
        The attached deposit in yoctoNEAR (10^-24 NEAR)

    Note:
        This is a mock function in the local environment and will return 0.
    """
    return 0


def prepaid_gas() -> int:
    """
    Get the amount of gas attached to the current function call.

    Returns:
        The prepaid gas in gas units

    Note:
        This is a mock function in the local environment and will return 0.
    """
    return 0


def used_gas() -> int:
    """
    Get the amount of gas used so far in the current function call.

    Returns:
        The used gas in gas units

    Note:
        This is a mock function in the local environment and will return 0.
    """
    return 0
