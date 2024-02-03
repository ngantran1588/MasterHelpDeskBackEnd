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

    # Execute the custom script on the server
    server_manager.execute_script(script_path)

    # Execute the show_status.sh script
    server_manager.execute_script("src/scripts/firewall/show_status.sh")

    # Execute the allow_port.sh script with port 8080
    server_manager.execute_script("src/scripts/firewall/allow_port.sh", 8080)

    # Execute the deny_port.sh script with port 8080
    server_manager.execute_script("src/scripts/firewall/deny_port.sh", 8080)

    # Execute the allow_ip.sh script with IP address 192.168.1.1
    server_manager.execute_script("src/scripts/firewall/allow_ip.sh", "192.168.1.1")
    server_manager.execute_script("src/scripts/firewall/deny_ip.sh", "192.168.1.1")

    # Disconnect from the server
    server_manager.disconnect()