#!/usr/bin/env python3
"""
Backfill AI-generated images for historical dates using Nano Banana Pro.

Supports reference images for character consistency and multiple art styles.

Usage examples:
  # Generate for last 7 days (default editorial style)
  python scripts/posters/backfill-ai-images.py --days 7

  # Generate with a specific art style
  python scripts/posters/backfill-ai-images.py --days 7 --style anime
  python scripts/posters/backfill-ai-images.py --days 7 --style vintage

  # Generate with council characters for consistency
  python scripts/posters/backfill-ai-images.py --days 7 --use-council
  python scripts/posters/backfill-ai-images.py --days 7 --style council

  # Generate with specific characters
  python scripts/posters/backfill-ai-images.py --days 7 --characters eliza marc

  # Generate for specific dates
  python scripts/posters/backfill-ai-images.py --dates 2025-12-01 2025-12-05 2025-12-10

  # Generate for date range
  python scripts/posters/backfill-ai-images.py --from 2025-12-01 --to 2025-12-10

  # Use custom prompt instead of facts-based generation
  python scripts/posters/backfill-ai-images.py --dates 2025-12-01 --custom-prompt "A solarpunk city at dawn"

  # Skip existing images
  python scripts/posters/backfill-ai-images.py --days 30 --skip-existing

  # Dry run to see what would be generated
  python scripts/posters/backfill-ai-images.py --days 7 --dry-run

  # List available styles
  python scripts/posters/backfill-ai-images.py --list-styles
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# Import from main generate-ai-image script
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from importlib.util import spec_from_file_location, module_from_spec
spec = spec_from_file_location("generate_ai_image", SCRIPT_DIR / "generate-ai-image.py")
generate_ai_image = module_from_spec(spec)
spec.loader.exec_module(generate_ai_image)

# Re-export needed functions and constants
OPENROUTER_API_KEY = generate_ai_image.OPENROUTER_API_KEY
FACTS_DIR = generate_ai_image.FACTS_DIR
OUTPUT_DIR = generate_ai_image.OUTPUT_DIR
DEFAULT_REFERENCES = generate_ai_image.DEFAULT_REFERENCES

load_facts = generate_ai_image.load_facts
generate_image_prompt = generate_ai_image.generate_image_prompt
generate_image = generate_ai_image.generate_image
get_available_styles = generate_ai_image.get_available_styles
style_requires_references = generate_ai_image.style_requires_references
load_style_presets = generate_ai_image.load_style_presets

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def get_dates_from_args(args) -> list[str]:
    """Parse command line args to get list of dates to process."""
    dates = []

    if args.dates:
        # Specific dates provided
        for d in args.dates:
            try:
                datetime.strptime(d, "%Y-%m-%d")
                dates.append(d)
            except ValueError:
                logging.error(f"Invalid date format: {d} (use YYYY-MM-DD)")
                sys.exit(1)

    elif args.days:
        # Last N days
        today = datetime.now()
        for i in range(args.days):
            date = today - timedelta(days=i)
            dates.append(date.strftime("%Y-%m-%d"))

    elif args.from_date and args.to_date:
        # Date range
        try:
            start = datetime.strptime(args.from_date, "%Y-%m-%d")
            end = datetime.strptime(args.to_date, "%Y-%m-%d")
        except ValueError as e:
            logging.error(f"Invalid date format: {e}")
            sys.exit(1)

        if start > end:
            start, end = end, start

        current = start
        while current <= end:
            dates.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)

    else:
        # Default: today only
        dates.append(datetime.now().strftime("%Y-%m-%d"))

    return dates


def get_reference_images(args) -> list[Path]:
    """Get reference images based on CLI args."""
    images = []

    if args.references:
        for ref in args.references:
            path = Path(ref)
            if path.exists():
                images.append(path)

    elif args.characters:
        for char in args.characters:
            char_lower = char.lower()
            if char_lower in DEFAULT_REFERENCES:
                images.append(DEFAULT_REFERENCES[char_lower])

    elif args.use_council:
        images = [p for p in DEFAULT_REFERENCES.values() if p.exists()]

    return images


def process_date(date_str: str, style: str, custom_prompt: Optional[str],
                 skip_existing: bool, dry_run: bool,
                 reference_images: Optional[list[Path]] = None) -> bool:
    """Process a single date. Returns True if successful."""
    # Determine output filename based on style
    if style != "editorial":
        output_path = OUTPUT_DIR / f"{date_str}_ai-{style}.png"
    else:
        output_path = OUTPUT_DIR / f"{date_str}_ai-daily.png"

    if skip_existing and output_path.exists():
        logging.info(f"[{date_str}] Skipping - image already exists: {output_path.name}")
        return True

    if dry_run:
        ref_info = f" (with {len(reference_images)} reference images)" if reference_images else ""
        if custom_prompt:
            logging.info(f"[{date_str}] Would generate with style '{style}'{ref_info}: {custom_prompt[:50]}...")
        else:
            try:
                facts = load_facts(date_str)
                if facts:
                    logging.info(f"[{date_str}] Would generate with style '{style}'{ref_info} (summary: {facts.get('overall_summary', 'N/A')[:50]}...)")
                else:
                    logging.info(f"[{date_str}] Would skip - no facts available")
            except FileNotFoundError:
                logging.info(f"[{date_str}] Would skip - no facts file")
        return True

    try:
        character_names = [p.stem for p in reference_images] if reference_images else []

        if custom_prompt:
            prompt = custom_prompt
            logging.info(f"[{date_str}] Using custom prompt with style '{style}'")
        else:
            try:
                facts = load_facts(date_str)
            except FileNotFoundError:
                logging.warning(f"[{date_str}] Skipping - no facts file")
                return False

            logging.info(f"[{date_str}] Generating prompt with style '{style}'...")
            prompt = generate_image_prompt(facts, style=style, character_names=character_names)

        logging.info(f"[{date_str}] Prompt: {prompt[:100]}...")
        if reference_images:
            logging.info(f"[{date_str}] Using {len(reference_images)} reference image(s) for consistency")
        logging.info(f"[{date_str}] Generating image...")

        image_bytes = generate_image(prompt, reference_images=reference_images)

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(image_bytes)

        logging.info(f"[{date_str}] Saved: {output_path}")
        return True

    except Exception as e:
        logging.error(f"[{date_str}] Failed: {e}")
        return False


def main():
    # Get available styles for help text
    available_styles = get_available_styles()
    styles_list = ", ".join(available_styles) if available_styles else "editorial, anime, infographic, council, risograph, vintage"

    parser = argparse.ArgumentParser(
        description="Backfill AI-generated images for historical dates using Nano Banana Pro",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Date selection (mutually exclusive groups)
    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument(
        "-d", "--days",
        type=int,
        help="Generate for last N days (including today)"
    )
    date_group.add_argument(
        "--dates",
        nargs="+",
        help="Specific dates to generate (YYYY-MM-DD format)"
    )

    # Date range (used together)
    parser.add_argument(
        "--from",
        dest="from_date",
        help="Start date for range (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--to",
        dest="to_date",
        help="End date for range (YYYY-MM-DD)"
    )

    # Style options
    parser.add_argument(
        "-s", "--style",
        default="editorial",
        help=f"Art style to use (default: editorial). Available: {styles_list}"
    )
    parser.add_argument(
        "--list-styles",
        action="store_true",
        help="List all available styles and exit"
    )

    # Reference image options (mutually exclusive)
    ref_group = parser.add_mutually_exclusive_group()
    ref_group.add_argument(
        "--use-council",
        action="store_true",
        help="Use all council character images (eliza, marc, peepo, spartan) for consistency"
    )
    ref_group.add_argument(
        "--characters", "-c",
        nargs="+",
        choices=list(DEFAULT_REFERENCES.keys()),
        help="Specific council characters to use as reference"
    )
    ref_group.add_argument(
        "--references", "-r",
        nargs="+",
        help="Custom reference image paths (up to 14 images)"
    )

    # Options
    parser.add_argument(
        "-p", "--custom-prompt",
        help="Use custom prompt instead of generating from facts"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip dates that already have generated images"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without making API calls"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Handle --list-styles
    if args.list_styles:
        presets = load_style_presets()
        styles = presets.get("styles", {})
        print("Available styles:")
        for name, config in styles.items():
            desc = config.get("description", "No description")
            requires_ref = " (requires --use-council)" if config.get("requires_references") else ""
            print(f"  {name}: {desc}{requires_ref}")
        return 0

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not OPENROUTER_API_KEY and not args.dry_run:
        logging.error("OPENROUTER_API_KEY environment variable not set")
        sys.exit(1)

    # Get dates to process
    dates = get_dates_from_args(args)

    if not dates:
        logging.error("No dates to process")
        sys.exit(1)

    # Get reference images for character consistency
    reference_images = get_reference_images(args)

    # Auto-enable council references if council style is selected
    style = args.style
    if style_requires_references(style) and not reference_images:
        logging.info(f"Style '{style}' requires references, auto-enabling council characters")
        reference_images = [p for p in DEFAULT_REFERENCES.values() if p.exists()]

    if reference_images:
        logging.info(f"Using {len(reference_images)} reference image(s): {[p.name for p in reference_images]}")

    logging.info(f"Processing {len(dates)} date(s): {dates[0]} to {dates[-1]}" if len(dates) > 1 else f"Processing date: {dates[0]}")
    logging.info(f"Using style: {style}")

    if args.dry_run:
        logging.info("DRY RUN - no images will be generated")

    # Process each date
    success = 0
    failed = 0

    for date_str in dates:
        result = process_date(
            date_str,
            style=style,
            custom_prompt=args.custom_prompt,
            skip_existing=args.skip_existing,
            dry_run=args.dry_run,
            reference_images=reference_images
        )
        if result:
            success += 1
        else:
            failed += 1

    # Summary
    logging.info(f"\nComplete: {success} succeeded, {failed} failed")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
