#!/usr/bin/env python3
"""
Generate icons for entities using AI image generation with CoinGecko integration.

Smart routing for tokens:
  - Tries CoinGecko API first (free, fast) for mapped tokens
  - Falls back to AI generation if not found on CoinGecko

Modes:
  --batch <type>       Generate 4x4 grid of icons for an entity type
  --entity <name>      Generate single icon for specific entity
  --missing            Generate icons for all missing entities (smart routing)
  --list               Show entities that need icons

Entity types: token, project, user

Icon naming convention:
  - tokens: token-{name}-{n}.png (numbered, prefixed)
  - users: user-{name}-{n}.png (numbered, prefixed)
  - projects: {name}-{n}.png (numbered)

The numbering allows multiple icons per entity (artist reference/moodboard).

Usage:
  python scripts/posters/generate-icons.py --missing                # All types, smart routing
  python scripts/posters/generate-icons.py --missing --type token   # Tokens with CoinGecko
  python scripts/posters/generate-icons.py --entity Discord
  python scripts/posters/generate-icons.py --list
"""

import os
import sys
import io
import json
import re
import base64
import time
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
ENTITY_INVENTORY = ASSETS_DIR / "manifest.json"
FACTS_DIR = WORKSPACE_ROOT / "the-council" / "facts"

GRID_SIZE = 4  # 4x4 grid = 16 icons per batch
ICON_SIZE = 256  # Output icon size
COINGECKO_RATE_LIMIT = 3  # seconds between CoinGecko requests

# CoinGecko ID mappings for common tokens
# Maps normalized entity name -> CoinGecko coin ID
# NOTE: Be careful with ambiguous names - verify CoinGecko IDs before adding
COINGECKO_IDS = {
    # Major tokens
    "bitcoin": "bitcoin",
    "btc": "bitcoin",
    "ethereum": "ethereum",
    "eth": "ethereum",
    "solana": "solana",
    "sol": "solana",
    "usdc": "usd-coin",
    "usdt": "tether",
    "weth": "weth",
    "wbtc": "wrapped-bitcoin",
    "bonk": "bonk",
    "dogwifhat": "dogwifcoin",
    # Ecosystem tokens
    "ai16z": "ai16z",              # ElizaOS project token (rebranded from ai16z)
    "elizaos": "ai16z",            # ElizaOS token = ai16z on CoinGecko
    "elizaos token": "ai16z",
    # NOTE: "eliza" is a DIFFERENT token on CoinGecko (not ElizaOS)
    # Do NOT add "eliza" -> "eliza" mapping to avoid confusion
    "virtual": "virtual-protocol",
    "worldcoin": "worldcoin-wld",
    "wld": "worldcoin-wld",
    "dot": "polkadot",
    "icp": "internet-computer",
    "bnb": "binancecoin",
    "avax": "avalanche-2",
    "matic": "matic-network",
    "polygon": "matic-network",
    "xmr": "monero",
    "monero": "monero",
}

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
    """Get entity info from inventory."""
    entities = inventory.get("entities", [])

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
    return [e for e in entities if isinstance(e, dict) and e.get("type") == entity_type]




def slugify_name(name: str) -> str:
    """Convert entity name to filename-safe slug."""
    return name.lower().strip().replace(" ", "-").replace(".", "-").lstrip("$@")


def get_icon_base(entity: dict) -> str:
    """Get the base icon filename pattern for an entity (without number/extension).

    Convention:
    - tokens: token-{name}
    - users: user-{name}
    - everything else: {name}
    """
    name = slugify_name(entity.get("name", "unknown"))
    entity_type = entity.get("type", "project")

    if entity_type == "token":
        return f"token-{name}"
    elif entity_type == "user":
        return f"user-{name}"
    else:
        return name


def get_next_icon_filename(entity: dict, icons_dir: Path = None) -> str:
    """Get next available numbered filename for entity icon.

    Returns filename like: token-bitcoin-1.png, discord-2.png
    """
    if icons_dir is None:
        icons_dir = ICONS_DIR

    base = get_icon_base(entity)

    # Find existing numbered files
    existing = list(icons_dir.glob(f"{base}-*.png")) + list(icons_dir.glob(f"{base}-*.jpg"))

    if not existing:
        return f"{base}-1.png"

    # Get highest number from existing files
    nums = []
    for f in existing:
        match = re.search(rf"{re.escape(base)}-(\d+)\.", f.name)
        if match:
            nums.append(int(match.group(1)))

    next_num = max(nums, default=0) + 1
    return f"{base}-{next_num}.png"


def get_icon_filename(entity: dict) -> str:
    """Get the primary icon filename for an entity."""
    base = get_icon_base(entity)
    return f"{base}-1.png"


def get_existing_icons() -> set:
    """Get set of existing icon filenames (lowercase)."""
    if not ICONS_DIR.exists():
        return set()
    return {f.name.lower() for f in ICONS_DIR.iterdir() if f.is_file() and not f.name.startswith("_")}


def get_missing_entities(inventory: dict, entity_type: str = None) -> list[dict]:
    """Get entities that don't have icons yet.

    Uses icon_paths field from inventory (populated by validate-icons.py --sync-only).
    Only includes entities with status="keep" (or no status field for backward compat).
    """
    entities = inventory.get("entities", [])

    # Filter by type if specified
    if entity_type:
        entities = [e for e in entities if isinstance(e, dict) and e.get("type") == entity_type]

    missing = []
    for entity in entities:
        if not isinstance(entity, dict):
            continue
        name = entity.get("name", "")
        if len(name) < 2:
            continue

        # Skip entities marked as skip or review
        status = entity.get("status")
        if status in ("skip", "review"):
            continue

        # Check if entity has icon_paths (populated by validate-icons.py)
        if not entity.get("icon_paths"):
            missing.append(entity)

    return missing


# =============================================================================
# CoinGecko Integration
# =============================================================================

def fetch_coingecko_icon(coin_id: str, entity: dict) -> Optional[Path]:
    """Fetch token icon from CoinGecko API.

    Returns Path to saved icon if successful, None otherwise.
    Uses numbered filename scheme.
    """
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Get the large image URL
        image_url = data.get("image", {}).get("large")
        if not image_url:
            logging.warning(f"  [warn] {coin_id} - no image found")
            return None

        # Download the image
        img_response = requests.get(image_url, timeout=10)
        img_response.raise_for_status()

        # Save with numbered filename
        ICONS_DIR.mkdir(parents=True, exist_ok=True)
        filename = get_next_icon_filename(entity)
        output_path = ICONS_DIR / filename

        output_path.write_bytes(img_response.content)
        logging.info(f"  [coingecko] {coin_id} -> {output_path.name}")
        return output_path

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logging.debug(f"  [404] {coin_id} - not found on CoinGecko")
        else:
            logging.warning(f"  [error] {coin_id} - {e}")
        return None
    except Exception as e:
        logging.warning(f"  [error] {coin_id} - {e}")
        return None


def try_coingecko(entity: dict) -> Optional[Path]:
    """Try to fetch icon from CoinGecko using hardcoded mappings.

    Returns Path to saved icon if successful, None if not mapped or fetch failed.
    Only works for token entities with entries in COINGECKO_IDS.
    """
    name = entity.get("name", "").lower().strip().lstrip("$")

    # Check hardcoded mapping
    coin_id = COINGECKO_IDS.get(name)

    # Try aliases if name not mapped
    if not coin_id:
        for alias in entity.get("aliases", []):
            normalized_alias = alias.lower().strip().lstrip("$")
            coin_id = COINGECKO_IDS.get(normalized_alias)
            if coin_id:
                break

    if not coin_id:
        return None

    return fetch_coingecko_icon(coin_id, entity)


# =============================================================================
# Prompt Building
# =============================================================================

def build_icon_prompt(
    entities: list[dict] | dict,
    batch: bool = True,
    entity_type: str = None,
    use_context: bool = True
) -> str:
    """Build prompt for icon generation.

    Args:
        entities: List of entities (batch) or single entity dict
        batch: If True, generate grid layout; if False, single icon
        entity_type: Override type for style selection (batch mode)
        use_context: Include context in prompts
    """
    # Normalize to list
    if not batch:
        entities = [entities]

    if batch and len(entities) > 1:
        # Batch mode: grid of icons
        rows = (len(entities) + GRID_SIZE - 1) // GRID_SIZE
        cols = min(len(entities), GRID_SIZE)

        entity_lines = []
        for i, entity in enumerate(entities, 1):
            name = entity.get("name", "Unknown")
            desc = entity.get("description", "")

            # Format: "1. Discord — gaming chat platform"
            line = f"{i}. {name}"
            if desc:
                # Truncate long descriptions
                short_desc = desc[:80] + "..." if len(desc) > 80 else desc
                line += f" — {short_desc}"
            entity_lines.append(line)

        entities_text = "\n".join(entity_lines)

        return f"""Generate a {rows}x{cols} grid image of logos/icons.

GRID LAYOUT:
- {rows} rows × {cols} columns = {len(entities)} equal square cells
- NO gridlines, NO borders, NO separators between cells
- Background: pure white (#FFFFFF)
- Each logo centered in its cell with equal padding
- All logos visually balanced to same optical size (~70% of cell)
- NO overlap between cells

ENTITIES (left to right, top to bottom):
{entities_text}

IMPORTANT:
- For KNOWN brands/projects, recreate their ACTUAL official logo as accurately as possible
- For unknown/new projects, create a distinctive, professional icon
- If uncertain about a logo, create a clean symbolic icon rather than guessing wrong
- NO text labels on the icons
- Flat vector style, full brand colors where known"""

    else:
        # Single icon mode
        entity = entities[0]
        name = entity.get("name", "Unknown")
        desc = entity.get("description", "")
        etype = entity.get("type", "project")
        context = entity.get("_context", [])

        details = []
        if desc:
            details.append(f"Description: {desc}")
        if context and use_context:
            context_text = " ".join(c[:200] for c in context[:2])
            details.append(f"Context: {context_text}")

        details_text = "\n".join(details) if details else ""

        return f"""Generate a single logo/icon for: {name}

Type: {etype}
{details_text}

REQUIREMENTS:
- Background: pure white or transparent
- Logo centered with padding (~70% of image)
- If this is a KNOWN brand/project, recreate the ACTUAL official logo accurately
- If unknown, create a distinctive, professional, memorable icon
- NO text labels
- Flat vector style, clean lines
- Should work at small sizes (high contrast, simple shapes)"""


def generate_image(prompt: str, aspect_ratio: str = "1:1") -> bytes:
    """Call OpenRouter to generate image, return PNG bytes.

    Args:
        prompt: Text prompt for image generation
        aspect_ratio: Image aspect ratio (default "1:1" = 1024x1024)
            Supported: 1:1, 2:3, 3:2, 3:4, 4:3, 9:16, 16:9
    """
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
            }],
            "image_config": {
                "aspect_ratio": aspect_ratio
            }
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


def save_icon(icon: Image.Image, entity: dict, use_numbered: bool = True) -> Path:
    """Save icon to the flat icons directory.

    Args:
        icon: PIL Image to save
        entity: Entity dict
        use_numbered: If True, use auto-incrementing numbered filename
    """
    ICONS_DIR.mkdir(parents=True, exist_ok=True)

    if use_numbered:
        filename = get_next_icon_filename(entity)
    else:
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


def generate_single(entity: dict, use_context: bool = True, skip_coingecko: bool = False, force: bool = False) -> Optional[Path]:
    """Generate a single icon for an entity.

    For tokens, tries CoinGecko first (unless skip_coingecko=True), falls back to AI.
    Skips if icon already exists (unless force=True).
    """
    name = entity.get("name", "Unknown")
    entity_type = entity.get("type", "project")

    # Check if icon already exists
    icon_path = ICONS_DIR / get_icon_filename(entity)
    if icon_path.exists() and not force:
        logging.info(f"Icon already exists for {name}, skipping (use --force to regenerate)")
        return icon_path

    # For tokens, try CoinGecko first
    if entity_type == "token" and not skip_coingecko:
        logging.info(f"Trying CoinGecko for {name}...")
        cg_path = try_coingecko(entity)
        if cg_path:
            return cg_path
        logging.info(f"CoinGecko failed for {name}, falling back to AI")

    # Enrich with context for AI generation
    if use_context:
        entity = enrich_entity_with_context(entity)
        if entity.get("_context"):
            logging.info(f"Found context for {name}")

    logging.info(f"Generating icon for {name} via AI...")

    prompt = build_icon_prompt(entity, batch=False)
    image_bytes = generate_image(prompt)

    # Load and process
    icon = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    processed = process_icon(icon)

    output_path = save_icon(processed, entity)
    logging.info(f"Saved: {output_path}")

    return output_path


def list_missing(inventory: dict, entity_type: str = None):
    """List entities missing icons."""
    entity_types = [entity_type] if entity_type else ["token", "project", "user"]

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
        choices=["token", "project", "user"],
        help="Entity type to filter (use with --missing, --list, or --entity)"
    )
    parser.add_argument(
        "--no-context",
        action="store_true",
        help="Skip context lookup from facts (faster, simpler prompts)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate icons even if they already exist"
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

            generate_single(entity, use_context=use_context, force=args.force)

        elif args.missing:
            # Generate all missing
            entity_types = [args.entity_type] if args.entity_type else ["token", "project", "user"]

            for et in entity_types:
                missing = get_missing_entities(inventory, et)
                if not missing:
                    continue

                logging.info(f"\n=== {et.upper()} ({len(missing)} missing) ===")

                # For tokens: try CoinGecko first, collect failures for AI batch
                if et == "token":
                    coingecko_success = 0
                    ai_needed = []

                    for i, entity in enumerate(missing[:args.limit]):
                        name = entity.get("name", "?")
                        logging.info(f"  [{i+1}/{min(len(missing), args.limit)}] {name}...")

                        if try_coingecko(entity):
                            coingecko_success += 1
                        else:
                            ai_needed.append(entity)

                        # Rate limit CoinGecko requests
                        if i < min(len(missing), args.limit) - 1:
                            time.sleep(COINGECKO_RATE_LIMIT)

                    logging.info(f"CoinGecko: {coingecko_success} fetched, {len(ai_needed)} need AI")

                    # Generate remaining with AI in batches
                    if ai_needed:
                        for i in range(0, len(ai_needed), GRID_SIZE * GRID_SIZE):
                            batch = ai_needed[i:i + GRID_SIZE * GRID_SIZE]
                            generate_batch(et, batch, use_context=use_context)
                else:
                    # Non-tokens: AI batch generation
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
