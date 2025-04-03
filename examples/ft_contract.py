from typing import Optional, Tuple

import near
from near_sdk_py import Contract, StorageError, call, init, view
from near_sdk_py.collections import LookupMap
from near_sdk_py.promises import CrossContract, Promise, PromiseResult, callback

# Constants
FT_METADATA_SPEC = "ft-1.0.0"
DATA_IMAGE_SVG_NEAR_ICON = "data:image/svg+xml,%3Csvg xmlns='http:#www.w3.org/2000/svg' viewBox='0 0 288 288'%3E%3Cg id='l' data-name='l'%3E%3Cpath d='M187.58,79.81l-30.1,44.69a3.2,3.2,0,0,0,4.75,4.2L191.86,103a1.2,1.2,0,0,1,2,.91v80.46a1.2,1.2,0,0,1-2.12.77L102.18,77.93A15.35,15.35,0,0,0,90.47,72.5H87.34A15.34,15.34,0,0,0,72,87.84V201.16A15.34,15.34,0,0,0,87.34,216.5h0a15.35,15.35,0,0,0,13.08-7.31l30.1-44.69a3.2,3.2,0,0,0-4.75-4.2L96.14,186a1.2,1.2,0,0,1-2-.91V104.61a1.2,1.2,0,0,1,2.12-.77l89.55,107.23a15.35,15.35,0,0,0,11.71,5.43h3.13A15.34,15.34,0,0,0,216,201.16V87.84A15.34,15.34,0,0,0,200.66,72.5h0A15.35,15.35,0,0,0,187.58,79.81Z'/%3E%3C/g%3E%3C/svg%3E"

# Gas constants
TGAS = 10**12  # 1 TGas
GAS_FOR_RESOLVE_TRANSFER = 5 * TGAS
GAS_FOR_FT_TRANSFER_CALL = 30 * TGAS


class FungibleToken(Contract):
    """
    Implementation of a fungible token standard.
    Follows the NEP-141 standard.
    """

    def __init__(self):
        super().__init__()
        # Initialize collections
        self.accounts = LookupMap("accounts")
        self.account_storage_usage = 0

    @init
    def new(self, owner_id: str, total_supply: str, metadata: dict) -> None:
        """
        Initializes the contract with the given total supply owned by the given `owner_id` with
        the given fungible token metadata.
        """
        if "total_supply" in self.storage:
            raise StorageError("Already initialized")

        # Set initial state
        self.storage["total_supply"] = 0
        self.account_storage_usage = self._measure_account_storage_usage()
        self.storage["account_storage_usage"] = self.account_storage_usage

        # Register the owner account and deposit the total supply
        self._internal_register_account(owner_id)
        self._internal_deposit(owner_id, int(total_supply))

        # Store the metadata
        metadata = self._validate_metadata(metadata)
        self.storage["metadata"] = metadata

        # Emit mint event
        self.log_info("Emitting mint event")
        self.log_event(
            "ft_mint",
            {
                "owner_id": owner_id,
                "amount": total_supply,
                "memo": "new tokens are minted",
            },
        )

    @init
    def new_default_meta(self, owner_id: str, total_supply: str) -> None:
        """
        Initializes the contract with default metadata and the given total supply and owner_id.
        """
        default_metadata = {
            "spec": FT_METADATA_SPEC,
            "name": "Example NEAR fungible token",
            "symbol": "EXAMPLE",
            "icon": DATA_IMAGE_SVG_NEAR_ICON,
            "reference": None,
            "reference_hash": None,
            "decimals": 24,
        }
        self.new(owner_id, total_supply, default_metadata)

    @call
    def ft_transfer(
        self, receiver_id: str, amount: str | int, memo: Optional[str] = None
    ) -> None:
        """
        Transfer tokens from the caller to the receiver account.
        """
        self.assert_one_yocto()
        amount = int(amount)
        sender_id = self.predecessor_account_id
        self._internal_transfer(sender_id, receiver_id, amount, memo)

    @call
    def ft_transfer_call(
        self,
        receiver_id: str,
        amount: str | int,
        memo: Optional[str] = None,
        msg: str = "",
    ) -> str:
        """
        Transfer tokens and call a method on the receiver contract.
        """
        self.assert_one_yocto()
        if self.prepaid_gas < GAS_FOR_FT_TRANSFER_CALL:
            raise Exception("Not enough gas attached")

        amount = int(amount)
        sender_id = self.predecessor_account_id
        self.log_info(
            f"ft_transfer_call({receiver_id}, {amount}, {memo}, {msg}): sender_id {sender_id}"
        )

        # Transfer the tokens
        self._internal_transfer(sender_id, receiver_id, amount, memo)

        # Calculate remaining gas for the receiver call
        receiver_gas = self.prepaid_gas - GAS_FOR_FT_TRANSFER_CALL

        ft_on_transfer_args = {"sender_id": sender_id, "amount": amount, "msg": msg}

        promise = (
            CrossContract(receiver_id)
            .gas(receiver_gas)
            .deposit(amount)
            .call("ft_on_transfer", **ft_on_transfer_args)
            .then_call(
                self.current_account_id,
                "ft_resolve_transfer",
                sender_id=sender_id,
                receiver_id=receiver_id,
                amount=amount,
            )
            .gas(GAS_FOR_RESOLVE_TRANSFER)
            .value()
        )

        return str(promise)

    @view
    def ft_total_supply(self) -> str:
        """
        Return the total token supply.
        """
        return self.storage.get("total_supply", "0")

    @view
    def ft_balance_of(self, account_id: str) -> str:
        """
        Return the account balance.
        """
        return str(self._get_account_balance(account_id) or 0)

    @callback
    def ft_resolve_transfer(
        self, result: PromiseResult, sender_id: str, receiver_id: str, amount: str | int
    ) -> Tuple[int, int]:
        """
        Resolve the transfer call by returning the unused amount.
        """
        amount = int(amount)
        self.log_info(f"ft_resolve_transfer({sender_id}, {receiver_id}, {amount})")

        unused_amount = amount  # Default to returning all if the call failed
        if result.success:
            # Get the unused amount from the result
            try:
                unused_amount = int(result.data) if result.data else 0
                unused_amount = min(amount, unused_amount)
            except (ValueError, TypeError):
                unused_amount = 0  # If we can't parse it, assume all tokens were used

        if unused_amount > 0:
            receiver_balance = self._get_account_balance(receiver_id) or 0

            if receiver_balance > 0:
                refund_amount = min(receiver_balance, unused_amount)
                self.accounts.set(receiver_id, receiver_balance - refund_amount)

                sender_balance = self._get_account_balance(sender_id)
                if sender_balance is not None:
                    # Return tokens to sender
                    self.accounts.set(sender_id, sender_balance + refund_amount)

                    # Emit refund event
                    self.log_event(
                        "ft_transfer",
                        {
                            "old_owner_id": receiver_id,
                            "new_owner_id": sender_id,
                            "amount": str(refund_amount),
                            "memo": "refund",
                        },
                    )

                    used_amount = amount - refund_amount
                    return (used_amount, 0)
                else:
                    # Sender account was deleted, burn tokens
                    total_supply = (
                        int(self.storage.get("total_supply", "0")) - refund_amount
                    )
                    self.storage["total_supply"] = str(total_supply)

                    self.log_info("The account of the sender was deleted")
                    self.log_event(
                        "ft_burn",
                        {
                            "owner_id": receiver_id,
                            "amount": str(refund_amount),
                            "memo": "refund",
                        },
                    )

                    return (amount, refund_amount)

        return (amount, 0)

    @call
    def storage_deposit(
        self, account_id: Optional[str] = None, registration_only: bool = False
    ) -> Optional[dict]:
        """
        Register an account and pay for its storage.
        """
        deposit = self.attached_deposit
        account_id = account_id if account_id else self.predecessor_account_id

        # If account is already registered, refund the deposit
        if self._get_account_balance(account_id) is not None:
            self.log_info("The account is already registered, refunding the deposit")
            if deposit > 0:
                Promise.create_batch(self.predecessor_account_id).transfer(
                    deposit
                ).value()
        else:
            # Calculate minimum required balance
            min_balance = self._internal_storage_balance_bounds()["min"]

            if deposit < min_balance:
                raise Exception(
                    "The attached deposit is less than the minimum storage balance"
                )

            # Register the account
            self._internal_register_account(account_id)

            # Refund excess deposit
            refund = deposit - min_balance
            if refund > 0:
                Promise.create_batch(self.predecessor_account_id).transfer(
                    refund
                ).value()

        return self._internal_storage_balance_of(account_id)

    @call
    def storage_withdraw(self, amount: Optional[str] = None) -> dict:
        """
        Withdraw excess storage deposit.
        """
        self.assert_one_yocto()
        predecessor_account_id = self.predecessor_account_id

        storage_balance = self._internal_storage_balance_of(predecessor_account_id)
        if storage_balance is None:
            raise Exception(f"The account {predecessor_account_id} is not registered")

        if amount and int(amount) > 0:
            raise Exception("The amount is greater than the available storage balance")

        return storage_balance

    @call
    def storage_unregister(self, force: bool = False) -> bool:
        """
        Unregister an account and withdraw all deposited funds.
        """
        self.assert_one_yocto()
        account_id = self.predecessor_account_id

        balance = self._get_account_balance(account_id)
        if balance is not None:
            if balance == 0 or force:
                # Remove the account
                self.accounts.remove(account_id)

                # Update total supply
                total_supply = int(self.storage.get("total_supply", "0")) - balance
                self.storage["total_supply"] = str(total_supply)

                # Return storage deposit
                storage_bounds = self._internal_storage_balance_bounds()
                deposit_amount = storage_bounds["min"] + 1

                Promise.create_batch(account_id).transfer(deposit_amount).value()

                self.log_info(f"Closed @{account_id} with: {balance}")
                return True
            else:
                raise Exception(
                    "Can't unregister the account with the positive balance without force"
                )
        else:
            self.log_info(f"The account {account_id} is not registered")

        return False

    @view
    def storage_balance_bounds(self) -> dict:
        """
        Return the minimum and maximum storage balance.
        """
        return self._internal_storage_balance_bounds()

    @view
    def storage_balance_of(self, account_id: str) -> Optional[dict]:
        """
        Return the storage balance of the given account.
        """
        return self._internal_storage_balance_of(account_id)

    @view
    def ft_metadata(self) -> dict:
        """
        Return the token metadata.
        """
        return self.storage.get("metadata", {})

    # === Internal methods ===

    def _measure_account_storage_usage(self) -> int:
        """Measure the storage usage of a single account"""
        initial_storage_usage = near.storage_usage()

        # Create a temporary account to measure its storage
        tmp_account_id = "a" * 64
        self._internal_register_account(tmp_account_id)

        # Calculate the difference
        account_storage_usage = near.storage_usage() - initial_storage_usage

        # Clean up
        self.accounts.remove(tmp_account_id)

        self.log_info(f"measure_account_storage_usage(): {account_storage_usage}")
        return account_storage_usage

    def _internal_register_account(self, account_id: str) -> None:
        """Register a new account with zero balance"""
        self.log_info(f"internal_register_account({account_id})")

        if account_id in self.accounts:
            self.log_info(f"Account {account_id} is already registered")
            raise Exception("The account is already registered")

        self.log_info(f"Registering account: {account_id}")

        self.accounts[account_id] = 0

    def _get_account_balance(self, account_id: str) -> Optional[int]:
        """Get account balance or None if account doesn't exist"""
        return self.accounts.get(account_id)

    def _internal_deposit(self, account_id: str, amount: int) -> None:
        """Deposit tokens to an account and update total supply"""
        self.log_info(f"internal_deposit({account_id}, {amount})")

        # Get current balance
        balance = self._get_account_balance(account_id)
        if balance is None:
            raise Exception(f"The account {account_id} is not registered")

        # Update account balance
        new_balance = balance + amount
        self.accounts.set(account_id, new_balance)

        # Update total supply
        total_supply = int(self.storage.get("total_supply", 0)) + amount
        self.storage["total_supply"] = str(total_supply)

    def _internal_withdraw(self, account_id: str, amount: int) -> None:
        """Withdraw tokens from an account and update total supply"""
        self.log_info(f"internal_withdraw({account_id}, {amount})")

        # Get current balance
        balance = self._get_account_balance(account_id)
        if balance is None:
            raise Exception(f"The account {account_id} is not registered")

        if balance < amount:
            raise Exception(
                f"Not enough balance to withdraw {amount} from {account_id}"
            )

        # Update account balance
        new_balance = balance - amount
        self.accounts.set(account_id, new_balance)

        # Update total supply
        total_supply = int(self.storage.get("total_supply", "0")) - amount
        self.storage["total_supply"] = str(total_supply)

    def _internal_transfer(
        self, sender_id: str, receiver_id: str, amount: int, memo: Optional[str] = None
    ) -> None:
        """Transfer tokens from one account to another"""
        self.log_info(
            f"internal_transfer({sender_id}, {receiver_id}, {amount}, {memo})"
        )

        assert sender_id != receiver_id, "Sender and receiver should be different"
        assert amount > 0, "The amount should be a positive number"

        # Withdraw from sender
        self._internal_withdraw(sender_id, amount)

        # Deposit to receiver
        self._internal_deposit(receiver_id, amount)

        # Emit transfer event
        self.log_event(
            "ft_transfer",
            {
                "old_owner_id": sender_id,
                "new_owner_id": receiver_id,
                "amount": str(amount),
                "memo": memo,
            },
        )

    def _validate_metadata(self, metadata: dict) -> dict:
        """Validate the token metadata"""
        assert metadata["spec"] == FT_METADATA_SPEC
        assert isinstance(metadata["name"], str) and len(metadata["name"]) > 0
        assert isinstance(metadata["symbol"], str) and len(metadata["symbol"]) > 0
        assert metadata["decimals"] == 24
        return metadata

    def _storage_byte_cost(self) -> int:
        """Get the storage cost per byte"""
        return 10000000000000000000  # 10^19

    def _internal_storage_balance_bounds(self) -> dict:
        """Get the minimum and maximum storage balance"""
        account_storage_usage = int(self.storage.get("account_storage_usage", 0))
        required_storage_balance = self._storage_byte_cost() * account_storage_usage
        return {
            "min": required_storage_balance,
            "max": required_storage_balance,
        }

    def _internal_storage_balance_of(self, account_id: str) -> Optional[dict]:
        """Get the storage balance of an account"""
        balance = self._get_account_balance(account_id)
        if balance is None:
            return None

        bounds = self._internal_storage_balance_bounds()
        return {
            "total": bounds["min"],
            "available": "0",
        }
