#!/usr/bin/env bash

# Script to generate tweets from GitHub activity logs using AI via OpenRouter API
# Usage: ./tweet-summarizer.sh -i <input_file> [-m <model>] [-o <output_file>] [-k <api_key>] [-b <brand>] [-p <prompt_file>]

set -e

# Source .env file if it exists
if [ -f "$(dirname "$0")/../.env" ]; then
  source "$(dirname "$0")/../.env"
fi

# Default values
MODEL="anthropic/claude-3.7-sonnet"
API_KEY=${OPENROUTER_API_KEY:-""}
OUTPUT_FILE=""
BRAND="elizaos"  # Default brand
PROMPT_FILE=""   # Default prompt file

# Function to display usage info
usage() {
  echo "Usage: $0 -i <input_file> [-m <model>] [-o <output_file>] [-k <api_key>] [-b <brand>] [-p <prompt_file>]"
  echo
  echo "Options:"
  echo "  -i  Input file to summarize (required): markdown file from github/day or github/week"
  echo "  -m  OpenRouter model to use (default: anthropic/claude-3.7-sonnet)"
  echo "  -o  Output file for the tweet (default: tweets/input_filename_brand_tweet.txt)"
  echo "  -k  OpenRouter API key (optional, can also use OPENROUTER_API_KEY env var or .env file)"
  echo "  -b  Brand style to use: 'elizaos' (default) or 'autofun'"
  echo "  -p  Custom prompt file to use (optional, overrides -b option)"
  echo "  -h  Display this help message"
  exit 1
}

# Parse command-line arguments
while getopts "i:m:o:k:b:p:h" opt; do
  case ${opt} in
    i )
      INPUT_FILE=$OPTARG
      ;;
    m )
      MODEL=$OPTARG
      ;;
    o )
      OUTPUT_FILE=$OPTARG
      ;;
    k )
      API_KEY=$OPTARG
      ;;
    b )
      BRAND=$OPTARG
      ;;
    p )
      PROMPT_FILE=$OPTARG
      ;;
    h )
      usage
      ;;
    \? )
      usage
      ;;
  esac
done

# Check if input file was provided
if [ -z "$INPUT_FILE" ]; then
  echo "Error: Input file is required"
  usage
fi

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
  echo "Error: File '$INPUT_FILE' not found"
  exit 1
fi

# Check if API key is available
if [ -z "$API_KEY" ]; then
  echo "Error: OpenRouter API key is required"
  echo "Either set the OPENROUTER_API_KEY environment variable, use the -k option, or add it to the .env file"
  exit 1
fi

# Check for required tools
for cmd in curl jq; do
  if ! command -v $cmd &> /dev/null; then
    echo "Error: $cmd is required but not installed"
    exit 1
  fi
done

# Create tweets directory if it doesn't exist
mkdir -p tweets

# Read the content of the input file
CONTENT=$(cat "$INPUT_FILE")

# Determine if this is a daily or weekly update
if [[ "$INPUT_FILE" == *"/day/"* ]]; then
  UPDATE_TYPE="daily"
else
  UPDATE_TYPE="weekly"
fi

# Determine which prompt file to use
if [ -n "$PROMPT_FILE" ]; then
  # Use custom prompt file if provided
  if [ ! -f "$PROMPT_FILE" ]; then
    echo "Error: Prompt file '$PROMPT_FILE' not found"
    exit 1
  fi
  PROMPT_TEMPLATE=$(cat "$PROMPT_FILE")
elif [ "$BRAND" = "autofun" ]; then
  # Use auto.fun prompt
  PROMPT_TEMPLATE=$(cat "$(dirname "$0")/prompts/comms/autofun_prompt.txt")
else
  # Use elizaOS prompt
  PROMPT_TEMPLATE=$(cat "$(dirname "$0")/prompts/comms/elizaos_prompt.txt")
fi

# Create a temporary file for the prompt with placeholders replaced
TEMP_PROMPT=$(mktemp)
echo "$PROMPT_TEMPLATE" > "$TEMP_PROMPT"

# Replace the activity_log placeholder with the actual content
# Using awk to avoid sed escaping issues
awk -v content="$CONTENT" '{gsub(/{activity_log}/, content); print}' "$TEMP_PROMPT" > "${TEMP_PROMPT}.new"
mv "${TEMP_PROMPT}.new" "$TEMP_PROMPT"

# Read the final prompt
BRAND_PROMPT=$(cat "$TEMP_PROMPT")
rm "$TEMP_PROMPT"

# Make API request to OpenRouter
echo "Sending request to $MODEL via OpenRouter..."
RESPONSE=$(curl -s "https://openrouter.ai/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -H "HTTP-Referer: https://github.com/elizaos/eliza" \
  -H "X-Title: elizaOS Tweet Generator" \
  -d @- << EOF
{
  "model": "$MODEL",
  "messages": [
    {
      "role": "user",
      "content": $(printf '%s\n' "$BRAND_PROMPT" | jq -Rs .)
    }
  ]
}
EOF
)

# Extract the response content using jq
TWEET=$(echo "$RESPONSE" | jq -r '.choices[0].message.content')

# Check if we got a valid response
if [ -z "$TWEET" ] || [ "$TWEET" == "null" ]; then
  echo "Error: Failed to get a valid response"
  echo "API Response: $RESPONSE"
  exit 1
fi

# Print the tweet
echo -e "\n===== TWEET =====\n"
echo "$TWEET"
echo -e "\n================="

# Determine output file path
if [ -z "$OUTPUT_FILE" ]; then
  # Get the base filename without path and extension
  BASE_FILENAME=$(basename "$INPUT_FILE" .md)
  
  # Default output file name if none specified
  OUTPUT_FILE="tweets/${BASE_FILENAME}_${BRAND}_tweet.txt"
fi

# Save the tweet to file
echo "$TWEET" > "$OUTPUT_FILE"
echo -e "\nTweet saved to: $OUTPUT_FILE" 