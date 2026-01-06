#!/usr/bin/env python3
"""
Enrich facts.json with media URLs from aggregated data and poster manifest.

Combines:
1. Source media (images/videos) from aggregated daily JSON content
2. Generated poster CDN URLs from poster manifest

Usage:
  python scripts/etl/enrich-facts-media.py \\
    -f the-council/facts/2026-01-06.json \\
    -a the-council/aggregated/2026-01-06.json \\
    -m media/2026-01-06/manifest.json \\
    -v

  # Dry run
  python scripts/etl/enrich-facts-media.py \\
    -f the-council/facts/2026-01-06.json \\
    --dry-run -v
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Default CDN base URL
DEFAULT_CDN_BASE = "https://m3tv.b-cdn.net/media"


def validate_url(url: str) -> bool:
    """Validate URL is well-formed and uses http/https."""
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def deduplicate_urls(urls: list[str]) -> list[str]:
    """Remove duplicate URLs while preserving order."""
    seen = set()
    result = []
    for url in urls:
        if not url:
            continue
        normalized = url.rstrip("/")
        if normalized not in seen:
            seen.add(normalized)
            result.append(url)
    return result


def extract_source_media(aggregated_path: Path) -> tuple[list[str], list[str]]:
    """
    Extract images and videos from aggregated JSON.

    Parses ai_news_elizaos_daily_json_* and ai_news_elizaos_json_* entries
    to collect media URLs from nested categories.

    Returns:
        (images_list, videos_list)
    """
    images = []
    videos = []

    try:
        with open(aggregated_path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Failed to read aggregated file: {e}")
        return [], []

    # Look for ai_news entries with JSON content
    for key, value in data.items():
        if not isinstance(value, dict):
            continue

        # Match keys like ai_news_elizaos_daily_json_*, ai_news_elizaos_json_*
        if not (key.startswith("ai_news") and "json" in key):
            continue

        content = value.get("content", {})
        if not isinstance(content, dict):
            continue

        # Navigate: content.categories[].content[].images/videos
        categories = content.get("categories", [])
        for category in categories:
            if not isinstance(category, dict):
                continue
            for item in category.get("content", []):
                if not isinstance(item, dict):
                    continue

                # Extract images
                item_images = item.get("images", [])
                if isinstance(item_images, list):
                    images.extend(item_images)
                elif isinstance(item_images, str) and item_images:
                    images.append(item_images)

                # Extract videos
                item_videos = item.get("videos", [])
                if isinstance(item_videos, list):
                    videos.extend(item_videos)
                elif isinstance(item_videos, str) and item_videos:
                    videos.append(item_videos)

    # Validate and deduplicate
    images = deduplicate_urls([u for u in images if validate_url(u)])
    videos = deduplicate_urls([u for u in videos if validate_url(u)])

    return images, videos


def extract_poster_urls(manifest_path: Path, cdn_base: str = None) -> dict:
    """
    Extract poster URLs from manifest.json.

    Args:
        manifest_path: Path to poster manifest
        cdn_base: CDN base URL for constructing fallback URLs

    Returns:
        {category: cdn_url} mapping, e.g. {"overall": "https://...", "github_updates": "https://..."}
    """
    if not manifest_path or not manifest_path.exists():
        return {}

    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Failed to read manifest: {e}")
        return {}

    posters = {}
    cdn_urls = manifest.get("cdn_urls", {})
    facts_date = manifest.get("facts_date")

    # Construct fallback CDN base if not provided
    if not cdn_base and facts_date:
        cdn_base = f"{DEFAULT_CDN_BASE}/{facts_date}"

    # Process each generation
    for gen in manifest.get("generations", []):
        category = gen.get("category", "").replace("-", "_")
        output_file = gen.get("output_file")

        # Prefer cdn_url from generation, fall back to cdn_urls map, then construct
        cdn_url = (
            gen.get("cdn_url") or
            cdn_urls.get(output_file) or
            (f"{cdn_base}/{output_file}" if cdn_base and output_file else None)
        )

        if category and cdn_url and validate_url(cdn_url):
            posters[category] = cdn_url

    # Handle icon sheet
    icon_sheet = manifest.get("icon_sheet", {})
    if icon_sheet:
        output_file = icon_sheet.get("output_file")
        cdn_url = (
            icon_sheet.get("cdn_url") or
            cdn_urls.get(output_file) or
            (f"{cdn_base}/{output_file}" if cdn_base and output_file else None)
        )
        if cdn_url and validate_url(cdn_url):
            posters["icon_sheet"] = cdn_url

    return posters


def merge_media_into_facts(
    facts: dict,
    source_images: list[str],
    source_videos: list[str],
    posters: dict
) -> dict:
    """
    Merge media URLs into facts structure.

    Structure:
    - facts["images"] = [source_images + poster_urls] (flat array)
    - facts["videos"] = [source_videos] (flat array)
    - facts["overall_poster"] = posters["overall"] (top-level)
    - facts["icon_sheet"] = posters["icon_sheet"] (top-level)
    - facts["categories"][cat]["poster"] = url (per dict-type category)
    """
    # Build images array: source media + all poster URLs
    all_images = source_images.copy()
    for category, url in posters.items():
        if url and url not in all_images:
            all_images.append(url)

    facts["images"] = all_images
    facts["videos"] = source_videos

    # Set overall poster at top level
    if "overall" in posters:
        facts["overall_poster"] = posters["overall"]

    # Set icon sheet at top level
    if "icon_sheet" in posters:
        facts["icon_sheet"] = posters["icon_sheet"]

    # Set per-category posters (only for dict-type categories)
    categories = facts.get("categories", {})
    for cat_name, cat_content in categories.items():
        if cat_name in posters and isinstance(cat_content, dict):
            cat_content["poster"] = posters[cat_name]

    # Update metadata
    if "_metadata" not in facts:
        facts["_metadata"] = {}
    facts["_metadata"]["media_enriched_at"] = datetime.utcnow().isoformat() + "Z"
    facts["_metadata"]["source_images_count"] = len(source_images)
    facts["_metadata"]["source_videos_count"] = len(source_videos)
    facts["_metadata"]["poster_count"] = len(posters)

    return facts


def enrich_facts(
    facts_path: Path,
    aggregated_path: Path = None,
    manifest_path: Path = None,
    cdn_base: str = None,
    dry_run: bool = False,
    output_path: Path = None,
) -> bool:
    """
    Main enrichment function with graceful degradation.

    Args:
        facts_path: Path to facts JSON file
        aggregated_path: Path to aggregated JSON file (optional)
        manifest_path: Path to poster manifest (optional)
        cdn_base: CDN base URL for constructing poster URLs
        dry_run: If True, show changes without writing
        output_path: Output path (default: overwrite input)

    Returns:
        True if successful
    """
    # Load facts file
    try:
        with open(facts_path) as f:
            facts = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to read facts file: {e}")
        return False

    source_images, source_videos = [], []
    posters = {}

    # Extract source media (optional)
    if aggregated_path and aggregated_path.exists():
        source_images, source_videos = extract_source_media(aggregated_path)
        logger.info(f"Extracted {len(source_images)} images, {len(source_videos)} videos from aggregated")
    else:
        logger.info("No aggregated file provided, skipping source media extraction")

    # Extract poster URLs (optional)
    if manifest_path and manifest_path.exists():
        posters = extract_poster_urls(manifest_path, cdn_base)
        logger.info(f"Extracted {len(posters)} poster URLs from manifest")
    else:
        logger.info("No manifest file provided, skipping poster extraction")

    # Skip if nothing to add
    if not source_images and not source_videos and not posters:
        logger.warning("No media found to enrich - skipping")
        return True  # Not an error, just nothing to do

    # Merge media into facts
    enriched = merge_media_into_facts(facts, source_images, source_videos, posters)

    if dry_run:
        logger.info("Dry run - would add:")
        logger.info(f"  images: {len(enriched.get('images', []))} URLs")
        logger.info(f"  videos: {len(enriched.get('videos', []))} URLs")
        if "overall_poster" in enriched:
            logger.info(f"  overall_poster: {enriched['overall_poster']}")
        if "icon_sheet" in enriched:
            logger.info(f"  icon_sheet: {enriched['icon_sheet']}")

        # Show per-category posters
        for cat_name, cat_content in enriched.get("categories", {}).items():
            if isinstance(cat_content, dict) and "poster" in cat_content:
                logger.info(f"  categories.{cat_name}.poster: {cat_content['poster']}")
        return True

    # Write output
    output = output_path or facts_path
    try:
        with open(output, "w") as f:
            json.dump(enriched, f, indent=2)
        logger.info(f"Wrote enriched facts to: {output}")
        return True
    except IOError as e:
        logger.error(f"Failed to write output: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Enrich facts.json with media URLs from aggregated data and poster manifest",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "-f", "--facts",
        type=Path,
        required=True,
        help="Path to facts JSON file",
    )
    parser.add_argument(
        "-a", "--aggregated",
        type=Path,
        help="Path to aggregated JSON file (auto-detected from date if not provided)",
    )
    parser.add_argument(
        "-m", "--manifest",
        type=Path,
        help="Path to poster manifest JSON (auto-detected from date if not provided)",
    )
    parser.add_argument(
        "--cdn-base",
        help=f"CDN base URL for constructing poster URLs (default: {DEFAULT_CDN_BASE}/{{date}})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be added without writing",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output path (default: overwrite input)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate facts file exists
    if not args.facts.exists():
        logger.error(f"Facts file not found: {args.facts}")
        sys.exit(1)

    # Try to auto-detect paths from facts filename if not provided
    facts_date = None
    facts_name = args.facts.stem
    if len(facts_name) == 10 and facts_name[4] == "-" and facts_name[7] == "-":
        facts_date = facts_name  # Looks like YYYY-MM-DD

    aggregated_path = args.aggregated
    if not aggregated_path and facts_date:
        auto_path = Path(f"the-council/aggregated/{facts_date}.json")
        if auto_path.exists():
            aggregated_path = auto_path
            logger.debug(f"Auto-detected aggregated: {aggregated_path}")

    manifest_path = args.manifest
    if not manifest_path and facts_date:
        # Try multiple manifest locations
        for pattern in [f"media/{facts_date}/manifest.json", f"media/daily/{facts_date}/manifest.json"]:
            auto_path = Path(pattern)
            if auto_path.exists():
                manifest_path = auto_path
                logger.debug(f"Auto-detected manifest: {manifest_path}")
                break

    cdn_base = args.cdn_base
    if not cdn_base and facts_date:
        cdn_base = f"{DEFAULT_CDN_BASE}/{facts_date}"

    success = enrich_facts(
        facts_path=args.facts,
        aggregated_path=aggregated_path,
        manifest_path=manifest_path,
        cdn_base=cdn_base,
        dry_run=args.dry_run,
        output_path=args.output,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
