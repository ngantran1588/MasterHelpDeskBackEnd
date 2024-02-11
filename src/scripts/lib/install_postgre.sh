#!/bin/bash

# Update package index
sudo apt update

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib --fix-missing

# Output installation completion message
echo "PostgreSQL installation completed."
