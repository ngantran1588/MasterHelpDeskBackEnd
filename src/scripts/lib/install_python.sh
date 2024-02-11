#!/bin/bash

# Update package index
sudo apt update

# Install Python
sudo apt install -y python3 --fix-missing

# Output installation completion message
echo "Python installation completed."
