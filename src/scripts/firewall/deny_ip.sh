#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <ip_address>"
    exit 1
fi

sudo ufw deny from $1
echo "Denied traffic from IP: $1"
