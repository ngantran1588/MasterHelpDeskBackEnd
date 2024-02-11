#!/bin/bash

# Function to add a new user with a password
add_user_with_password() {
    local username=$1
    local password=$2

    # Add a new user with a password
    sudo useradd -m -s /bin/bash $username
    echo "$username:$password" | sudo chpasswd

    # Output success message
    echo "User $username added successfully with password"
}

# Main script
username=$1
password=$2

add_user_with_password $username $password
