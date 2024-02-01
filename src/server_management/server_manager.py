import paramiko

class ServerManager:
    def __init__(self, hostname, username, password=None, private_key_path=None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.private_key_path = private_key_path
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        try:
            if self.private_key_path:
                # Use private key authentication
                private_key = paramiko.RSAKey(filename=self.private_key_path)
                self.client.connect(self.hostname, username=self.username, pkey=private_key)
            elif self.password:
                # Use password authentication
                self.client.connect(self.hostname, username=self.username, password=self.password)
            else:
                print("No authentication method provided.")
                return

            print("Connected to the server.")
        except paramiko.AuthenticationException:
            print("Authentication failed, please verify your credentials.")
        except Exception as e:
            print(f"Error: {e}")

    def execute_script(self, script_path):
        try:
            # Open the script file and read the commands
            with open(script_path, 'r') as script_file:
                commands = script_file.read()

            # Execute the commands on the remote server
            stdin, stdout, stderr = self.client.exec_command(commands)
            print(stdout.read().decode())
            print(stderr.read().decode())
        except Exception as e:
            print(f"Error executing script: {e}")

    def disconnect(self):
        self.client.close()
        print("Disconnected from the server.")