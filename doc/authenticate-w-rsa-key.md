## 1. Generate SSH Key Pair Locally:

Open a terminal on your local machine and run the following command to generate a new SSH key pair:

```bash
ssh-keygen -t rsa -b 2048
```

You'll be prompted to provide a file path to save the key pair. Press Enter to accept the default path (~/.ssh/id_rsa) or specify a custom path.

This command generates a private key (id_rsa) and a public key (id_rsa.pub). The private key should be kept secure, and the public key is what you'll add to the remote server.

## 2. Copy Public Key to Remote Server:

Use the following command to copy the public key to the remote server. Replace `your_username` and `your_remote_server_ip` with your actual username and server IP address:

```bash
ssh-copy-id -i ~/.ssh/id_rsa.pub your_username@your_remote_server_ip
```
This command adds your public key to the ~/.ssh/authorized_keys file on the remote server. You may be prompted to enter your password for the remote server.

## 3. Ensure Correct Permissions:
Make sure the permissions on the .ssh directory and the authorized_keys file are secure on the remote server:
```
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```
## 4. Test SSH Connection:
Now, you should be able to SSH into the remote server without entering a password:
```
ssh your_username@your_remote_server_ip
```
If everything is set up correctly, you should be logged in without being prompted for a password.

After completing these steps, you can use the private key (id_rsa) for authentication in your Python script, and the corresponding public key is already added to the remote server's authorized_keys file.