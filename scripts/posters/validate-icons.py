#!/usr/bin/env python3
"""
Validate downloaded icons are valid images with minimum quality.

Usage:
  python scripts/posters/validate-icons.py
  python scripts/posters/validate-icons.py --fix  # Remove invalid icons
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow required. Install with: pip install Pillow")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent.resolve()
ICONS_DIR = SCRIPT_DIR / "assets" / "icons"
MIN_SIZE = 64  # minimum 64x64


def validate_icons(fix: bool = False) -> bool:
    """Validate all icons and optionally remove invalid ones."""
    errors = []
    valid_count = 0

    for category_dir in ICONS_DIR.iterdir():
        if not category_dir.is_dir():
            continue

        for icon in category_dir.iterdir():
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
                        errors.append(f"{category_dir.name}/{icon.name}: too small ({width}x{height})")
                        if fix:
                            icon.unlink()
                            print(f"  Removed: {icon.name}")
                    else:
                        valid_count += 1

            except Exception as e:
                errors.append(f"{category_dir.name}/{icon.name}: invalid - {e}")
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


def main():
    parser = argparse.ArgumentParser(description="Validate icon files")
    parser.add_argument("--fix", action="store_true", help="Remove invalid icons")
    args = parser.parse_args()

    success = validate_icons(fix=args.fix)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
