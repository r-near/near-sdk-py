import near
import json
from near_sdk_py.constants import ONE_TGAS
from .promise import Promise
from .batch import PromiseBatch


class CrossContract:
    """Fluent interface for calling contract methods."""

    def __init__(self, account_id: str, gas: int = 10 * ONE_TGAS, deposit: int = 0):
        """
        Initialize a contract proxy.

        Args:
            account_id: The contract's account ID
            gas: Default gas to use for calls (default: 5 TGas)
            deposit: Default deposit amount (default: 0)
        """
        self.account_id = account_id
        self._gas = gas
        self._deposit = deposit

    def gas(self, amount: int) -> "CrossContract":
        """
        Set the default gas amount for calls to this contract.

        Args:
            amount: Gas amount in gas units

        Returns:
            A new CrossContract with updated gas setting
        """
        return CrossContract(self.account_id, gas=amount, deposit=self._deposit)

    def deposit(self, amount: int) -> "CrossContract":
        """
        Set the default deposit amount for calls to this contract.

        Args:
            amount: Deposit amount in yoctoNEAR

        Returns:
            A new CrossContract with updated deposit setting
        """
        return CrossContract(self.account_id, gas=self._gas, deposit=amount)

    def call(self, method: str, **kwargs) -> Promise:
        """
        Call a method on this contract with keyword arguments.

        Args:
            method: The method name to call
            **kwargs: Keyword arguments to pass to the method

        Returns:
            A Promise object representing the call
        """
        if kwargs is None:
            args_str = ""
        elif isinstance(kwargs, str):
            args_str = kwargs
        else:
            args_str = json.dumps(kwargs)

        promise_id = near.promise_create(
            self.account_id, method, args_str, self._deposit, self._gas
        )

        return Promise(promise_id, gas=self._gas)

    def batch(self) -> PromiseBatch:
        """
        Create a batch of actions to execute on this contract.

        Returns:
            A new PromiseBatch for adding actions
        """
        promise_id = near.promise_batch_create(self.account_id)
        return PromiseBatch(promise_id, self._gas)
