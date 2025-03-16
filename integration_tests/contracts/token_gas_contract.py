"""
Token and Gas Management contract for testing the Promise API.

This contract demonstrates how to:
- Attach tokens to function calls
- Manage gas allocation for promises
- Transfer tokens between accounts
"""

from typing import Optional

from near_sdk_py import ONE_TGAS, Context, Log, Storage, call, view
from near_sdk_py.promises import CrossContract, PromiseResult, callback


class TokenGasContract:
    """Contract demonstrating token and gas management with promises"""

    @view
    def get_value(self, key: str):
        """Get a value from storage or return default."""
        return Storage.get_string(key) or "default_value"

    @call
    def set_value(self, key: str, value: str):
        """Set a value in storage."""
        Storage.set(key, value)
        return {"success": True, "key": key, "value": value}

    @call
    def call_with_tokens(self, contract_id: str, method: str, args: dict, amount: int):
        """Call a contract method with attached tokens.

        This demonstrates how to attach NEAR tokens to cross-contract calls.

        Args:
            contract_id: Target contract ID
            method: Method to call on the target contract
            args: Arguments to pass to the method
            amount: Amount of yoctoNEAR to attach
        """
        Log.info(f"Attaching {amount} yoctoNEAR to call")

        # Create contract with the specified deposit
        contract = CrossContract(contract_id).deposit(amount)

        # Make the call with attached tokens
        promise = contract.call(method, **args)

        # Add a callback to process the result
        final_promise = promise.then("process_token_call")

        return final_promise.value()

    @callback
    def process_token_call(self, result: PromiseResult):
        """Process the result of a call with attached tokens.

        Args:
            result: Result from the contract call
        """
        if not result.success:
            return {"success": False, "error": "Token call failed"}

        return {"success": True, "result": result.data, "tokens_attached": True}

    @call
    def call_with_fixed_gas(
        self, contract_id: str, method: str, args: dict, gas_amount: int
    ):
        """Call a contract method with a fixed gas amount.

        This demonstrates setting a specific gas limit for a promise.

        Args:
            contract_id: Target contract ID
            method: Method to call on the target contract
            args: Arguments to pass to the method
            gas_amount: Gas to attach (in gas units)
        """
        Log.info(f"Attaching {gas_amount} gas to call")

        # Create contract with specified gas
        contract = CrossContract(contract_id, gas=gas_amount)

        # Make the call with fixed gas
        promise = contract.call(method, **args)

        # Add a callback with some gas reserved for it
        callback_gas = ONE_TGAS * 5
        final_promise = promise.then("process_fixed_gas_call").gas(callback_gas)

        return final_promise.value()

    @callback
    def process_fixed_gas_call(self, result: PromiseResult):
        """Process the result of a call with fixed gas.

        Args:
            result: Result from the contract call
        """
        if not result.success:
            return {"success": False, "error": "Fixed gas call failed"}

        return {"success": True, "result": result.data, "fixed_gas_used": True}

    @call
    def call_with_proportional_gas(
        self, contract_id: str, method: str, args: dict, gas_fraction: int
    ):
        """Call a contract method with proportional gas allocation.

        This demonstrates dynamic gas management based on available gas.

        Args:
            contract_id: Target contract ID
            method: Method to call on the target contract
            args: Arguments to pass to the method
            gas_fraction: Denominator for gas fraction (e.g., 2 means 1/2 of available gas)
        """
        # Calculate available gas
        available_gas = Context.prepaid_gas() - Context.used_gas() - ONE_TGAS * 5

        # Calculate proportional gas amount
        if gas_fraction <= 0:
            gas_fraction = 1  # Default to all available gas

        gas_to_use = available_gas // gas_fraction
        Log.info(f"Using {gas_to_use} gas ({1}/{gas_fraction} of available)")

        # Create contract with calculated gas
        contract = CrossContract(contract_id, gas=gas_to_use)

        # Make the call
        promise = contract.call(method, **args)

        # Add a callback with remaining gas
        remaining_gas = available_gas - gas_to_use
        final_promise = promise.then("process_proportional_call").gas(remaining_gas)

        return final_promise.value()

    @callback
    def process_proportional_call(self, result: PromiseResult):
        """Process the result of a call with proportional gas.

        Args:
            result: Result from the contract call
        """
        if not result.success:
            return {"success": False, "error": "Proportional gas call failed"}

        return {"success": True, "result": result.data, "proportional_gas_used": True}

    @call
    def transfer_and_call(
        self,
        recipient_id: str,
        amount: int,
        method: Optional[str] = None,
        args: Optional[dict] = None,
    ):
        """Transfer NEAR tokens and optionally call a method on the recipient.

        This demonstrates a common pattern of transferring tokens and
        then calling a method on the recipient.

        Args:
            recipient_id: Account to receive tokens
            amount: Amount of yoctoNEAR to transfer
            method: Optional method to call after transfer
            args: Arguments for the method call
        """
        Log.info(f"Transferring {amount} yoctoNEAR to {recipient_id}")

        # Create a batch for operations on the recipient account
        contract = CrossContract(recipient_id)
        batch = contract.batch()

        # Add transfer action
        batch.transfer(amount)

        # Add function call if specified
        if method is not None:
            Log.info(f"Also calling {method} on recipient")
            batch.function_call(method, args or {}, gas=10 * ONE_TGAS)

        # Add callback to handle the result
        promise = batch.then(Context.current_account_id()).function_call(
            "transfer_callback",
            {"recipient_id": recipient_id, "amount": amount},
            gas=10 * ONE_TGAS,
        )

        return promise.value()

    @callback
    def transfer_callback(self, result: PromiseResult, recipient_id: str, amount: int):
        """Handle completion of a token transfer.

        Args:
            result: Result of the transfer operation
            recipient_id: Account that received tokens
            amount: Amount transferred
        """
        if not result.success:
            return {"success": False, "error": f"Transfer failed: {result.status_code}"}

        return {
            "success": True,
            "recipient_id": recipient_id,
            "amount": amount,
            "message": f"Successfully transferred {amount} yoctoNEAR",
        }

    @call
    def receive_funds(self):
        """Method that can be called when receiving funds.

        This demonstrates how attached deposits work.
        """
        deposit = Context.attached_deposit()
        sender = Context.predecessor_account_id()

        return {
            "success": True,
            "message": f"Received {deposit} yoctoNEAR from {sender}",
            "deposit": deposit,
            "sender": sender,
        }
