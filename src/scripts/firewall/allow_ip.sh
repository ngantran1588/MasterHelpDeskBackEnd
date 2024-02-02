#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <ip_address>"
    exit 1
fi

sudo ufw allow from $1
echo "Allowed traffic from IP: $1"
