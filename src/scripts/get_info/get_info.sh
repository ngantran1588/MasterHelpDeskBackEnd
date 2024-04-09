#!/bin/bash

# Get RAM information
ram=$(free -h | awk 'NR==2{print $2}')

# Get CPU information (current percentage)
cpu=$(cat /proc/stat | grep cpu | tail -1 | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage "%"}')

# Get disk space information
disk_space=$(df -h --total | grep 'total' | awk '{print $3 " of " $2}')

# Get operating system information
os=$(cat /etc/os-release | grep "^PRETTY_NAME" | cut -d= -f2-)

# Get version information
version=$(cat /etc/os-release | grep "^VERSION=")

# Construct JSON response
response='{
    "RAM": "'"$ram"'",
    "CPU": "'"$cpu"'",
    "Disk_Space": "'"$disk_space"'",
    "Operating_System": '"$os"',
    "Version": '"$version"'
}'

echo $response
