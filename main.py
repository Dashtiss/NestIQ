from AIManager import OllamaController, ToolRegistry
from insteonManager import  InsteonController

if __name__ == "__main__":
    ollama = OllamaController(model="llama3.2", host="10.0.50.53", port=11434)
    insteon = InsteonController(
        hub_address="192.168.x.x",
        hub_port=25105,
        hub_user="username",
        hub_pass="password"
    )

    user_message = "Hello, AI." 
    
    ollama_response = ollama.generate_response(user_message)
    
    print("Ollama Response:", ollama_response)

    if "light" in ollama_response:
        device_id = ollama_response.split(" ")[-1]
        #insteon_response = await insteon.control_device(device_id, "on")