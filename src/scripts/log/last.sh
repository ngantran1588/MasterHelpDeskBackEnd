#!/bin/bash

# Capture last login information
last_output=$( last )

# Function to parse each last log line
parse_last_line() {
  local line="$1"
  local username="${line%% *}"
  local rest="${line#* }"

  # Check for "still logged in" format
  if [[ $rest == *"still logged in"* ]]; then
    local tty="${rest%% *}"
    local message="still logged in"
  else
    local tty="${rest%% *}"
    local from_to="${rest#* }"
    local duration="${from_to##*()}"  # Extract duration if present
    local message="${from_to%(*)}"  # Extract login message
  fi

  # Create JSON object (adjust structure as needed)
  echo "{ \"username\": \"$username\", \"tty\": \"$tty\", \"message\": \"$message\", \"duration\": \"$duration\" }"
}

# Process each last log line
last_entries=""
while read -r line; do
  # Skip header line
  [[ -z "$line" ]] && continue
  json_entry=$(parse_last_line "$line")
  last_entries+="$json_entry,"
done <<< "$last_output"

# Remove trailing comma
last_entries="${last_entries%,}"

# Wrap entries in a JSON array
echo "[ $last_entries ]"
