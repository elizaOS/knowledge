#!/usr/bin/env python3
"""
Generate asset checklist comparing entity inventory to existing assets.

Usage:
  python scripts/posters/generate-asset-checklist.py
  python scripts/posters/generate-asset-checklist.py -o scripts/posters/assets/asset-checklist.md
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.resolve()
ASSETS_DIR = SCRIPT_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
ENTITY_INVENTORY = ASSETS_DIR / "manifest.json"


def get_all_assets() -> set:
    """Get lowercase names of ALL existing assets across all folders."""
    assets = set()
    for cat_dir in ICONS_DIR.iterdir():
        if cat_dir.is_dir():
            for f in cat_dir.iterdir():
                if f.is_file():
                    assets.add(f.stem.lower())
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


def get_existing_assets(category: str, all_assets: set = None) -> set:
    """Get asset names for a category.

    For tech/projects, check all_assets since icons may exist in other folders.
    """
    SHARED_CATEGORIES = {"tech", "projects"}

    if category in SHARED_CATEGORIES and all_assets:
        return all_assets

    cat_dir = ICONS_DIR / category
    if not cat_dir.exists():
        return all_assets if all_assets else set()

    assets = set()
    for f in cat_dir.iterdir():
        if f.is_file():
            assets.add(f.stem.lower())
    return assets


def load_entities() -> dict:
    """Load entities from inventory (simple array format)."""
    with open(ENTITY_INVENTORY) as f:
        data = json.load(f)

    result = {}
    for category, items in data.get("entities", {}).items():
        # Dedupe by lowercase, keep original for display
        seen = {}
        for item in items:
            key = item.lower()
            if key not in seen:
                seen[key] = item
        result[category] = seen
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

    # Calculate coverage for each category
    coverage = {}
    for category in ["tokens", "platforms", "tech", "projects", "plugins"]:
        entity_set = entities.get(category, {})
        assets = get_existing_assets(category, all_assets)

        # Count matches using fuzzy containment
        have = sum(1 for entity in entity_set.values() if entity_matches_asset(entity, assets))
        total = len(entity_set)
        pct = (have / total * 100) if total > 0 else 0

        coverage[category] = {"have": have, "total": total, "pct": pct, "assets": assets}
        lines.append(f"- **{category.title()}**: {have}/{total} ({pct:.0f}%)")

    lines.append("")

    # Generate checklist for each category
    for category in ["tokens", "platforms", "plugins"]:
        entity_set = entities.get(category, {})
        assets = coverage[category]["assets"]

        lines.append(f"## {category.title()}")
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

    # Tech and projects are large - just show summary
    for category in ["tech", "projects"]:
        entity_set = entities.get(category, {})
        assets = coverage[category]["assets"]
        have_count = coverage[category]["have"]

        lines.append(f"## {category.title()}")
        lines.append("")
        lines.append(f"*{len(entity_set)} entities, {have_count} with assets*")
        lines.append("")

        # Show only items we have assets for
        items = [display for display in entity_set.values() if entity_matches_asset(display, assets)]
        if items:
            lines.append("### Have:")
            for display in sorted(items, key=str.lower):
                lines.append(f"- [x] {display}")
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
