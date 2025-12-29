#!/usr/bin/env python3
"""
Validate downloaded icons and sync icon_paths to manifest.json.

Usage:
  python scripts/posters/validate-icons.py                  # Validate + sync inventory
  python scripts/posters/validate-icons.py --fix            # Remove invalid + sync
  python scripts/posters/validate-icons.py --sync-only      # Just sync inventory (no validation)
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


def main():
    parser = argparse.ArgumentParser(description="Validate icons and sync inventory")
    parser.add_argument("--fix", action="store_true", help="Remove invalid icons")
    parser.add_argument("--sync-only", action="store_true", help="Only sync inventory (skip validation)")
    args = parser.parse_args()

    success = True

    # Validate icons (unless --sync-only)
    if not args.sync_only:
        success = validate_icons(fix=args.fix)

    # Always sync inventory
    sync_inventory_icons()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
