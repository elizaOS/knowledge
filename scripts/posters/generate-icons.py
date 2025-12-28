#!/usr/bin/env python3
"""
Generate icons for entities using AI image generation.

Modes:
  --batch <type>       Generate 4x4 grid of icons for an entity type, slice into individual icons
  --entity <name>      Generate single icon for specific entity
  --missing            Generate icons for all entities missing from assets/icons/

Entity types: token, platform, project

Icon naming convention:
  - tokens: token-{name}.png (prefixed for CoinGecko compatibility)
  - platforms/projects: {name}.png (shortname only)

Uses OpenRouter (Gemini) for image generation, PIL for slicing.

Usage:
  python scripts/posters/generate-icons.py --batch platform
  python scripts/posters/generate-icons.py --entity Discord
  python scripts/posters/generate-icons.py --missing --type token
  python scripts/posters/generate-icons.py --list  # Show entities needing icons
"""

import os
import sys
import io
import json
import base64
import argparse
import logging
from pathlib import Path
from typing import Optional

import requests

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow required. Install with: pip install Pillow")
    sys.exit(1)

# Config
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
IMAGE_MODEL = "google/gemini-3-pro-image-preview"

SCRIPT_DIR = Path(__file__).parent.resolve()
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent
ASSETS_DIR = SCRIPT_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
ENTITY_INVENTORY = ASSETS_DIR / "entity-inventory.json"
FACTS_DIR = WORKSPACE_ROOT / "the-council" / "facts"

GRID_SIZE = 4  # 4x4 grid = 16 icons per batch
ICON_SIZE = 256  # Output icon size

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%H:%M:%S'
)


def load_inventory() -> dict:
    """Load entity inventory."""
    if not ENTITY_INVENTORY.exists():
        logging.error(f"Entity inventory not found: {ENTITY_INVENTORY}")
        sys.exit(1)

    with open(ENTITY_INVENTORY) as f:
        return json.load(f)


def find_entity_context(entity_name: str, limit: int = 3) -> list[str]:
    """Search recent facts files for context about an entity.

    Returns list of text snippets mentioning the entity.
    """
    if not FACTS_DIR.exists():
        return []

    contexts = []
    name_lower = entity_name.lower()

    # Search recent facts files (newest first)
    facts_files = sorted(FACTS_DIR.glob("*.json"), reverse=True)[:30]

    for facts_file in facts_files:
        if facts_file.name == "daily.json":
            continue

        try:
            content = facts_file.read_text()
            if name_lower not in content.lower():
                continue

            data = json.loads(content)

            # Search in overall summary
            summary = data.get("overall_summary", "")
            if name_lower in summary.lower():
                contexts.append(summary)

            # Search in categories
            for cat_name, cat_data in data.get("categories", {}).items():
                if isinstance(cat_data, list):
                    for item in cat_data:
                        if isinstance(item, dict):
                            for key, val in item.items():
                                if isinstance(val, str) and name_lower in val.lower():
                                    contexts.append(val[:500])
                elif isinstance(cat_data, dict):
                    for key, val in cat_data.items():
                        if isinstance(val, str) and name_lower in val.lower():
                            contexts.append(val[:500])
                        elif isinstance(val, list):
                            for item in val:
                                if isinstance(item, dict):
                                    for k, v in item.items():
                                        if isinstance(v, str) and name_lower in v.lower():
                                            contexts.append(v[:500])

            if len(contexts) >= limit:
                break

        except Exception:
            continue

    return contexts[:limit]


def enrich_entity_with_context(entity: dict) -> dict:
    """Add context from facts to entity if not already described."""
    if entity.get("description"):
        return entity

    name = entity.get("name", "")
    contexts = find_entity_context(name)

    if contexts:
        # Combine context snippets into description
        entity = entity.copy()
        entity["_context"] = contexts

    return entity


def get_entity_info(inventory: dict, name: str, entity_type: str = None) -> dict:
    """Get entity info from inventory (flat schema v2)."""
    entities = inventory.get("entities", [])

    # Skip if legacy format (dict of categories)
    if isinstance(entities, dict):
        logging.warning("Legacy inventory format detected. Run extract-entities.py to regenerate.")
        return None

    for entity in entities:
        if not isinstance(entity, dict):
            continue

        entity_name = entity.get("name", "")
        aliases = entity.get("aliases", [])

        # Match by name or alias
        if entity_name.lower() == name.lower() or name.lower() in [a.lower() for a in aliases]:
            # Filter by type if specified
            if entity_type and entity.get("type") != entity_type:
                continue
            return entity

    return None


def get_entities_by_type(inventory: dict, entity_type: str) -> list[dict]:
    """Get all entities of a given type."""
    entities = inventory.get("entities", [])

    # Skip if legacy format (dict of categories)
    if isinstance(entities, dict):
        logging.warning("Legacy inventory format detected. Run extract-entities.py to regenerate.")
        return []

    return [e for e in entities if isinstance(e, dict) and e.get("type") == entity_type]




def get_icon_filename(entity: dict) -> str:
    """Get the icon filename for an entity.

    Convention:
    - tokens: token-{name}.png (prefixed for CoinGecko compatibility)
    - users: user-{name}.png (for avatars/profile pics)
    - everything else: {name}.png (shortname only)
    """
    name = entity.get("name", "unknown").lower().strip().replace(" ", "-")
    entity_type = entity.get("type", "project")

    if entity_type == "token":
        return f"token-{name}.png"
    elif entity_type == "user":
        return f"user-{name}.png"
    else:
        return f"{name}.png"


def get_existing_icons() -> set:
    """Get set of existing icon filenames (lowercase)."""
    if not ICONS_DIR.exists():
        return set()
    return {f.name.lower() for f in ICONS_DIR.iterdir() if f.is_file() and not f.name.startswith("_")}


def get_missing_entities(inventory: dict, entity_type: str = None) -> list[dict]:
    """Get entities that don't have icons yet."""
    entities = inventory.get("entities", [])

    # Skip if legacy format (dict of categories) - requires regeneration
    if isinstance(entities, dict):
        logging.warning("Legacy inventory format detected. Run extract-entities.py to regenerate.")
        return []

    # Filter by type if specified
    if entity_type:
        entities = [e for e in entities if isinstance(e, dict) and e.get("type") == entity_type]

    existing = get_existing_icons()

    missing = []
    for entity in entities:
        if not isinstance(entity, dict):
            continue
        name = entity.get("name", "")
        if len(name) < 2:
            continue

        icon_filename = get_icon_filename(entity)
        if icon_filename.lower() not in existing:
            missing.append(entity)

    return missing


def build_icon_prompt(entities: list[dict], entity_type: str = None, use_context: bool = True) -> str:
    """Build prompt for generating a grid of icons."""
    # Build entity descriptions using rich metadata
    entity_lines = []
    for i, entity in enumerate(entities, 1):
        name = entity.get("name", "Unknown")
        desc = entity.get("description", "")
        visual_hints = entity.get("visual_hints", "")
        context = entity.get("_context", [])

        parts = [f"{i}. {name}"]
        if desc:
            parts.append(f"({desc})")
        if visual_hints:
            parts.append(f"[style: {visual_hints}]")
        elif context and use_context:
            # Use first context snippet as hint
            hint = context[0][:100].replace("\n", " ")
            parts.append(f"[context: {hint}...]")

        entity_lines.append(" ".join(parts))

    entities_text = "\n".join(entity_lines)

    # Type-specific style hints
    style_hints = {
        "token": "cryptocurrency token logos, coin/token style, clean geometric designs",
        "platform": "tech company logos, app icons, recognizable brand marks",
        "project": "software project logos, modern tech emblems, distinctive brand marks",
    }
    style = style_hints.get(entity_type, "clean modern icons")

    rows = (len(entities) + GRID_SIZE - 1) // GRID_SIZE
    cols = min(len(entities), GRID_SIZE)

    prompt = f"""Generate a {rows}x{cols} grid of icon logos.

ENTITIES (in order, left-to-right, top-to-bottom):
{entities_text}

STYLE: {style}

REQUIREMENTS:
- Each icon in its own cell, evenly spaced grid
- Clean, simple, recognizable designs
- Solid or transparent backgrounds (no gradients behind icons)
- Professional quality, suitable for UI use
- Each icon should be distinct and match its entity
- No text labels on the icons
- Consistent size and spacing between icons
- Square aspect ratio for the overall image"""

    return prompt


def build_single_icon_prompt(entity: dict) -> str:
    """Build prompt for generating a single icon."""
    name = entity.get("name", "Unknown")
    desc = entity.get("description", "")
    visual_hints = entity.get("visual_hints", "")
    entity_type = entity.get("type", "project")
    context = entity.get("_context", [])

    details = []
    if desc:
        details.append(f"Description: {desc}")
    if visual_hints:
        details.append(f"Visual style: {visual_hints}")
    if context:
        # Add context as background info
        context_text = " ".join(c[:200] for c in context[:2])
        details.append(f"Context: {context_text}")

    details_text = "\n".join(details) if details else "Create a distinctive, recognizable icon"

    # Type-specific hints
    type_hints = {
        "token": "cryptocurrency/blockchain token style",
        "platform": "tech company/service logo style",
        "project": "software project/protocol logo style",
    }
    type_hint = type_hints.get(entity_type, "")

    prompt = f"""Generate a single icon logo for: {name}

{details_text}
{f"Style category: {type_hint}" if type_hint else ""}

REQUIREMENTS:
- Clean, professional icon design
- Transparent or solid color background
- Recognizable and distinctive
- Suitable for use as app icon or logo
- No text or labels
- Square format, centered design
- High contrast, works at small sizes"""

    return prompt


def generate_image(prompt: str) -> bytes:
    """Call OpenRouter to generate image, return PNG bytes."""
    logging.info("Generating image via OpenRouter...")

    response = requests.post(
        OPENROUTER_ENDPOINT,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/elizaOS/knowledge",
            "X-Title": "ElizaOS Icon Generator"
        },
        json={
            "model": IMAGE_MODEL,
            "modalities": ["image", "text"],
            "messages": [{
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }]
        },
        timeout=180
    )
    response.raise_for_status()

    result = response.json()

    try:
        images = result["choices"][0]["message"]["images"]
        if not images:
            raise ValueError("No images in response")

        image_url = images[0]["image_url"]["url"]
        if not image_url.startswith("data:"):
            raise ValueError(f"Unexpected image URL format: {image_url[:50]}")

        base64_data = image_url.split(",", 1)[1]
        return base64.b64decode(base64_data)

    except (KeyError, IndexError) as e:
        logging.error(f"Failed to extract image: {e}")
        logging.error(f"Response: {json.dumps(result, indent=2)[:500]}")
        raise ValueError(f"Failed to extract image from API response: {e}")


def slice_grid(image_bytes: bytes, num_icons: int) -> list[Image.Image]:
    """Slice a grid image into individual icons."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    width, height = img.size

    # Calculate grid dimensions
    cols = min(num_icons, GRID_SIZE)
    rows = (num_icons + GRID_SIZE - 1) // GRID_SIZE

    cell_width = width // cols
    cell_height = height // rows

    icons = []
    for i in range(num_icons):
        row = i // cols
        col = i % cols

        left = col * cell_width
        top = row * cell_height
        right = left + cell_width
        bottom = top + cell_height

        icon = img.crop((left, top, right, bottom))
        icons.append(icon)

    return icons


def process_icon(icon: Image.Image) -> Image.Image:
    """Process icon: resize to standard size."""
    icon = icon.resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)
    return icon


def save_icon(icon: Image.Image, entity: dict) -> Path:
    """Save icon to the flat icons directory."""
    ICONS_DIR.mkdir(parents=True, exist_ok=True)

    filename = get_icon_filename(entity)
    output_path = ICONS_DIR / filename

    icon.save(output_path, "PNG", optimize=True)
    return output_path


def generate_batch(entity_type: str, entities: list[dict], use_context: bool = True) -> list[Path]:
    """Generate a batch of icons for entities."""
    if not entities:
        logging.info("No entities to generate")
        return []

    # Limit to 16 per batch (4x4 grid)
    batch = entities[:GRID_SIZE * GRID_SIZE]

    # Enrich with context from facts
    if use_context:
        enriched_batch = []
        for entity in batch:
            enriched = enrich_entity_with_context(entity)
            if enriched.get("_context"):
                logging.debug(f"  Found context for {entity.get('name')}")
            enriched_batch.append(enriched)
        batch = enriched_batch

    logging.info(f"Generating batch of {len(batch)} icons for {entity_type}...")

    # Build prompt and generate
    prompt = build_icon_prompt(batch, entity_type)
    logging.debug(f"Prompt:\n{prompt}")

    image_bytes = generate_image(prompt)

    # Save raw grid for debugging
    grid_path = ICONS_DIR / f"_grid_{entity_type}_latest.png"
    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    grid_path.write_bytes(image_bytes)
    logging.info(f"Saved grid: {grid_path}")

    # Slice into individual icons
    icons = slice_grid(image_bytes, len(batch))

    # Process and save each icon
    saved = []
    for i, (icon, entity) in enumerate(zip(icons, batch)):
        name = entity.get("name", f"icon_{i}")

        try:
            processed = process_icon(icon)
            output_path = save_icon(processed, entity)
            saved.append(output_path)
            logging.info(f"  [{i+1}/{len(batch)}] {name} -> {output_path.name}")
        except Exception as e:
            logging.error(f"  [{i+1}/{len(batch)}] {name} failed: {e}")

    return saved


def generate_single(entity: dict, use_context: bool = True) -> Optional[Path]:
    """Generate a single icon for an entity."""
    name = entity.get("name", "Unknown")

    # Enrich with context
    if use_context:
        entity = enrich_entity_with_context(entity)
        if entity.get("_context"):
            logging.info(f"Found context for {name}")

    logging.info(f"Generating icon for {name}...")

    prompt = build_single_icon_prompt(entity)
    image_bytes = generate_image(prompt)

    # Load and process
    icon = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    processed = process_icon(icon)

    output_path = save_icon(processed, entity)
    logging.info(f"Saved: {output_path}")

    return output_path


def list_missing(inventory: dict, entity_type: str = None):
    """List entities missing icons."""
    entity_types = [entity_type] if entity_type else ["token", "platform", "project"]

    for et in entity_types:
        missing = get_missing_entities(inventory, et)
        if missing:
            print(f"\n{et.upper()} ({len(missing)} missing):")
            for entity in missing[:20]:  # Limit output
                name = entity.get("name", "?")
                desc = entity.get("description", "")
                if desc:
                    print(f"  - {name}: {desc[:50]}...")
                else:
                    print(f"  - {name}")
            if len(missing) > 20:
                print(f"  ... and {len(missing) - 20} more")


def main():
    parser = argparse.ArgumentParser(
        description="Generate icons for entities using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Mode selection
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--batch",
        metavar="TYPE",
        help="Generate 4x4 grid batch for entity type (token, platform, project)"
    )
    mode.add_argument(
        "--entity",
        metavar="NAME",
        help="Generate single icon for specific entity"
    )
    mode.add_argument(
        "--missing",
        action="store_true",
        help="Generate icons for all missing entities"
    )
    mode.add_argument(
        "--list",
        action="store_true",
        help="List entities that need icons"
    )

    # Options
    parser.add_argument(
        "--type", "-t",
        dest="entity_type",
        choices=["token", "platform", "project"],
        help="Entity type to filter (use with --missing, --list, or --entity)"
    )
    parser.add_argument(
        "--no-context",
        action="store_true",
        help="Skip context lookup from facts (faster, simpler prompts)"
    )
    parser.add_argument(
        "--limit", "-n",
        type=int,
        default=16,
        help="Max icons to generate in batch mode (default: 16)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load inventory
    inventory = load_inventory()

    # Handle --list
    if args.list:
        list_missing(inventory, args.entity_type)
        return 0

    # Check API key for generation modes
    if not args.list and not OPENROUTER_API_KEY:
        logging.error("OPENROUTER_API_KEY environment variable not set")
        return 1

    # Context lookup enabled by default
    use_context = not args.no_context

    try:
        if args.batch:
            # Batch mode for entity type
            entity_type = args.batch
            missing = get_missing_entities(inventory, entity_type)
            if not missing:
                logging.info(f"No missing icons for {entity_type}")
                return 0

            # Limit batch size
            to_generate = missing[:args.limit]
            logging.info(f"Found {len(missing)} missing, generating {len(to_generate)}")

            saved = generate_batch(entity_type, to_generate, use_context=use_context)
            logging.info(f"Generated {len(saved)} icons")

        elif args.entity:
            # Single entity mode
            entity = get_entity_info(inventory, args.entity, args.entity_type)
            if not entity:
                logging.error(f"Entity not found: {args.entity}")
                return 1

            generate_single(entity, use_context=use_context)

        elif args.missing:
            # Generate all missing
            entity_types = [args.entity_type] if args.entity_type else ["token", "platform", "project"]

            for et in entity_types:
                missing = get_missing_entities(inventory, et)
                if not missing:
                    continue

                logging.info(f"\n=== {et.upper()} ({len(missing)} missing) ===")

                # Process in batches
                for i in range(0, min(len(missing), args.limit), GRID_SIZE * GRID_SIZE):
                    batch = missing[i:i + GRID_SIZE * GRID_SIZE]
                    generate_batch(et, batch, use_context=use_context)
        else:
            parser.print_help()
            return 1

        return 0

    except requests.RequestException as e:
        logging.error(f"API error: {e}")
        return 1
    except Exception as e:
        logging.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
