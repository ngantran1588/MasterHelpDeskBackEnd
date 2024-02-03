#!/bin/bash

sudo sh -c 'echo "export ftp_proxy=http://$1:$2" | tee -a /etc/environment' sh "$1" "$2"
echo "FTP Proxy configured successfully with host: $1 and port:$2"

# Apply the changes
source /etc/environment
echo "Proxy changes applied successfully."
