"""
This module provides higher-level abstractions over the low-level NEAR API,
making it easier to write smart contracts with Python.
"""

from .contract import Contract, ContractError, StorageError, InputError
from .storage import Storage
from .input import Input
from .context import Context
from .log import Log
from .value_return import ValueReturn
from .cross_contract import CrossContract
from .decorators import export, contract_method, view, call, init, callback
from .constants import ONE_TGAS, MAX_GAS, ONE_NEAR


# Type definitions
AccountId = str
Balance = int
Gas = int
PublicKey = bytes

__all__ = [
    "Contract",
    "ContractError",
    "StorageError",
    "InputError",
    "Storage",
    "Input",
    "Context",
    "Log",
    "ValueReturn",
    "CrossContract",
    "export",
    "contract_method",
    "view",
    "call",
    "init",
    "callback",
    "ONE_NEAR",
    "ONE_TGAS",
    "MAX_GAS",
    "AccountId",
    "Balance",
    "Gas",
    "PublicKey",
]
