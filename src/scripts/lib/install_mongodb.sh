#!/bin/bash

# Import MongoDB GPG key
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 9DA31620334BD75D9DCB49F368818C72E52529D4

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -sc)/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list

# Update package index
sudo apt update

# Install MongoDB
sudo apt install -y mongodb-org --fix-missing

# Output installation completion message
echo "MongoDB installation completed."
