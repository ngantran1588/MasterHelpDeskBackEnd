#!/bin/bash

sudo sh -c 'echo "export http_proxy=http://$1:$2" | tee -a /etc/environment' sh "$1" "$2"
echo "HTTP Proxy configured successfully with host: $1 and port:$2"

source /etc/environment
echo "Proxy changes applied successfully."
