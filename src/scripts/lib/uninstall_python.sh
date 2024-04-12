#!/bin/bash

# Uninstall Python
sudo apt purge -y python3

# Remove Python directories and files
sudo rm -rf /usr/lib/python3
sudo rm -rf /usr/local/lib/python3

# Output uninstallation completion message
echo "Python uninstallation completed."
