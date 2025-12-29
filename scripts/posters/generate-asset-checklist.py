#!/usr/bin/env python3
"""
Generate asset checklist comparing entity inventory to existing assets.

Usage:
  python scripts/posters/generate-asset-checklist.py
  python scripts/posters/generate-asset-checklist.py -o scripts/posters/assets/asset-checklist.md
"""

import json
import argparse
import re
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.resolve()
ASSETS_DIR = SCRIPT_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
ENTITY_INVENTORY = ASSETS_DIR / "manifest.json"


def get_all_assets() -> set:
    """Get lowercase names of ALL existing assets (flat directory structure)."""
    assets = set()
    if not ICONS_DIR.exists():
        return assets
    for f in ICONS_DIR.iterdir():
        if f.is_file() and not f.name.startswith('_'):
            # Strip numbered suffix: "discord-1.png" -> "discord"
            stem = f.stem.lower()
            # Remove trailing -N suffix
            match = re.match(r'^(.+?)-\d+$', stem)
            if match:
                assets.add(match.group(1))
            else:
                assets.add(stem)
    return assets


def entity_matches_asset(entity: str, assets: set) -> bool:
    """Check if entity has a matching asset using fuzzy containment."""
    e = entity.lower()
    # Direct match
    if e in assets:
        return True
    # Check if any asset name is contained in entity
    for a in assets:
        if len(a) >= 2 and a in e:
            return True
    return False


def get_existing_assets(entity_type: str, all_assets: set = None) -> set:
    """Get asset names for an entity type.

    With flat icon directory, all types share the same asset pool.
    Type prefixes (token-, user-) are stripped by get_all_assets().
    """
    # All types now share the flat icons directory
    return all_assets if all_assets else set()


def load_entities() -> dict:
    """Load entities from manifest (flat list with type field).

    New schema: {"entities": [{"name": "Bitcoin", "type": "token", ...}]}
    Groups entities by type and returns: {"token": {"bitcoin": "Bitcoin"}, ...}
    """
    with open(ENTITY_INVENTORY) as f:
        data = json.load(f)

    result = {}
    entities = data.get("entities", [])

    for entity in entities:
        if not isinstance(entity, dict):
            continue
        name = entity.get("name", "")
        entity_type = entity.get("type", "project")
        status = entity.get("status", "keep")

        # Skip entities marked as skip or review
        if status in ("skip", "review"):
            continue

        if entity_type not in result:
            result[entity_type] = {}

        # Dedupe by lowercase, keep original for display
        key = name.lower()
        if key not in result[entity_type]:
            result[entity_type][key] = name

    return result


def generate_checklist() -> str:
    """Generate markdown checklist."""
    entities = load_entities()
    all_assets = get_all_assets()

    lines = [
        "# Asset Library Checklist",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Coverage Summary",
        ""
    ]

    # Entity types in the new schema
    entity_types = ["token", "project", "user"]

    # Calculate coverage for each type
    coverage = {}
    for entity_type in entity_types:
        entity_set = entities.get(entity_type, {})
        assets = get_existing_assets(entity_type, all_assets)

        # Count matches using fuzzy containment
        have = sum(1 for entity in entity_set.values() if entity_matches_asset(entity, assets))
        total = len(entity_set)
        pct = (have / total * 100) if total > 0 else 0

        coverage[entity_type] = {"have": have, "total": total, "pct": pct, "assets": assets}
        lines.append(f"- **{entity_type.title()}**: {have}/{total} ({pct:.0f}%)")

    lines.append("")

    # Generate detailed checklist for tokens (smaller set)
    for entity_type in ["token"]:
        entity_set = entities.get(entity_type, {})
        assets = coverage[entity_type]["assets"]

        lines.append(f"## {entity_type.title()}s")
        lines.append("")

        # Sort by status (have first), then alphabetically
        items = []
        for key, display in entity_set.items():
            have = entity_matches_asset(display, assets)
            items.append((have, display))

        items.sort(key=lambda x: (not x[0], x[1].lower()))

        for have, display in items:
            check = "x" if have else " "
            lines.append(f"- [{check}] {display}")

        lines.append("")

    # Projects and users are large - just show summary
    for entity_type in ["project", "user"]:
        entity_set = entities.get(entity_type, {})
        assets = coverage[entity_type]["assets"]
        have_count = coverage[entity_type]["have"]

        lines.append(f"## {entity_type.title()}s")
        lines.append("")
        lines.append(f"*{len(entity_set)} entities, {have_count} with assets*")
        lines.append("")

        # Show only items we have assets for
        items = [display for display in entity_set.values() if entity_matches_asset(display, assets)]
        if items:
            lines.append("### Have:")
            for display in sorted(items, key=str.lower)[:50]:  # Limit to 50
                lines.append(f"- [x] {display}")
            if len(items) > 50:
                lines.append(f"- ... and {len(items) - 50} more")
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate asset checklist")
    parser.add_argument("-o", "--output", type=Path, default=ASSETS_DIR / "asset-checklist.md",
                        help="Output file path")
    args = parser.parse_args()

    checklist = generate_checklist()

    args.output.write_text(checklist)
    print(f"Checklist written to {args.output}")

    # Also print summary
    print("\n" + checklist.split("## Tokens")[0])


if __name__ == "__main__":
    main()
