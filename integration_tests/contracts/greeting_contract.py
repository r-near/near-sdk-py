from near_sdk_py import Contract, call, init, view


class GreetingContract(Contract):
    """
    A simple greeting contract demonstrating the basic features
    of the Contract base class.
    """

    @init
    def initialize(self, default_message="Hello, NEAR world!"):
        """
        Initialize the contract with a default greeting message.

        Args:
            default_message: The initial greeting message
        """
        self.storage["greeting"] = default_message
        return {"success": True}

    @call
    def set_greeting(self, message: str):
        self.storage["greeting"] = message
        return {"success": True}

    @view
    def get_greeting(self):
        """
        Retrieve the current greeting message.

        Returns:
            The current greeting message
        """
        self.log_info(f"Getting greeting from account {self.current_account_id}")
        return self.storage.get("greeting", "Hello, NEAR world!")

    @view
    def get_greeting_with_language(self, language="english"):
        """
        Get the greeting in the specified language.

        Args:
            language: The language for the greeting (english or spanish)

        Returns:
            Greeting in the specified language
        """
        base_greeting = self.storage.get("greeting", "Hello world!")

        if language == "spanish":
            # Just a demo conversion, not actually translating
            if base_greeting == "Hello world!":
                return "¡Hola mundo!"

        return base_greeting
