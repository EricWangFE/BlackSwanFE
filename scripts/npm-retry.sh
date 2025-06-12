#!/bin/bash
# Retry npm install with exponential backoff for 504 Gateway Timeout errors

retry_npm() {
  local command="${1:-ci}"
  local n=1
  local max=5
  local delay=10
  
  echo "Running npm $command with retry logic..."
  
  while true; do
    echo "Attempt $n/$max:"
    
    # Try the npm command
    if npm $command; then
      echo "npm $command succeeded!"
      return 0
    else
      exit_code=$?
      
      # Check if it's a network error (504, 503, etc.)
      if [ $n -lt $max ]; then
        echo "npm $command failed with exit code $exit_code"
        echo "Retrying in $delay seconds..."
        sleep $delay
        
        # Exponential backoff
        delay=$((delay * 2))
        ((n++))
        
        # Clear npm cache on repeated failures
        if [ $n -eq 3 ]; then
          echo "Clearing npm cache..."
          npm cache clean --force
        fi
      else
        echo "npm $command failed after $max attempts"
        
        # If ci failed, try install as fallback
        if [ "$command" = "ci" ]; then
          echo "Falling back to npm install..."
          npm install
          return $?
        else
          return 1
        fi
      fi
    fi
  done
}

# Main execution
if [ $# -eq 0 ]; then
  retry_npm "ci"
else
  retry_npm "$1"
fi