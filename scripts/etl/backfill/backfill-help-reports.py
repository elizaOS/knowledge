#!/usr/bin/env python3
"""
Backfills help reports for all historical months with Discord data.

This script detects all months with Discord JSON data and processes them
by running the extraction and analysis pipeline for each month.

Run manually or via GitHub Actions to backfill historical data.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime, timedelta
from calendar import monthrange

# Load environment variables from .env if available (for local testing)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, use system environment variables

# --- Configuration ---
SCRIPT_DIR = Path(__file__).parent.resolve()
SCRIPTS_ROOT = SCRIPT_DIR.parent  # scripts/
WORKSPACE_ROOT = SCRIPTS_ROOT.parent  # repository root

DISCORD_JSON_DIR = WORKSPACE_ROOT / "ai-news" / "elizaos" / "discord" / "json"
HELP_REPORTS_DIR = WORKSPACE_ROOT / "the-council" / "help-reports"

EXTRACT_SCRIPT = SCRIPT_DIR / "extract-help-interactions.py"
ANALYZE_SCRIPT = SCRIPT_DIR / "generate-monthly-help-report.py"

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(levelname)s - %(message)s')


def detect_available_months() -> list[tuple[int, int]]:
    """
    Detect all months with Discord JSON data.

    Returns list of (year, month) tuples sorted chronologically.
    """
    if not DISCORD_JSON_DIR.exists():
        logging.error(f"Discord JSON directory not found: {DISCORD_JSON_DIR}")
        return []

    # Scan for JSON files and extract dates
    dates = set()
    for json_file in DISCORD_JSON_DIR.glob("????-??-??.json"):
        try:
            date_str = json_file.stem  # YYYY-MM-DD
            date = datetime.strptime(date_str, "%Y-%m-%d")
            dates.add((date.year, date.month))
        except ValueError:
            continue

    return sorted(dates)


def month_already_processed(year: int, month: int) -> bool:
    """Check if a month has already been processed."""
    interactions_file = HELP_REPORTS_DIR / f"{year}-{month:02d}-interactions.json"
    report_file = HELP_REPORTS_DIR / f"{year}-{month:02d}-report.json"
    return interactions_file.exists() and report_file.exists()


def process_month(year: int, month: int, skip_if_exists: bool = True) -> bool:
    """
    Process a single month through the extraction and analysis pipeline.

    Returns True if successful, False otherwise.
    """
    month_str = f"{year}-{month:02d}"
    month_name = datetime(year, month, 1).strftime("%B %Y")

    if skip_if_exists and month_already_processed(year, month):
        logging.info(f"[{month_str}] Already processed, skipping")
        return True

    logging.info(f"[{month_str}] Processing {month_name}")

    # Step 1: Extract interactions
    logging.info(f"[{month_str}] Step 1/2: Extracting interactions...")
    try:
        result = subprocess.run(
            ["python", str(EXTRACT_SCRIPT), "-y", str(year), "-m", str(month)],
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            logging.error(f"[{month_str}] Extraction failed: {result.stderr}")
            return False

        logging.info(f"[{month_str}] Extraction completed")

    except subprocess.TimeoutExpired:
        logging.error(f"[{month_str}] Extraction timed out")
        return False
    except Exception as e:
        logging.error(f"[{month_str}] Extraction error: {e}")
        return False

    # Step 2: Generate report
    logging.info(f"[{month_str}] Step 2/2: Generating report...")
    try:
        result = subprocess.run(
            ["python", str(ANALYZE_SCRIPT), "-y", str(year), "-m", str(month)],
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            timeout=600,
            env={**os.environ}  # Pass through environment variables (for API key)
        )

        if result.returncode != 0:
            logging.error(f"[{month_str}] Analysis failed: {result.stderr}")
            return False

        logging.info(f"[{month_str}] Report generated successfully")
        return True

    except subprocess.TimeoutExpired:
        logging.error(f"[{month_str}] Analysis timed out")
        return False
    except Exception as e:
        logging.error(f"[{month_str}] Analysis error: {e}")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Backfill help reports for all historical months")
    parser.add_argument("--force", action="store_true", help="Reprocess already processed months")
    parser.add_argument("--start", type=str, help="Start from this month (YYYY-MM)")
    parser.add_argument("--end", type=str, help="End at this month (YYYY-MM)")
    parser.add_argument("--limit", type=int, help="Limit number of months to process")
    args = parser.parse_args()

    logging.info("Detecting available months...")
    available_months = detect_available_months()

    if not available_months:
        logging.error("No months with Discord data found")
        sys.exit(1)

    logging.info(f"Found {len(available_months)} months with data: {available_months[0]} to {available_months[-1]}")

    # Apply filters
    months_to_process = available_months

    if args.start:
        start_date = datetime.strptime(args.start, "%Y-%m")
        months_to_process = [(y, m) for y, m in months_to_process if (y, m) >= (start_date.year, start_date.month)]

    if args.end:
        end_date = datetime.strptime(args.end, "%Y-%m")
        months_to_process = [(y, m) for y, m in months_to_process if (y, m) <= (end_date.year, end_date.month)]

    # Exclude current month (incomplete data)
    today = datetime.now()
    current_month = (today.year, today.month)
    months_to_process = [(y, m) for y, m in months_to_process if (y, m) != current_month]

    if args.limit:
        months_to_process = months_to_process[:args.limit]

    logging.info(f"Will process {len(months_to_process)} months")

    if not months_to_process:
        logging.info("No months to process")
        return

    # Process each month
    successful = 0
    failed = 0
    skipped = 0

    for year, month in months_to_process:
        if not args.force and month_already_processed(year, month):
            skipped += 1
            continue

        success = process_month(year, month, skip_if_exists=not args.force)
        if success:
            successful += 1
        else:
            failed += 1

    # Print summary
    print(f"\n{'='*60}")
    print(f"Backfill Summary")
    print(f"{'='*60}")
    print(f"Total months: {len(months_to_process)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")

    if failed > 0:
        logging.warning(f"{failed} months failed to process")
        sys.exit(1)


if __name__ == "__main__":
    main()
