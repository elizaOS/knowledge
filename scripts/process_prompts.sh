#!/usr/bin/env bash

# Script to process the aggregated daily context JSON through specific prompts
# provided as command-line arguments, using the summarize.sh script.

set -e

# --- Configuration ---
INPUT_JSON="the-council/daily.json"
PROMPTS_DIR="scripts/prompts"
OUTPUT_DIR="scripts/output"
SUMMARIZE_SCRIPT="scripts/summarize.sh"
# --- End Configuration ---

# --- Usage Function ---
usage() {
  echo "Usage: $0 <prompt_filename1> [prompt_filename2] ..."
  echo
  echo "Processes the content from $INPUT_JSON using the specified prompt files"
  echo "from the $PROMPTS_DIR directory."
  echo "Example: $0 elizaos_prompt.txt autofun_prompt.txt"
  exit 1
}

# Check if any arguments were provided
if [ $# -eq 0 ]; then
    echo "Error: No prompt filenames provided."
    usage
fi

# Check for required tools
if ! command -v jq &> /dev/null; then
  echo "Error: jq is required but not installed. Please install jq (e.g., 'sudo apt install jq' or 'brew install jq')."
  exit 1
fi

if [ ! -f "$SUMMARIZE_SCRIPT" ]; then
    echo "Error: Summarization script not found at '$SUMMARIZE_SCRIPT'"
    exit 1
fi

if [ ! -f "$INPUT_JSON" ]; then
    echo "Error: Input JSON file not found at '$INPUT_JSON'"
    exit 1
fi

if [ ! -d "$PROMPTS_DIR" ]; then
    echo "Error: Prompts directory not found at '$PROMPTS_DIR'"
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Create a temporary file for the aggregated content
TEMP_INPUT_FILE=$(mktemp)
# Ensure temporary file is cleaned up on script exit
trap 'rm -f -- "$TEMP_INPUT_FILE"' EXIT

echo "Aggregating content from $INPUT_JSON..."
# Extract all 'content' fields recursively and join them into the temp file
jq -r '.. | .content? // empty' "$INPUT_JSON" > "$TEMP_INPUT_FILE"

echo "Processing content through specified prompts..."

# Iterate through the command-line arguments (prompt filenames)
for prompt_name in "$@"; do
    prompt_file="$PROMPTS_DIR/$prompt_name"
    TODAY_DATE=$(date +%Y-%m-%d) # Get current date

    if [ -f "$prompt_file" ]; then
        # Use prompt filename (without extension) for the output markdown file
        # Prepend date to the filename
        output_file="hackmd/${TODAY_DATE}-${prompt_name%.*}.md" # NEW Path with Date

        echo "  - Using prompt: $prompt_name -> $output_file"

        # Call the summarize script
        # Assumes OPENROUTER_API_KEY is set in the environment
        "$SUMMARIZE_SCRIPT" -i "$TEMP_INPUT_FILE" -p "$prompt_file" -o "$output_file"

        if [ $? -ne 0 ]; then
            echo "    Error processing prompt $prompt_name. Check summarize.sh output."
        else
            echo "    Successfully generated $output_file"
        fi
    else
        echo "    Warning: Prompt file not found: $prompt_file. Skipping."
    fi
done

echo "Processing complete. Outputs are in the '$OUTPUT_DIR' directory."

exit 0 
