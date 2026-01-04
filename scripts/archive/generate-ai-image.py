#!/usr/bin/env python3
"""
Generate daily AI image from facts using OpenRouter.
Uses GPT-5.2 to create an image prompt from the day's news summary,
then calls Nano Banana Pro (Gemini 3 Pro) to generate the actual image.

Supports reference images for character consistency (up to 14 images, 5 people).
Supports multiple art styles via --style flag and style presets.
"""

import os
import json
import base64
import requests
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

# Config
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
LLM_MODEL = "openai/gpt-5.2"
IMAGE_MODEL = "google/gemini-3-pro-image-preview"

SCRIPT_DIR = Path(__file__).parent.resolve()
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent
FACTS_DIR = WORKSPACE_ROOT / "the-council" / "facts"
OUTPUT_DIR = WORKSPACE_ROOT / "media" / "quick"
STYLE_PRESETS_FILE = SCRIPT_DIR / "config" / "style-presets.json"

# Default character reference images (council members)
DEFAULT_REFERENCES = {
    "eliza": SCRIPT_DIR / "assets" / "eliza.png",
    "marc": SCRIPT_DIR / "assets" / "marc.png",
    "peepo": SCRIPT_DIR / "assets" / "peepo.png",
    "spartan": SCRIPT_DIR / "assets" / "spartan.png",
}

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def load_style_presets() -> dict:
    """Load style presets from JSON config file."""
    if not STYLE_PRESETS_FILE.exists():
        logging.warning(f"Style presets file not found: {STYLE_PRESETS_FILE}")
        return {"styles": {}, "categories": {}, "defaults": {"style": "editorial"}}

    with open(STYLE_PRESETS_FILE) as f:
        return json.load(f)


def get_available_styles() -> list[str]:
    """Get list of available style names."""
    presets = load_style_presets()
    return list(presets.get("styles", {}).keys())


def get_style_prompt(style_name: str, character_names: list[str] = None) -> str:
    """Get the system prompt for a given style."""
    presets = load_style_presets()
    styles = presets.get("styles", {})

    if style_name not in styles:
        default_style = presets.get("defaults", {}).get("style", "editorial")
        logging.warning(f"Style '{style_name}' not found, using '{default_style}'")
        style_name = default_style

    style_config = styles[style_name]
    system_prompt = style_config["system_prompt"]

    # Replace character names placeholder if present
    if character_names and "{character_names}" in system_prompt:
        system_prompt = system_prompt.replace("{character_names}", ", ".join(character_names))

    return system_prompt


def style_requires_references(style_name: str) -> bool:
    """Check if a style requires character reference images."""
    presets = load_style_presets()
    styles = presets.get("styles", {})
    if style_name in styles:
        return styles[style_name].get("requires_references", False)
    return False


def load_facts(date: str = None) -> dict:
    """Load facts JSON for given date or daily.json."""
    if date:
        facts_file = FACTS_DIR / f"{date}.json"
    else:
        facts_file = FACTS_DIR / "daily.json"

    if not facts_file.exists():
        raise FileNotFoundError(f"Facts file not found: {facts_file}")

    logging.info(f"Loading facts from: {facts_file}")
    with open(facts_file) as f:
        return json.load(f)


def generate_image_prompt(facts: dict, style: str = "editorial", character_names: list[str] = None) -> str:
    """Use LLM to create a detailed image prompt from facts summary.

    Args:
        facts: Facts dictionary with overall_summary
        style: Art style to use (from style-presets.json)
        character_names: Optional list of character names for council style
    """
    summary = facts.get("overall_summary", "")

    if not summary:
        raise ValueError("No overall_summary found in facts")

    logging.info(f"Generating image prompt with style '{style}' from summary: {summary[:100]}...")

    # Get system prompt from style presets
    system_prompt = get_style_prompt(style, character_names)

    response = requests.post(
        OPENROUTER_ENDPOINT,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": LLM_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Today's tech/AI news summary:\n\n{summary}"
                }
            ]
        },
        timeout=60
    )
    response.raise_for_status()

    result = response.json()
    prompt = result["choices"][0]["message"]["content"].strip()
    logging.info(f"Generated image prompt: {prompt}")
    return prompt


def load_reference_image(path: Path) -> Optional[str]:
    """Load an image file and return as base64 data URL."""
    if not path.exists():
        logging.warning(f"Reference image not found: {path}")
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

    # Filter to existing files
    existing = [p for p in image_paths if p.exists()]
    if not existing:
        return None

    try:
        # Create temp file for montage
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name

        # Build montage command
        # Tile horizontally, resize each to consistent height, add labels
        cmd = [
            "montage",
            *[str(p) for p in existing],
            "-tile", f"{len(existing)}x1",  # horizontal row
            "-geometry", "256x256+10+10",   # resize each, add padding
            "-background", "white",
            tmp_path
        ]

        logging.info(f"Creating reference montage with {len(existing)} images...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            logging.warning(f"Montage failed: {result.stderr}")
            return None

        # Read and encode the montage
        with open(tmp_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")

        # Clean up
        Path(tmp_path).unlink(missing_ok=True)

        return f"data:image/png;base64,{data}"

    except subprocess.TimeoutExpired:
        logging.warning("Montage creation timed out")
        return None
    except FileNotFoundError:
        logging.warning("ImageMagick montage not found - falling back to individual images")
        return None
    except Exception as e:
        logging.warning(f"Montage creation failed: {e}")
        return None


def generate_image(prompt: str, reference_images: Optional[list[Path]] = None) -> bytes:
    """Call Nano Banana Pro to generate image, return PNG bytes.

    Args:
        prompt: Text prompt for image generation
        reference_images: Optional list of image paths for character consistency
    """
    logging.info("Calling Nano Banana Pro image generation API...")

    # Build message content
    content = []
    char_names = []

    # Add reference images for character consistency
    if reference_images:
        char_names = [p.stem for p in reference_images if p.exists()]

        # Try to create a montage first (cleaner single image)
        montage_url = create_reference_montage(reference_images)

        if montage_url:
            content.append({
                "type": "image_url",
                "image_url": {"url": montage_url}
            })
            logging.info(f"Using montage of {len(char_names)} character(s): {char_names}")
        else:
            # Fallback to individual images
            loaded_count = 0
            for img_path in reference_images[:14]:
                data_url = load_reference_image(img_path)
                if data_url:
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": data_url}
                    })
                    loaded_count += 1
            logging.info(f"Loaded {loaded_count} individual reference image(s)")

        # Prepend instruction about reference images
        ref_instruction = f"""The attached reference image shows the characters: {', '.join(char_names)}.
Use these EXACT character designs in the illustration. Maintain their appearance, colors, and style.

"""
        prompt = ref_instruction + prompt

    # Add text prompt
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

    # Extract base64 image from response
    # Format: response.choices[0].message.images[0].image_url.url
    # URL format: "data:image/png;base64,..."
    try:
        images = result["choices"][0]["message"]["images"]
        if not images:
            raise ValueError("No images in response")

        image_url = images[0]["image_url"]["url"]
        if not image_url.startswith("data:"):
            raise ValueError(f"Unexpected image URL format: {image_url[:50]}")

        # Extract base64 data after the comma
        base64_data = image_url.split(",", 1)[1]
        return base64.b64decode(base64_data)

    except (KeyError, IndexError) as e:
        logging.error(f"Failed to extract image from response: {e}")
        logging.error(f"Response structure: {json.dumps(result, indent=2)[:500]}")
        raise ValueError(f"Failed to extract image from API response: {e}")


def get_reference_images(args) -> list[Path]:
    """Get reference images based on CLI args."""
    images = []

    if args.references:
        # Custom reference images provided
        for ref in args.references:
            path = Path(ref)
            if path.exists():
                images.append(path)
            else:
                logging.warning(f"Reference image not found: {ref}")

    elif args.characters:
        # Use specific council characters
        for char in args.characters:
            char_lower = char.lower()
            if char_lower in DEFAULT_REFERENCES:
                images.append(DEFAULT_REFERENCES[char_lower])
            else:
                logging.warning(f"Unknown character: {char}. Available: {list(DEFAULT_REFERENCES.keys())}")

    elif args.use_council:
        # Use all council characters
        images = [p for p in DEFAULT_REFERENCES.values() if p.exists()]

    return images


def get_category_summary(facts: dict, category: str) -> Optional[str]:
    """Extract summary text from a specific category in facts.

    Returns combined text from all items in the category, or None if empty.
    """
    presets = load_style_presets()
    category_config = presets.get("categories", {}).get(category, {})
    extract_key = category_config.get("extract_key", "summary")

    categories = facts.get("categories", {})
    if category not in categories:
        return None

    category_data = categories[category]

    # Handle different category structures
    if isinstance(category_data, list):
        # discord_updates, user_feedback, strategic_insights, market_analysis
        texts = []
        for item in category_data:
            if isinstance(item, dict):
                text = item.get(extract_key) or item.get("summary") or item.get("observation")
                if text:
                    texts.append(text)
        return " ".join(texts) if texts else None

    elif isinstance(category_data, dict):
        # github_updates has nested structure
        if "overall_focus" in category_data:
            focus_items = category_data.get("overall_focus", [])
            texts = [item.get("claim", "") for item in focus_items if isinstance(item, dict)]
            return " ".join(texts) if texts else None
        # twitter_news_highlights may be empty list in dict
        return None

    return None


def generate_category_images(facts: dict, date_str: str, output_dir: Path,
                             categories: list[str] = None) -> list[Path]:
    """Generate images for specific fact categories.

    Args:
        facts: Full facts dictionary
        date_str: Date string for output filenames
        output_dir: Directory to save images
        categories: List of categories to process (default: all non-empty)

    Returns list of generated image paths.
    """
    presets = load_style_presets()
    category_configs = presets.get("categories", {})

    # Default to all configured categories
    if categories is None:
        categories = list(category_configs.keys())

    generated = []

    for category in categories:
        summary = get_category_summary(facts, category)
        if not summary:
            logging.info(f"Skipping category '{category}': no content")
            continue

        config = category_configs.get(category, {})
        suggested_styles = config.get("suggested_styles", ["editorial"])
        style = suggested_styles[0]  # Use first suggested style

        logging.info(f"Generating image for category '{category}' with style '{style}'")

        try:
            # Create a temporary facts dict with just this category's summary
            category_facts = {"overall_summary": summary}

            # Get reference images if style requires them
            reference_images = None
            character_names = None
            if style_requires_references(style):
                reference_images = [p for p in DEFAULT_REFERENCES.values() if p.exists()]
                character_names = [p.stem for p in reference_images]

            prompt = generate_image_prompt(category_facts, style=style, character_names=character_names)
            image_bytes = generate_image(prompt, reference_images=reference_images)

            output_path = output_dir / f"{date_str}_ai-{category}.png"
            output_path.write_bytes(image_bytes)
            # Save prompt alongside image
            prompt_path = output_path.with_suffix('.txt')
            prompt_path.write_text(prompt)
            generated.append(output_path)
            logging.info(f"  Saved: {output_path} (+prompt)")

        except Exception as e:
            logging.error(f"  Failed to generate image for '{category}': {e}")
            continue

    return generated


def generate_preview_all_styles(facts: dict, date_str: str, output_dir: Path) -> list[Path]:
    """Generate images in all available styles for preview/comparison.

    Returns list of generated image paths.
    """
    styles = get_available_styles()
    generated = []

    logging.info(f"Generating preview images for {len(styles)} styles...")

    for style in styles:
        try:
            logging.info(f"Generating style: {style}")

            # Get reference images if style requires them
            reference_images = None
            character_names = None
            if style_requires_references(style):
                reference_images = [p for p in DEFAULT_REFERENCES.values() if p.exists()]
                character_names = [p.stem for p in reference_images]
                logging.info(f"  Using council references for '{style}' style")

            prompt = generate_image_prompt(facts, style=style, character_names=character_names)
            image_bytes = generate_image(prompt, reference_images=reference_images)

            output_path = output_dir / f"{date_str}_ai-{style}.png"
            output_path.write_bytes(image_bytes)
            # Save prompt alongside image
            prompt_path = output_path.with_suffix('.txt')
            prompt_path.write_text(prompt)
            generated.append(output_path)
            logging.info(f"  Saved: {output_path} (+prompt)")

        except Exception as e:
            logging.error(f"  Failed to generate '{style}' style: {e}")
            continue

    return generated


def main():
    # Get available styles for help text
    available_styles = get_available_styles()
    styles_list = ", ".join(available_styles) if available_styles else "editorial, anime, infographic, council, risograph, vintage"

    parser = argparse.ArgumentParser(
        description="Generate AI image from daily facts using Nano Banana Pro",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  # Basic generation from today's facts (default editorial style)
  python generate-ai-image.py

  # Generate with a specific art style
  python generate-ai-image.py --style anime
  python generate-ai-image.py --style infographic
  python generate-ai-image.py --style council --use-council

  # Generate ALL style variations for preview/comparison
  python generate-ai-image.py --preview-styles

  # Generate per-category images (github, discord, etc.)
  python generate-ai-image.py --per-category
  python generate-ai-image.py --per-category --categories discord_updates github_updates

  # Generate with all council characters for consistency
  python generate-ai-image.py --use-council

  # Generate with specific characters
  python generate-ai-image.py --characters eliza marc

  # Generate with custom reference images
  python generate-ai-image.py --references path/to/img1.png path/to/img2.png

  # Generate for a specific date
  python generate-ai-image.py -d 2025-12-10 --style vintage

  # List available styles
  python generate-ai-image.py --list-styles

Available styles: {styles_list}
"""
    )
    parser.add_argument("-d", "--date", help="Date in YYYY-MM-DD format (default: use daily.json)")
    parser.add_argument("-o", "--output", help="Output path (default: posters/YYYY-MM-DD_ai-daily.png)")

    # Style options
    parser.add_argument(
        "-s", "--style",
        default="editorial",
        help=f"Art style to use (default: editorial). Available: {styles_list}"
    )
    parser.add_argument(
        "--preview-styles",
        action="store_true",
        help="Generate images in ALL available styles for comparison"
    )
    parser.add_argument(
        "--list-styles",
        action="store_true",
        help="List all available styles and exit"
    )
    parser.add_argument(
        "--per-category",
        action="store_true",
        help="Generate separate images for each fact category (github, discord, etc.)"
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        help="Specific categories to generate images for (use with --per-category)"
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

    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
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

    if not OPENROUTER_API_KEY:
        logging.error("OPENROUTER_API_KEY environment variable not set")
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        facts = load_facts(args.date)
        date_str = facts.get("briefing_date", datetime.now().strftime("%Y-%m-%d"))

        # Handle --preview-styles mode
        if args.preview_styles:
            generated = generate_preview_all_styles(facts, date_str, OUTPUT_DIR)
            logging.info(f"Generated {len(generated)} style previews")
            for path in generated:
                print(f"  {path}")
            return 0

        # Handle --per-category mode
        if args.per_category:
            generated = generate_category_images(
                facts, date_str, OUTPUT_DIR,
                categories=args.categories
            )
            logging.info(f"Generated {len(generated)} category images")
            for path in generated:
                print(f"  {path}")
            return 0

        # Get reference images for character consistency
        reference_images = get_reference_images(args)
        character_names = [p.stem for p in reference_images] if reference_images else []

        # Auto-enable council references if council style is selected
        style = args.style
        if style_requires_references(style) and not reference_images:
            logging.info(f"Style '{style}' requires references, auto-enabling council characters")
            reference_images = [p for p in DEFAULT_REFERENCES.values() if p.exists()]
            character_names = [p.stem for p in reference_images]

        if reference_images:
            logging.info(f"Using {len(reference_images)} reference image(s): {[p.name for p in reference_images]}")

        prompt = generate_image_prompt(facts, style=style, character_names=character_names)
        image_bytes = generate_image(prompt, reference_images=reference_images)

        if args.output:
            output_path = Path(args.output)
        else:
            # Include style in filename if not editorial (default)
            if style != "editorial":
                output_path = OUTPUT_DIR / f"{date_str}_ai-{style}.png"
            else:
                output_path = OUTPUT_DIR / f"{date_str}_ai-daily.png"

        output_path.write_bytes(image_bytes)
        # Save prompt alongside image
        prompt_path = output_path.with_suffix('.txt')
        prompt_path.write_text(prompt)
        logging.info(f"Saved AI-generated image: {output_path} (+prompt)")

        return 0

    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        return 1
    except requests.RequestException as e:
        logging.error(f"API request failed: {e}")
        return 1
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
