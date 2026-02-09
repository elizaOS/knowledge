#!/bin/bash
#
# Backfill Facts Pipeline
#
# Regenerates missing facts and downstream data for dates when
# extract-facts.py was broken due to {username} KeyError bug.
#
# Usage:
#   ./scripts/backfill-facts-pipeline.sh
#   ./scripts/backfill-facts-pipeline.sh --start 2026-01-15 --end 2026-01-20
#   ./scripts/backfill-facts-pipeline.sh --dry-run
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default date range (6 days when pipeline was broken)
START_DATE="2026-01-15"
END_DATE="2026-01-20"
DRY_RUN=false
SKIP_AGGREGATION=false
SKIP_HIGHLIGHTS=false
SKIP_COUNCIL=false
SKIP_RSS=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --start)
      START_DATE="$2"
      shift 2
      ;;
    --end)
      END_DATE="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --skip-aggregation)
      SKIP_AGGREGATION=true
      shift
      ;;
    --skip-highlights)
      SKIP_HIGHLIGHTS=true
      shift
      ;;
    --skip-council)
      SKIP_COUNCIL=true
      shift
      ;;
    --skip-rss)
      SKIP_RSS=true
      shift
      ;;
    --help)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --start DATE          Start date (default: 2026-01-15)"
      echo "  --end DATE            End date (default: 2026-01-20)"
      echo "  --dry-run             Show what would be done without executing"
      echo "  --skip-aggregation    Skip re-aggregation step (if aggregated files exist)"
      echo "  --skip-highlights     Skip highlights generation"
      echo "  --skip-council        Skip council briefing generation"
      echo "  --skip-rss            Skip RSS feed regeneration"
      echo "  --help                Show this help message"
      echo ""
      echo "Environment variables:"
      echo "  OPENROUTER_API_KEY    Required for LLM calls"
      echo ""
      echo "Examples:"
      echo "  $0"
      echo "  $0 --start 2026-01-10 --end 2026-01-14"
      echo "  $0 --skip-aggregation  # If aggregated files already exist"
      echo "  $0 --dry-run           # Preview what would be done"
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Check environment
if [ -z "$OPENROUTER_API_KEY" ] && [ "$DRY_RUN" = false ]; then
  echo -e "${RED}ERROR: OPENROUTER_API_KEY not set${NC}"
  echo "Please set it with: export OPENROUTER_API_KEY='your-key'"
  exit 1
fi

# Generate date array
dates=()
current_date="$START_DATE"
while [[ "$current_date" < "$END_DATE" ]] || [[ "$current_date" == "$END_DATE" ]]; do
  dates+=("$current_date")
  # Increment date by 1 day (works on both Linux and macOS)
  current_date=$(date -I -d "$current_date + 1 day" 2>/dev/null || date -j -v+1d -f "%Y-%m-%d" "$current_date" +%Y-%m-%d)
done

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          ElizaOS Facts Pipeline Backfill                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Date range:${NC} $START_DATE to $END_DATE (${#dates[@]} days)"
echo -e "${YELLOW}Dry run:${NC} $DRY_RUN"
echo ""
echo -e "${YELLOW}Pipeline steps:${NC}"
echo "  1. Aggregate sources (skip: $SKIP_AGGREGATION)"
echo "  2. Extract facts (required)"
echo "  3. Generate highlights (skip: $SKIP_HIGHLIGHTS)"
echo "  4. Generate council briefings (skip: $SKIP_COUNCIL)"
echo "  5. Update RSS feeds (skip: $SKIP_RSS)"
echo ""

if [ "$DRY_RUN" = true ]; then
  echo -e "${YELLOW}DRY RUN MODE - No changes will be made${NC}"
  echo ""
fi

read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 0
fi

echo ""

# Track success/failures
declare -A step_results
total_steps=0
successful_steps=0
failed_steps=0

# Helper function to run command
run_command() {
  local step_name="$1"
  local command="$2"
  local date="$3"

  total_steps=$((total_steps + 1))

  if [ "$DRY_RUN" = true ]; then
    echo -e "${BLUE}[DRY RUN]${NC} $step_name"
    echo "  Command: $command"
    step_results["$date:$step_name"]="skipped"
    return 0
  fi

  echo -e "${BLUE}▶${NC} $step_name"

  if eval "$command"; then
    echo -e "${GREEN}✓${NC} $step_name completed"
    step_results["$date:$step_name"]="success"
    successful_steps=$((successful_steps + 1))
    return 0
  else
    echo -e "${RED}✗${NC} $step_name failed"
    step_results["$date:$step_name"]="failed"
    failed_steps=$((failed_steps + 1))
    return 1
  fi
}

# Step 1: Aggregate Sources (optional)
if [ "$SKIP_AGGREGATION" = false ]; then
  echo -e "${YELLOW}═══ Step 1/5: Aggregating Sources ═══${NC}"
  echo ""

  for date in "${dates[@]}"; do
    echo -e "${BLUE}Date: $date${NC}"

    # Check if aggregated file exists
    if [ -f "the-council/aggregated/$date.json" ]; then
      echo -e "${YELLOW}⚠${NC} Aggregated file exists, skipping (use --skip-aggregation to skip this check)"
    fi

    run_command \
      "Aggregate sources for $date" \
      "python scripts/etl/aggregate-sources.py $date" \
      "$date"

    echo ""
  done
else
  echo -e "${YELLOW}⊘ Skipping aggregation step${NC}"
  echo ""
fi

# Step 2: Extract Facts (required)
echo -e "${YELLOW}═══ Step 2/5: Extracting Facts ═══${NC}"
echo ""

for date in "${dates[@]}"; do
  echo -e "${BLUE}Date: $date${NC}"

  input_file="the-council/aggregated/$date.json"
  output_file="the-council/facts/$date.json"
  md_file="hackmd/facts/$date.md"

  # Check if input exists
  if [ ! -f "$input_file" ]; then
    echo -e "${RED}✗${NC} Input file missing: $input_file"
    echo -e "${YELLOW}  Run with --skip-aggregation=false to generate it${NC}"
    step_results["$date:extract-facts"]="failed"
    failed_steps=$((failed_steps + 1))
    total_steps=$((total_steps + 1))
    echo ""
    continue
  fi

  run_command \
    "Extract facts for $date" \
    "python scripts/etl/extract-facts.py -i '$input_file' -o '$output_file' -md '$md_file'" \
    "$date"

  if [ "$DRY_RUN" = false ]; then
    sleep 5  # Rate limiting
  fi

  echo ""
done

# Step 3: Generate Highlights (optional)
if [ "$SKIP_HIGHLIGHTS" = false ]; then
  echo -e "${YELLOW}═══ Step 3/5: Generating Highlights ═══${NC}"
  echo ""

  for date in "${dates[@]}"; do
    echo -e "${BLUE}Date: $date${NC}"

    run_command \
      "Generate highlights for $date" \
      "python scripts/etl/generate-daily-highlights.py --date $date" \
      "$date"

    if [ "$DRY_RUN" = false ]; then
      sleep 5  # Rate limiting
    fi

    echo ""
  done
else
  echo -e "${YELLOW}⊘ Skipping highlights generation${NC}"
  echo ""
fi

# Step 4: Generate Council Briefings (optional)
if [ "$SKIP_COUNCIL" = false ]; then
  echo -e "${YELLOW}═══ Step 4/5: Generating Council Briefings ═══${NC}"
  echo ""

  for date in "${dates[@]}"; do
    echo -e "${BLUE}Date: $date${NC}"

    input_file="the-council/aggregated/$date.json"
    output_file="the-council/council_briefing/$date.json"

    if [ ! -f "$input_file" ]; then
      echo -e "${RED}✗${NC} Input file missing: $input_file"
      step_results["$date:council-briefing"]="failed"
      failed_steps=$((failed_steps + 1))
      total_steps=$((total_steps + 1))
      echo ""
      continue
    fi

    run_command \
      "Generate council briefing for $date" \
      "python scripts/etl/generate-council-context.py '$input_file' '$output_file'" \
      "$date"

    if [ "$DRY_RUN" = false ]; then
      sleep 5  # Rate limiting
    fi

    echo ""
  done
else
  echo -e "${YELLOW}⊘ Skipping council briefing generation${NC}"
  echo ""
fi

# Step 5: Update RSS Feeds (once at the end)
if [ "$SKIP_RSS" = false ]; then
  echo -e "${YELLOW}═══ Step 5/5: Updating RSS Feeds ═══${NC}"
  echo ""

  run_command \
    "Regenerate RSS feeds" \
    "python scripts/etl/generate-rss.py" \
    "all"

  echo ""
else
  echo -e "${YELLOW}⊘ Skipping RSS feed generation${NC}"
  echo ""
fi

# Summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    Backfill Complete                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$DRY_RUN" = true ]; then
  echo -e "${YELLOW}DRY RUN - No changes were made${NC}"
  echo ""
  echo "Run without --dry-run to execute the backfill."
else
  echo -e "${GREEN}✓ Successful: $successful_steps${NC}"
  if [ $failed_steps -gt 0 ]; then
    echo -e "${RED}✗ Failed: $failed_steps${NC}"
    echo ""
    echo -e "${YELLOW}Failed steps:${NC}"
    for key in "${!step_results[@]}"; do
      if [ "${step_results[$key]}" = "failed" ]; then
        echo "  - $key"
      fi
    done
  fi
  echo ""

  echo -e "${YELLOW}Dates processed:${NC}"
  for date in "${dates[@]}"; do
    echo "  - $date"
  done
  echo ""

  echo -e "${YELLOW}Next steps:${NC}"
  echo "  1. Verify facts files: ls -lh the-council/facts/*.json"
  echo "  2. Check for errors: grep -i error the-council/facts/*.json"
  echo "  3. Inspect a sample: cat the-council/facts/$START_DATE.json | jq ."
  echo "  4. Update HackMD (if needed): python scripts/integrations/hackmd/update.py"
  echo "  5. Post to Discord (if needed): python scripts/integrations/discord/webhook.py"
fi

echo ""

exit 0
