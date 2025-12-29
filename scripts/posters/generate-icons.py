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

# Retry configuration
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2  # seconds


def retry_with_backoff(func, max_retries: int = MAX_RETRIES, backoff_base: float = RETRY_BACKOFF_BASE):
    """Decorator/wrapper for retrying API calls with exponential backoff.

    Retries on:
    - Connection errors
    - Timeout errors
    - 429 (rate limit) and 5xx (server) HTTP errors
    """
    def wrapper(*args, **kwargs):
        last_exception = None
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.Timeout as e:
                last_exception = e
                wait_time = backoff_base ** attempt
                logging.warning(f"Timeout on attempt {attempt + 1}/{max_retries}, retrying in {wait_time}s...")
                time.sleep(wait_time)
            except requests.exceptions.ConnectionError as e:
                last_exception = e
                wait_time = backoff_base ** attempt
                logging.warning(f"Connection error on attempt {attempt + 1}/{max_retries}, retrying in {wait_time}s...")
                time.sleep(wait_time)
            except requests.exceptions.HTTPError as e:
                # Only retry on rate limit (429) or server errors (5xx)
                if e.response is not None and (e.response.status_code == 429 or e.response.status_code >= 500):
                    last_exception = e
                    wait_time = backoff_base ** attempt
                    logging.warning(f"HTTP {e.response.status_code} on attempt {attempt + 1}/{max_retries}, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise  # Don't retry client errors (4xx except 429)
        raise last_exception
    return wrapper


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
    Uses numbered filename scheme. Includes retry logic for transient errors.
    """
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"

    def get_coin_data():
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp

    try:
        response = retry_with_backoff(get_coin_data)()
        data = response.json()

        # Get the large image URL
        image_url = data.get("image", {}).get("large")
        if not image_url:
            logging.warning(f"  [warn] {coin_id} - no image found")
            return None

        # Download the image (with retry)
        def download_image():
            resp = requests.get(image_url, timeout=10)
            resp.raise_for_status()
            return resp

        img_response = retry_with_backoff(download_image)()

        # Save with numbered filename
        ICONS_DIR.mkdir(parents=True, exist_ok=True)
        filename = get_next_icon_filename(entity)
        output_path = ICONS_DIR / filename

        output_path.write_bytes(img_response.content)
        logging.info(f"  [coingecko] {coin_id} -> {output_path.name}")
        return output_path

    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
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
# Reference Image Fetching (for accurate logo recreation)
# =============================================================================

# Try to import cairosvg for SVG->PNG conversion
try:
    import cairosvg
    HAS_CAIROSVG = True
except ImportError:
    HAS_CAIROSVG = False
    logging.debug("cairosvg not available, SVG icons will be skipped")


def svg_to_png(svg_bytes: bytes, size: int = 256) -> Optional[bytes]:
    """Convert SVG to PNG using cairosvg.

    Returns PNG bytes or None if conversion fails.
    """
    if not HAS_CAIROSVG:
        return None

    try:
        png_bytes = cairosvg.svg2png(
            bytestring=svg_bytes,
            output_width=size,
            output_height=size
        )
        return png_bytes
    except Exception as e:
        logging.debug(f"  SVG conversion failed: {e}")
        return None


def fetch_simple_icon(name: str) -> Optional[bytes]:
    """Fetch icon from Simple Icons CDN, converted to PNG.

    Simple Icons has 3000+ tech brand icons.
    https://simpleicons.org/

    Returns PNG bytes (converted from SVG) or None.
    """
    # Normalize name to slug format
    slug = name.lower().replace(" ", "").replace(".", "").replace("-", "")
    url = f"https://cdn.simpleicons.org/{slug}"

    try:
        resp = requests.get(url, timeout=10)
        if resp.ok and resp.headers.get("content-type", "").startswith("image/svg"):
            # Convert SVG to PNG for Gemini compatibility
            png_bytes = svg_to_png(resp.content)
            if png_bytes:
                logging.debug(f"  [simpleicons] Found {slug} (converted to PNG)")
                return png_bytes
            else:
                logging.debug(f"  [simpleicons] Found {slug} but SVG conversion failed")
    except Exception as e:
        logging.debug(f"  [simpleicons] {slug} failed: {e}")
    return None


def fetch_github_avatar(org_or_user: str) -> Optional[bytes]:
    """Fetch avatar from GitHub.

    Works for both organizations and users.
    """
    url = f"https://github.com/{org_or_user}.png?size=256"

    try:
        resp = requests.get(url, timeout=10, allow_redirects=True)
        if resp.ok and "image" in resp.headers.get("content-type", ""):
            logging.debug(f"  [github] Found {org_or_user}")
            return resp.content
    except Exception as e:
        logging.debug(f"  [github] {org_or_user} failed: {e}")
    return None


def fetch_google_favicon(domain: str) -> Optional[bytes]:
    """Fetch favicon via Google's service.

    Universal fallback - works for any domain.
    """
    # Clean domain
    domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
    url = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"

    try:
        resp = requests.get(url, timeout=10)
        if resp.ok and "image" in resp.headers.get("content-type", ""):
            # Check if it's not the default favicon (very small)
            if len(resp.content) > 500:
                logging.debug(f"  [favicon] Found {domain}")
                return resp.content
    except Exception as e:
        logging.debug(f"  [favicon] {domain} failed: {e}")
    return None


# =============================================================================
# Simple Icons Fuzzy Matching (with false positive prevention)
# =============================================================================

SIMPLE_ICONS_DATA_URL = "https://cdn.jsdelivr.net/npm/simple-icons@latest/_data/simple-icons.json"
_simple_icons_cache: dict = None  # Cached data with full metadata
MIN_SUBSTRING_LENGTH = 4  # Minimum name length for substring matching


def _load_simple_icons_data() -> dict:
    """Load and cache Simple Icons data with full metadata.

    Returns dict with two indices:
    - "by_title": {lowercase_title: {slug, title, source, aliases}}
    - "by_alias": {lowercase_alias: {slug, title, source, aliases}}
    """
    global _simple_icons_cache
    if _simple_icons_cache is not None:
        return _simple_icons_cache

    _simple_icons_cache = {"by_title": {}, "by_alias": {}}
    try:
        resp = requests.get(SIMPLE_ICONS_DATA_URL, timeout=15)
        if not resp.ok:
            logging.warning(f"Failed to load Simple Icons data: {resp.status_code}")
            return _simple_icons_cache

        data = resp.json()
        for icon in data:
            title = icon.get("title", "")
            if not title:
                continue

            # Slug defaults to slugified title if not specified
            slug = icon.get("slug") or title.lower().replace(" ", "").replace(".", "").replace("-", "")

            # Collect all aliases
            icon_aliases = icon.get("aliases", {})
            all_aliases = []
            all_aliases.extend(icon_aliases.get("aka", []))
            all_aliases.extend(icon_aliases.get("old", []))

            entry = {
                "slug": slug,
                "title": title,
                "source": icon.get("source", ""),
                "aliases": [a.lower() for a in all_aliases],
            }

            # Index by title
            _simple_icons_cache["by_title"][title.lower()] = entry

            # Index by each alias
            for alias in all_aliases:
                _simple_icons_cache["by_alias"][alias.lower()] = entry

        total = len(_simple_icons_cache["by_title"]) + len(_simple_icons_cache["by_alias"])
        logging.debug(f"Loaded {len(_simple_icons_cache['by_title'])} Simple Icons ({total} total mappings)")

    except Exception as e:
        logging.warning(f"Error loading Simple Icons data: {e}")

    return _simple_icons_cache


def _extract_domain(url: str) -> str:
    """Extract domain from URL for verification."""
    if not url:
        return ""
    # Remove protocol and path
    domain = url.replace("https://", "").replace("http://", "").split("/")[0]
    # Remove www prefix
    if domain.startswith("www."):
        domain = domain[4:]
    return domain.lower()


def _is_word_boundary_match(search: str, target: str) -> bool:
    """Check if search term matches target at word boundaries.

    "Gemini" should match "Google Gemini" but "Go" should NOT match "Google".
    """
    search = search.lower()
    target = target.lower()

    # Split target into words
    words = target.replace("-", " ").replace(".", " ").split()

    # Search must match a complete word or be the target itself
    return search in words or search == target


def find_simple_icon_slug(name: str, description: str = "") -> Optional[str]:
    """Find Simple Icons slug with false positive prevention.

    Matching priority:
    1. Exact title match (HIGH confidence)
    2. Alias match (HIGH confidence)
    3. Suffix-stripped match (MEDIUM confidence)
    4. Word boundary substring match (only if name >= 4 chars)

    Args:
        name: Entity name to search for
        description: Entity description for domain verification (bonus, not required)

    Returns slug or None if no confident match.
    """
    icons = _load_simple_icons_data()
    if not icons.get("by_title"):
        return None

    name_lower = name.lower().strip()
    desc_lower = description.lower() if description else ""

    # 1. Exact title match (HIGH confidence)
    if name_lower in icons["by_title"]:
        match = icons["by_title"][name_lower]
        logging.debug(f"  [simpleicons] Exact title match: {name} -> {match['slug']}")
        return match["slug"]

    # 2. Alias match (HIGH confidence)
    if name_lower in icons["by_alias"]:
        match = icons["by_alias"][name_lower]
        logging.debug(f"  [simpleicons] Alias match: {name} -> {match['slug']} (alias of {match['title']})")
        return match["slug"]

    # 3. Suffix-stripped match (MEDIUM confidence)
    for suffix in [" api", " sdk", " plugin", " client", " integration", " app"]:
        if name_lower.endswith(suffix):
            stripped = name_lower[:-len(suffix)].strip()
            if stripped in icons["by_title"]:
                match = icons["by_title"][stripped]
                # Domain verification as bonus (prefer verified, accept without)
                source_domain = _extract_domain(match["source"])
                if source_domain and source_domain in desc_lower:
                    logging.debug(f"  [simpleicons] Suffix match (verified): {name} -> {match['slug']}")
                else:
                    logging.debug(f"  [simpleicons] Suffix match: {name} -> {match['slug']}")
                return match["slug"]

    # 4. Word boundary substring match (only if name >= MIN_SUBSTRING_LENGTH)
    if len(name_lower) >= MIN_SUBSTRING_LENGTH:
        # Look for icons where our name appears as a complete word
        best_match = None
        for title, entry in icons["by_title"].items():
            if _is_word_boundary_match(name_lower, title):
                # Prefer shorter titles (more specific match)
                if best_match is None or len(title) < len(best_match["title"]):
                    best_match = entry

        if best_match:
            logging.debug(f"  [simpleicons] Word boundary match: {name} -> {best_match['slug']} (from {best_match['title']})")
            return best_match["slug"]

    return None


# GitHub org mappings for brands where org name differs from brand
GITHUB_ORG_MAPPINGS = {
    "anthropic": "anthropics",
    "eliza": "elizaos",
    "elizaos": "elizaos",
}


def get_name_variations(name: str, aliases: list[str] = None, description: str = "") -> list[str]:
    """Generate variations of entity name for lookup.

    Args:
        name: Primary entity name
        aliases: Alternative names for the entity
        description: Entity description for domain verification

    Returns list of slugs to try, in priority order.
    """
    variations = []
    base = name.lower().strip()

    # 1. Try smart match against Simple Icons data first
    if matched_slug := find_simple_icon_slug(base, description):
        variations.append(matched_slug)

    # 2. Try aliases with smart match
    if aliases:
        for alias in aliases:
            if matched_slug := find_simple_icon_slug(alias, description):
                if matched_slug not in variations:
                    variations.append(matched_slug)

    # 3. Original name (slugified) as fallback for CDN direct lookup
    slug = base.replace(" ", "").replace(".", "").replace("-", "")
    if slug not in variations:
        variations.append(slug)

    # 4. Try without common suffixes (for CDN fallback)
    for suffix in [" api", " sdk", " plugin", " integration", " client"]:
        if base.endswith(suffix):
            clean = base[:-len(suffix)].replace(" ", "").replace(".", "")
            if clean not in variations:
                variations.append(clean)

    return variations


def fetch_reference_image(entity: dict) -> Optional[bytes]:
    """Try to fetch a reference image for an entity.

    Tries sources in priority order:
    1. Simple Icons (tech brands) - with smart matching
    2. GitHub avatar (with org mappings)
    3. Google Favicon (website fallback)

    Returns image bytes or None if not found.
    """
    name = entity.get("name", "")
    aliases = entity.get("aliases", [])
    description = entity.get("description", "")

    # Get all name variations to try (pass description for verification)
    variations = get_name_variations(name, aliases, description)

    # 1. Try Simple Icons with all variations
    for variant in variations:
        if img := fetch_simple_icon(variant):
            return img

    # 2. Try GitHub avatar
    github_url = entity.get("github_url", "")
    if github_url:
        # Extract org/user from URL
        parts = github_url.replace("https://github.com/", "").split("/")
        if parts and parts[0]:
            if img := fetch_github_avatar(parts[0]):
                return img

    # Try mapped GitHub orgs
    name_lower = name.lower().strip()
    if name_lower in GITHUB_ORG_MAPPINGS:
        if img := fetch_github_avatar(GITHUB_ORG_MAPPINGS[name_lower]):
            return img

    # Try guessing GitHub org from variations
    for variant in variations[:3]:  # Limit attempts
        if img := fetch_github_avatar(variant):
            return img

    # 3. Try Google Favicon
    website = entity.get("website", "")
    if website:
        if img := fetch_google_favicon(website):
            return img
    else:
        # Try guessing domain
        for variant in variations[:2]:
            for tld in [".com", ".ai"]:
                if img := fetch_google_favicon(f"{variant}{tld}"):
                    return img

    return None


# =============================================================================
# Prompt Building
# =============================================================================

# Prompt style for A/B testing (set via --prompt-style flag)
PROMPT_STYLE = "proportional"  # "exact" or "proportional"


def build_icon_prompt(
    entities: list[dict] | dict,
    batch: bool = True,
    entity_type: str = None,
    use_context: bool = True,
    prompt_style: str = None
) -> str:
    """Build prompt for icon generation.

    Args:
        entities: List of entities (batch) or single entity dict
        batch: If True, generate grid layout; if False, single icon
        entity_type: Override type for style selection (batch mode)
        use_context: Include context in prompts
        prompt_style: "exact" (pixel specs) or "proportional" (relative specs)
    """
    style = prompt_style or PROMPT_STYLE

    # Normalize to list
    if not batch:
        entities = [entities]

    if batch and len(entities) > 1:
        # Batch mode: grid of icons (square-ish layout)
        rows, cols = calculate_grid_dimensions(len(entities))

        entity_lines = []
        for i, entity in enumerate(entities, 1):
            name = entity.get("name", "Unknown")
            desc = entity.get("description", "")

            # Format: "1. Discord — gaming chat platform"
            line = f"{i}. {name}"
            if desc:
                line += f" — {desc}"
            entity_lines.append(line)

        entities_text = "\n".join(entity_lines)

        if style == "exact":
            # A/B Test A: Exact pixel specifications
            cell_size = 1024 // max(rows, cols)
            logo_size = int(cell_size * 0.7)

            return f"""Search the web for official logos, then generate a {rows}x{cols} grid image.

IMAGE SPECIFICATIONS:
- Output: exactly 1024x1024 pixels
- Grid: {rows} rows × {cols} columns = {len(entities)} equal cells
- Each cell: exactly {cell_size}x{cell_size} pixels
- Background: pure white (#FFFFFF)

CELL LAYOUT:
- Each logo centered exactly in its cell
- Logo size: {logo_size}x{logo_size} pixels max (70% of cell)
- Equal padding on all sides within each cell

Search for and recreate the ACTUAL OFFICIAL LOGOS of these companies/projects:

{entities_text}

CRITICAL:
- Use web search to find each brand's current official logo
- Recreate logos accurately based on search results
- Symbol/icon marks only (not wordmarks or text-based logos)
- Flat vector style, full brand colors
- Seamless cells with clean edges (no visible gridlines or borders)
- Leave cell WHITE if logo cannot be found"""

        else:
            # A/B Test B: Proportional specifications (default)
            return f"""Search the web for official logos, then generate a {rows}x{cols} grid image.

IMAGE SPECIFICATIONS:
- Square image output
- Grid: {rows} rows × {cols} columns = {len(entities)} equal cells
- Background: pure white (#FFFFFF)

CELL LAYOUT:
- Each cell: equal square portion of the image
- Each logo centered in its cell, ~70% of cell size
- Equal padding on all sides
- Seamless cells (no visible gridlines or borders between them)

Search for and recreate the ACTUAL OFFICIAL LOGOS of these companies/projects:

{entities_text}

CRITICAL:
- Use web search to find each brand's current official logo
- Recreate logos accurately based on search results
- Symbol/icon marks only (not wordmarks or text-based logos)
- Flat vector style, full brand colors
- Leave cell WHITE if logo cannot be found"""

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

        return f"""Search the web for the official logo, then generate a single logo/icon for: {name}

Type: {etype}
{details_text}

REQUIREMENTS:
- Use web search to find the actual official logo
- Background: pure white
- Logo centered with padding (~70% of image)
- Symbol/icon mark only (not wordmarks or text-based logos)
- Recreate the ACTUAL official logo accurately based on search results
- If not found via search, create a distinctive, professional icon
- Flat vector style, clean lines, full brand colors
- Should work at small sizes (high contrast, simple shapes)"""


def generate_image(
    prompt: str,
    aspect_ratio: str = "1:1",
    use_search: bool = True,
    reference_images: list[tuple[int, str, bytes]] = None
) -> tuple[bytes, str]:
    """Call OpenRouter to generate image with optional labeled reference images.

    Args:
        prompt: Text prompt for image generation
        aspect_ratio: Image aspect ratio (default "1:1" = 1024x1024)
            Supported: 1:1, 2:3, 3:2, 3:4, 4:3, 9:16, 16:9
        use_search: Enable web search grounding (text context only)
        reference_images: List of (grid_position, entity_name, image_bytes) tuples.
            Each image is labeled with its grid cell number and entity name.

    Returns:
        Tuple of (image_bytes, text_response) where text_response contains
        model's description/confidence about generated icons.
    """
    ref_count = len(reference_images) if reference_images else 0
    logging.info(f"Generating image via OpenRouter (refs={ref_count}, search={'on' if use_search else 'off'})...")

    # Build content array - interleave labels with images to prevent mixups
    content = []

    if reference_images:
        # First, show all labeled reference images with grid positions
        content.append({"type": "text", "text": "REFERENCE IMAGES WITH GRID CELL NUMBERS:"})
        for grid_pos, entity_name, img_bytes in reference_images:
            # Add label with cell number before each image
            content.append({"type": "text", "text": f"[Cell #{grid_pos}: {entity_name}]"})
            # Convert to base64 data URL
            b64 = base64.b64encode(img_bytes).decode("utf-8")
            # Detect image type from magic bytes
            if img_bytes[:4] == b'\x89PNG':
                mime = "image/png"
            elif img_bytes[:2] == b'\xff\xd8':
                mime = "image/jpeg"
            else:
                mime = "image/png"  # Default (SVGs should be converted to PNG already)
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}"}
            })
        content.append({"type": "text", "text": "---"})

    # Add the main prompt after reference images
    content.append({"type": "text", "text": prompt})

    request_json = {
        "model": IMAGE_MODEL,
        "modalities": ["image", "text"],
        "messages": [{"role": "user", "content": content}],
        "image_config": {
            "aspect_ratio": aspect_ratio
        }
    }

    # Enable web search grounding (OpenRouter's web plugin)
    # Note: Search provides TEXT context that helps model understand/verify reference images
    # Always enable if use_search=True - search COMPLEMENTS references, doesn't replace them
    if use_search:
        request_json["plugins"] = [{"id": "web", "max_results": 5}]

    # Debug: show request payload (excluding prompt for brevity)
    debug_payload = {k: v for k, v in request_json.items() if k != "messages"}
    logging.debug(f"Request payload: {json.dumps(debug_payload, indent=2)}")

    def make_request():
        resp = requests.post(
            OPENROUTER_ENDPOINT,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json=request_json,
            timeout=180
        )
        if not resp.ok:
            logging.error(f"API error response: {resp.text[:500]}")
        resp.raise_for_status()
        return resp

    response = retry_with_backoff(make_request)()
    result = response.json()

    # Debug: check for annotations (indicates search was used)
    if logging.getLogger().level <= logging.DEBUG:
        annotations = result.get("choices", [{}])[0].get("message", {}).get("annotations", [])
        if annotations:
            logging.debug(f"Search annotations found: {len(annotations)} citations")
        else:
            logging.debug("No search annotations in response")

    try:
        message = result["choices"][0]["message"]
        logging.debug(f"Response message keys: {message.keys()}")

        # Extract text response (model's description/confidence)
        text_response = message.get("content", "")
        logging.debug(f"Raw content type: {type(text_response)}, preview: {str(text_response)[:200]}")

        if isinstance(text_response, list):
            # Handle structured content format
            text_parts = [p.get("text", "") for p in text_response if p.get("type") == "text"]
            text_response = "\n".join(text_parts)
        elif not isinstance(text_response, str):
            text_response = str(text_response) if text_response else ""

        # Extract image - check multiple possible locations
        images = message.get("images", [])

        # OpenRouter may return images in content array for some models
        if not images and isinstance(message.get("content"), list):
            for part in message["content"]:
                if part.get("type") == "image_url":
                    images.append(part)
                elif part.get("type") == "image" and part.get("image_url"):
                    images.append(part)

        if not images:
            logging.error(f"No images found. Response text: {text_response[:500] if text_response else 'None'}")
            logging.debug(f"Full message: {json.dumps(message, indent=2)[:1000]}")
            raise ValueError("No images in response")

        image_url = images[0]["image_url"]["url"]
        if not image_url.startswith("data:"):
            raise ValueError(f"Unexpected image URL format: {image_url[:50]}")

        base64_data = image_url.split(",", 1)[1]
        image_bytes = base64.b64decode(base64_data)

        if text_response:
            logging.info(f"Model response: {text_response[:200]}...")

        return image_bytes, text_response

    except (KeyError, IndexError) as e:
        logging.error(f"Failed to extract image: {e}")
        logging.error(f"Response: {json.dumps(result, indent=2)[:500]}")
        raise ValueError(f"Failed to extract image from API response: {e}")


def calculate_grid_dimensions(num_icons: int) -> tuple[int, int]:
    """Calculate square-ish grid dimensions for N icons.

    Returns (rows, cols) optimized for square grids:
    - 1-4 icons: 2x2
    - 5-9 icons: 3x3
    - 10-16 icons: 4x4
    """
    import math
    cols = math.ceil(math.sqrt(num_icons))
    rows = math.ceil(num_icons / cols)
    return rows, cols


def parse_grid_from_text(text_response: str, num_icons: int) -> tuple[int, int] | None:
    """Try to parse grid dimensions from model's text response.

    Looks for patterns like:
    - "GRID: 2x2" or "LAYOUT: 4x4"
    - "2 rows x 2 columns"
    - "arranged in a 3x3 grid"

    Returns (rows, cols) or None if not found.
    """
    import re

    # Pattern: NxM or N×M
    match = re.search(r'(\d+)\s*[x×]\s*(\d+)', text_response, re.IGNORECASE)
    if match:
        rows, cols = int(match.group(1)), int(match.group(2))
        # Sanity check: should fit our icons
        if rows * cols >= num_icons and rows <= 4 and cols <= 4:
            return rows, cols

    return None


def slice_grid(image_bytes: bytes, num_icons: int, text_response: str = "") -> list[Image.Image]:
    """Slice a grid image into individual icons.

    Args:
        image_bytes: PNG image data
        num_icons: Number of icons to extract
        text_response: Model's text response (may contain layout info)
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    width, height = img.size

    # Try to get grid dimensions from model's text response first
    parsed_dims = parse_grid_from_text(text_response, num_icons) if text_response else None

    if parsed_dims:
        rows, cols = parsed_dims
        logging.info(f"Using model-specified grid: {rows}x{cols}")
    else:
        # Fall back to calculated square-ish grid
        rows, cols = calculate_grid_dimensions(num_icons)
        logging.debug(f"Using calculated grid: {rows}x{cols}")

    cell_width = width // cols
    cell_height = height // rows

    logging.debug(f"Slicing {width}x{height} image into {rows}x{cols} grid ({cell_width}x{cell_height} cells)")

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


def generate_batch(entity_type: str, entities: list[dict], use_context: bool = True, use_search: bool = True, prompt_style: str = None) -> list[Path]:
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

    # Try to fetch reference images for each entity
    # Store as (grid_position, entity_name, image_bytes) tuples to ensure correct placement
    reference_images = []
    for idx, entity in enumerate(batch, start=1):
        name = entity.get("name", "?")
        ref_img = fetch_reference_image(entity)
        if ref_img:
            reference_images.append((idx, name, ref_img))

    if reference_images:
        ref_names = [f"{pos}:{name}" for pos, name, _ in reference_images]
        logging.info(f"  Found {len(reference_images)} reference images: {', '.join(ref_names)}")

    # Build prompt and generate
    prompt = build_icon_prompt(batch, batch=True, entity_type=entity_type, use_context=use_context, prompt_style=prompt_style)

    # If we have reference images, modify prompt to emphasize using them
    if reference_images:
        ref_list = [f"Cell #{pos}: {name}" for pos, name, _ in reference_images]
        prompt = f"""Above are labeled reference images with their GRID CELL NUMBERS.

REFERENCE IMAGE ASSIGNMENTS:
{chr(10).join(ref_list)}

TASK: Place each logo in its NUMBERED grid cell position.

{prompt}

CRITICAL PLACEMENT RULES:
- [Cell #N: EntityName] means put that logo in grid cell N (numbered left-to-right, top-to-bottom)
- Use web search to verify what each logo should look like
- Reference images show the correct logo - match colors, shapes, proportions
- For cells WITHOUT a reference image, search for the official logo"""

    logging.debug(f"Prompt:\n{prompt}")

    image_bytes, text_response = generate_image(
        prompt,
        use_search=use_search,
        reference_images=reference_images if reference_images else None
    )

    # Save raw grid for debugging
    grid_path = ICONS_DIR / f"_grid_{entity_type}_latest.png"
    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    grid_path.write_bytes(image_bytes)
    logging.info(f"Saved grid: {grid_path}")

    # Save model's text response for post-processing insights
    if text_response:
        response_path = ICONS_DIR / f"_grid_{entity_type}_latest.txt"
        response_path.write_text(text_response)
        logging.info(f"Saved model response: {response_path}")

    # Slice into individual icons (pass text_response for layout hints)
    icons = slice_grid(image_bytes, len(batch), text_response)

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


def generate_single(entity: dict, use_context: bool = True, skip_coingecko: bool = False, force: bool = False, use_search: bool = True) -> Optional[Path]:
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
    image_bytes, text_response = generate_image(prompt, use_search=use_search)

    if text_response:
        logging.info(f"Model notes: {text_response[:150]}...")

    # Load and process
    icon = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    processed = process_icon(icon)

    output_path = save_icon(processed, entity)
    logging.info(f"Saved: {output_path}")

    return output_path


def sync_manifest_icons():
    """Sync icon_paths in manifest with actual files on disk."""
    inventory = load_inventory()
    all_icons = [f.name for f in ICONS_DIR.iterdir()
                 if f.is_file() and f.suffix.lower() in ('.png', '.jpg', '.jpeg')
                 and not f.name.startswith('_')]

    updated = 0
    for entity in inventory.get("entities", []):
        base = get_icon_base(entity)
        # Find matching icons (base-1.png, base-2.png, etc.)
        matches = [f for f in all_icons if f.startswith(base + "-") or f.startswith(base + ".")]

        old_paths = entity.get("icon_paths", [])
        new_paths = [f"icons/{m}" for m in sorted(matches)]

        if new_paths != old_paths:
            if new_paths:
                entity["icon_paths"] = new_paths
            else:
                entity.pop("icon_paths", None)
            updated += 1

    with open(ENTITY_INVENTORY, "w") as f:
        json.dump(inventory, f, indent=2)

    return updated


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
        help="Generate 4x4 grid batch for entity type (token, project, user)"
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
    mode.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Interactive mode: generate, curate, repeat"
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
        "--no-search",
        action="store_true",
        help="Disable Google Search grounding (faster, but less accurate for known brands)"
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
    parser.add_argument(
        "--prompt-style",
        choices=["exact", "proportional"],
        default="proportional",
        help="Prompt style: 'exact' (pixel specs) or 'proportional' (relative specs). Default: proportional"
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

    # Context lookup and search grounding enabled by default
    use_context = not args.no_context
    use_search = not args.no_search

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

            saved = generate_batch(entity_type, to_generate, use_context=use_context, use_search=use_search, prompt_style=args.prompt_style)
            logging.info(f"Generated {len(saved)} icons")

        elif args.entity:
            # Single entity mode
            entity = get_entity_info(inventory, args.entity, args.entity_type)
            if not entity:
                logging.error(f"Entity not found: {args.entity}")
                return 1

            generate_single(entity, use_context=use_context, force=args.force, use_search=use_search)

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
                            generate_batch(et, batch, use_context=use_context, use_search=use_search, prompt_style=args.prompt_style)
                else:
                    # Non-tokens: AI batch generation
                    for i in range(0, min(len(missing), args.limit), GRID_SIZE * GRID_SIZE):
                        batch = missing[i:i + GRID_SIZE * GRID_SIZE]
                        generate_batch(et, batch, use_context=use_context, use_search=use_search, prompt_style=args.prompt_style)
        elif args.interactive:
            # Interactive curation loop
            entity_type = args.entity_type or "project"
            batch_size = min(args.limit, 9)  # Cap at 9 for search token limits

            print(f"\n=== Interactive Icon Generation ({entity_type}) ===")
            print(f"Batch size: {batch_size}")
            print(f"Icons dir: {ICONS_DIR}")
            print("\nWorkflow: Generate → Curate (delete bad ones) → Enter → Repeat")
            print("Deleted icons → entity marked 'review' (won't regenerate)")
            print("Press Ctrl+C to exit\n")

            round_num = 0
            while True:
                round_num += 1

                # Reload inventory and get missing (picks up deletions)
                inventory = load_inventory()
                missing = get_missing_entities(inventory, entity_type)

                if not missing:
                    print(f"\nNo more missing {entity_type} icons!")
                    break

                print(f"\n--- Round {round_num}: {len(missing)} missing ---")
                batch = missing[:batch_size]
                names = [e.get("name", "?") for e in batch]
                print(f"Generating: {', '.join(names)}")

                try:
                    saved = generate_batch(entity_type, batch, use_context=use_context, use_search=use_search, prompt_style=args.prompt_style)
                    print(f"\nGenerated {len(saved)} icons:")
                    for p in saved:
                        print(f"  {p}")

                    # Show model's text response if available
                    response_file = ICONS_DIR / f"_grid_{entity_type}_latest.txt"
                    if response_file.exists():
                        text = response_file.read_text().strip()
                        if text:
                            print(f"\nModel notes:\n{text[:500]}")
                except Exception as e:
                    logging.error(f"Generation failed: {e}")
                    continue

                # Map saved paths to entities for tracking
                saved_map = {p.name: batch[i] for i, p in enumerate(saved) if i < len(batch)}

                # Wait for user curation
                print(f"\n>>> Review icons in: {ICONS_DIR}")
                print(">>> Delete any bad ones, then press Enter to continue (or 'q' to quit)")

                try:
                    user_input = input().strip().lower()
                    if user_input in ('q', 'quit', 'exit'):
                        break
                except (KeyboardInterrupt, EOFError):
                    print("\nExiting...")
                    break

                # Check which icons were kept vs deleted
                kept = []
                deleted = []
                for filename, entity in saved_map.items():
                    if (ICONS_DIR / filename).exists():
                        kept.append(entity.get("name"))
                    else:
                        deleted.append(entity.get("name"))

                # Update manifest: mark deleted as "review", sync kept icons
                inventory = load_inventory()
                for entity in inventory.get("entities", []):
                    name = entity.get("name")
                    if name in deleted:
                        entity["status"] = "review"
                        entity.pop("icon_paths", None)

                with open(ENTITY_INVENTORY, "w") as f:
                    json.dump(inventory, f, indent=2)

                # Sync icon_paths for kept ones
                updated = sync_manifest_icons()

                print(f"Kept: {len(kept)}, Marked for review: {len(deleted)}")
                if deleted:
                    print(f"  Review: {', '.join(deleted)}")

            print("\nDone!")

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
