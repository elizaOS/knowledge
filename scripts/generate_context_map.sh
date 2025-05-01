#!/usr/bin/env bash

# Script to generate a JSON file containing aggregated content from relevant source files.
# Usage: ./scripts/generate_context_map.sh [YYYY-MM-DD]
# If no date is provided, defaults to the current date.

set -e

# Determine the target date (use argument or default to today)
TARGET_DATE=${1:-$(date +%Y-%m-%d)}
echo "Generating context map for date: $TARGET_DATE"

# Updated output filename to include the target date
OUTPUT_FILE="the-council/${TARGET_DATE}.json"
TMP_DIR=$(mktemp -d)

# Cleanup temporary directory on exit
trap 'rm -rf -- "$TMP_DIR"' EXIT

# --- Helper Functions ---

# Function to get content of all files in a directory, sorted by filename
# Writes JSON array to a specified output file: [{ "filename": "...", "content": "..." }, ...]
get_dir_content_to_file() {
    local dir="$1"
    local output_temp_file="$2"
    local all_json_objects=""
    local file_list=()

    if [ -d "$dir" ]; then
        # Collect filenames first
        while IFS= read -r -d $'\0' file; do
            file_list+=("$file")
        done < <(find "$dir" -maxdepth 1 -type f -print0)

        # Sort the filenames (lexicographical sort works due to YYYY-MM-DD format)
        mapfile -t sorted_files < <(printf "%s\n" "${file_list[@]}" | sort)

        # Process sorted files
        for file in "${sorted_files[@]}"; do
            if [ -f "$file" ]; then # Double check file exists
                local filename=$(basename "$file")
                local raw_content=$(cat "$file")
                # Create jq command to generate the object safely
                local file_json_object=$(jq -n --arg fn "$filename" --arg rc "$raw_content" '{filename: $fn, content: $rc}')
                # Append object and newline
                all_json_objects+=$(printf "%s\n" "$file_json_object")
            fi
        done
    fi

    # Use jq's slurp (-s) flag to combine all JSON objects into a single array and write to file
    if [ -z "$all_json_objects" ]; then
        echo "[]" > "$output_temp_file"
    else
        # Pipe the objects into jq -s
        printf "%s" "$all_json_objects" | jq -s . > "$output_temp_file"
    fi
}

# Function to get content of the single MOST RECENT file in a directory (based on filename sort)
# Writes JSON array to a specified output file: [{ "filename": "...", "content": "..." }] or []
get_latest_file_content_to_file() {
    local dir="$1"
    local output_temp_file="$2"
    local file_list=()
    local latest_file=""

    if [ -d "$dir" ]; then
        # Collect filenames
        while IFS= read -r -d $'\0' file; do
            file_list+=("$file")
        done < <(find "$dir" -maxdepth 1 -type f -print0)

        # Sort and get the last one (most recent)
        if [ ${#file_list[@]} -gt 0 ]; then
            latest_file=$(printf "%s\n" "${file_list[@]}" | sort | tail -n 1)
        fi
    fi

    # Process only the latest file if found
    if [ -n "$latest_file" ] && [ -f "$latest_file" ]; then
        local filename=$(basename "$latest_file")
        local raw_content=$(cat "$latest_file")
        # Create jq command to generate the object safely
        local file_json_object=$(jq -n --arg fn "$filename" --arg rc "$raw_content" '{filename: $fn, content: $rc}')
        # Output as a single-element array
        echo "[$file_json_object]" > "$output_temp_file"
    else
        # No files found or error, output empty array
        echo "[]" > "$output_temp_file"
    fi
}


# Function to get content of markdown files from the last N days based on YYYY-MM-DD filename
# Writes JSON array to a specified output file: [{ "filename": "YYYY-MM-DD.md", "content": "..." }, ...]
# This function inherently processes in date order due to how dates are generated
get_recent_md_content_to_file() {
    local dir="$1"
    local days="$2"
    local output_temp_file="$3"
    local target_date_ref="$4" # Added: Pass the target date for reference
    local temp_dates=$(mktemp -p "$TMP_DIR")
    local all_json_objects=""

    if [ ! -d "$dir" ]; then
        echo "[]" > "$output_temp_file"
        rm "$temp_dates"
        return
    fi

    # Generate date strings relative to the target date
    for i in $(seq 0 $((days - 1))); do
        # Use the target date as the reference for calculating past dates
        date -d "$target_date_ref -$i days" +%Y-%m-%d >> "$temp_dates"
    done

    # Iterate through target dates (already sorted chronologically)
    while IFS= read -r date_str; do
        local target_filename="${date_str}.md"
        local target_filepath="${dir}/${target_filename}"

        if [ -f "$target_filepath" ]; then
            local raw_content=$(cat "$target_filepath")
            # Create jq command to generate the object safely
            local file_json_object=$(jq -n --arg fn "$target_filename" --arg rc "$raw_content" '{filename: $fn, content: $rc}')
            # Append object and newline
            all_json_objects+=$(printf "%s\n" "$file_json_object")
        fi
    done < "$temp_dates"

    rm "$temp_dates"

    # Use jq's slurp (-s) flag to combine all JSON objects into a single array and write to file
    if [ -z "$all_json_objects" ]; then
        echo "[]" > "$output_temp_file"
    else
         # Pipe the objects into jq -s
        printf "%s" "$all_json_objects" | jq -s . > "$output_temp_file"
    fi
}

# --- Main Logic ---

echo "Aggregating context..."

# Define source directories
AI_NEWS_DISCORD_MD="ai-news/elizaos/discord/md"
AI_NEWS_DEV_MD="ai-news/elizaos/dev/md"
# GITHUB_STATS_WEEK="github/stats/week" # Removed: Not needed for council context
# GITHUB_STATS_MONTH="github/stats/month" # Removed: Not needed for council context
GITHUB_SUMMARIES_WEEK="github/summaries/week"
GITHUB_SUMMARIES_MONTH="github/summaries/month"

# Define temporary file paths
DISCORD_MD_TMP="$TMP_DIR/discord_md.json"
DEV_MD_TMP="$TMP_DIR/dev_md.json"
# STATS_WEEK_TMP="$TMP_DIR/stats_week.json" # Removed
# STATS_MONTH_TMP="$TMP_DIR/stats_month.json" # Removed
SUMMARIES_WEEK_TMP="$TMP_DIR/summaries_week.json"
SUMMARIES_MONTH_TMP="$TMP_DIR/summaries_month.json"

# Generate content JSON arrays into temporary files
echo "Processing Discord MD (last 3 days relative to $TARGET_DATE)..."
get_recent_md_content_to_file "$AI_NEWS_DISCORD_MD" 3 "$DISCORD_MD_TMP" "$TARGET_DATE" # Pass TARGET_DATE
echo "Processing Dev MD (last 3 days relative to $TARGET_DATE)..."
get_recent_md_content_to_file "$AI_NEWS_DEV_MD" 3 "$DEV_MD_TMP" "$TARGET_DATE" # Pass TARGET_DATE
# echo "Processing GitHub Stats Week (latest)..." # Removed
# get_latest_file_content_to_file "$GITHUB_STATS_WEEK" "$STATS_WEEK_TMP" # Removed
# echo "Processing GitHub Stats Month (latest)..." # Removed
# get_latest_file_content_to_file "$GITHUB_STATS_MONTH" "$STATS_MONTH_TMP" # Removed
echo "Processing GitHub Summaries Week (latest)..."
get_latest_file_content_to_file "$GITHUB_SUMMARIES_WEEK" "$SUMMARIES_WEEK_TMP"
echo "Processing GitHub Summaries Month (latest)..."
get_latest_file_content_to_file "$GITHUB_SUMMARIES_MONTH" "$SUMMARIES_MONTH_TMP"


echo "Constructing final JSON..."
# Construct the final JSON using jq --slurpfile
# Removed stats_week and stats_month from --slurpfile arguments and the JSON structure
jq -n \
  --slurpfile discord_md "$DISCORD_MD_TMP" \
  --slurpfile dev_md "$DEV_MD_TMP" \
  --slurpfile summaries_week "$SUMMARIES_WEEK_TMP" \
  --slurpfile summaries_month "$SUMMARIES_MONTH_TMP" \
  '{
    "ai-news": {
      "elizaos": {
        # $varname from --slurpfile is already an array
        "discord_md_last_3_days": $discord_md[0], # Updated key name
        "dev_md_last_3_days": $dev_md[0] # Updated key name
      }
    },
    "github": {
      # "stats": { # Removed stats section
      #   "week": $stats_week[0],
      #   "month": $stats_month[0]
      # },
      "summaries": {
        "week": $summaries_week[0],
        "month": $summaries_month[0]
      }
    }
  }' > "$OUTPUT_FILE" # Output directly to file

# Ensure output directory exists - already done by writing temp files
# mkdir -p "$(dirname "$OUTPUT_FILE")"

# No need to echo $OUTPUT_JSON as it's written directly

echo "Aggregated context saved to: $OUTPUT_FILE"

# Temporary directory is removed by trap
exit 0 