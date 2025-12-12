#!/bin/bash
# Backfill missing facts data for dates 2025-11-13 through 2025-12-11
#
# Usage:
#   OPENROUTER_API_KEY=your_key ./scripts/backfill-facts.sh
#   or
#   export OPENROUTER_API_KEY=your_key && ./scripts/backfill-facts.sh
#
# This script will process all missing dates sequentially.
# Each date takes ~30-60 seconds depending on API response time.

set -e

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "ERROR: OPENROUTER_API_KEY environment variable is not set"
    echo "Usage: OPENROUTER_API_KEY=your_key ./scripts/backfill-facts.sh"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$REPO_ROOT"

# Missing dates to backfill (2025-11-13 through 2025-12-11)
DATES=(
    "2025-11-13" "2025-11-14" "2025-11-15" "2025-11-16" "2025-11-17" "2025-11-18"
    "2025-11-19" "2025-11-20" "2025-11-21" "2025-11-22" "2025-11-23" "2025-11-24"
    "2025-11-25" "2025-11-26" "2025-11-27" "2025-11-28" "2025-11-29" "2025-11-30"
    "2025-12-01" "2025-12-02" "2025-12-03" "2025-12-04" "2025-12-05" "2025-12-06"
    "2025-12-07" "2025-12-08" "2025-12-09" "2025-12-10" "2025-12-11"
)

TOTAL=${#DATES[@]}
CURRENT=0
SUCCESS=0
FAILED=0

echo "========================================"
echo "Facts Backfill Script"
echo "Total dates to process: $TOTAL"
echo "========================================"
echo ""

for DATE in "${DATES[@]}"; do
    CURRENT=$((CURRENT + 1))
    INPUT_FILE="the-council/aggregated/${DATE}.json"
    OUTPUT_JSON="the-council/facts/${DATE}.json"
    OUTPUT_MD="hackmd/facts/${DATE}.md"

    echo "[$CURRENT/$TOTAL] Processing $DATE..."

    # Check if input file exists
    if [ ! -f "$INPUT_FILE" ]; then
        echo "  SKIP: Aggregated file not found: $INPUT_FILE"
        FAILED=$((FAILED + 1))
        continue
    fi

    # Check if output already exists
    if [ -f "$OUTPUT_JSON" ]; then
        echo "  SKIP: Facts file already exists: $OUTPUT_JSON"
        continue
    fi

    # Ensure output directories exist
    mkdir -p "the-council/facts"
    mkdir -p "hackmd/facts"

    # Run the extraction
    if python scripts/extract-facts.py -i "$INPUT_FILE" -o "$OUTPUT_JSON" -md "$OUTPUT_MD"; then
        echo "  SUCCESS: Generated $OUTPUT_JSON"
        SUCCESS=$((SUCCESS + 1))
    else
        echo "  FAILED: Error processing $DATE"
        FAILED=$((FAILED + 1))
    fi

    # Small delay to avoid rate limiting
    sleep 2
done

echo ""
echo "========================================"
echo "Backfill Complete"
echo "  Success: $SUCCESS"
echo "  Failed:  $FAILED"
echo "  Skipped: $((TOTAL - SUCCESS - FAILED))"
echo "========================================"

# Update daily.json permalink to latest date
LATEST_FACTS=$(ls -1 the-council/facts/2025-*.json 2>/dev/null | grep -v daily | sort | tail -1)
if [ -n "$LATEST_FACTS" ]; then
    cp "$LATEST_FACTS" "the-council/facts/daily.json"
    echo "Updated daily.json to: $(basename "$LATEST_FACTS")"
fi
