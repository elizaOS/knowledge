#!/usr/bin/env python3
"""
Create icon sheet montages for poster composition.

Multi-source icon lookup:
  1. Local manifest.json (entities with saved icons)
  2. selfhst/icons (2300+ self-hosted app icons)
  3. gilbarbara/logos (1000+ tech brand logos)
  4. Simple Icons (3000+ brand icons, API)

Usage:
  # From entity names
  python scripts/posters/utils/icon_sheet.py bitcoin ethereum discord -o tokens.png

  # From facts file (extract entities with icons)
  python scripts/posters/utils/icon_sheet.py -f the-council/facts/2025-12-14.json -o daily.png

  # Filter by entity type
  python scripts/posters/utils/icon_sheet.py -f facts.json -t token -o tokens.png

  # Show what icons would be included (dry run)
  python scripts/posters/utils/icon_sheet.py -f facts.json --dry-run

  # Output to stdout as base64
  python scripts/posters/utils/icon_sheet.py bitcoin ethereum --base64
"""

import argparse
import base64
import io
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

# Optional: cairosvg for SVG conversion
try:
    import cairosvg
    HAS_CAIROSVG = True
except ImportError:
    HAS_CAIROSVG = False

# Optional: rapidfuzz for fuzzy matching
try:
    from rapidfuzz import fuzz, process
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False

# Paths
SCRIPT_DIR = Path(__file__).parent.parent.resolve()
ASSETS_DIR = SCRIPT_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
MANIFEST_PATH = ASSETS_DIR / "manifest.json"

# External icon libraries (optional, via env vars)
SELFHST_ICONS_PATH = os.environ.get("SELFHST_ICONS_PATH", "")
GILBARBARA_LOGOS_PATH = os.environ.get("GILBARBARA_LOGOS_PATH", "")

# Sheet layout
CELL_WIDTH = 128
CELL_HEIGHT = 160  # 128 icon + 32 label
ICON_SIZE = 100
LABEL_HEIGHT = 32
COLS = 4
PADDING = 12
BG_COLOR = (255, 255, 255, 255)
LABEL_COLOR = (60, 60, 60)

# Fuzzy matching
FUZZY_THRESHOLD = 85


# =============================================================================
# Index Caches
# =============================================================================

_manifest_cache: dict = None
_selfhst_cache: list = None
_gilbarbara_cache: list = None


def load_manifest() -> dict:
    """Load and cache entity manifest."""
    global _manifest_cache
    if _manifest_cache is not None:
        return _manifest_cache

    if not MANIFEST_PATH.exists():
        _manifest_cache = {"entities": []}
        return _manifest_cache

    with open(MANIFEST_PATH) as f:
        _manifest_cache = json.load(f)
    return _manifest_cache


def load_selfhst_index() -> list:
    """Load and cache selfhst/icons index."""
    global _selfhst_cache
    if _selfhst_cache is not None:
        return _selfhst_cache

    if not SELFHST_ICONS_PATH:
        _selfhst_cache = []
        return _selfhst_cache

    index_path = Path(SELFHST_ICONS_PATH) / "index.json"
    if not index_path.exists():
        _selfhst_cache = []
        return _selfhst_cache

    try:
        _selfhst_cache = json.loads(index_path.read_text())
    except Exception:
        _selfhst_cache = []
    return _selfhst_cache


def load_gilbarbara_index() -> list:
    """Load and cache gilbarbara/logos index."""
    global _gilbarbara_cache
    if _gilbarbara_cache is not None:
        return _gilbarbara_cache

    if not GILBARBARA_LOGOS_PATH:
        _gilbarbara_cache = []
        return _gilbarbara_cache

    index_path = Path(GILBARBARA_LOGOS_PATH) / "logos.json"
    if not index_path.exists():
        _gilbarbara_cache = []
        return _gilbarbara_cache

    try:
        _gilbarbara_cache = json.loads(index_path.read_text())
    except Exception:
        _gilbarbara_cache = []
    return _gilbarbara_cache


# =============================================================================
# Icon Lookup
# =============================================================================

def slugify(name: str) -> str:
    """Convert name to lookup slug."""
    return name.lower().replace(" ", "-").replace(".", "-").lstrip("$@")


def svg_to_png(svg_bytes: bytes, size: int = 256) -> Optional[bytes]:
    """Convert SVG to PNG using cairosvg."""
    if not HAS_CAIROSVG:
        return None
    try:
        return cairosvg.svg2png(
            bytestring=svg_bytes,
            output_width=size,
            output_height=size
        )
    except Exception:
        return None


def normalize_icon(img: Image.Image, target_size: int = ICON_SIZE) -> Image.Image:
    """Normalize icon to consistent size with aspect ratio preserved.

    - Converts to RGBA
    - Fits within target_size x target_size
    - Centers on transparent background
    """
    img = img.convert("RGBA")

    # Resize to fit within target
    img.thumbnail((target_size, target_size), Image.LANCZOS)

    # Create centered canvas
    canvas = Image.new("RGBA", (target_size, target_size), (255, 255, 255, 0))
    x = (target_size - img.width) // 2
    y = (target_size - img.height) // 2
    canvas.paste(img, (x, y), img)

    return canvas


def find_icon_in_manifest(name: str, entity_type: str = None) -> Optional[tuple[str, Image.Image]]:
    """Find icon in local manifest by name/alias (exact or fuzzy)."""
    manifest = load_manifest()
    entities = manifest.get("entities", [])

    name_lower = name.lower().strip()

    # Build searchable list
    candidates = []
    for entity in entities:
        if entity.get("status") in ("skip", "review"):
            continue
        if not entity.get("icon_paths"):
            continue
        if entity_type and entity.get("type") != entity_type:
            continue

        ent_name = entity.get("name", "")
        candidates.append((ent_name.lower(), entity))
        for alias in entity.get("aliases", []):
            candidates.append((alias.lower(), entity))

    # Exact match first
    for key, entity in candidates:
        if key == name_lower:
            icon = load_icon_from_entity(entity)
            if icon:
                return (entity["name"], icon)

    # Fuzzy match if available
    if HAS_RAPIDFUZZ and candidates:
        keys = [c[0] for c in candidates]
        match = process.extractOne(name_lower, keys, scorer=fuzz.ratio)
        if match and match[1] >= FUZZY_THRESHOLD:
            for key, entity in candidates:
                if key == match[0]:
                    icon = load_icon_from_entity(entity)
                    if icon:
                        return (entity["name"], icon)

    return None


def load_icon_from_entity(entity: dict) -> Optional[Image.Image]:
    """Load first available icon for entity."""
    for icon_path in entity.get("icon_paths", []):
        full_path = ASSETS_DIR / icon_path
        if full_path.exists():
            try:
                return Image.open(full_path)
            except Exception:
                continue
    return None


def find_icon_in_selfhst(name: str) -> Optional[tuple[str, Image.Image]]:
    """Find icon in selfhst/icons by Name or Reference (exact or fuzzy)."""
    index = load_selfhst_index()
    if not index:
        return None

    name_lower = name.lower().strip()
    icons_dir = Path(SELFHST_ICONS_PATH)

    # Build searchable list
    candidates = []
    for entry in index:
        entry_name = entry.get("Name", "")
        entry_ref = entry.get("Reference", "")
        candidates.append((entry_name.lower(), entry))
        if entry_ref:
            candidates.append((entry_ref.lower(), entry))

    def try_load(entry):
        ref = entry.get("Reference", "")
        for variant in [f"{ref}.png", f"{ref}-light.png"]:
            png_path = icons_dir / "png" / variant
            if png_path.exists():
                try:
                    return Image.open(png_path)
                except Exception:
                    pass
        return None

    # Exact match first
    for key, entry in candidates:
        if key == name_lower:
            icon = try_load(entry)
            if icon:
                return (entry["Name"], icon)

    # Fuzzy match
    if HAS_RAPIDFUZZ and candidates:
        keys = list(set(c[0] for c in candidates))
        match = process.extractOne(name_lower, keys, scorer=fuzz.ratio)
        if match and match[1] >= FUZZY_THRESHOLD:
            for key, entry in candidates:
                if key == match[0]:
                    icon = try_load(entry)
                    if icon:
                        return (entry["Name"], icon)

    return None


def find_icon_in_gilbarbara(name: str) -> Optional[tuple[str, Image.Image]]:
    """Find icon in gilbarbara/logos by name or shortname (exact or fuzzy)."""
    logos = load_gilbarbara_index()
    if not logos:
        return None

    name_lower = name.lower().strip()
    logos_dir = Path(GILBARBARA_LOGOS_PATH) / "logos"

    # Build searchable list
    candidates = []
    for entry in logos:
        entry_name = entry.get("name", "")
        entry_short = entry.get("shortname", "")
        candidates.append((entry_name.lower(), entry))
        if entry_short:
            candidates.append((entry_short.lower(), entry))

    def try_load(entry):
        for svg_file in entry.get("files", []):
            svg_path = logos_dir / svg_file
            if svg_path.exists():
                svg_bytes = svg_path.read_bytes()
                png_bytes = svg_to_png(svg_bytes, ICON_SIZE)
                if png_bytes:
                    try:
                        return Image.open(io.BytesIO(png_bytes))
                    except Exception:
                        pass
        return None

    # Exact match first
    for key, entry in candidates:
        if key == name_lower:
            icon = try_load(entry)
            if icon:
                return (entry["name"], icon)

    # Fuzzy match
    if HAS_RAPIDFUZZ and candidates:
        keys = list(set(c[0] for c in candidates))
        match = process.extractOne(name_lower, keys, scorer=fuzz.ratio)
        if match and match[1] >= FUZZY_THRESHOLD:
            for key, entry in candidates:
                if key == match[0]:
                    icon = try_load(entry)
                    if icon:
                        return (entry["name"], icon)

    return None


def find_icon(name: str, entity_type: str = None) -> Optional[tuple[str, Image.Image]]:
    """Find icon for entity name across all sources.

    Search order:
      1. Local manifest.json (already downloaded icons)
      2. selfhst/icons (PNG, fast)
      3. gilbarbara/logos (SVG, requires cairosvg)

    Returns (display_name, PIL.Image) or None.
    """
    # 1. Local manifest
    result = find_icon_in_manifest(name, entity_type)
    if result:
        return result

    # 2. selfhst/icons
    result = find_icon_in_selfhst(name)
    if result:
        return result

    # 3. gilbarbara/logos
    if HAS_CAIROSVG:
        result = find_icon_in_gilbarbara(name)
        if result:
            return result

    return None


# =============================================================================
# Facts Extraction
# =============================================================================

def extract_entities_from_facts(facts_path: Path, entity_type: str = None) -> list[str]:
    """Extract entity names mentioned in a facts file.

    Looks for entity references in:
    - overall_summary
    - category content (claims, observations, insights)
    """
    with open(facts_path) as f:
        facts = json.load(f)

    manifest = load_manifest()

    # Build lookup of all entity names and aliases
    entity_lookup = {}  # lowercase name/alias -> entity name
    for entity in manifest.get("entities", []):
        if entity.get("status") in ("skip", "review"):
            continue
        if not entity.get("icon_paths"):
            continue
        if entity_type and entity.get("type") != entity_type:
            continue

        name = entity.get("name", "")
        entity_lookup[name.lower()] = name
        for alias in entity.get("aliases", []):
            if len(alias) >= 2:
                entity_lookup[alias.lower()] = name

    # Extract text content from facts
    text_content = []

    if facts.get("overall_summary"):
        text_content.append(facts["overall_summary"])

    for cat_data in facts.get("categories", {}).values():
        if isinstance(cat_data, list):
            for item in cat_data:
                if isinstance(item, dict):
                    for key in ("claim", "summary", "observation", "insight", "content"):
                        if item.get(key):
                            text_content.append(item[key])
        elif isinstance(cat_data, dict):
            for sublist in cat_data.values():
                if isinstance(sublist, list):
                    for item in sublist:
                        if isinstance(item, dict):
                            for key in ("claim", "summary"):
                                if item.get(key):
                                    text_content.append(item[key])

    # Find entity mentions in text
    full_text = " ".join(text_content).lower()
    found = set()

    for lookup_key, entity_name in entity_lookup.items():
        # Word boundary match to avoid partial matches
        pattern = r'\b' + re.escape(lookup_key) + r'\b'
        if re.search(pattern, full_text):
            found.add(entity_name)

    return sorted(found)


# =============================================================================
# Sheet Generation
# =============================================================================

def make_icon_sheet(
    entity_names: list[str],
    entity_type: str = None,
    cols: int = COLS,
    cell_width: int = CELL_WIDTH,
    cell_height: int = CELL_HEIGHT,
    icon_size: int = ICON_SIZE,
) -> tuple[Optional[bytes], list[str]]:
    """Create icon sheet montage from entity names.

    Returns (PNG bytes, list of found entity names) or (None, []).
    """
    # Collect entities with icons
    found_icons = []  # [(display_name, normalized_icon)]
    found_names = []

    for name in entity_names:
        result = find_icon(name, entity_type)
        if result:
            display_name, icon = result
            if display_name not in found_names:
                normalized = normalize_icon(icon, icon_size)
                found_icons.append((display_name, normalized))
                found_names.append(display_name)

    if not found_icons:
        return None, []

    # Calculate grid dimensions
    count = len(found_icons)
    rows = (count + cols - 1) // cols

    width = cols * cell_width + (cols + 1) * PADDING
    height = rows * cell_height + (rows + 1) * PADDING

    # Create sheet
    sheet = Image.new("RGBA", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(sheet)

    # Try to load a font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except Exception:
        font = ImageFont.load_default()

    # Place icons
    for idx, (name, icon) in enumerate(found_icons):
        row = idx // cols
        col = idx % cols

        x = PADDING + col * (cell_width + PADDING)
        y = PADDING + row * (cell_height + PADDING)

        # Center icon in cell
        icon_x = x + (cell_width - icon.width) // 2
        icon_y = y + (cell_height - LABEL_HEIGHT - icon.height) // 2

        # Paste icon
        sheet.paste(icon, (icon_x, icon_y), icon if icon.mode == "RGBA" else None)

        # Draw label
        label = name[:14] + "..." if len(name) > 15 else name
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = x + (cell_width - text_width) // 2
        text_y = y + cell_height - LABEL_HEIGHT + 4

        draw.text((text_x, text_y), label, fill=LABEL_COLOR, font=font)

    # Convert to PNG bytes
    buffer = io.BytesIO()
    sheet.save(buffer, "PNG", optimize=True)
    return buffer.getvalue(), found_names


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Create icon sheet montages for poster composition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "entities",
        nargs="*",
        help="Entity names to include in sheet"
    )
    parser.add_argument(
        "-f", "--facts",
        type=Path,
        help="Extract entities from facts JSON file"
    )
    parser.add_argument(
        "-t", "--type",
        choices=["token", "project", "user"],
        help="Filter entities by type"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=16,
        help="Maximum number of icons (default: 16)"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output path (default: stdout as PNG)"
    )
    parser.add_argument(
        "--base64",
        action="store_true",
        help="Output as base64 string"
    )
    parser.add_argument(
        "--cols",
        type=int,
        default=COLS,
        help=f"Number of columns (default: {COLS})"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what icons would be included without generating"
    )

    args = parser.parse_args()

    # Collect entity names
    entity_names = list(args.entities) if args.entities else []

    if args.facts:
        if not args.facts.exists():
            print(f"Error: Facts file not found: {args.facts}", file=sys.stderr)
            sys.exit(1)
        facts_entities = extract_entities_from_facts(args.facts, args.type)
        entity_names.extend(facts_entities)

    if not entity_names:
        print("Error: No entities specified. Use entity names or -f facts.json", file=sys.stderr)
        sys.exit(1)

    # Dedupe and limit
    entity_names = list(dict.fromkeys(entity_names))[:args.limit]

    # Dry run - just show what would be included
    if args.dry_run:
        print(f"Searching for icons for {len(entity_names)} entities...")
        found = []
        for name in entity_names:
            result = find_icon(name, args.type)
            if result:
                found.append(result[0])
                print(f"  [x] {name} -> {result[0]}")
            else:
                print(f"  [ ] {name}")
        print(f"\nFound {len(found)}/{len(entity_names)} icons")
        sys.exit(0)

    # Create sheet
    sheet_bytes, found_names = make_icon_sheet(
        entity_names, entity_type=args.type, cols=args.cols
    )

    if not sheet_bytes:
        print("Error: No icons found for specified entities", file=sys.stderr)
        sys.exit(1)

    # Output
    if args.output:
        args.output.write_bytes(sheet_bytes)
        print(f"Saved: {args.output} ({len(found_names)} icons)", file=sys.stderr)
    elif args.base64:
        print(base64.b64encode(sheet_bytes).decode("utf-8"))
    else:
        sys.stdout.buffer.write(sheet_bytes)


if __name__ == "__main__":
    main()
