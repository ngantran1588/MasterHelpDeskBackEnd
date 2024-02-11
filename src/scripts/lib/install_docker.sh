#!/bin/bash

# Update package index
sudo apt update

# Install Docker
sudo apt install -y docker.io --fix-missing

# Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Output installation completion message
echo "Docker installation completed."
