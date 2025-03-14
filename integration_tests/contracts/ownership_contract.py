from near_sdk_py import Contract, view, call, init


class OwnershipContract(Contract):
    """
    A contract demonstrating ownership and access control features
    of the Contract base class.
    """

    @init
    def initialize(self, owner=None):
        """
        Initialize the contract with an owner.

        Args:
            owner: Account ID of the owner. If not provided,
                  defaults to the deployer of the contract.
        """
        # Set the owner to the provided value or the deployer
        self.storage["owner"] = owner or self.predecessor_account_id

        # Initialize an empty config
        self.storage["config"] = {}

        return {"success": True}

    @view
    def get_owner(self):
        """
        Get the current owner of the contract.

        Returns:
            Account ID of the contract owner
        """
        return self.storage["owner"]

    @view
    def get_config(self, key):
        """
        Get a configuration value.

        Args:
            key: The configuration key to retrieve

        Returns:
            The configuration value or None if not found
        """
        config = self.storage.get("config", {})
        return config.get(key)

    @call
    def update_config(self, key, value):
        """
        Update a configuration value. Only the owner can call this.

        Args:
            key: The configuration key to update
            value: The new value

        Returns:
            Success status
        """
        # Check if caller is the owner
        self.assert_owner()

        # Update the config
        config = self.storage.get("config", {})
        config[key] = value
        self.storage["config"] = config

        # Log the update
        self.log_event("config_updated", {"key": key, "value": value})

        return {"success": True}

    @call
    def transfer_ownership(self, new_owner):
        """
        Transfer ownership of the contract to a new account.
        Only the current owner can call this.

        Args:
            new_owner: Account ID of the new owner

        Returns:
            Success status
        """
        # Check if caller is the owner
        self.assert_owner()

        # Update the owner
        self.storage["owner"] = new_owner

        # Log the ownership transfer
        self.log_event(
            "ownership_transferred",
            {"previous_owner": self.predecessor_account_id, "new_owner": new_owner},
        )

        return {"success": True}
