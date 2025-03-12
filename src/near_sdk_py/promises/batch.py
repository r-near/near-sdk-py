import json
from typing import Any, List, Optional

import near
from near_sdk_py.constants import ONE_TGAS


class BatchAction:
    """Represents a batch action for a NEAR promise."""

    CREATE_ACCOUNT = "create_account"
    DEPLOY_CONTRACT = "deploy_contract"
    FUNCTION_CALL = "function_call"
    TRANSFER = "transfer"
    STAKE = "stake"
    ADD_KEY_FULL_ACCESS = "add_key_full_access"
    ADD_KEY_FUNCTION_CALL = "add_key_function_call"
    DELETE_KEY = "delete_key"
    DELETE_ACCOUNT = "delete_account"


class PromiseBatch:
    """A batch of actions to be executed on a NEAR account."""

    def __init__(self, promise_id: int, gas: int = 5 * ONE_TGAS):
        """
        Initialize a promise batch.

        Args:
            promise_id: The NEAR promise ID to wrap
            gas: Gas to use for subsequent operations (default: 5 TGas)
        """
        self._promise_id = promise_id
        self._gas = gas

    def create_account(self) -> "PromiseBatch":
        """
        Add CreateAccount action to this batch.

        Returns:
            Self for method chaining
        """
        near.promise_batch_action_create_account(self._promise_id)
        return self

    def deploy_contract(self, code: bytes) -> "PromiseBatch":
        """
        Add DeployContract action to this batch.

        Args:
            code: The Wasm binary of the contract

        Returns:
            Self for method chaining
        """
        near.promise_batch_action_deploy_contract(self._promise_id, code)
        return self

    def function_call(
        self, method: str, args: Any = None, amount: int = 0, gas: Optional[int] = None
    ) -> "PromiseBatch":
        """
        Add FunctionCall action to this batch.

        Args:
            method: Name of the method to call
            args: Arguments to pass to the method (dict, will be serialized to JSON)
            amount: Amount of NEAR tokens to attach (in yoctoNEAR)
            gas: Gas to attach (if None, uses the batch's gas setting)

        Returns:
            Self for method chaining
        """
        if gas is None:
            gas = self._gas

        if args is None:
            args_str = ""
        elif isinstance(args, str):
            args_str = args
        else:
            args_str = json.dumps(args)

        near.promise_batch_action_function_call(
            self._promise_id, method, args_str, amount, gas
        )
        return self

    def transfer(self, amount: int) -> "PromiseBatch":
        """
        Add Transfer action to this batch.

        Args:
            amount: Amount of NEAR tokens to transfer (in yoctoNEAR)

        Returns:
            Self for method chaining
        """
        near.promise_batch_action_transfer(self._promise_id, amount)
        return self

    def stake(self, amount: int, public_key: bytes) -> "PromiseBatch":
        """
        Add Stake action to this batch.

        Args:
            amount: Amount of NEAR tokens to stake (in yoctoNEAR)
            public_key: Validator key to stake with

        Returns:
            Self for method chaining
        """
        near.promise_batch_action_stake(self._promise_id, amount, public_key)
        return self

    def add_full_access_key(self, public_key: bytes, nonce: int = 0) -> "PromiseBatch":
        """
        Add a full access key to the account.

        Args:
            public_key: The public key to add
            nonce: Nonce for the access key

        Returns:
            Self for method chaining
        """
        near.promise_batch_action_add_key_with_full_access(
            self._promise_id, public_key, nonce
        )
        return self

    def add_access_key(
        self,
        public_key: bytes,
        allowance: Optional[int],
        receiver_id: str,
        method_names: List[str],
        nonce: int = 0,
    ) -> "PromiseBatch":
        """
        Add an access key with function call permission.

        Args:
            public_key: The public key to add
            allowance: Allowance for the key (None means unlimited)
            receiver_id: Which account the key is allowed to call
            method_names: Which methods the key is allowed to call
            nonce: Nonce for the access key

        Returns:
            Self for method chaining
        """
        # Convert None allowance to 0 for unlimited
        allowance_value = 0 if allowance is None else allowance

        # Join method names with commas
        methods_str = ",".join(method_names)

        near.promise_batch_action_add_key_with_function_call(
            self._promise_id,
            public_key,
            nonce,
            allowance_value,
            receiver_id,
            methods_str,
        )
        return self

    def delete_key(self, public_key: bytes) -> "PromiseBatch":
        """
        Delete an access key.

        Args:
            public_key: The public key to delete

        Returns:
            Self for method chaining
        """
        near.promise_batch_action_delete_key(self._promise_id, public_key)
        return self

    def delete_account(self, beneficiary_id: str) -> "PromiseBatch":
        """
        Delete the account and send remaining funds to beneficiary.

        Args:
            beneficiary_id: Account to receive remaining funds

        Returns:
            Self for method chaining
        """
        near.promise_batch_action_delete_account(self._promise_id, beneficiary_id)
        return self

    def then(self, account_id: str) -> "PromiseBatch":
        """
        Create a promise batch that will execute after this one completes.

        Args:
            account_id: Account ID to execute the next batch on

        Returns:
            A new PromiseBatch for the next execution
        """
        promise_id = near.promise_batch_then(self._promise_id, account_id)
        return PromiseBatch(promise_id, self._gas)

    def value(self):
        """
        Return this batch's result to the caller.

        This should be the final operation in your batch chain.
        Similar to Promise.value(), this tells the NEAR VM to return
        the result of this promise to the caller.
        """
        near.promise_return(self._promise_id)
        return None  # The actual return happens asynchronously
