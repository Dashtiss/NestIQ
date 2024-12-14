from ollama import ChatResponse, Client
from ollama._types.Message import ToolCall
from typing import Any, Dict, Callable, List, Sequence
from functools import wraps
import pyttsx3

class ToolRegistry:
    _tools: List[Dict[str, Any]] = []

    @classmethod
    def register(cls, name: str, description: str, parameters: Dict[str, Any]):
        def decorator(func: Callable):
            cls._tools.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters
                },
                "implementation": func
            })
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    @classmethod
    def get_all_tools(cls) -> List[Dict[str, Any]]:
        return [
            {
                "type": tool["type"],
                "function": tool["function"]
            }
            for tool in cls._tools
        ]

    @classmethod
    def get_tool(cls, name: str) -> Callable | None:
        for tool in cls._tools:
            if tool["function"]["name"] == name:
                return tool["implementation"]
        return None

    @classmethod
    def call_tool(cls, name: str, parameters: Dict[str, Any]) -> Any:
        for tool in cls._tools:
            if tool["function"]["name"] == name:
                return tool["implementation"](**parameters)
        raise ValueError(f"Tool '{name}' is not registered.")

class OllamaController:
    def __init__(self, model: str, host: str = "127.0.0.1", port: int = 11434):
        """Initialize the Ollama AI Controller.

        Args:
            model (str): The local model name to use with the Ollama library.
            host (str): The IP address of the Ollama server.
            port (int): The port number of the Ollama server.
        """
        self.model = model # Model name
        self.host = host # IP address
        self.port = port # Port
        self.client = Client(host=f"http://{self.host}:{self.port}") # Ollama client
        self.messages = []

    def generate_response(self, user_message: str) -> tuple[str, List[ToolCall]]:
        """Generate a response from the local Ollama AI model with tools.

        Args:
            user_message (str): The user's input message.

        Returns:
            str: The generated AI response.
        """
        try:
            tools_list = ToolRegistry.get_all_tools()
            self.messages.append({"role": "user", "content": user_message})
            response: ChatResponse = self.client.chat(
                model=self.model,
                messages=self.messages,
                tools=tools_list
            )
            #print(response.message)
            self.messages.append({"role": "assistant", "content": response.message.content})

            return str(response.message.content) if response.message.content is not None else "", list(response.message.tool_calls) if response.message.tool_calls is not None else []
        except Exception as e:
            print(e)
            raise RuntimeError(f"Error generating response: {e}")

    def reply(self, message: str) -> None:
        """Speak the provided message to the user."""
        engine = pyttsx3.init()
        engine.say(message)
        engine.runAndWait()

    def handle_tool(self, tool_name: str, **kwargs) -> Any:
        """Handle execution of a tool by name with provided parameters."""
        tool = ToolRegistry.get_tool(tool_name)
        if tool:
            try:
                return tool(**kwargs)
            except Exception as e:
                print(f"Error executing tool '{tool_name}': {e}")
        else:
            print(f"Tool '{tool_name}' not found.")
        return None

# Registering tools
@ToolRegistry.register(
    name="turn_on_light",
    description="Turn on a light in a specified room.",
    parameters={
        "type": "object",
        "properties": {
            "device_id": {
                "type": "string",
                "description": "The ID of the light device."
            }
        },
        "required": ["device_id"]
    }
)
def turn_on_light(device_id: str) -> str:
    return f"Turning on the light with ID {device_id}."

@ToolRegistry.register(
    name="turn_off_light",
    description="Turn off a light in a specified room.",
    parameters={
        "type": "object",
        "properties": {
            "device_id": {
                "type": "string",
                "description": "The ID of the light device."
            }
        },
        "required": ["device_id"]
    }
)
def turn_off_light(device_id: str) -> str:
    return f"Turning off the light with ID {device_id}."

@ToolRegistry.register(
    name="get_device_ids",
    description="Retrieve the list of all device IDs in the system.",
    parameters={
        "type": "object",
        "properties": {},
        "required": []
    }
)
def get_device_ids() -> Dict[str, Any]:
    return {"device_ids": ["light1", "light2", "thermostat1"]}

@ToolRegistry.register(
    name="speak",
    description="Speak a message to the user.",
    parameters={
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "The message to speak."
            }
        },
        "required": ["message"]
    }
)
def speak(message: str) -> None:
    """Convert the message to speech and speak it to the user."""
    engine = pyttsx3.init()
    engine.say(message)
    engine.runAndWait()

# Example usage
if __name__ == "__main__":
    ollama = OllamaController(model="llama3.1", host="192.168.1.100", port=11434)

    user_message = "Hello, AI. Please turn on the light in the kitchen."
    response = ollama.generate_response(user_message)

    print(response)
