#!/bin/bash
# Backfill missing facts data for a date range
#
# Usage:
#   ./scripts/etl/backfill-facts.sh                    # Default: 2024-10-15 to 2025-03-31
#   ./scripts/etl/backfill-facts.sh 2025-01-01         # From date to 2025-03-31
#   ./scripts/etl/backfill-facts.sh 2025-01-01 2025-01-31  # Custom range
#
# Environment:
#   OPENROUTER_API_KEY=your_key (required)
#
# Each date takes ~30-60 seconds depending on API response time.

set -e

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "ERROR: OPENROUTER_API_KEY environment variable is not set"
    echo "Usage: OPENROUTER_API_KEY=your_key $0 [start_date] [end_date]"
    exit 1
fi

# Default date range
START_DATE="${1:-2024-10-15}"
END_DATE="${2:-2025-03-31}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$REPO_ROOT"

# Generate date array
DATES=()
current="$START_DATE"
while [[ "$current" < "$END_DATE" || "$current" == "$END_DATE" ]]; do
    DATES+=("$current")
    current=$(date -d "$current + 1 day" +%Y-%m-%d)
done

TOTAL=${#DATES[@]}
CURRENT=0
SUCCESS=0
FAILED=0
SKIPPED=0

echo "========================================"
echo "Facts Backfill Script"
echo "Date range: $START_DATE to $END_DATE"
echo "Total dates to process: $TOTAL"
echo "========================================"
echo ""

for DATE in "${DATES[@]}"; do
    CURRENT=$((CURRENT + 1))
    INPUT_FILE="the-council/aggregated/${DATE}.json"
    OUTPUT_JSON="the-council/facts/${DATE}.json"
    OUTPUT_MD="hackmd/facts/${DATE}.md"

    echo -n "[$CURRENT/$TOTAL] $DATE... "

    # Check if input file exists
    if [ ! -f "$INPUT_FILE" ]; then
        echo "SKIP (no aggregated file)"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    # Check if output already exists
    if [ -f "$OUTPUT_JSON" ]; then
        echo "SKIP (already exists)"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    # Ensure output directories exist
    mkdir -p "the-council/facts"
    mkdir -p "hackmd/facts"

    # Run the extraction
    if python scripts/etl/extract-facts.py -i "$INPUT_FILE" -o "$OUTPUT_JSON" -md "$OUTPUT_MD" 2>&1 | tail -1; then
        SUCCESS=$((SUCCESS + 1))
    else
        echo "FAILED"
        FAILED=$((FAILED + 1))
    fi

    # Small delay to avoid rate limiting
    sleep 1
done

echo ""
echo "========================================"
echo "Backfill Complete"
echo "  Success: $SUCCESS"
echo "  Skipped: $SKIPPED"
echo "  Failed:  $FAILED"
echo "========================================"

# Update daily.json permalink to latest date
LATEST_FACTS=$(ls -1 the-council/facts/20*.json 2>/dev/null | grep -v daily | sort | tail -1)
if [ -n "$LATEST_FACTS" ]; then
    cp "$LATEST_FACTS" "the-council/facts/daily.json"
    echo "Updated daily.json to: $(basename "$LATEST_FACTS")"
fi
