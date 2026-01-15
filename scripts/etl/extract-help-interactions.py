#!/usr/bin/env python3
"""
Extracts help interactions from Discord JSON files and applies weighted scoring.

This script processes daily Discord summaries from ai-news/elizaos/discord/json/,
extracts structured help interactions (Helper | Helpee | Context | Resolution),
and applies dual weighting based on channel visibility and temporal context.

Run monthly to generate interaction data for contributor analysis.
"""

import os
import sys
import json
import re
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone
from calendar import monthrange
from collections import defaultdict
from typing import Optional

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

# Input/Output directories
DISCORD_JSON_DIR = WORKSPACE_ROOT / "ai-news" / "elizaos" / "discord" / "json"
OUTPUT_DIR = WORKSPACE_ROOT / "the-council" / "help-reports"

# Weighting configuration
NORTH_STAR_TRANSITION_DATE = "2025-12-01"  # When project goals shifted

CHANNEL_WEIGHTS = {
    "discussion": 1.0,          # Public, newcomer help
    "💬-discussion": 1.0,
    "coders": 1.0,              # Public, technical help
    "💻-coders": 1.0,
    "💬-coders": 1.0,
    "partners": 0.7,            # Semi-private
    "🥇-partners": 0.7,
    "tokenomics": 0.7,          # Semi-private
    "core-devs": 0.5,           # Private, internal collaboration
    "ideas-feedback-rants": 0.8,
    "spartan_holders": 0.6,
    "3d-ai-tv": 0.6,
}

DEFAULT_CHANNEL_WEIGHT = 1.0

# Temporal weights (alignment with project values)
TEMPORAL_WEIGHT_PRE_NORTH_STAR = 0.8    # Before Dec 2025
TEMPORAL_WEIGHT_POST_NORTH_STAR = 1.0   # Dec 2025 onwards

# Regex patterns for parsing help interactions
HELP_PATTERN_FULL = re.compile(
    r'Helper:\s*(.+?)\s*\|\s*Helpee:\s*(.+?)\s*\|\s*Context:\s*(.+?)\s*\|\s*Resolution:\s*(.+?)(?:\n|$)',
    re.IGNORECASE | re.DOTALL
)

HELP_PATTERN_NO_RESOLUTION = re.compile(
    r'Helper:\s*(.+?)\s*\|\s*Helpee:\s*(.+?)\s*\|\s*Context:\s*(.+?)(?:\n|$)',
    re.IGNORECASE | re.DOTALL
)

# Generic helpee patterns (get lower weight)
GENERIC_HELPEE_PATTERNS = [
    "multiple users", "community members", "several people", "several users",
    "community", "multiple", "channel members", "the community", "users"
]

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(levelname)s - %(message)s')


def get_channel_weight(channel_name: str) -> float:
    """Get the weight for a given channel name."""
    # Try exact match first
    if channel_name in CHANNEL_WEIGHTS:
        return CHANNEL_WEIGHTS[channel_name]

    # Try case-insensitive match
    channel_lower = channel_name.lower()
    for known_channel, weight in CHANNEL_WEIGHTS.items():
        if known_channel.lower() == channel_lower:
            return weight

    # Try substring match (for emoji variants)
    for known_channel, weight in CHANNEL_WEIGHTS.items():
        if known_channel in channel_name or channel_name in known_channel:
            return weight

    return DEFAULT_CHANNEL_WEIGHT


def get_temporal_weight(date_str: str) -> float:
    """Get temporal weight based on date (pre/post North Star transition)."""
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        transition = datetime.strptime(NORTH_STAR_TRANSITION_DATE, "%Y-%m-%d")

        if date >= transition:
            return TEMPORAL_WEIGHT_POST_NORTH_STAR
        else:
            return TEMPORAL_WEIGHT_PRE_NORTH_STAR
    except ValueError:
        logging.warning(f"Invalid date format: {date_str}, using default weight")
        return TEMPORAL_WEIGHT_PRE_NORTH_STAR


def normalize_username(name: str) -> str:
    """Normalize username for consistency."""
    return name.strip().lower()


def is_generic_helpee(helpee: str) -> bool:
    """Check if helpee is a generic reference rather than specific user."""
    helpee_lower = helpee.lower().strip()
    return any(pattern in helpee_lower for pattern in GENERIC_HELPEE_PATTERNS)


def parse_help_section(summary: str, channel_name: str, channel_id: str, date_str: str) -> list[dict]:
    """
    Extract help interactions from Discord summary text.

    Returns list of interaction dicts with structure:
    {
        "date": "2025-01-15",
        "channel_id": "...",
        "channel_name": "discussion",
        "helper": "jin",
        "helpee": "tomosman",
        "context": "...",
        "resolution": "...",
        "is_generic_helpee": false,
        "weights": {
            "channel": 1.0,
            "temporal": 0.8,
            "helpee_modifier": 1.0,
            "combined": 0.8
        }
    }

    Note: helper and helpee are display names as captured from Discord.
    Username consistency should be handled upstream in Discord data.
    """
    interactions = []

    # Look for "## 3. Help Interactions" section
    help_section_pattern = r'##\s*3\.\s*Help Interactions.*?(?=##|\Z)'
    match = re.search(help_section_pattern, summary, re.IGNORECASE | re.DOTALL)

    if not match:
        logging.debug(f"No Help Interactions section found for {channel_name} on {date_str}")
        return []

    help_section = match.group(0)

    # Check for explicit "no help" message
    if "no significant help" in help_section.lower():
        return []

    # Try to parse each line with full pattern (all 4 fields)
    for match in HELP_PATTERN_FULL.finditer(help_section):
        helper = match.group(1).strip()
        helpee = match.group(2).strip()
        context = match.group(3).strip()
        resolution = match.group(4).strip()

        if not helper or not helpee:
            continue

        # Calculate weights
        channel_weight = get_channel_weight(channel_name)
        temporal_weight = get_temporal_weight(date_str)

        # Apply generic helpee modifier
        helpee_modifier = 0.5 if is_generic_helpee(helpee) else 1.0

        combined_weight = channel_weight * temporal_weight * helpee_modifier

        interactions.append({
            "date": date_str,
            "channel_id": channel_id,
            "channel_name": channel_name,
            "helper": helper,
            "helpee": helpee,
            "context": context,
            "resolution": resolution,
            "is_generic_helpee": is_generic_helpee(helpee),
            "weights": {
                "channel": channel_weight,
                "temporal": temporal_weight,
                "helpee_modifier": helpee_modifier,
                "combined": round(combined_weight, 3)
            }
        })

    # Try fallback pattern for entries missing resolution
    for match in HELP_PATTERN_NO_RESOLUTION.finditer(help_section):
        helper = match.group(1).strip()
        helpee = match.group(2).strip()
        context = match.group(3).strip()

        if not helper or not helpee:
            continue

        # Skip if already matched by full pattern
        if any(i["helper"] == helper and
               i["helpee"] == helpee and
               i["context"] == context
               for i in interactions):
            continue

        # Calculate weights
        channel_weight = get_channel_weight(channel_name)
        temporal_weight = get_temporal_weight(date_str)
        helpee_modifier = 0.5 if is_generic_helpee(helpee) else 1.0
        combined_weight = channel_weight * temporal_weight * helpee_modifier

        interactions.append({
            "date": date_str,
            "channel_id": channel_id,
            "channel_name": channel_name,
            "helper": helper,
            "helpee": helpee,
            "context": context,
            "resolution": "Unanswered",
            "is_generic_helpee": is_generic_helpee(helpee),
            "weights": {
                "channel": channel_weight,
                "temporal": temporal_weight,
                "helpee_modifier": helpee_modifier,
                "combined": round(combined_weight, 3)
            }
        })

    return interactions


def process_discord_file(file_path: Path, date_str: str) -> tuple[list[dict], list[str]]:
    """
    Process a single Discord JSON file.

    Returns:
        (interactions, errors) - list of interactions and list of error messages
    """
    interactions = []
    errors = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        categories = data.get("categories", [])

        for category in categories:
            channel_id = category.get("channelId", "")
            channel_name = category.get("channelName", "unknown")
            summary = category.get("summary", "")

            if not summary:
                continue

            try:
                channel_interactions = parse_help_section(summary, channel_name, channel_id, date_str)
                interactions.extend(channel_interactions)
            except Exception as e:
                error_msg = f"Error parsing {channel_name} on {date_str}: {e}"
                errors.append(error_msg)
                logging.warning(error_msg)

    except FileNotFoundError:
        error_msg = f"File not found: {file_path}"
        errors.append(error_msg)
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in {file_path}: {e}"
        errors.append(error_msg)
        logging.error(error_msg)
    except Exception as e:
        error_msg = f"Error processing {file_path}: {e}"
        errors.append(error_msg)
        logging.error(error_msg)

    return interactions, errors


def get_month_dates(year: int, month: int) -> tuple[str, str, list[str]]:
    """Get first day, last day, and all dates for a given month."""
    first_day = datetime(year, month, 1)
    last_day_num = monthrange(year, month)[1]
    last_day = datetime(year, month, last_day_num)

    all_dates = []
    current = first_day
    while current <= last_day:
        all_dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    return first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d"), all_dates


def extract_month_interactions(year: int, month: int) -> dict:
    """
    Extract all help interactions for a given month.

    Returns structured output with interactions and metadata.
    """
    month_name = datetime(year, month, 1).strftime("%B %Y")
    logging.info(f"Extracting help interactions for {month_name}")

    first_day, last_day, all_dates = get_month_dates(year, month)
    logging.info(f"Processing {len(all_dates)} days: {first_day} to {last_day}")

    all_interactions = []
    days_with_data = []
    days_missing = []
    all_errors = []
    channels_seen = set()

    for date_str in all_dates:
        file_path = DISCORD_JSON_DIR / f"{date_str}.json"

        if not file_path.exists():
            days_missing.append(date_str)
            logging.debug(f"No data for {date_str}")
            continue

        interactions, errors = process_discord_file(file_path, date_str)

        if interactions:
            days_with_data.append(date_str)
            all_interactions.extend(interactions)
            channels_seen.update(i["channel_name"] for i in interactions)

        all_errors.extend(errors)

    # Calculate statistics
    helper_counts = defaultdict(int)
    helpee_counts = defaultdict(int)
    channel_counts = defaultdict(int)

    for interaction in all_interactions:
        helper_counts[interaction["helper"]] += 1
        if not interaction["is_generic_helpee"]:
            helpee_counts[interaction["helpee"]] += 1
        channel_counts[interaction["channel_name"]] += 1

    # Build output
    output = {
        "month": f"{year}-{month:02d}",
        "date_range": {
            "start": first_day,
            "end": last_day
        },
        "interactions": all_interactions,
        "_metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
            "days_processed": len(all_dates),
            "days_with_data": len(days_with_data),
            "days_missing": days_missing,
            "total_interactions": len(all_interactions),
            "unique_helpers": len(helper_counts),
            "unique_helpees": len(helpee_counts),
            "channels_tracked": sorted(channels_seen),
            "channel_distribution": dict(channel_counts),
            "north_star_transition": NORTH_STAR_TRANSITION_DATE,
            "parse_errors": len(all_errors),
            "error_details": all_errors[:10] if all_errors else []  # First 10 errors
        }
    }

    logging.info(f"Extracted {len(all_interactions)} interactions from {len(days_with_data)} days")
    logging.info(f"Unique helpers: {len(helper_counts)}, Unique helpees: {len(helpee_counts)}")
    logging.info(f"Channels: {sorted(channels_seen)}")

    if all_errors:
        logging.warning(f"Encountered {len(all_errors)} parse errors (see metadata for details)")

    return output


def main():
    parser = argparse.ArgumentParser(
        description="Extract help interactions from Discord JSON files with weighted scoring"
    )
    parser.add_argument(
        "-y", "--year",
        type=int,
        help="Year to process (default: previous month's year)"
    )
    parser.add_argument(
        "-m", "--month",
        type=int,
        help="Month to process (1-12, default: previous month)"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file path (default: the-council/help-reports/YYYY-MM-interactions.json)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be processed without writing output"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose debug logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Default to previous month
    today = datetime.now()
    if args.year and args.month:
        target_year, target_month = args.year, args.month
    else:
        first_of_this_month = today.replace(day=1)
        last_month = first_of_this_month - timedelta(days=1)
        target_year, target_month = last_month.year, last_month.month

    month_name = datetime(target_year, target_month, 1).strftime("%B %Y")

    if args.dry_run:
        print(f"\nDry run for {month_name}:")
        print(f"  Would process: {DISCORD_JSON_DIR / f'{target_year}-{target_month:02d}-*.json'}")
        first_day, last_day, all_dates = get_month_dates(target_year, target_month)
        print(f"  Date range: {first_day} to {last_day} ({len(all_dates)} days)")

        # Count available files
        available = sum(1 for d in all_dates if (DISCORD_JSON_DIR / f"{d}.json").exists())
        print(f"  Files available: {available}/{len(all_dates)}")
        return

    # Extract interactions
    result = extract_month_interactions(target_year, target_month)

    # Determine output path
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = args.output or OUTPUT_DIR / f"{target_year}-{target_month:02d}-interactions.json"

    # Write output
    logging.info(f"Writing output to {output_file}")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=True)
        logging.info(f"Successfully wrote {len(result['interactions'])} interactions to {output_file}")
    except Exception as e:
        logging.error(f"Error writing output file: {e}")
        sys.exit(1)

    # Print summary
    metadata = result["_metadata"]
    print(f"\n{'='*60}")
    print(f"Help Interaction Extraction: {month_name}")
    print(f"{'='*60}")
    print(f"Date range: {result['date_range']['start']} to {result['date_range']['end']}")
    print(f"Days processed: {metadata['days_processed']}")
    print(f"Days with data: {metadata['days_with_data']}")
    print(f"Days missing: {len(metadata['days_missing'])}")
    print(f"\nInteractions extracted: {metadata['total_interactions']}")
    print(f"Unique helpers: {metadata['unique_helpers']}")
    print(f"Unique helpees: {metadata['unique_helpees']}")
    print(f"\nChannels tracked: {', '.join(metadata['channels_tracked'])}")
    print(f"\nChannel distribution:")
    for channel, count in sorted(metadata['channel_distribution'].items(), key=lambda x: -x[1]):
        print(f"  {channel}: {count}")

    if metadata['parse_errors'] > 0:
        print(f"\nWarning: {metadata['parse_errors']} parse errors encountered")
        print("  See _metadata.error_details in output JSON for details")

    print(f"\nOutput: {output_file}")


if __name__ == "__main__":
    main()
