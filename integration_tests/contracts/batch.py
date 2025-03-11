"""
A minimal contract to test the Promise batch API with account creation.
"""

from near_sdk_py import call, ONE_TGAS, Log
import near

from near_sdk_py.promises import Promise


class SimpleAccountCreator:
    """Simple contract for testing the Promise batch API."""

    @call
    def create_subaccount(self, name: str, public_key: str):
        """
        Create a subaccount of the current account.

        Args:
            name: Name of the subaccount (will be {name}.{current_account})
            public_key: Hex-encoded public key for the new account
        """
        # Form the new account ID
        Log.info(f"name: {name}, public_key: {public_key}")
        current_account = near.current_account_id()
        new_account_id = f"{name}.{current_account}"

        # Decode the public key
        Log.info("Decoding")
        key_bytes = bytes.fromhex(public_key)
        Log.info(f"Public key: {key_bytes!r}")

        initial_balance = 4242424242

        # Create a batch of actions
        batch = Promise.create_batch(new_account_id)

        # Add actions to the batch
        batch.create_account().transfer(initial_balance).add_full_access_key(key_bytes)

        # Return a success message
        Log.info("Returning success")
        return {
            "success": True,
            "account_id": new_account_id,
            "initial_balance": initial_balance,
        }

    @call
    def transfer_and_call(self, account_id: str, amount: int):
        """
        Transfer funds to an account and call a simple method on it.

        Args:
            account_id: Account to transfer to and call
            amount: Amount to transfer in yoctoNEAR
        """
        # Create a batch
        batch = Promise.create_batch(account_id)

        # Transfer and then call a method
        batch.transfer(amount).function_call(
            "log_receipt", {"sender": near.current_account_id()}, 0, 5 * ONE_TGAS
        )

        # Return the promise
        return {"success": True, "message": "Transfer and call initiated"}

    @call
    def log_receipt(self, sender: str):
        """Simple method to be called by transfer_and_call."""
        Log.info(f"Received funds from {sender} at {near.block_timestamp()}")

        # Just return a receipt message
        return {
            "message": "Funds received",
            "from": sender,
            "received_at": near.block_timestamp(),
            "receiver": near.current_account_id(),
        }


account = SimpleAccountCreator()
create_subaccount = account.create_subaccount
transfer_and_call = account.transfer_and_call
log_receipt = account.log_receipt
