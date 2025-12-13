#!/usr/bin/env python3
"""
Generate daily AI image from facts using OpenRouter.
Uses GPT-5.2 to create an image prompt from the day's news summary,
then calls Nano Banana Pro (Gemini 3 Pro) to generate the actual image.

Supports reference images for character consistency (up to 14 images, 5 people).
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


def generate_image_prompt(facts: dict, use_characters: bool = False, character_names: list[str] = None) -> str:
    """Use LLM to create a detailed image prompt from facts summary."""
    summary = facts.get("overall_summary", "")

    if not summary:
        raise ValueError("No overall_summary found in facts")

    logging.info(f"Generating image prompt from summary: {summary[:100]}...")

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


def main():
    parser = argparse.ArgumentParser(
        description="Generate AI image from daily facts using Nano Banana Pro",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic generation from today's facts
  python generate-ai-image.py

  # Generate with all council characters for consistency
  python generate-ai-image.py --use-council

  # Generate with specific characters
  python generate-ai-image.py --characters eliza marc

  # Generate with custom reference images
  python generate-ai-image.py --references path/to/img1.png path/to/img2.png

  # Generate for a specific date
  python generate-ai-image.py -d 2025-12-10 --use-council
"""
    )
    parser.add_argument("-d", "--date", help="Date in YYYY-MM-DD format (default: use daily.json)")
    parser.add_argument("-o", "--output", help="Output path (default: posters/YYYY-MM-DD_ai-daily.png)")

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

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not OPENROUTER_API_KEY:
        logging.error("OPENROUTER_API_KEY environment variable not set")
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        facts = load_facts(args.date)
        date_str = facts.get("briefing_date", datetime.now().strftime("%Y-%m-%d"))

        # Get reference images for character consistency
        reference_images = get_reference_images(args)
        use_characters = bool(reference_images)
        character_names = [p.stem for p in reference_images] if reference_images else []

        if reference_images:
            logging.info(f"Using {len(reference_images)} reference image(s): {[p.name for p in reference_images]}")

        prompt = generate_image_prompt(facts, use_characters=use_characters, character_names=character_names)
        image_bytes = generate_image(prompt, reference_images=reference_images)

        if args.output:
            output_path = Path(args.output)
        else:
            output_path = OUTPUT_DIR / f"{date_str}_ai-daily.png"

        output_path.write_bytes(image_bytes)
        logging.info(f"Saved AI-generated image: {output_path}")

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
