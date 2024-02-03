#!/bin/bash

sudo echo "export https_proxy=http://$1" >> /etc/environment
echo "HTTPS Proxy configured successfully with host: $1"

# Apply the changes
source /etc/environment
echo "Proxy changes applied successfully."
