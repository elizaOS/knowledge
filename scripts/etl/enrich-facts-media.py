#!/usr/bin/env python3
"""
Enrich facts.json or source json-cdn files with media URLs.

Two modes:
1. Facts mode (default): Enrich facts.json with images/videos from aggregated data
   and poster URLs from manifest.
2. Source mode (--source): Enrich json-cdn files with poster URLs based on topic field.

Usage:
  # Facts mode: Enrich facts.json
  python scripts/etl/enrich-facts-media.py \\
    -f the-council/facts/2026-01-06.json \\
    -a the-council/aggregated/2026-01-06.json \\
    -m media/2026-01-06/manifest.json \\
    -v

  # Source mode: Enrich json-cdn file with poster URLs
  python scripts/etl/enrich-facts-media.py --source \\
    -f ai-news/elizaos/json-cdn/2026-01-03.json \\
    -m media/daily/2026-01-03/manifest.json \\
    --cdn-base "https://cdn.elizaos.news/media/daily/2026-01-03" \\
    -v

  # Dry run (either mode)
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
DEFAULT_CDN_BASE = "https://cdn.elizaos.news/posters"


def get_as_list(obj: dict, key: str) -> list:
    """
    Get field as list, handling both scalar and array values.

    Supports the ai-news format where:
    - Single items are scalar: {"images": "url"}
    - Multiple items are array: {"images": ["url1", "url2"]}
    - Empty fields are omitted entirely

    Examples:
        get_as_list({"images": "url"}, "images") → ["url"]
        get_as_list({"images": ["a", "b"]}, "images") → ["a", "b"]
        get_as_list({}, "images") → []
    """
    val = obj.get(key)
    if val is None:
        return []
    return val if isinstance(val, list) else [val]


# Topic → poster category mapping (for --source mode)
# Maps json-cdn category topics to poster filenames
TOPIC_TO_POSTER = {
    # GitHub-related topics
    "github_summary": "github_updates",
    "pull_request": "github_updates",
    "issue": "github_updates",
    "completed_items": "github_updates",
    "contributors": "github_updates",
    # Discord-related topics
    "discordrawdata": "discord_updates",
    "discord": "discord_updates",
    # Market-related topics
    "crypto market": "market_analysis",
    "market": "market_analysis",
}


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

                # Extract images (handles both scalar and array formats)
                images.extend(get_as_list(item, "images"))

                # Extract videos (handles both scalar and array formats)
                videos.extend(get_as_list(item, "videos"))

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
    posters: dict,
    skip_existing: bool = False,
) -> dict:
    """
    Merge media URLs into facts structure.

    Structure:
    - facts["images"] = [source_images + poster_urls] (flat array)
    - facts["videos"] = [source_videos] (flat array)
    - facts["overall_poster"] = posters["overall"] (top-level)
    - facts["icon_sheet"] = posters["icon_sheet"] (top-level)
    - facts["categories"][cat]["poster"] = url (per dict-type category)

    Args:
        skip_existing: If True, preserve existing values (don't overwrite upstream data)
    """
    # Build images array: source media + all poster URLs
    if not skip_existing or not facts.get("images"):
        all_images = source_images.copy()
        for category, url in posters.items():
            if url and url not in all_images:
                all_images.append(url)
        facts["images"] = all_images

    if not skip_existing or not facts.get("videos"):
        facts["videos"] = source_videos

    # Set overall poster at top level (skip if exists and flag set)
    if "overall" in posters:
        if not skip_existing or not facts.get("overall_poster"):
            facts["overall_poster"] = posters["overall"]

    # Set icon sheet at top level (skip if exists and flag set)
    if "icon_sheet" in posters:
        if not skip_existing or not facts.get("icon_sheet"):
            facts["icon_sheet"] = posters["icon_sheet"]

    # Set per-category posters (only for dict-type categories, skip if exists)
    categories = facts.get("categories", {})
    for cat_name, cat_content in categories.items():
        if cat_name in posters and isinstance(cat_content, dict):
            if not skip_existing or not cat_content.get("poster"):
                cat_content["poster"] = posters[cat_name]

    # Update metadata
    if "_metadata" not in facts:
        facts["_metadata"] = {}
    facts["_metadata"]["media_enriched_at"] = datetime.utcnow().isoformat() + "Z"
    facts["_metadata"]["source_images_count"] = len(source_images)
    facts["_metadata"]["source_videos_count"] = len(source_videos)
    facts["_metadata"]["poster_count"] = len(posters)

    return facts


def enrich_source_file(
    source_path: Path,
    manifest_path: Path,
    cdn_base: str = None,
    dry_run: bool = False,
    output_path: Path = None,
    skip_existing: bool = False,
) -> bool:
    """
    Enrich json-cdn source file with poster URLs based on topic field.

    This mode enriches the upstream source file (ai-news json-cdn output)
    by adding poster URLs to each category based on the topic field mapping.

    Args:
        source_path: Path to json-cdn source file
        manifest_path: Path to poster manifest
        cdn_base: CDN base URL for constructing poster URLs
        dry_run: If True, show changes without writing
        output_path: Output path (default: overwrite input)
        skip_existing: If True, preserve existing poster/meme URLs

    Returns:
        True if successful
    """
    # Load source file
    try:
        with open(source_path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to read source file: {e}")
        return False

    # Extract poster URLs from manifest
    if not manifest_path or not manifest_path.exists():
        logger.error(f"Manifest file not found: {manifest_path}")
        return False

    posters = extract_poster_urls(manifest_path, cdn_base)
    if not posters:
        logger.warning("No poster URLs extracted from manifest")
        return True  # Not an error, just nothing to do

    logger.info(f"Extracted {len(posters)} poster URLs from manifest")

    # Add poster to each category based on topic
    enriched_count = 0
    skipped_count = 0
    categories = data.get("categories", [])
    for cat in categories:
        if not isinstance(cat, dict):
            continue
        topic = cat.get("topic", "").lower()
        poster_key = TOPIC_TO_POSTER.get(topic)
        if poster_key and poster_key in posters:
            # Skip if already has poster and skip_existing is set
            if skip_existing and cat.get("poster"):
                skipped_count += 1
                logger.debug(f"  {topic} → skipped (existing: {cat.get('poster')[:50]}...)")
                continue
            cat["poster"] = posters[poster_key]
            enriched_count += 1
            logger.debug(f"  {topic} → {poster_key}")

    if skipped_count:
        logger.info(f"Skipped {skipped_count} categories with existing poster URLs")

    # Add overall poster at top level (skip if exists and flag set)
    if "overall" in posters:
        if not skip_existing or not data.get("poster"):
            data["poster"] = posters["overall"]
        elif skip_existing and data.get("poster"):
            logger.info(f"Skipped top-level poster (existing: {data.get('poster')[:50]}...)")

    # Add icon_sheet at top level (skip if exists and flag set)
    if "icon_sheet" in posters:
        if not skip_existing or not data.get("icon_sheet"):
            data["icon_sheet"] = posters["icon_sheet"]
        elif skip_existing and data.get("icon_sheet"):
            logger.info(f"Skipped icon_sheet (existing: {data.get('icon_sheet')[:50]}...)")

    if dry_run:
        logger.info("Dry run - would add:")
        logger.info(f"  categories enriched: {enriched_count}/{len(categories)}")
        if "poster" in data:
            logger.info(f"  poster: {data['poster']}")
        if "icon_sheet" in data:
            logger.info(f"  icon_sheet: {data['icon_sheet']}")
        for cat in categories:
            if isinstance(cat, dict) and "poster" in cat:
                logger.info(f"  {cat.get('topic', 'unknown')}.poster: {cat['poster']}")
        return True

    # Write output
    output = output_path or source_path
    try:
        with open(output, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Wrote enriched source to: {output} ({enriched_count} categories)")
        return True
    except IOError as e:
        logger.error(f"Failed to write output: {e}")
        return False


def enrich_facts(
    facts_path: Path,
    aggregated_path: Path = None,
    manifest_path: Path = None,
    cdn_base: str = None,
    dry_run: bool = False,
    output_path: Path = None,
    skip_existing: bool = False,
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
        skip_existing: If True, preserve existing media URLs

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
    enriched = merge_media_into_facts(facts, source_images, source_videos, posters, skip_existing)

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
    parser.add_argument(
        "--source",
        action="store_true",
        help="Enrich source file (json-cdn) instead of facts file. "
             "Adds poster URLs to categories based on topic field.",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip fields that already have valid URLs (preserve upstream values). "
             "Useful when upstream json-cdn already has poster/meme URLs.",
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

    # Handle --source mode (json-cdn enrichment) vs default (facts enrichment)
    if args.source:
        if not manifest_path:
            logger.error("--source mode requires -m/--manifest to be provided or auto-detected")
            sys.exit(1)
        success = enrich_source_file(
            source_path=args.facts,
            manifest_path=manifest_path,
            cdn_base=cdn_base,
            dry_run=args.dry_run,
            output_path=args.output,
            skip_existing=args.skip_existing,
        )
    else:
        success = enrich_facts(
            facts_path=args.facts,
            aggregated_path=aggregated_path,
            manifest_path=manifest_path,
            cdn_base=cdn_base,
            dry_run=args.dry_run,
            output_path=args.output,
            skip_existing=args.skip_existing,
        )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
