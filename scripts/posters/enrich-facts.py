#!/usr/bin/env python3
"""
Enrich facts.json with CDN image URLs.

Adds an 'images' field to facts files with URLs to illustrations on cdn.elizaos.news.

Usage:
  # Enrich a specific facts file
  python scripts/posters/enrich-facts.py the-council/facts/2025-05-15.json

  # Dry run - show what would be added
  python scripts/posters/enrich-facts.py the-council/facts/2025-05-15.json --dry-run

  # Output to different file
  python scripts/posters/enrich-facts.py the-council/facts/2025-05-15.json -o enriched.json
"""

import json
import argparse
from pathlib import Path

# CDN config
DEFAULT_CDN_BASE = "https://cdn.elizaos.news"
CDN_FOLDER_PREFIX = "posters"

# Map categories to image filenames
IMAGE_CATEGORIES = {
    "overall.png": "overall",
    "github-updates.png": "github_updates",
    "discord-updates.png": "discord_updates",
    "strategic-insights.png": "strategic_insights",
    "market-analysis.png": "market_analysis",
    "icons.png": "icons",
}


def enrich_facts(facts_path: Path) -> dict:
    """Add CDN image URLs to facts data."""
    with open(facts_path) as f:
        facts = json.load(f)

    date_str = facts.get("briefing_date", facts_path.stem)

    # Build CDN URLs for standard image set
    # CDN structure: {cdn_base}/posters/{date}/{filename}
    images = {}
    for filename, category in IMAGE_CATEGORIES.items():
        images[category] = f"{DEFAULT_CDN_BASE}/{CDN_FOLDER_PREFIX}/{date_str}/{filename}"

    facts["images"] = images
    return facts


def main():
    parser = argparse.ArgumentParser(
        description="Enrich facts.json with image paths",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument("facts", help="Path to facts.json file")
    parser.add_argument("-o", "--output", help="Output path (default: overwrite input)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be added")

    args = parser.parse_args()

    facts_path = Path(args.facts)
    if not facts_path.exists():
        print(f"Error: Facts file not found: {facts_path}")
        return 1

    # Enrich with CDN URLs
    enriched = enrich_facts(facts_path)

    if args.dry_run:
        print("Would add images:")
        for cat, url in enriched.get("images", {}).items():
            print(f"  {cat}: {url}")
        return 0

    # Save
    output_path = Path(args.output) if args.output else facts_path
    with open(output_path, "w") as f:
        json.dump(enriched, f, indent=2)

    print(f"Enriched: {output_path}")
    print(f"Added {len(enriched.get('images', {}))} image URLs")

    return 0


if __name__ == "__main__":
    exit(main())
