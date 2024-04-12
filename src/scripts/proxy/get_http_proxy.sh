#!/bin/bash

# Get proxy lines from /etc/environment
proxies=$(grep -E 'http_proxy=' /etc/environment)

# Initialize an empty array to store proxy details
proxy_details=()

# Loop through each line containing a proxy definition
while IFS= read -r line; do
    # Extract protocol and details from each line
    protocol=$(echo "$line" | cut -d'=' -f1 | sed 's/export //')
    details=$(echo "$line" | cut -d'=' -f2)

    # Append protocol and details as JSON object to array
    proxy_details+=("{\"protocol\":\"$protocol\", \"details\":\"$details\"}")
done <<< "$proxies"

# Convert array to JSON and print
echo "["$(IFS=,; echo "${proxy_details[*]}")"]"
