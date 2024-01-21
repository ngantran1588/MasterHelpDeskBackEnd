from src.models.server_manager import ServerManager

if __name__ == "__main__":
    # Replace these with your server details
    server_hostname = "your_server_ip_or_hostname"
    server_username = "your_username"
    private_key_path = "/path/to/your/private/key"  # Replace with the actual path

    # Initialize the ServerManager with private key authentication
    server_manager = ServerManager(server_hostname, server_username, private_key_path=private_key_path)

    # Connect to the server
    server_manager.connect()

    # Execute the custom script on the server
    script_path = "../scripts/custom_script.sh"  # Adjust the path based on your folder structure
    server_manager.execute_script(script_path)

    # Disconnect from the server
    server_manager.disconnect()