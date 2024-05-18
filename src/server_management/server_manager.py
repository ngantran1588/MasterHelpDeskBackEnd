import paramiko
from getpass import getpass
import os
import stat
import zipfile
import tempfile

class ServerManager:
    def __init__(self, hostname, username, password=None, private_key=None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.private_key = private_key
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        try:
            if self.private_key:
                # Use private key authentication
                private_key = paramiko.RSAKey(key=self.private_key)
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

    def execute_script_in_remote_server(self, script_relative_path, *args):
        try:
            # Construct the full path of the script on the server
            script_full_path = f"{script_relative_path} {' '.join(args)}"

            # Execute script on the remote server
            stdin, stdout, stderr = self.client.exec_command(f"bash {script_full_path}")
            stdout.channel.recv_exit_status()

            # Read stdout and stderr
            stdout_data = stdout.read().decode()
            stderr_data = stderr.read()
            
            # Return stdout and stderr data
            return stdout_data, stderr_data
        except Exception as e:
            print(f"Error executing script: {e}")

    def grant_permission(self, script_relative_path, role):
        try:
            # Execute script on the remote server
            stdin, stdout, stderr = self.client.exec_command(f"chmod {role} {script_relative_path}")
            # Print script output
            print(stdout.read().decode())
            print(stderr.read().decode())
            return(stdout.read().decode())
        except Exception as e:
            print(f"Error executing script: {e}")

    def check_script_exists_on_remote(self, remote_file_path):
        try:
            # Check if the remote script file exists
            stdin, stdout, stderr = self.client.exec_command(f'stat {remote_file_path}')
            
            # Read the output stream to get the command result
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            if error:
                return "No such file or directory" not in error
            return "No such file or directory" not in output

        except Exception as e:
            print(f"Error in checking script: {e}")
            return False

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

    def get_file_name(self, file_path):
        return os.path.basename(file_path)

    def remove_carriage_return(self, file_path):
        try:
            with open(file_path, 'r', newline='') as file:
                lines = file.readlines()

            with open(file_path, 'w', newline='') as file:
                for line in lines:
                    file.write(line.rstrip('\r\n') + '\n')

            print("Carriage return characters removed successfully.")

        except Exception as e:
            print(f"Error: {e}")

    def upload_file_to_remote(self, local_file_path, remote_file_path):
        try:
            self.remove_carriage_return(local_file_path)

            self.create_remote_directory_if_not_exists(remote_file_path)
            # Upload the file to the remote server
            sftp = self.client.open_sftp()
            file_name = self.get_file_name(local_file_path)
            remote_file_path = f"{remote_file_path}/{file_name}"
            sftp.put(local_file_path, remote_file_path)
            sftp.close()

            print(f"File '{local_file_path}' uploaded to '{remote_file_path}' successfully.")

        except Exception as e:
            print(f"Error: {e}")
       
    def create_remote_directory_if_not_exists(self, remote_directory):
        try:
            # Check if the directory exists
            sftp = self.client.open_sftp()
            sftp.stat(remote_directory)
            print(f"Directory '{remote_directory}' already exists on the server.")
        except FileNotFoundError:
            # Directory does not exist, create it
            sftp.mkdir(remote_directory)
            print(f"Directory '{remote_directory}' created on the server.")
        finally:
            sftp.close()

    def download_file_from_remote(self, remote_file_path, local_file_path):
        try:
            # Download the file from the remote server
            sftp = self.client.open_sftp()
            file_name = self.get_file_name(remote_file_path)
            local_file_path = f"{local_file_path}/{file_name}"

            sftp.get(remote_file_path, local_file_path)
            sftp.close()

            print(f"File '{remote_file_path}' downloaded to '{local_file_path}' successfully.")

        except Exception as e:
            print(f"Error: {e}")

    def upload_folder(self, local_folder, remote_folder):
        try:
            sftp = self.client.open_sftp()
            for root, dirs, files in os.walk(local_folder):
                # Construct the remote directory path
                remote_dir = f"{remote_folder}{os.path.basename(local_folder)}"
      
                if os.path.basename(remote_dir) not in sftp.listdir(os.path.dirname(remote_dir)):
                    # Create the remote directory if it doesn't exist
                    sftp.mkdir(remote_dir)

                for file in files:
                    if os.path.dirname(os.path.join(root, file)) == local_folder:
                        local_path = f"{local_folder}/{os.path.basename(file)}"
                        remote_path = f"{remote_dir}/{os.path.basename(file)}"
                        # Upload the file
                        sftp.put(local_path, remote_path)
                # Recursively upload subfolders
                for subdir in dirs:
                    self.upload_folder(f"{local_folder}/{subdir}", f"{remote_dir}/")
            sftp.close()
        except Exception as e:
            print(f"Error: {e}")
 
    def download_folder(self, remote_folder, local_zip_file):
        try:
            sftp = self.client.open_sftp()
            local_zip_file = f"{local_zip_file}/{os.path.basename(remote_folder)}"
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Download all files and directories from the remote folder to the temporary directory
                self._download_recursive(sftp, remote_folder, temp_dir)

                # Compress the entire temporary directory into a single zip file
                with zipfile.ZipFile(local_zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, _, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, os.path.relpath(file_path, temp_dir))

            # Close the SFTP connection
            sftp.close()

            os.rename(local_zip_file, f"{local_zip_file}.zip")

            print(f"Downloaded folder '{remote_folder}' and saved as '{local_zip_file}'")

        except Exception as e:
            print(f"Error: {e}")

    def _download_recursive(self, sftp, remote_folder, local_folder):
        # Download all files and directories from the remote folder to the local folder
        for entry in sftp.listdir_attr(remote_folder):
            remote_path = f"{remote_folder}/{entry.filename}"
            local_path = os.path.join(local_folder, entry.filename)
            if stat.S_ISDIR(entry.st_mode):
                # If it's a directory, create the corresponding local directory and download its contents
                os.makedirs(local_path, exist_ok=True)
                self._download_recursive(sftp, remote_path, local_path)
            else:
                # If it's a file, download it to the local directory
                sftp.get(remote_path, local_path)

    def disconnect(self):
        self.client.close()
        print("Disconnected from the server.")