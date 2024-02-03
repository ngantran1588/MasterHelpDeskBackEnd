#!/bin/bash

sudo echo "export ftp_proxy=http://$1" >> /etc/environment
echo "FTP Proxy configured successfully with host: $1"

# Apply the changes
source /etc/environment
echo "Proxy changes applied successfully."
