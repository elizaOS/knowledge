#!/usr/bin/env python3
"""
Backfill AI-generated images for historical dates using Nano Banana Pro.

Supports reference images for character consistency (up to 14 images, 5 people).

Usage examples:
  # Generate for last 7 days
  python scripts/posters/backfill-ai-images.py --days 7

  # Generate with council characters for consistency
  python scripts/posters/backfill-ai-images.py --days 7 --use-council

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
"""

import os
import sys
import json
import base64
import requests
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# Config
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
LLM_MODEL = "openai/gpt-5.2"
IMAGE_MODEL = "google/gemini-3-pro-image-preview"

SCRIPT_DIR = Path(__file__).parent.resolve()
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent
FACTS_DIR = WORKSPACE_ROOT / "the-council" / "facts"
OUTPUT_DIR = WORKSPACE_ROOT / "posters"

# Default character reference images (council members)
DEFAULT_REFERENCES = {
    "eliza": SCRIPT_DIR / "eliza.png",
    "marc": SCRIPT_DIR / "marc.png",
    "peepo": SCRIPT_DIR / "peepo.png",
    "spartan": SCRIPT_DIR / "spartan.png",
}

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def load_facts(date_str: str) -> Optional[dict]:
    """Load facts JSON for a specific date."""
    facts_file = FACTS_DIR / f"{date_str}.json"

    if not facts_file.exists():
        logging.warning(f"No facts file for {date_str}")
        return None

    with open(facts_file) as f:
        return json.load(f)


def generate_image_prompt(facts: dict, use_characters: bool = False, character_names: list[str] = None) -> str:
    """Use LLM to create a detailed image prompt from facts summary."""
    summary = facts.get("overall_summary", "")

    if not summary:
        raise ValueError("No overall_summary found in facts")

    if use_characters and character_names:
        # Prompt for council character scenes
        system_prompt = f"""You are an expert AI art director creating illustrated poster art featuring the ElizaOS Council characters.

**Characters available** (reference images will be provided):
{', '.join(character_names)}

**Art Style Requirements:**
- Illustrated, hand-drawn aesthetic (NOT photorealistic)
- Think: editorial illustration, vintage poster art, risograph prints, flat design with texture
- Studio Ghibli-inspired, Moebius comics, or modern editorial illustration
- Clean lines, bold shapes, stylized characters
- Textured backgrounds (paper grain, halftone dots, watercolor washes)

**Your task:**
Given today's news summary, create a scene showing the council characters reacting to or discussing the day's themes.

**Prompt structure:**
1. **Scene**: What are the characters doing? (debating, celebrating, worried, strategizing)
2. **Setting**: Simple illustrated background (council chamber, abstract shapes, symbolic elements)
3. **Style**: "illustrated poster art style, hand-drawn aesthetic, [specific influence]"
4. **Colors**: Bold, limited palette (2-4 colors max)
5. **Mood**: Match the tone of the news (optimistic, tense, triumphant, cautious)

**Rules:**
- Feature the characters prominently - they ARE the subject
- NO photorealism, NO 3D renders, NO cinematic photography
- NO text, words, or typography in the image
- Keep it simple and iconic, like a movie poster or editorial spread
- Describe each character's pose/expression briefly

**Output ONLY the image prompt, nothing else.**"""
    else:
        # Prompt for standalone illustrated art (no characters)
        system_prompt = """You are an expert AI art director creating illustrated poster art.

**Art Style Requirements:**
- Illustrated, hand-drawn aesthetic (NOT photorealistic)
- Think: editorial illustration, vintage poster art, risograph prints, infographic art
- Moebius comics, Charley Harper, or modern flat design with texture
- Clean lines, bold shapes, symbolic imagery
- Textured backgrounds (paper grain, halftone dots, geometric patterns)

**Your task:**
Given today's tech/AI news summary, create an illustrated scene that captures the day's themes symbolically.

**Prompt structure:**
1. **Subject**: Symbolic visual (robots, abstract tech shapes, nature-meets-tech, metaphorical scenes)
2. **Composition**: Simple, iconic, poster-worthy
3. **Style**: "illustrated poster art, hand-drawn, [specific influence like risograph, vintage travel poster, editorial illustration]"
4. **Colors**: Bold, limited palette (2-4 colors)
5. **Mood**: Match the news tone

**Rules:**
- NO photorealism, NO 3D renders, NO cinematic photography
- NO text, words, logos, or typography
- NO literal screens, code, or UI elements
- Think symbolic and artistic, not literal
- Simple and iconic, not cluttered

**Output ONLY the image prompt, nothing else.**"""

    response = requests.post(
        OPENROUTER_ENDPOINT,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Today's tech/AI news summary:\n\n{summary}"}
            ]
        },
        timeout=60
    )
    response.raise_for_status()

    result = response.json()
    return result["choices"][0]["message"]["content"].strip()


def load_reference_image(path: Path) -> Optional[str]:
    """Load an image file and return as base64 data URL."""
    if not path.exists():
        return None

    suffix = path.suffix.lower()
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    mime_type = mime_types.get(suffix, "image/png")

    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{data}"


def create_reference_montage(image_paths: list[Path]) -> Optional[str]:
    """Create a montage of reference images using ImageMagick, return as base64 data URL."""
    import subprocess
    import tempfile

    if not image_paths:
        return None

    existing = [p for p in image_paths if p.exists()]
    if not existing:
        return None

    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name

        cmd = [
            "montage",
            *[str(p) for p in existing],
            "-tile", f"{len(existing)}x1",
            "-geometry", "256x256+10+10",
            "-background", "white",
            tmp_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return None

        with open(tmp_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")

        Path(tmp_path).unlink(missing_ok=True)
        return f"data:image/png;base64,{data}"

    except Exception:
        return None


def generate_image(prompt: str, reference_images: Optional[list[Path]] = None) -> bytes:
    """Call Nano Banana Pro to generate image, return PNG bytes."""
    content = []
    char_names = []

    if reference_images:
        char_names = [p.stem for p in reference_images if p.exists()]

        # Try montage first
        montage_url = create_reference_montage(reference_images)
        if montage_url:
            content.append({
                "type": "image_url",
                "image_url": {"url": montage_url}
            })
        else:
            # Fallback to individual images
            for img_path in reference_images[:14]:
                data_url = load_reference_image(img_path)
                if data_url:
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": data_url}
                    })

        # Prepend instruction about reference images
        ref_instruction = f"""The attached reference image shows the characters: {', '.join(char_names)}.
Use these EXACT character designs in the illustration. Maintain their appearance, colors, and style.

"""
        prompt = ref_instruction + prompt

    content.append({"type": "text", "text": prompt})

    response = requests.post(
        OPENROUTER_ENDPOINT,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/elizaOS/knowledge",
            "X-Title": "ElizaOS Daily AI Image"
        },
        json={
            "model": IMAGE_MODEL,
            "modalities": ["image", "text"],
            "messages": [{"role": "user", "content": content}]
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


def process_date(date_str: str, custom_prompt: Optional[str], skip_existing: bool,
                 dry_run: bool, reference_images: Optional[list[Path]] = None) -> bool:
    """Process a single date. Returns True if successful."""
    output_path = OUTPUT_DIR / f"{date_str}_ai-daily.png"

    if skip_existing and output_path.exists():
        logging.info(f"[{date_str}] Skipping - image already exists")
        return True

    if dry_run:
        ref_info = f" (with {len(reference_images)} reference images)" if reference_images else ""
        if custom_prompt:
            logging.info(f"[{date_str}] Would generate with custom prompt{ref_info}: {custom_prompt[:50]}...")
        else:
            facts = load_facts(date_str)
            if facts:
                logging.info(f"[{date_str}] Would generate from facts{ref_info} (summary: {facts.get('overall_summary', 'N/A')[:50]}...)")
            else:
                logging.info(f"[{date_str}] Would skip - no facts available")
        return True

    try:
        use_characters = bool(reference_images)
        character_names = [p.stem for p in reference_images] if reference_images else []

        if custom_prompt:
            prompt = custom_prompt
            logging.info(f"[{date_str}] Using custom prompt")
        else:
            facts = load_facts(date_str)
            if not facts:
                logging.warning(f"[{date_str}] Skipping - no facts file")
                return False

            logging.info(f"[{date_str}] Generating prompt from facts...")
            prompt = generate_image_prompt(facts, use_characters=use_characters, character_names=character_names)

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
        "-s", "--skip-existing",
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
    if reference_images:
        logging.info(f"Using {len(reference_images)} reference image(s): {[p.name for p in reference_images]}")

    logging.info(f"Processing {len(dates)} date(s): {dates[0]} to {dates[-1]}" if len(dates) > 1 else f"Processing date: {dates[0]}")

    if args.dry_run:
        logging.info("DRY RUN - no images will be generated")

    # Process each date
    success = 0
    failed = 0

    for date_str in dates:
        result = process_date(
            date_str,
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
