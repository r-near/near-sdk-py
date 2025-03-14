from near_sdk_py import call, view, Contract


class GreetingContract(Contract):
    @call
    def set_greeting(self, message: str):
        self.log_info(f"Setting greeting to {message}")
        self.storage["greeting"] = message
        return f"Greeting updated to: {message}"

    @view
    def get_greeting(self) -> str:
        self.log_info(f"The current account Id is {self.current_account_id}")
        return self.storage.get("greeting", "Hello, NEAR world!")
