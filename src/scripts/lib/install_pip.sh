#!/bin/bash

# Update package index
sudo apt update

# Install Pip for Python 3
sudo apt install -y python3-pip --fix-missing

# Output installation completion message
echo "Pip installation completed."
