#!/bin/bash
# Backfill monthly retrospectives for months with sufficient data

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RETRO_SCRIPT="$SCRIPT_DIR/generate-monthly-retro.py"

# Check which months have facts data
echo "Checking available data..."

for year in 2024 2025; do
    for month in $(seq 1 12); do
        month_padded=$(printf "%02d" $month)
        
        # Skip future months
        if [[ "$year" == "2025" && "$month" -gt "11" ]]; then
            continue
        fi
        
        # Check if retro already exists
        retro_file="$SCRIPT_DIR/../the-council/retros/${year}-${month_padded}-retro.json"
        if [[ -f "$retro_file" ]]; then
            echo "[$year-$month_padded] Already exists, skipping"
            continue
        fi
        
        # Count facts files for this month
        facts_count=$(ls "$SCRIPT_DIR/../the-council/facts/${year}-${month_padded}-"*.json 2>/dev/null | wc -l || echo 0)
        
        if [[ "$facts_count" -lt 5 ]]; then
            echo "[$year-$month_padded] Only $facts_count facts files, skipping (need at least 5)"
            continue
        fi
        
        echo "[$year-$month_padded] Found $facts_count facts files, generating retro..."
        python "$RETRO_SCRIPT" -y "$year" -m "$month" || echo "  Failed, continuing..."
        
        # Small delay to avoid rate limiting
        sleep 2
    done
done

echo ""
echo "Backfill complete! Generated retros:"
ls -la "$SCRIPT_DIR/../the-council/retros/"
