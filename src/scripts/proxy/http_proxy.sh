#!/bin/bash

sudo echo "export http_proxy=http://$1" >> /etc/environment
echo "HTTP Proxy configured successfully with host: $1"

source /etc/environment
echo "Proxy changes applied successfully."
