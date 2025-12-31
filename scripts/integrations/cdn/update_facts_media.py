#!/usr/bin/env python3
"""
Update facts.json with media URLs from poster manifest.

Usage:
  # Update facts file with CDN URLs from manifest
  python scripts/integrations/cdn/update_facts_media.py \\
    --facts the-council/facts/2025-12-21.json \\
    --manifest posters/2025-12-21/manifest.json

  # Dry run
  python scripts/integrations/cdn/update_facts_media.py \\
    --facts the-council/facts/2025-12-21.json \\
    --manifest posters/2025-12-21/manifest.json \\
    --dry-run
"""

import argparse
import json
import sys
from pathlib import Path


def update_facts_with_media(
    facts_path: Path,
    manifest_path: Path,
    dry_run: bool = False,
) -> bool:
    """Update facts.json with media URLs from manifest.

    Adds a 'media' section to facts.json with poster URLs.

    Args:
        facts_path: Path to facts JSON file
        manifest_path: Path to poster manifest JSON file
        dry_run: If True, print changes without writing

    Returns:
        True if successful
    """
    # Load files
    try:
        with open(facts_path) as f:
            facts = json.load(f)
        with open(manifest_path) as f:
            manifest = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading files: {e}", file=sys.stderr)
        return False

    # Check for cdn_urls in manifest
    cdn_urls = manifest.get("cdn_urls", {})
    if not cdn_urls:
        print("No cdn_urls found in manifest. Run upload.py --update-manifest first.", file=sys.stderr)
        return False

    # Build media section
    media = {
        "posters": {},
        "generated_at": manifest.get("generated_at"),
        "source_manifest": str(manifest_path),
    }

    # Map category files to URLs
    for gen in manifest.get("generations", []):
        category = gen.get("category", "").replace("-", "_")
        output_file = gen.get("output_file")
        cdn_url = gen.get("cdn_url") or cdn_urls.get(output_file)

        if category and cdn_url:
            media["posters"][category] = cdn_url

    # Add icon sheet if present
    icon_sheet = manifest.get("icon_sheet")
    if icon_sheet:
        icon_file = icon_sheet.get("output_file")
        icon_url = icon_sheet.get("cdn_url") or cdn_urls.get(icon_file)
        if icon_url:
            media["posters"]["icon_sheet"] = icon_url

    # Update facts
    facts["media"] = media

    if dry_run:
        print("Would add to facts.json:")
        print(json.dumps({"media": media}, indent=2))
        return True

    # Write updated facts
    try:
        with open(facts_path, "w") as f:
            json.dump(facts, f, indent=2)
        print(f"Updated: {facts_path}")
        print(f"  Added {len(media['posters'])} poster URLs")
        return True
    except IOError as e:
        print(f"Error writing facts: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Update facts.json with media URLs from poster manifest",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--facts", "-f",
        type=Path,
        required=True,
        help="Path to facts JSON file",
    )
    parser.add_argument(
        "--manifest", "-m",
        type=Path,
        required=True,
        help="Path to poster manifest JSON file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show changes without writing",
    )

    args = parser.parse_args()

    if not args.facts.exists():
        print(f"Error: Facts file not found: {args.facts}", file=sys.stderr)
        sys.exit(1)

    if not args.manifest.exists():
        print(f"Error: Manifest file not found: {args.manifest}", file=sys.stderr)
        sys.exit(1)

    success = update_facts_with_media(args.facts, args.manifest, args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
