Note: Change to Bridged Adaptor for Ubuntu VM VirtualBox.

## 1.Verify SSH Server Installation and Status 
One of the most common reasons for not being able to SSH into an Ubuntu machine is because the OpenSSH server hasn’t been installed. 
To check if you have OpenSSH installed, run the following command: 
```
sudo apt-get install openssh-server
```
This command will either install the OpenSSH server or inform you that it’s already installed. 

Next, check if the SSH service is running by executing: 
```
sudo systemctl status ssh
```
If the output indicates that the SSH server is running, you can move on to the next troubleshooting step. If not, start the service using: 
```
sudo systemctl start ssh
```
## 2. Check Firewall and Port Settings 
Another common issue when trying to SSH into Ubuntu is incorrect firewall settings. This can mean that the SSH port is either blocked or not properly configured. 

First, verify if the firewall is running:
```
sudo ufw status
```

If the firewall is active, make sure the SSH port (usually port 22) is allowed. You can do this by running: 
```
sudo ufw allow ssh
```
If you’re using a custom SSH port, replace “ssh” with the relevant port number (e.g., “sudo ufw allow 2222”).

 To check if the firewall is the issue, temporarily disable it with the following command:
 ```
 sudo ufw disable
 ```
 Attempt to connect again. If successful, re-enable the firewall, and ensure your rules are properly configured. 
 ## 3.Network Connectivity Issues 
 Sometimes, the problem isn’t with your Ubuntu machine or SSH settings but rather with network connectivity. 
 
 First, try pinging the target machine from your local system using:
 ```
 ping target_machine_ip
 ```
 If the ping is successful, it means there is network connectivity between the two devices. If not, you might have a network issue. 
 
 Check if both machines are on the same subnet or if there is any routing issue. Another possible network problem could be related to DNS resolution. To check this, try connecting to your Ubuntu machine via its IP address instead of the hostname. If this works, you may need to update your DNS settings or configure the `/etc/hosts` file on the local system.

Source : https://locall.host/why-cant-i-ssh-into-ubuntu/
