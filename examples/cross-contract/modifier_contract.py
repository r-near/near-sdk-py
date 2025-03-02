from near_sdk_py import call, view, CrossContract, callback, ONE_TGAS

class GreetingModifier:
    """Contract that interacts with the greeting storage"""
    
    @call
    def make_greeting_excited(self, storage_account: str) -> int:
        """
        Fetches greeting from storage contract and makes it excited!
        Returns a promise that will be handled by the callback
        """
        # Call the storage contract to get the greeting
        promise = CrossContract.call(
            storage_account,
            "get_greeting",
            gas=5 * ONE_TGAS,
            callback_method=self.on_greeting_received
        )
        CrossContract.return_value(promise)
    
    @callback(gas=5 * ONE_TGAS)
    def on_greeting_received(self):
        """Handle the greeting we received"""
        if not CrossContract.result_success():
            return "Failed to get greeting"
        
        # Get the greeting and make it excited
        greeting = CrossContract.result_value()
        excited_greeting = f"{greeting}!!!"
        
        # Return the modified greeting
        return excited_greeting
    
    @call
    def update_remote_greeting(self, storage_account: str, message: str) -> int:
        """
        Updates the greeting in the storage contract
        Returns a promise that will be handled by the callback
        """
        promise = CrossContract.call(
            storage_account,
            "set_greeting",
            args={"message": message},
            gas=5 * ONE_TGAS,
            callback_method=self.on_greeting_updated
        )
        CrossContract.return_value(promise)
    
    @callback(gas=5 * ONE_TGAS)
    def on_greeting_updated(self):
        """Handle the result of updating the greeting"""
        if CrossContract.result_success():
            return "Successfully updated greeting"
        return f"Failed to update greeting: {CrossContract.result_error()}"

# Export contract methods
contract = GreetingModifier()
make_greeting_excited = contract.make_greeting_excited
update_remote_greeting = contract.update_remote_greeting