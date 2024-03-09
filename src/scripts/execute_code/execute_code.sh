#!/bin/bash

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

install_python_libraries() {
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
}

# Check if the file has a Python extension
if [[ "$1" == *".py" ]]; then
    # Try running the Python script using python3
    if command_exists "python3"; then
        python3 "$1"
        if [ $? -ne 0 ]; then
            install_python_libraries
            python3 "$1"
        fi
    # If python3 is not available, try running using python
    elif command_exists "python"; then
        python "$1"
        if [ $? -ne 0 ]; then
            install_python_libraries
            python "$1"
        fi
    else
        echo "Python is not installed. Please install Python to run this script."
    fi
elif [[ "$1" == *".js" ]]; then
    # Run the JavaScript file using Node.js
    node "$1"
    # Check if Node.js modules are missing
    if [ $? -ne 0 ]; then
        # Check if node_modules directory exists
        if [ -d "node_modules" ]; then
            # Install required Node.js modules
            npm install
            # Retry running the JavaScript file
            node "$1"
        else
            echo "No node_modules directory found. Skipping installation."
        fi
    fi
elif [[ "$1" == *".go" ]]; then
    # Run the Go file using the Go runtime
    go run "$1"
else
    echo "Unsupported file type."
fi
