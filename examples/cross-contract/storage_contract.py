from near_sdk_py import call, view, Storage

class GreetingStorage:
    """A simple contract that stores a greeting"""
    
    @call
    def set_greeting(self, message: str) -> str:
        """Store a greeting message"""
        Storage.set("greeting", message)
        return f"Stored greeting: {message}"
    
    @view
    def get_greeting(self) -> str:
        """Retrieve the greeting message"""
        return Storage.get_string("greeting") or "Hello"

# Export contract methods
contract = GreetingStorage()
set_greeting = contract.set_greeting
get_greeting = contract.get_greeting