#!/bin/bash

# Update package index
sudo apt update

# Install NGINX
sudo apt install -y nginx --fix-missing

# Output installation completion message
echo "NGINX installation completed."
