import paramiko
from getpass import getpass

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

    def execute_script(self, script_path, *args):
        try:
            # Open the script file and read the commands
            with open(script_path, 'r') as script_file:
                commands = script_file.read().splitlines()

            # Execute each command on the remote server
            for command in commands:
                # Replace arguments in the command
                for i, arg in enumerate(args):
                    command = command.replace(f'${i + 1}', str(arg))

                # Check if the command starts with "sudo"
                is_sudo_command = command.strip().startswith("sudo")

                if is_sudo_command:
                    attempts = 3
                    while attempts > 0:
                        password = getpass("Enter your password for sudo command: ")
                        # Replace arguments in the command
                        full_command = f"echo {password} | sudo -S {command[5:]}"
                        stdin, stdout, stderr = self.client.exec_command(full_command)
                        error_output = stderr.read().decode()

                        if "incorrect password attempt" not in error_output.lower():
                            # Successful sudo command execution or other errors
                            print(stdout.read().decode())
                            print(error_output)
                            break
                        else:
                            # Incorrect password, prompt for a new password
                            print(f"Incorrect password. Attempts left: {attempts - 1}")
                            attempts -= 1
                            if attempts == 0:
                                print("Cannot use sudo command because of the wrong password")
                else:
                    # Execute non-sudo commands directly
                    stdin, stdout, stderr = self.client.exec_command(command)
                    print(stdout.read().decode())
                    print(stderr.read().decode())
        except Exception as e:
            print(f"Error executing script: {e}")

    def disconnect(self):
        self.client.close()
        print("Disconnected from the server.")