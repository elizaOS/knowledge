#!/bin/bash

echo "Starting poster generation process..."
POSTER_OUTPUT_DIR="posters"

src_dirs=(
  "ai-news/elizaos/md/"
  "ai-news/elizaos/dev/md/"
  "ai-news/elizaos/discord/md/"
  "github/summaries/day/"
  "github/summaries/week/"
  "github/summaries/month/"
  "daily-silk/"
  "hackmd/council/"
  "hackmd/facts/"
  "hackmd/comms/discord-announcement/"
  "hackmd/comms/elizaos-tweets/"
  "hackmd/comms/user-feedback/"
  "hackmd/comms/weekly-newsletter/"
  "hackmd/dev/developer-update/"
  "hackmd/dev/issue-triage/"
  "hackmd/strategy/intel/"
  "hackmd/strategy/team-development/"
)

out_bases=(
  "ainews-elizaos"
  "ainews-elizaos-dev"
  "ainews-elizaos-discord"
  "github-summaries-day"
  "github-summaries-week"
  "github-summaries-month"
  "daily-silk"
  "hackmd-council-briefing"
  "hackmd-facts-briefing"
  "hackmd-comms-discord-announcement"
  "hackmd-comms-elizaos-tweets"
  "hackmd-comms-user-feedback"
  "hackmd-comms-weekly-newsletter"
  "hackmd-dev-developer-update"
  "hackmd-dev-issue-triage"
  "hackmd-strategy-intel"
  "hackmd-strategy-team-development"
)

generated_posters_count=0

for i in ${!src_dirs[@]}; do
  SRC_DIR="${src_dirs[$i]}"
  OUT_BASE_NAME="${out_bases[$i]}"
  LATEST_MD_FILE=""
  LATEST_DATED_FILE=""

  echo "Processing directory: $SRC_DIR"
  if [ ! -d "$SRC_DIR" ]; then
    echo "Source directory $SRC_DIR not found. Skipping."
    continue
  fi

  # Find latest YYYY-MM-DD.md file
  _latest_basename=$(find "$SRC_DIR" -maxdepth 1 -type f -name "????-??-??.md" -print0 2>/dev/null | xargs -0 -r basename -a 2>/dev/null | sort -r | head -n 1)
  if [ -n "$_latest_basename" ]; then
    LATEST_DATED_FILE="${SRC_DIR}${_latest_basename}"
  fi

  if [ -n "$LATEST_DATED_FILE" ] && [ -f "$LATEST_DATED_FILE" ]; then
    LATEST_MD_FILE="$LATEST_DATED_FILE"
    echo "   Found latest dated file: $LATEST_MD_FILE"
  elif [ -f "${SRC_DIR}daily.md" ]; then
    LATEST_MD_FILE="${SRC_DIR}daily.md"
    echo "   No dated files found. Using preferred: daily.md"
  elif [ -f "${SRC_DIR}index.md" ]; then
    LATEST_MD_FILE="${SRC_DIR}index.md"
    echo "   No dated or daily.md. Using preferred: index.md"
  elif [ -f "${SRC_DIR}README.md" ]; then
    LATEST_MD_FILE="${SRC_DIR}README.md"
    echo "   No dated, daily.md or index.md. Using preferred: README.md"
  else
    LATEST_MD_FILE=$(find "$SRC_DIR" -maxdepth 1 -type f -name '*.md' -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -n1 | cut -d' ' -f2-)
    if [ -n "$LATEST_MD_FILE" ] && [ -f "$LATEST_MD_FILE" ]; then
      echo "   No dated or specific preferred files. Using most recently modified: $LATEST_MD_FILE"
    else
      LATEST_MD_FILE=""
    fi
  fi
  
  if [ -n "$LATEST_MD_FILE" ]; then
    echo "   Selected markdown file for $SRC_DIR: $LATEST_MD_FILE"
    CLEAN_OUT_BASE_NAME=$(echo "$OUT_BASE_NAME" | sed 's|/|-|g')
    
    # Generate timestamped poster filename to avoid Discord caching
    CURRENT_DATE=$(date +%Y-%m-%d)
    PERMALINK_POSTER_FILENAME="${CURRENT_DATE}_${CLEAN_OUT_BASE_NAME}.png"
    PERMALINK_POSTER_PATH="${POSTER_OUTPUT_DIR}/${PERMALINK_POSTER_FILENAME}"
    
    echo "   Generating poster: $PERMALINK_POSTER_PATH"

    if ./scripts/posters-enhanced.sh "$LATEST_MD_FILE" "$PERMALINK_POSTER_PATH"; then
      if [ -f "$PERMALINK_POSTER_PATH" ] && [ -s "$PERMALINK_POSTER_PATH" ]; then
        echo "   Successfully generated poster: $PERMALINK_POSTER_PATH"
        generated_posters_count=$((generated_posters_count + 1))
      else
        echo "   ERROR: posters-enhanced.sh exited 0 for $LATEST_MD_FILE, but $PERMALINK_POSTER_PATH was not found or is empty."
      fi
    else
      echo "   ERROR: posters-enhanced.sh failed for $LATEST_MD_FILE (exit code $?). Check scripts/posters-enhanced.sh logs or errors."
    fi
  else
    echo "   No suitable markdown file found in $SRC_DIR after filtering. Skipping poster generation."
  fi
  echo "----"
done

if [ "$generated_posters_count" -eq 0 ]; then
  echo "No posters were successfully generated in this run."
  exit 1
else
  echo "Total posters successfully created: $generated_posters_count"
  exit 0
fi