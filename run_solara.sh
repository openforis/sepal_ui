#!/bin/bash

# Default values
SOLARA_FILE="solara_app.py"
PORT="8900"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --port)
      PORT="$2"
      shift 2
      ;;
    --*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      SOLARA_FILE="$1"
      shift
      ;;
  esac
done

while IFS= read -r line; do
  [[ $line =~ ^#.*$ || -z $line ]] && continue
  
  if [[ $line =~ ^([^=]+)=(.*)$ ]]; then
    name="${BASH_REMATCH[1]}"
    value="${BASH_REMATCH[2]}"
    
    # Remove quotes if present
    value="${value#\'}"
    value="${value%\'}"
    value="${value#\"}"
    value="${value%\"}"
    
    export "$name=$value"
  fi
done < .env

# solara run "$SOLARA_FILE" --port 8900 --no-open
# solara run "$SOLARA_FILE" --port $PORT --no-open --log-level debug
solara run "$SOLARA_FILE" --port $PORT --no-open 
