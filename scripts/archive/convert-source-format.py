#!/usr/bin/env python3
"""
Convert old source format to new file path format in facts JSON files.

Old: ai_news_elizaos_daily_json_2025-12-23.content.categories[3].content[0].text
New: ai-news/elizaos/json/2025-12-23.json

Usage:
  python scripts/etl/convert-source-format.py                    # Fix all facts files
  python scripts/etl/convert-source-format.py --dry-run          # Preview changes
  python scripts/etl/convert-source-format.py -f 2025-12-24.json # Single file
"""

import argparse
import json
import re
from pathlib import Path

# Mapping from old key prefixes to new file paths
SOURCE_MAPPINGS = [
    # Order matters - more specific patterns first
    (r"ai_news_elizaos_daily_discord_json_(\d{4}-\d{2}-\d{2})", r"ai-news/elizaos/discord/json/\1.json"),
    (r"ai_news_elizaos_daily_discord_md_(\d{4}-\d{2}-\d{2})", r"ai-news/elizaos/discord/md/\1.md"),
    (r"ai_news_elizaos_discord_json_(\d{4}-\d{2}-\d{2})", r"ai-news/elizaos/discord/json/\1.json"),
    (r"ai_news_elizaos_discord_md_(\d{4}-\d{2}-\d{2})", r"ai-news/elizaos/discord/md/\1.md"),
    (r"ai_news_elizaos_daily_json_(\d{4}-\d{2}-\d{2})", r"ai-news/elizaos/json/\1.json"),
    (r"ai_news_elizaos_daily_md_(\d{4}-\d{2}-\d{2})", r"ai-news/elizaos/md/\1.md"),
    (r"ai_news_elizaos_json_(\d{4}-\d{2}-\d{2})", r"ai-news/elizaos/json/\1.json"),
    (r"ai_news_elizaos_md_(\d{4}-\d{2}-\d{2})", r"ai-news/elizaos/md/\1.md"),
    (r"github_summaries_daily_(\d{4}-\d{2}-\d{2})", r"github/summaries/day/\1.md"),
    (r"github_summaries_week_latest_(\d{4}-\d{2}-\d{2})\.md", r"github/summaries/week/\1.md"),
    (r"github_summaries_month_latest_(\d{4}-\d{2}-\d{2})\.md", r"github/summaries/month/\1.md"),
]


def convert_source(source_str: str) -> str:
    """Convert a single source string from old to new format."""
    # Strip any .content.* suffix (JSON path details)
    base = re.sub(r"\.content.*$", "", source_str)

    for pattern, replacement in SOURCE_MAPPINGS:
        if re.match(pattern, base):
            return re.sub(pattern, replacement, base)

    # Return original if no match (might already be new format)
    return source_str


def process_value(value):
    """Recursively process a value, converting source fields."""
    if isinstance(value, dict):
        result = {}
        for k, v in value.items():
            if k == "source":
                if isinstance(v, list):
                    result[k] = [convert_source(s) for s in v]
                elif isinstance(v, str):
                    result[k] = convert_source(v)
                else:
                    result[k] = v
            else:
                result[k] = process_value(v)
        return result
    elif isinstance(value, list):
        return [process_value(item) for item in value]
    else:
        return value


def convert_file(file_path: Path, dry_run: bool = False) -> tuple[bool, int]:
    """Convert source formats in a facts file. Returns (changed, count)."""
    with open(file_path) as f:
        original = f.read()
        data = json.loads(original)

    # Check if file has old format
    if "ai_news_elizaos_" not in original:
        return False, 0

    # Count old format occurrences before
    old_count = original.count("ai_news_elizaos_")

    # Process the data
    converted = process_value(data)
    new_json = json.dumps(converted, indent=2, ensure_ascii=True)

    # Count remaining old format (should be 0)
    remaining = new_json.count("ai_news_elizaos_")
    converted_count = old_count - remaining

    if dry_run:
        print(f"  Would convert {converted_count} sources ({remaining} remaining)")
        return True, converted_count

    # Write back
    with open(file_path, 'w') as f:
        f.write(new_json)

    return True, converted_count


def main():
    parser = argparse.ArgumentParser(description="Convert old source format to file paths")
    parser.add_argument("-f", "--file", type=Path, help="Single file to convert")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--dir", type=Path, default=Path("the-council/facts"),
                        help="Directory to process (default: the-council/facts)")
    args = parser.parse_args()

    if args.file:
        files = [args.file]
    else:
        files = sorted(args.dir.glob("*.json"))
        files = [f for f in files if f.name != "daily.json"]

    print(f"Processing {len(files)} files..." + (" (dry run)" if args.dry_run else ""))

    changed = 0
    total_converted = 0

    for f in files:
        was_changed, count = convert_file(f, args.dry_run)
        if was_changed:
            changed += 1
            total_converted += count
            print(f"  {f.name}: {count} sources converted")

    print(f"\nDone: {changed} files updated, {total_converted} total sources converted")


if __name__ == "__main__":
    main()
