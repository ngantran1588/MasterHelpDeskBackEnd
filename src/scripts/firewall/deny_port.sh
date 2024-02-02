#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <port>"
    exit 1
fi

sudo ufw deny $1
echo "Denied traffic on port $1"
