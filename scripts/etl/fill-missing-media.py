#!/usr/bin/env python3
"""
Fill missing posters/memes in json-cdn files using local generation pipeline.

Detects content items missing media and queues them for generation.
Works with both cleaned JSON (empty arrays omitted) and uncleaned JSON.

Usage:
    # Analyze what's missing (dry run)
    python scripts/etl/fill-missing-media.py -f ai-news/elizaos/json-cdn/2026-01-06.json --dry-run

    # Generate missing posters
    python scripts/etl/fill-missing-media.py -f ai-news/elizaos/json-cdn/2026-01-06.json --generate

    # Generate and save enriched output
    python scripts/etl/fill-missing-media.py -f input.json -o the-council/enriched/2026-01-06.json --generate
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Map category topics to illustration styles
TOPIC_STYLES = {
    "discord": "community-chat",
    "github": "code-development",
    "twitter": "social-media",
    "development": "technical",
    "community": "community",
    "announcements": "announcement",
    "partnerships": "business",
    "issues": "bug-fix",
    "contributors": "team",
}


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

# Default CDN base for generated media
DEFAULT_CDN_BASE = "https://cdn.elizaos.news/media/generated"


def extract_summary(text: str, max_chars: int = 200) -> str:
    """Extract a brief summary from markdown text for image generation prompt."""
    # Remove markdown headers
    lines = []
    for line in text.split('\n'):
        if line.startswith('#'):
            # Extract header text without #
            header_text = line.lstrip('#').strip()
            if header_text:
                lines.append(header_text)
            continue
        if line.strip():
            lines.append(line.strip())

    summary = ' '.join(lines)[:max_chars]
    if len(summary) >= max_chars:
        summary = summary.rsplit(' ', 1)[0] + '...'
    return summary


def infer_topic_from_title(title: str) -> str:
    """Infer topic from category title if not explicitly set."""
    title_lower = title.lower()

    if 'discord' in title_lower:
        return 'discord'
    elif 'github' in title_lower or 'issue' in title_lower or 'pr' in title_lower:
        return 'github'
    elif 'twitter' in title_lower or 'tweet' in title_lower:
        return 'twitter'
    elif 'contributor' in title_lower:
        return 'contributors'
    elif 'development' in title_lower or 'technical' in title_lower:
        return 'development'
    elif 'community' in title_lower:
        return 'community'
    elif 'announcement' in title_lower:
        return 'announcements'
    elif 'partner' in title_lower:
        return 'partnerships'
    else:
        return 'other'


def analyze_media_gaps(data: dict) -> dict:
    """
    Analyze json-cdn data for missing media.

    Works with both:
    - Cleaned JSON (empty arrays omitted)
    - Uncleaned JSON (empty arrays present)

    Returns:
        {
            "total_items": int,
            "missing_posters": [...],
            "missing_memes": [...],
            "has_overall_poster": bool,
            "has_icon_sheet": bool,
            "stats": {...}
        }
    """
    result = {
        "total_items": 0,
        "total_categories": 0,
        "missing_posters": [],
        "missing_memes": [],
        "has_overall_poster": bool(data.get("poster")),
        "has_icon_sheet": bool(data.get("icon_sheet")),
        "stats": {
            "items_with_posters": 0,
            "items_with_memes": 0,
            "items_with_images": 0,
            "categories_with_posters": 0,
        }
    }

    categories = data.get("categories", [])
    result["total_categories"] = len(categories)

    for cat_idx, category in enumerate(categories):
        if not isinstance(category, dict):
            continue

        cat_title = category.get("title", f"Category {cat_idx}")
        cat_topic = category.get("topic", "").lower() or infer_topic_from_title(cat_title)

        # Check category-level poster
        # .get() returns None if key missing, which is falsy
        if category.get("poster"):
            result["stats"]["categories_with_posters"] += 1
        else:
            result["missing_posters"].append({
                "type": "category",
                "category_idx": cat_idx,
                "item_idx": None,
                "title": cat_title,
                "topic": cat_topic,
                "summary": cat_title,
            })

        # Check content items
        content_items = category.get("content", [])
        for item_idx, item in enumerate(content_items):
            if not isinstance(item, dict):
                continue

            result["total_items"] += 1
            text = item.get("text", "")
            summary = extract_summary(text)

            # Check images (just for stats) - handles both scalar and array
            images = get_as_list(item, "images")
            if images:
                result["stats"]["items_with_images"] += 1

            # Check for posters - handles scalar, array, and missing
            posters = get_as_list(item, "posters")
            if posters:
                result["stats"]["items_with_posters"] += 1
            else:
                result["missing_posters"].append({
                    "type": "content",
                    "category_idx": cat_idx,
                    "item_idx": item_idx,
                    "title": cat_title,
                    "topic": cat_topic,
                    "summary": summary,
                    "has_images": bool(images),  # May want to skip if has images
                })

            # Check for memes - handles scalar, array, and missing
            memes = get_as_list(item, "memes")
            if memes:
                result["stats"]["items_with_memes"] += 1
            else:
                result["missing_memes"].append({
                    "type": "content",
                    "category_idx": cat_idx,
                    "item_idx": item_idx,
                    "title": cat_title,
                    "topic": cat_topic,
                    "summary": summary,
                })

    return result


def generate_poster_with_illustrate(
    summary: str,
    topic: str,
    output_path: Path,
    facts_file: Path = None,
) -> Optional[str]:
    """
    Generate a poster image using illustrate.py pipeline.

    Returns:
        Path to generated image, or None on failure
    """
    try:
        # Build command for illustrate.py
        cmd = [
            "python", "scripts/posters/illustrate.py",
            "--prompt", summary[:500],  # Limit prompt length
            "-o", str(output_path.parent),
        ]

        env = os.environ.copy()

        logger.debug(f"Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180,
            env=env,
            cwd=Path(__file__).parent.parent.parent,  # Repo root
        )

        if result.returncode == 0:
            # Find generated file
            if output_path.exists():
                logger.info(f"Generated poster: {output_path}")
                return str(output_path)
            # Check for any generated file in output dir
            generated = list(output_path.parent.glob("*.png"))
            if generated:
                logger.info(f"Generated poster: {generated[0]}")
                return str(generated[0])

        logger.warning(f"Poster generation failed: {result.stderr[:200]}")
        return None

    except subprocess.TimeoutExpired:
        logger.error("Poster generation timed out (180s)")
        return None
    except Exception as e:
        logger.error(f"Poster generation error: {e}")
        return None


def fill_missing_media(
    data: dict,
    gaps: dict,
    output_dir: Path,
    generate_posters: bool = True,
    generate_memes: bool = False,
    cdn_base: str = None,
    limit: int = None,
    skip_if_has_images: bool = True,
) -> tuple[dict, dict]:
    """
    Fill missing media in the data structure.

    Args:
        data: JSON data to enrich
        gaps: Output from analyze_media_gaps()
        output_dir: Directory for generated files
        generate_posters: Generate missing posters
        generate_memes: Generate missing memes (requires imgflip)
        cdn_base: CDN base URL for generated files
        limit: Max items to generate (for testing)
        skip_if_has_images: Skip poster generation if item has images

    Returns:
        Tuple of (updated_data, generation_stats)
    """
    # Extract date from data
    title = data.get("title", "")
    date_match = None
    if "20" in title:
        # Try to extract date from title like "Daily Report - 2026-01-06"
        import re
        match = re.search(r'(\d{4}-\d{2}-\d{2})', title)
        if match:
            date_match = match.group(1)

    date_str = date_match or datetime.now().strftime("%Y-%m-%d")
    media_dir = output_dir / date_str
    media_dir.mkdir(parents=True, exist_ok=True)

    stats = {
        "posters_generated": 0,
        "posters_failed": 0,
        "posters_skipped": 0,
        "memes_generated": 0,
        "memes_failed": 0,
    }

    cdn_base = cdn_base or DEFAULT_CDN_BASE

    # Generate missing posters
    if generate_posters:
        poster_gaps = gaps["missing_posters"]
        if limit:
            poster_gaps = poster_gaps[:limit]

        for i, gap in enumerate(poster_gaps):
            # Skip content items that already have images
            if skip_if_has_images and gap.get("has_images"):
                logger.debug(f"Skipping {gap['title'][:30]}... (has images)")
                stats["posters_skipped"] += 1
                continue

            cat_idx = gap["category_idx"]
            item_idx = gap["item_idx"]
            topic = gap["topic"]
            summary = gap["summary"]

            # Generate filename
            safe_topic = topic.replace(" ", "-").lower()[:20]
            if gap["type"] == "category":
                filename = f"cat-{cat_idx}-{safe_topic}.png"
            else:
                filename = f"cat-{cat_idx}-item-{item_idx}-{safe_topic}.png"

            output_path = media_dir / filename

            logger.info(f"[{i+1}/{len(poster_gaps)}] Generating: {filename}")

            poster_path = generate_poster_with_illustrate(
                summary=summary,
                topic=topic,
                output_path=output_path,
            )

            if poster_path:
                # Build CDN URL
                poster_url = f"{cdn_base}/{date_str}/{filename}"

                # Update data structure using new ai-news format
                # (singular key for single item, plural for multiple)
                if gap["type"] == "category":
                    data["categories"][cat_idx]["poster"] = poster_url
                else:
                    content = data["categories"][cat_idx]["content"][item_idx]
                    # Check existing posters using helper
                    existing = get_as_list(content, "posters")
                    if not existing:
                        # No existing posters - use scalar
                        content["posters"] = poster_url
                    elif len(existing) == 1:
                        # One existing scalar - convert to array
                        content["posters"] = existing + [poster_url]
                    else:
                        # Already array - append
                        content["posters"].append(poster_url)

                stats["posters_generated"] += 1
            else:
                stats["posters_failed"] += 1

    # Meme generation would require imgflip integration
    if generate_memes:
        logger.warning("Meme generation not yet implemented (requires imgflip API)")

    return data, stats


def main():
    parser = argparse.ArgumentParser(
        description="Fill missing posters/memes in json-cdn files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "-f", "--file",
        type=Path,
        required=True,
        help="Input json-cdn file",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file for enriched JSON",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("media/generated"),
        help="Directory for generated media files (default: media/generated)",
    )
    parser.add_argument(
        "--cdn-base",
        default=DEFAULT_CDN_BASE,
        help=f"CDN base URL (default: {DEFAULT_CDN_BASE})",
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate missing media (default: analysis only)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of items to generate (for testing)",
    )
    parser.add_argument(
        "--include-memes",
        action="store_true",
        help="Also generate missing memes (requires imgflip)",
    )
    parser.add_argument(
        "--force-all",
        action="store_true",
        help="Generate even for items that have images",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without doing it",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load input file
    if not args.file.exists():
        logger.error(f"File not found: {args.file}")
        sys.exit(1)

    with open(args.file) as f:
        data = json.load(f)

    # Analyze gaps
    gaps = analyze_media_gaps(data)

    # Print analysis
    print(f"\n{'='*60}")
    print(f"📊 Media Gap Analysis: {args.file.name}")
    print(f"{'='*60}")
    print(f"\n📁 Structure:")
    print(f"   Categories: {gaps['total_categories']}")
    print(f"   Content items: {gaps['total_items']}")

    print(f"\n✅ Present:")
    print(f"   Overall poster: {'Yes' if gaps['has_overall_poster'] else 'No'}")
    print(f"   Icon sheet: {'Yes' if gaps['has_icon_sheet'] else 'No'}")
    print(f"   Categories with posters: {gaps['stats']['categories_with_posters']}/{gaps['total_categories']}")
    print(f"   Items with posters: {gaps['stats']['items_with_posters']}/{gaps['total_items']}")
    print(f"   Items with memes: {gaps['stats']['items_with_memes']}/{gaps['total_items']}")
    print(f"   Items with images: {gaps['stats']['items_with_images']}/{gaps['total_items']}")

    print(f"\n❌ Missing:")
    print(f"   Posters needed: {len(gaps['missing_posters'])}")
    print(f"   Memes needed: {len(gaps['missing_memes'])}")

    if args.verbose or args.dry_run:
        if gaps["missing_posters"]:
            print(f"\n📸 Items needing posters:")
            for gap in gaps["missing_posters"][:10]:
                has_img = " (has images)" if gap.get("has_images") else ""
                print(f"   [{gap['type'][:3]}] {gap['title'][:45]}...{has_img}")
            if len(gaps["missing_posters"]) > 10:
                print(f"   ... and {len(gaps['missing_posters']) - 10} more")

    # Generate if requested
    if args.generate and not args.dry_run:
        print(f"\n{'='*60}")
        print("🎨 Generating missing media...")
        print(f"{'='*60}\n")

        updated_data, stats = fill_missing_media(
            data=data,
            gaps=gaps,
            output_dir=args.output_dir,
            generate_posters=True,
            generate_memes=args.include_memes,
            cdn_base=args.cdn_base,
            limit=args.limit,
            skip_if_has_images=not args.force_all,
        )

        print(f"\n📈 Generation Results:")
        print(f"   Posters generated: {stats['posters_generated']}")
        print(f"   Posters failed: {stats['posters_failed']}")
        print(f"   Posters skipped: {stats['posters_skipped']}")

        # Save output
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, 'w') as f:
                json.dump(updated_data, f, indent=2)
            print(f"\n✅ Saved enriched output: {args.output}")
        else:
            print("\n⚠️  No --output specified, enriched JSON not saved")
            print("   Use -o to save the enriched version")

    elif args.dry_run:
        skippable = sum(1 for g in gaps["missing_posters"] if g.get("has_images"))
        print(f"\n🔍 Dry run summary:")
        print(f"   Would generate: {len(gaps['missing_posters']) - skippable} posters")
        print(f"   Would skip: {skippable} (already have images)")
        if args.include_memes:
            print(f"   Would generate: {len(gaps['missing_memes'])} memes")

    else:
        print(f"\n💡 Next steps:")
        print(f"   --dry-run     Preview what would be generated")
        print(f"   --generate    Generate missing media")
        print(f"   --limit N     Test with N items first")


if __name__ == "__main__":
    main()
