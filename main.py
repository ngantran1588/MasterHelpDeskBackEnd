from src.server_management.server_manager import ServerManager
import os
from dotenv import load_dotenv

load_dotenv()
if __name__ == "__main__":
    
    # Replace these with your server details
    server_hostname = os.environ.get("SERVER_HOSTNAME")
    server_username = os.environ.get("SERVER_USERNAME")
    private_key_path = os.environ.get("PRIVATE_KEY_PATH")
    script_path = os.environ.get("SCRIPT_PATH")

    # Initialize the ServerManager with private key authentication
    server_manager = ServerManager(server_hostname, server_username, private_key_path=private_key_path)

    # Connect to the server
    server_manager.connect()


    # Disconnect from the server
    server_manager.disconnect()