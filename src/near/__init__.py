"""
NEAR blockchain host functions.

This module provides access to the NEAR blockchain host functions for smart contracts
written in Python. These functions allow contracts to interact with the NEAR blockchain,
including reading and writing state, making cross-contract calls, logging, and more.
"""

from typing import Callable

# Define __all__ to control what's exported with "from near import *"
__all__ = ["export"]  # Will add imported functions to this list

# Import and re-export all functions from submodules
from .registers import read_register, read_register_as_str, register_len, write_register

from .context import (
    current_account_id,
    signer_account_id,
    signer_account_pk,
    predecessor_account_id,
    input,
    input_as_str,
    block_height,
    block_timestamp,
    epoch_height,
    storage_usage,
)

from .economics import (
    account_balance,
    account_locked_balance,
    attached_deposit,
    prepaid_gas,
    used_gas,
)

from .math import (
    random_seed,
    sha256,
    keccak256,
    keccak512,
    ripemd160,
    ecrecover,
    ed25519_verify,
)

from .storage import storage_write, storage_read, storage_remove, storage_has_key

from .promises import (
    promise_create,
    promise_then,
    promise_and,
    promise_batch_create,
    promise_batch_then,
    promise_batch_action_create_account,
    promise_batch_action_deploy_contract,
    promise_batch_action_function_call,
    promise_batch_action_function_call_weight,
    promise_batch_action_transfer,
    promise_batch_action_stake,
    promise_batch_action_add_key_with_full_access,
    promise_batch_action_add_key_with_function_call,
    promise_batch_action_delete_key,
    promise_batch_action_delete_account,
    promise_yield_create,
    promise_yield_resume,
    promise_results_count,
    promise_result,
    promise_result_as_str,
    promise_return,
)

from .validator import validator_stake, validator_total_stake

from .misc import value_return, panic, panic_utf8, log_utf8, log, log_utf16, abort


# Update __all__ with all imported functions
# Register functions
__all__ += ["read_register", "read_register_as_str", "register_len", "write_register"]

# Context functions
__all__ += [
    "current_account_id",
    "signer_account_id",
    "signer_account_pk",
    "predecessor_account_id",
    "input",
    "input_as_str",
    "block_height",
    "block_timestamp",
    "epoch_height",
    "storage_usage",
]

# Economics functions
__all__ += [
    "account_balance",
    "account_locked_balance",
    "attached_deposit",
    "prepaid_gas",
    "used_gas",
]

# Math functions
__all__ += [
    "random_seed",
    "sha256",
    "keccak256",
    "keccak512",
    "ripemd160",
    "ecrecover",
    "ed25519_verify",
]

# Storage functions
__all__ += ["storage_write", "storage_read", "storage_remove", "storage_has_key"]

# Promise functions
__all__ += [
    "promise_create",
    "promise_then",
    "promise_and",
    "promise_batch_create",
    "promise_batch_then",
    "promise_batch_action_create_account",
    "promise_batch_action_deploy_contract",
    "promise_batch_action_function_call",
    "promise_batch_action_function_call_weight",
    "promise_batch_action_transfer",
    "promise_batch_action_stake",
    "promise_batch_action_add_key_with_full_access",
    "promise_batch_action_add_key_with_function_call",
    "promise_batch_action_delete_key",
    "promise_batch_action_delete_account",
    "promise_yield_create",
    "promise_yield_resume",
    "promise_results_count",
    "promise_result",
    "promise_result_as_str",
    "promise_return",
]

# Validator functions
__all__ += ["validator_stake", "validator_total_stake"]

# Miscellaneous functions
__all__ += [
    "value_return",
    "panic",
    "panic_utf8",
    "log_utf8",
    "log",
    "log_utf16",
    "abort",
]

# Testing functions
__all__ += [
    "test_method",
    "build_contract",
    "test_account_id",
    "test_add_extra_balance",
]


def export(fn: Callable) -> Callable:
    """
    Decorator for NEAR exported methods.

    This decorator marks a function as a public-facing contract method
    that can be called from outside the contract.

    Args:
        fn: The function to be exported

    Returns:
        The same function, marked for export

    Example:
        @near.export
        def my_method(param1: str, param2: int) -> str:
            # Contract method implementation
            return "Result"
    """
    return fn
