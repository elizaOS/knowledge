#!/bin/bash
# Backfill missing council briefings for a date range
#
# Usage:
#   ./scripts/etl/backfill-council.sh                    # Default: 2024-10-15 to 2025-04-17
#   ./scripts/etl/backfill-council.sh 2025-01-01         # From date to 2025-04-17
#   ./scripts/etl/backfill-council.sh 2025-01-01 2025-01-31  # Custom range
#
# Environment:
#   OPENROUTER_API_KEY=your_key (required)
#   FORCE=1 (optional) - Overwrite existing files
#
# Each date takes ~30-60 seconds depending on API response time.

set -e

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "ERROR: OPENROUTER_API_KEY environment variable is not set"
    echo "Usage: OPENROUTER_API_KEY=your_key $0 [start_date] [end_date]"
    exit 1
fi

# Default date range (fill gap before existing briefings)
START_DATE="${1:-2024-10-15}"
END_DATE="${2:-2025-04-17}"

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
echo "Council Briefing Backfill Script"
echo "Date range: $START_DATE to $END_DATE"
echo "Total dates to process: $TOTAL"
echo "========================================"
echo ""

for DATE in "${DATES[@]}"; do
    CURRENT=$((CURRENT + 1))
    INPUT_FILE="the-council/aggregated/${DATE}.json"
    OUTPUT_JSON="the-council/council_briefing/${DATE}.json"

    echo -n "[$CURRENT/$TOTAL] $DATE... "

    # Check if input file exists
    if [ ! -f "$INPUT_FILE" ]; then
        echo "SKIP (no aggregated file)"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    # Check if output already exists (skip unless FORCE=1)
    if [ -f "$OUTPUT_JSON" ] && [ "$FORCE" != "1" ]; then
        echo "SKIP (already exists)"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    # Ensure output directory exists
    mkdir -p "the-council/council_briefing"

    # Run the generation
    if python scripts/etl/generate-council-context.py "$INPUT_FILE" "$OUTPUT_JSON" 2>&1 | tail -1; then
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
LATEST=$(ls -1 the-council/council_briefing/20*.json 2>/dev/null | grep -v daily | sort | tail -1)
if [ -n "$LATEST" ]; then
    cp "$LATEST" "the-council/council_briefing/daily.json"
    echo "Updated daily.json to: $(basename "$LATEST")"
fi
