#!/bin/bash

# Number of lines to capture (adjust as needed)
log_lines=1000

# Capture last lines from syslog
logs=$(tail -n $log_lines /var/log/syslog)

# Function to parse each log line
parse_log_line() {
  local line="$1"
  # Modify regex if needed based on your specific log format
  local time="${line%% *}"
  local rest="${line#* }"
  local host="${rest%%:*}"  # Extract host up to the first colon
  local log="${rest#*:}"  # Extract log message after the first colon

  # Create JSON object (adjust structure as needed)
  echo "{ \"time\": \"$time\", \"host\": \"$host\", \"log\": \"$log\" }"
}

# Process each log line
for line in $logs; do
  # Parse line and convert to JSON
  json_log=$(parse_log_line "$line")
  echo "$json_log"
done

echo "Script completed."
