#!/usr/bin/env python3
"""
Convert old council briefing format to new format.

Old format:
  - strategic_context_summary → meeting_context
  - daily_focus_theme → daily_focus
  - key_strategic_points → key_points

Usage:
  python scripts/etl/convert-council-format.py                    # Fix all
  python scripts/etl/convert-council-format.py --dry-run          # Preview
  python scripts/etl/convert-council-format.py -f 2025-04-18.json # Single file
"""

import argparse
import json
from pathlib import Path

# Field mappings: old → new
FIELD_MAPPINGS = {
    "strategic_context_summary": "meeting_context",
    "daily_focus_theme": "daily_focus",
    "key_strategic_points": "key_points",
}


def convert_file(file_path: Path, dry_run: bool = False) -> tuple[bool, int]:
    """Convert old format to new format. Returns (changed, field_count)."""
    with open(file_path) as f:
        data = json.load(f)

    # Check if file has old format fields
    old_fields = [k for k in FIELD_MAPPINGS.keys() if k in data]
    if not old_fields:
        return False, 0

    if dry_run:
        print(f"  Would convert {len(old_fields)} fields: {old_fields}")
        return True, len(old_fields)

    # Convert fields
    for old_key, new_key in FIELD_MAPPINGS.items():
        if old_key in data:
            data[new_key] = data.pop(old_key)

    # Write back
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=True)

    return True, len(old_fields)


def main():
    parser = argparse.ArgumentParser(description="Convert old council format to new")
    parser.add_argument("-f", "--file", type=Path, help="Single file to convert")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--dir", type=Path, default=Path("the-council/council_briefing"),
                        help="Directory to process")
    args = parser.parse_args()

    if args.file:
        files = [args.file]
    else:
        files = sorted(args.dir.glob("*.json"))
        files = [f for f in files if f.name != "daily.json"]

    print(f"Processing {len(files)} files..." + (" (dry run)" if args.dry_run else ""))

    changed = 0
    total_fields = 0

    for f in files:
        was_changed, count = convert_file(f, args.dry_run)
        if was_changed:
            changed += 1
            total_fields += count
            print(f"  {f.name}: {count} fields converted")

    print(f"\nDone: {changed} files updated, {total_fields} total fields converted")


if __name__ == "__main__":
    main()
