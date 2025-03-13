"""
NEAR Promises API functions.

This module provides functions for creating and managing cross-contract call promises,
which allow NEAR smart contracts to call methods on other contracts.
"""

from typing import List, Tuple, Union


def promise_create(
    account_id: str, function_name: str, arguments: str, amount: int, gas: int
) -> int:
    """
    Create a new promise to perform a cross-contract call.

    Args:
        account_id: The account ID of the contract to call
        function_name: The name of the function to call
        arguments: The serialized arguments to pass to the function
        amount: The amount of NEAR tokens to attach to the call
        gas: The amount of gas to attach to the call

    Returns:
        A promise index that can be used to chain or return promise results

    Note:
        This is a mock function in the local environment and will return 0.
    """
    return 0


def promise_then(
    promise_index: int,
    account_id: str,
    function_name: str,
    arguments: str,
    amount: int,
    gas: int,
) -> int:
    """
    Chain a promise to be executed after the successful completion of the specified promise.

    Args:
        promise_index: The index of the promise that must be completed first
        account_id: The account ID of the contract to call in the callback
        function_name: The name of the function to call in the callback
        arguments: The serialized arguments to pass to the function
        amount: The amount of NEAR tokens to attach to the call
        gas: The amount of gas to attach to the call

    Returns:
        A promise index that can be used to chain or return promise results

    Note:
        This is a mock function in the local environment and will return 0.
    """
    return 0


def promise_and(promise_indices: List[int]) -> int:
    """
    Create a new promise that will execute after all the given promises are complete.

    Args:
        promise_indices: A list of promise indices that must be completed

    Returns:
        A promise index that can be used to chain or return promise results

    Note:
        This is a mock function in the local environment and will return 0.
    """
    return 0


def promise_batch_create(account_id: str) -> int:
    """
    Create a new promise batch to perform multiple actions on a single account.

    Args:
        account_id: The account ID to perform the batch on

    Returns:
        A promise batch index

    Note:
        This is a mock function in the local environment and will return 0.
    """
    return 0


def promise_batch_then(promise_index: int, account_id: str) -> int:
    """
    Create a new promise batch that will execute after the given promise is complete.

    Args:
        promise_index: The index of the promise that must be completed first
        account_id: The account ID to perform the batch on

    Returns:
        A promise batch index

    Note:
        This is a mock function in the local environment and will return 0.
    """
    return 0


def promise_batch_action_create_account(promise_index: int) -> None:
    """
    Add a "create account" action to the given promise batch.

    Args:
        promise_index: The index of the promise batch

    Note:
        This is a mock function in the local environment and has no effect.
    """
    pass


def promise_batch_action_deploy_contract(promise_index: int, code: bytes) -> None:
    """
    Add a "deploy contract" action to the given promise batch.

    Args:
        promise_index: The index of the promise batch
        code: The WASM code of the contract to deploy

    Note:
        This is a mock function in the local environment and has no effect.
    """
    pass


def promise_batch_action_function_call(
    promise_index: int, function_name: str, arguments: str, amount: int, gas: int
) -> None:
    """
    Add a "function call" action to the given promise batch.

    Args:
        promise_index: The index of the promise batch
        function_name: The name of the function to call
        arguments: The serialized arguments to pass to the function
        amount: The amount of NEAR tokens to attach to the call
        gas: The amount of gas to attach to the call

    Note:
        This is a mock function in the local environment and has no effect.
    """
    pass


def promise_batch_action_function_call_weight(
    promise_index: int,
    function_name: str,
    arguments: str,
    amount: int,
    gas: int,
    weight: int,
) -> None:
    """
    Add a "function call with weight" action to the given promise batch.

    Args:
        promise_index: The index of the promise batch
        function_name: The name of the function to call
        arguments: The serialized arguments to pass to the function
        amount: The amount of NEAR tokens to attach to the call
        gas: The amount of gas to attach to the call
        weight: The execution weight of this call

    Note:
        This is a mock function in the local environment and has no effect.
    """
    pass


def promise_batch_action_transfer(promise_index: int, amount: int) -> None:
    """
    Add a "transfer" action to the given promise batch.

    Args:
        promise_index: The index of the promise batch
        amount: The amount of NEAR tokens to transfer

    Note:
        This is a mock function in the local environment and has no effect.
    """
    pass


def promise_batch_action_stake(
    promise_index: int, amount: int, pub_key: Union[bytes, str]
) -> None:
    """
    Add a "stake" action to the given promise batch.

    Args:
        promise_index: The index of the promise batch
        amount: The amount of NEAR tokens to stake
        pub_key: The public key to use for staking

    Note:
        This is a mock function in the local environment and has no effect.
    """
    pass


def promise_batch_action_add_key_with_full_access(
    promise_index: int, public_key: Union[bytes, str], nonce: int
) -> None:
    """
    Add an "add full access key" action to the given promise batch.

    Args:
        promise_index: The index of the promise batch
        public_key: The public key to add (borsh-serialized)
        nonce: The nonce for the key

    Note:
        This is a mock function in the local environment and has no effect.
    """
    pass


def promise_batch_action_add_key_with_function_call(
    promise_index: int,
    public_key: Union[bytes, str],
    nonce: int,
    allowance: int,
    receiver_id: str,
    function_names: str,
) -> None:
    """
    Add an "add function call access key" action to the given promise batch.

    Args:
        promise_index: The index of the promise batch
        public_key: The public key to add
        nonce: The nonce for the key
        allowance: The amount of tokens this key is allowed to spend
        receiver_id: The account this key can call
        function_names: Comma-separated list of method names this key can call

    Note:
        This is a mock function in the local environment and has no effect.
    """
    pass


def promise_batch_action_delete_key(
    promise_index: int, public_key: Union[bytes, str]
) -> None:
    """
    Add a "delete key" action to the given promise batch.

    Args:
        promise_index: The index of the promise batch
        public_key: The public key to delete

    Note:
        This is a mock function in the local environment and has no effect.
    """
    pass


def promise_batch_action_delete_account(
    promise_index: int, beneficiary_id: str
) -> None:
    """
    Add a "delete account" action to the given promise batch.

    Args:
        promise_index: The index of the promise batch
        beneficiary_id: The account ID that will receive the remaining balance

    Note:
        This is a mock function in the local environment and has no effect.
    """
    pass


def promise_yield_create(
    function_name: str, arguments: str, gas: int, gas_weight: int
) -> Tuple[int, str]:
    """
    Create a promise yield that will call a function with given arguments.

    Args:
        function_name: The name of the function to call
        arguments: The serialized arguments to pass to the function
        gas: The amount of gas to attach to the call
        gas_weight: The execution weight of this call

    Returns:
        A tuple of (promise_id, data_id)

    Note:
        This is a mock function in the local environment and will return (0, "").
    """
    return (0, "")


def promise_yield_resume(data_id: str, payload: Union[bytes, str]) -> bool:
    """
    Resume a promise yield with the given payload.

    Args:
        data_id: The data ID of the promise yield
        payload: The payload to resume with

    Returns:
        True if the promise yield was successfully resumed, False otherwise

    Note:
        This is a mock function in the local environment and will return False.
    """
    return False


def promise_results_count() -> int:
    """
    Get the number of results available for the execution of the last promise.

    Returns:
        The number of results

    Note:
        This is a mock function in the local environment and will return 0.
    """
    return 0


def promise_result(result_idx: int) -> Tuple[int, bytes]:
    """
    Get the result of a promise at the given index.

    Args:
        result_idx: The index of the result

    Returns:
        A tuple of (status, result_bytes)

    Note:
        This is a mock function in the local environment and will return (0, b"").
    """
    return (0, b"")


def promise_result_as_str(result_idx: int) -> Tuple[int, str]:
    """
    Get the result of a promise at the given index as a string.

    Args:
        result_idx: The index of the result

    Returns:
        A tuple of (status, result_string)

    Note:
        This is a mock function in the local environment and will return (0, "").
    """
    return (0, "")


def promise_return(promise_id: int) -> None:
    """
    Return the result of the given promise as the result of the current function.

    Args:
        promise_id: The ID of the promise

    Note:
        This is a mock function in the local environment and has no effect.
    """
    pass
