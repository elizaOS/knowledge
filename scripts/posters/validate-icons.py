#!/usr/bin/env python3
"""
Validate downloaded icons and sync icon_paths to manifest.json.

Usage:
  python scripts/posters/validate-icons.py                  # Validate + sync inventory
  python scripts/posters/validate-icons.py --fix            # Remove invalid + sync
  python scripts/posters/validate-icons.py --sync-only      # Just sync inventory (no validation)
  python scripts/posters/validate-icons.py --stats          # Show coverage statistics
  python scripts/posters/validate-icons.py --stats -o coverage.md  # Save stats to file
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow required. Install with: pip install Pillow")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent.resolve()
ASSETS_DIR = SCRIPT_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
ENTITY_INVENTORY = ASSETS_DIR / "manifest.json"
MIN_SIZE = 64  # minimum 64x64
ENTITY_TYPES = ["token", "project", "user"]


def validate_icons(fix: bool = False) -> bool:
    """Validate all icons and optionally remove invalid ones."""
    errors = []
    valid_count = 0

    for icon in ICONS_DIR.iterdir():
        if not icon.is_file():
            continue

        # Skip non-image files
        if icon.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.svg'):
            continue

        # SVG files can't be validated with PIL
        if icon.suffix.lower() == '.svg':
            valid_count += 1
            continue

        try:
            with Image.open(icon) as img:
                width, height = img.size

                if width < MIN_SIZE or height < MIN_SIZE:
                    errors.append(f"{icon.name}: too small ({width}x{height})")
                    if fix:
                        icon.unlink()
                        print(f"  Removed: {icon.name}")
                else:
                    valid_count += 1

        except Exception as e:
            errors.append(f"{icon.name}: invalid - {e}")
            if fix:
                icon.unlink()
                print(f"  Removed: {icon.name}")

    if errors:
        print(f"Validation {'fixed' if fix else 'FAILED'}:")
        for e in errors:
            print(f"  - {e}")
        print(f"\n{valid_count} valid, {len(errors)} invalid")
        return fix  # Return True if we fixed them

    print(f"OK: {valid_count} icons validated")
    return True


def slugify(name: str) -> str:
    """Convert name to filename-safe slug."""
    return name.lower().replace(" ", "-").replace(".", "-").lstrip("$@")


def matches_slug(stem: str, slug: str, type_prefix: str = "") -> bool:
    """Check if icon stem matches a slug (exact or with number suffix).

    Matches:
      - "discord" matches slug "discord"
      - "discord-1" matches slug "discord"
      - "token-bitcoin" matches slug "bitcoin" with prefix "token-"
      - "token-bitcoin-2" matches slug "bitcoin" with prefix "token-"

    Does NOT match:
      - "autonome" does NOT match slug "auto"
      - "discord-alt" does NOT match slug "discord" (use alias instead)
    """
    # Exact match or match with number suffix
    patterns = [
        slug,                           # discord
        f"{slug}-",                      # discord- (has number after)
        f"{type_prefix}{slug}",          # token-bitcoin
        f"{type_prefix}{slug}-",         # token-bitcoin-
    ]

    for pattern in patterns:
        if stem == pattern.rstrip("-"):
            return True
        if stem.startswith(pattern) and (len(stem) == len(pattern) or stem[len(pattern):].isdigit() or
                                          (stem[len(pattern):].startswith("-") and stem[len(pattern)+1:].replace("-", "").isdigit())):
            return True

    return False


def find_icons_for_entity(entity: dict, all_icons: list[str]) -> list[str]:
    """Find all icons matching entity (by name/aliases).

    Matching rules:
      - Exact match: "discord.jpg" matches entity "Discord"
      - With number: "token-bitcoin-1.png" matches entity "Bitcoin" (type=token)
      - Via alias: "btc.jpg" matches entity "Bitcoin" if "BTC" is an alias

    Does NOT match partial words (e.g., "autonome" won't match "auto")
    """
    matches = []
    entity_type = entity.get("type", "")
    name_slug = slugify(entity["name"])
    type_prefix = f"{entity_type}-" if entity_type else ""

    # Collect all slugs to check (name + aliases)
    slugs_to_check = [name_slug]
    for alias in entity.get("aliases", []):
        alias_slug = slugify(alias)
        if len(alias_slug) >= 2 and alias_slug not in slugs_to_check:
            slugs_to_check.append(alias_slug)

    for icon in all_icons:
        stem = Path(icon).stem.lower()

        for slug in slugs_to_check:
            if matches_slug(stem, slug, type_prefix):
                if icon not in matches:
                    matches.append(icon)
                break

    return sorted(matches)


def sync_inventory_icons() -> dict:
    """Sync icon_paths in manifest.json with actual files."""
    if not ENTITY_INVENTORY.exists():
        print(f"Warning: Entity inventory not found: {ENTITY_INVENTORY}")
        return {}

    with open(ENTITY_INVENTORY) as f:
        inventory = json.load(f)

    # Get all icon files
    all_icons = [f.name for f in ICONS_DIR.iterdir()
                 if f.is_file() and f.suffix.lower() in ('.png', '.jpg', '.jpeg')]

    entities_with_icons = 0
    total_icon_matches = 0

    for entity in inventory.get("entities", []):
        # Find all matching icons
        matches = find_icons_for_entity(entity, all_icons)

        if matches:
            entity["icon_paths"] = [f"icons/{m}" for m in matches]
            entities_with_icons += 1
            total_icon_matches += len(matches)
        else:
            # Remove icon_paths if no icons found (handles deletions)
            entity.pop("icon_paths", None)

    # Write updated inventory
    with open(ENTITY_INVENTORY, "w") as f:
        json.dump(inventory, f, indent=2)

    print(f"Synced: {entities_with_icons} entities have icons ({total_icon_matches} total icon files)")
    return inventory


def show_coverage_stats(output_path: Path = None):
    """Show icon coverage statistics by entity type."""
    if not ENTITY_INVENTORY.exists():
        print(f"Error: Entity inventory not found: {ENTITY_INVENTORY}")
        return

    with open(ENTITY_INVENTORY) as f:
        inventory = json.load(f)

    entities = inventory.get("entities", [])

    # Group by type
    by_type = {t: [] for t in ENTITY_TYPES}
    for entity in entities:
        if not isinstance(entity, dict):
            continue
        status = entity.get("status", "keep")
        if status in ("skip", "review"):
            continue
        entity_type = entity.get("type", "project")
        if entity_type in by_type:
            by_type[entity_type].append(entity)

    lines = ["## Icon Coverage", ""]

    total_entities = 0
    total_with_icons = 0

    for entity_type in ENTITY_TYPES:
        type_entities = by_type[entity_type]
        with_icons = sum(1 for e in type_entities if e.get("icon_paths"))
        total = len(type_entities)
        pct = (with_icons / total * 100) if total > 0 else 0

        total_entities += total
        total_with_icons += with_icons

        lines.append(f"- **{entity_type.title()}**: {with_icons}/{total} ({pct:.0f}%)")

    # Overall
    overall_pct = (total_with_icons / total_entities * 100) if total_entities > 0 else 0
    lines.extend(["", f"**Total**: {total_with_icons}/{total_entities} ({overall_pct:.0f}%)"])

    # Detailed checklist for tokens (smaller set, show all)
    lines.extend(["", "### Tokens", ""])
    token_items = []
    for e in by_type.get("token", []):
        has_icon = bool(e.get("icon_paths"))
        token_items.append((has_icon, e["name"]))
    token_items.sort(key=lambda x: (not x[0], x[1].lower()))  # Have first, then alpha
    for has_icon, name in token_items:
        check = "x" if has_icon else " "
        lines.append(f"- [{check}] {name}")

    # Projects and users - just summary stats (too many to list)
    for entity_type in ["project", "user"]:
        type_entities = by_type.get(entity_type, [])
        have_count = sum(1 for e in type_entities if e.get("icon_paths"))
        missing_count = len(type_entities) - have_count

        lines.extend(["", f"### {entity_type.title()}s", ""])
        lines.append(f"- Have: {have_count}")
        lines.append(f"- Missing: {missing_count}")

    output = "\n".join(lines)
    print(output)

    # Write to file if path specified
    if output_path:
        output_path.write_text(output)
        print(f"\nWritten to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Validate icons and sync inventory")
    parser.add_argument("--fix", action="store_true", help="Remove invalid icons")
    parser.add_argument("--sync-only", action="store_true", help="Only sync inventory (skip validation)")
    parser.add_argument("--stats", action="store_true", help="Show coverage statistics")
    parser.add_argument("-o", "--output", type=Path, help="Output markdown file for --stats")
    args = parser.parse_args()

    # Stats mode - just show coverage
    if args.stats:
        show_coverage_stats(output_path=args.output)
        sys.exit(0)

    success = True

    # Validate icons (unless --sync-only)
    if not args.sync_only:
        success = validate_icons(fix=args.fix)

    # Always sync inventory
    sync_inventory_icons()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
