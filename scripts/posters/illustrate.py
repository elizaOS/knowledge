#!/usr/bin/env python3
"""
Generate story illustrations using character reference sheets.

Uses reference-sheet.png from each character folder to maintain consistency.

Usage:
  # Basic - character + prompt
  python scripts/posters/illustrate.py eliza "celebrating a product launch"

  # With art style
  python scripts/posters/illustrate.py eliza "presenting at conference" -s editorial

  # Multiple characters
  python scripts/posters/illustrate.py eliza marc "discussing code on whiteboard"

  # From facts file (generates prompt from summary)
  python scripts/posters/illustrate.py eliza -f the-council/facts/2025-12-14.json

  # Custom output
  python scripts/posters/illustrate.py eliza "happy moment" -o celebration.png

  # List available styles
  python scripts/posters/illustrate.py --list-styles
"""

import os
import sys
import io
import json
import base64
import argparse
import logging
from pathlib import Path
from datetime import datetime

import requests
from PIL import Image

# --------------- Config ---------------

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
LLM_MODEL = "openai/gpt-4.1"
IMAGE_MODEL = "google/gemini-3-pro-image-preview"

SCRIPT_DIR = Path(__file__).parent.resolve()
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent
CHARACTERS_DIR = WORKSPACE_ROOT / "posters" / "characters"
OUTPUT_DIR = WORKSPACE_ROOT / "posters"
STYLE_PRESETS_FILE = SCRIPT_DIR / "config" / "style-presets.json"

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

# --------------- Style System ---------------


def load_style_presets() -> dict:
    """Load style presets from JSON config file."""
    if not STYLE_PRESETS_FILE.exists():
        return {"styles": {}, "defaults": {"style": "editorial"}}

    with open(STYLE_PRESETS_FILE) as f:
        return json.load(f)


def get_available_styles() -> list[str]:
    """Get list of available style names."""
    presets = load_style_presets()
    return list(presets.get("styles", {}).keys())


def get_style_description(style_name: str) -> str:
    """Get style description for prompt building."""
    presets = load_style_presets()
    styles = presets.get("styles", {})

    if style_name not in styles:
        return "editorial illustration style"

    config = styles[style_name]
    return config.get("description", style_name)


# --------------- Reference Sheet Loading ---------------


def get_reference_sheet(character: str) -> Path:
    """Get path to character's reference sheet."""
    char_dir = CHARACTERS_DIR / character
    ref_sheet = char_dir / "reference-sheet.png"

    if not ref_sheet.exists():
        raise FileNotFoundError(
            f"No reference sheet for '{character}'. "
            f"Run: python scripts/posters/generate.py {character}"
        )

    return ref_sheet


def load_manifest(character: str) -> dict:
    """Load character manifest for description."""
    char_dir = CHARACTERS_DIR / character
    manifest_path = char_dir / "manifest.json"

    if not manifest_path.exists():
        return {"character": character, "description": character}

    with open(manifest_path) as f:
        return json.load(f)


def make_reference_collage(characters: list[str]) -> tuple[bytes, list[dict]]:
    """Create collage of reference sheets and return with manifests."""
    ref_sheets = []
    manifests = []

    for char in characters:
        ref_path = get_reference_sheet(char)
        ref_sheets.append(ref_path)
        manifests.append(load_manifest(char))

    if not ref_sheets:
        raise ValueError("No reference sheets found")

    # Load and combine images
    pil_images = []
    for ref in ref_sheets:
        img = Image.open(ref).convert("RGBA")
        pil_images.append(img)

    # Stack horizontally if multiple
    if len(pil_images) == 1:
        collage = pil_images[0]
    else:
        # Resize to consistent height
        target_height = 512
        resized = []
        for img in pil_images:
            ratio = target_height / img.height
            new_width = int(img.width * ratio)
            resized.append(img.resize((new_width, target_height), Image.LANCZOS))

        total_width = sum(img.width for img in resized)
        collage = Image.new("RGBA", (total_width, target_height), (255, 255, 255, 255))
        x = 0
        for img in resized:
            collage.paste(img, (x, 0))
            x += img.width

    buffer = io.BytesIO()
    collage.save(buffer, "PNG", optimize=True)
    return buffer.getvalue(), manifests


# --------------- Prompt Generation ---------------


def build_illustration_prompt(
    manifests: list[dict],
    scene: str,
    style: str = "editorial"
) -> str:
    """Build the illustration generation prompt."""
    # Character descriptions
    char_descriptions = []
    for m in manifests:
        name = m.get("character", "character")
        desc = m.get("description", name)
        char_descriptions.append(f"- {name.upper()}: {desc}")

    char_block = "\n".join(char_descriptions)

    # Style description
    style_desc = get_style_description(style)

    prompt = f"""Create an illustration for a tech news magazine.

CHARACTERS (use reference sheet for exact appearance):
{char_block}

SCENE: {scene}

ART STYLE: {style_desc}

REQUIREMENTS:
- Characters must match reference sheet EXACTLY (colors, costume, features)
- Dynamic composition suitable for editorial use
- Professional quality illustration
- No text or watermarks
- Scene should feel natural and engaging"""

    return prompt


def generate_prompt_from_facts(facts_path: Path, manifests: list[dict]) -> str:
    """Generate a scene description from a facts file."""
    with open(facts_path) as f:
        facts = json.load(f)

    summary = facts.get("overall_summary", "")
    if not summary:
        raise ValueError("No overall_summary in facts file")

    # Use LLM to convert summary to scene
    char_names = [m.get("character", "character") for m in manifests]

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
                    "content": f"""Convert this news summary into a brief scene description for an illustration.
The scene should feature: {', '.join(char_names)}
Keep it under 50 words. Focus on a single compelling moment that captures the news.
Output ONLY the scene description, no explanation."""
                },
                {
                    "role": "user",
                    "content": summary
                }
            ]
        },
        timeout=60
    )
    response.raise_for_status()

    result = response.json()
    return result["choices"][0]["message"]["content"].strip()


# --------------- Image Generation ---------------


def generate_illustration(collage_bytes: bytes, prompt: str) -> bytes:
    """Call image generation API."""
    collage_b64 = base64.b64encode(collage_bytes).decode("utf-8")

    preamble = (
        "Reference sheet showing character design(s). "
        "Use these EXACT character appearances in the illustration. "
        "Maintain colors, costume, and distinguishing features.\n\n"
    )

    content = [
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{collage_b64}"}
        },
        {
            "type": "text",
            "text": preamble + prompt
        }
    ]

    logging.info(f"Calling {IMAGE_MODEL}...")

    resp = requests.post(
        OPENROUTER_ENDPOINT,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/elizaOS/knowledge",
            "X-Title": "ElizaOS Illustrator"
        },
        json={
            "model": IMAGE_MODEL,
            "modalities": ["image", "text"],
            "messages": [{"role": "user", "content": content}]
        },
        timeout=180
    )
    resp.raise_for_status()

    result = resp.json()

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


# --------------- CLI ---------------


def list_styles():
    """List available styles."""
    presets = load_style_presets()
    styles = presets.get("styles", {})

    print("Available styles:")
    for name, config in styles.items():
        desc = config.get("description", "No description")
        print(f"  {name}: {desc}")


def list_characters():
    """List available characters with reference sheets."""
    print("Characters with reference sheets:")
    for char_dir in sorted(CHARACTERS_DIR.iterdir()):
        if char_dir.is_dir() and not char_dir.name.startswith("."):
            ref_sheet = char_dir / "reference-sheet.png"
            if ref_sheet.exists():
                print(f"  {char_dir.name} [ready]")
            else:
                print(f"  {char_dir.name} [needs generate.py]")


def main():
    parser = argparse.ArgumentParser(
        description="Generate story illustrations using character reference sheets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "args",
        nargs="*",
        help="Character name(s) followed by scene description"
    )
    parser.add_argument(
        "-s", "--style",
        default="editorial",
        help="Art style (default: editorial). Use --list-styles to see options"
    )
    parser.add_argument(
        "-f", "--facts",
        help="Generate scene from facts JSON file"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output path (default: posters/illustration-{timestamp}.png)"
    )
    parser.add_argument(
        "--list-styles",
        action="store_true",
        help="List available styles"
    )
    parser.add_argument(
        "--list-characters",
        action="store_true",
        help="List characters with reference sheets"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show prompt without generating"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Handle list commands
    if args.list_styles:
        list_styles()
        return 0

    if args.list_characters:
        list_characters()
        return 0

    # Validate args
    if not args.args:
        parser.error("Provide at least one character and a scene description")

    # API key check
    if not OPENROUTER_API_KEY and not args.dry_run:
        logging.error("OPENROUTER_API_KEY not set")
        return 1

    try:
        # Parse positional args: characters then scene
        # Last quoted arg or last arg is the scene
        characters = []
        scene = None

        for arg in args.args:
            char_dir = CHARACTERS_DIR / arg
            if char_dir.exists():
                characters.append(arg)
            else:
                # Not a character - must be the scene
                scene = arg
                break

        # If we found characters but no scene in args, remaining args are scene
        remaining_idx = len(characters)
        if remaining_idx < len(args.args):
            scene = " ".join(args.args[remaining_idx:])

        if not characters:
            parser.error("No valid characters found. Use --list-characters to see available.")

        if not scene and not args.facts:
            parser.error("Provide a scene description or use -f with a facts file")

        logging.info(f"Characters: {characters}")

        # Load reference sheets
        logging.info("Loading reference sheets...")
        collage_bytes, manifests = make_reference_collage(characters)
        logging.info(f"Loaded {len(manifests)} character(s)")

        # Get scene description
        if args.facts:
            facts_path = Path(args.facts)
            if not facts_path.exists():
                logging.error(f"Facts file not found: {facts_path}")
                return 1
            logging.info("Generating scene from facts...")
            scene = generate_prompt_from_facts(facts_path, manifests)
            logging.info(f"Scene: {scene}")

        # Build prompt
        prompt = build_illustration_prompt(manifests, scene, style=args.style)

        # Determine output path
        if args.output:
            output_path = Path(args.output)
        else:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            char_str = "-".join(characters)
            output_path = OUTPUT_DIR / f"illustration-{char_str}-{timestamp}.png"

        # Dry run
        if args.dry_run:
            print()
            print("=" * 60)
            print("DRY RUN")
            print("=" * 60)
            print(f"Characters: {characters}")
            print(f"Scene: {scene}")
            print(f"Style: {args.style}")
            print(f"Output: {output_path}")
            print()
            print("PROMPT:")
            print("-" * 60)
            print(prompt)
            print("-" * 60)
            return 0

        # Generate
        logging.info(f"Generating illustration (style: {args.style})...")
        image_bytes = generate_illustration(collage_bytes, prompt)

        # Save
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(image_bytes)
        logging.info(f"Saved: {output_path}")

        return 0

    except FileNotFoundError as e:
        logging.error(str(e))
        return 1
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
