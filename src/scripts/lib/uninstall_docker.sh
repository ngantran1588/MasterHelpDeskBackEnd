#!/bin/bash

# Stop and disable Docker service
sudo systemctl stop docker
sudo systemctl disable docker

# Uninstall Docker
sudo apt purge -y docker.io

# Remove Docker directories and files
sudo rm -rf /var/lib/docker
sudo rm -rf /etc/docker

# Output uninstallation completion message
echo "Docker uninstallation completed."
