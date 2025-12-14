#!/usr/bin/env python3
"""
Generate character reference sheets.

Creates a canonical reference sheet image with full body views and expressions.
The reference sheet is reusable for future illustration generation.

Usage:
  # Basic generation
  python scripts/posters/generate.py eliza

  # Iterate with adjustments (overwrites reference-sheet.png)
  python scripts/posters/generate.py eliza "shorter hair"
  python scripts/posters/generate.py eliza "more orange cap"

  # Themed variations (creates reference-sheet-{theme}.png)
  python scripts/posters/generate.py eliza cyberpunk
  python scripts/posters/generate.py eliza formal

  # Custom output path
  python scripts/posters/generate.py eliza -o my-version.png

  # Add extra reference images (e.g., outfit inspiration)
  python scripts/posters/generate.py eliza -i dress.png
  python scripts/posters/generate.py eliza formal -i suit-reference.png

  # Add extra instructions with -t
  python scripts/posters/generate.py eliza -t "more dynamic poses"
  python scripts/posters/generate.py eliza -i watercolor.jpg -t "apply style only to clothing"
  python scripts/posters/generate.py eliza -i ref.jpg -t "use this color palette for the background"

Workflow:
  1. Open preview.html in browser (auto-refreshes)
  2. Run generate.py to create/update reference sheet
  3. Iterate until happy
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
IMAGE_MODEL = "google/gemini-3-pro-image-preview"

SCRIPT_DIR = Path(__file__).parent.resolve()
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent
CHARACTERS_DIR = WORKSPACE_ROOT / "posters" / "characters"

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

# --------------- Known Themes ---------------

THEMES = {
    "cyberpunk": "cyberpunk aesthetic, neon lights, tech wear, glowing accents",
    "formal": "formal attire, business professional, elegant clothing",
    "casual": "casual everyday clothes, relaxed style",
    "fantasy": "fantasy RPG style, medieval/magical clothing",
    "scifi": "science fiction, futuristic uniform, space age",
    "streetwear": "urban streetwear, trendy fashion, sneakers",
    "athletic": "athletic wear, sports clothing, activewear",
    "vintage": "vintage retro style, classic fashion from past decades",
}

# --------------- Core Functions ---------------


def load_manifest(character: str) -> dict:
    """Load character manifest from posters/characters/{name}/manifest.json."""
    char_dir = CHARACTERS_DIR / character
    manifest_path = char_dir / "manifest.json"

    if not char_dir.exists():
        raise FileNotFoundError(f"Character folder not found: {char_dir}")

    if not manifest_path.exists():
        raise FileNotFoundError(
            f"No manifest.json for '{character}'. "
            f"Run: python scripts/posters/analyze.py {character}"
        )

    with open(manifest_path) as f:
        return json.load(f)


def select_refs(manifest: dict) -> list[Path]:
    """Select best reference images for the reference sheet.

    Picks a mix of full_body and face shots for comprehensive reference.
    """
    char_dir = CHARACTERS_DIR / manifest["character"]
    all_images = manifest.get("images", [])
    selected = []

    # Get full_body images (prefer front-facing)
    full_body = [img for img in all_images if img.get("pose") == "full_body"]
    front_full = [img for img in full_body if img.get("angle") in ["front", "3/4_left", "3/4_right"]]
    if front_full:
        selected.append(front_full[0])
    elif full_body:
        selected.append(full_body[0])

    # Get face shots
    face_shots = [img for img in all_images if img.get("pose") in ["bust", "portrait", "headshot"]]
    if face_shots:
        selected.append(face_shots[0])
        if len(face_shots) > 1:
            selected.append(face_shots[1])

    # Convert to paths
    paths = []
    for img in selected[:3]:
        path = char_dir / img["filename"]
        if path.exists():
            paths.append(path)

    logging.info(f"Selected {len(paths)} reference(s): {[p.name for p in paths]}")
    return paths


def make_collage(refs: list[Path]) -> bytes:
    """Create a reference collage from images using Pillow."""
    if not refs:
        raise ValueError("No reference images provided")

    # Load images
    pil_images = []
    for ref in refs:
        try:
            img = Image.open(ref).convert("RGBA")
            pil_images.append(img)
        except Exception as e:
            logging.warning(f"Failed to load {ref}: {e}")

    if not pil_images:
        raise ValueError("No images could be loaded")

    # Normalize to consistent size
    target_size = (512, 512)
    resized = []
    for img in pil_images:
        img_copy = img.copy()
        img_copy.thumbnail(target_size, Image.LANCZOS)
        canvas = Image.new("RGBA", target_size, (0, 0, 0, 0))
        x = (target_size[0] - img_copy.width) // 2
        y = (target_size[1] - img_copy.height) // 2
        canvas.paste(img_copy, (x, y), img_copy if img_copy.mode == "RGBA" else None)
        resized.append(canvas)

    # Create horizontal collage
    cols = len(resized)
    canvas_w = cols * target_size[0]
    canvas_h = target_size[1]
    collage = Image.new("RGBA", (canvas_w, canvas_h), (255, 255, 255, 255))

    for i, img in enumerate(resized):
        collage.paste(img, (i * target_size[0], 0), img)

    buffer = io.BytesIO()
    collage.save(buffer, "PNG", optimize=True)
    return buffer.getvalue()


def build_prompt(manifest: dict, adjustment: str = None, theme: str = None, extra_text: str = None) -> str:
    """Build the reference sheet generation prompt."""
    features = manifest.get("features", {})

    # Base costume description
    costume = features.get("costume", "character's default outfit")

    # Apply theme modification
    if theme and theme in THEMES:
        theme_desc = THEMES[theme]
        costume = f"{theme_desc} version of the character, inspired by their original design"

    # Apply adjustment
    if adjustment:
        costume = f"{costume}. ADJUSTMENT: {adjustment}"

    prompt = f"""Professional character reference sheet for {manifest.get("description", manifest["character"])}.

LAYOUT: Single image with two rows:
- TOP ROW: 4 full body views (front, 3/4 right, side profile, back) - same neutral standing pose, arms slightly away from body
- BOTTOM ROW: 6 head expressions (neutral, happy, angry, sad, surprised, thinking) - same front angle

COSTUME: {costume}
PRIMARY COLORS: {", ".join(features.get("colors", ["characteristic colors"]))}
ART STYLE: {features.get("style", "stylized character art")}

REQUIREMENTS:
- Consistent character design across ALL views and expressions
- Full body visible head to toe in top row
- Clean white/light gray background
- Professional character sheet layout
- No text, labels, or watermarks
- Game art / animation reference style"""

    # Append extra text instructions if provided
    if extra_text:
        prompt += f"\n\nADDITIONAL INSTRUCTIONS: {extra_text}"

    return prompt


def generate(collage_bytes: bytes, prompt: str, has_style_refs: bool = False) -> bytes:
    """Call image generation API."""
    collage_b64 = base64.b64encode(collage_bytes).decode("utf-8")

    # Adjust preamble based on whether extra style refs were provided
    if has_style_refs:
        preamble = (
            "Reference images show: (1) the character design to maintain, and "
            "(2) style/aesthetic references to apply. "
            "Keep the CHARACTER consistent but adopt the STYLE, colors, and artistic aesthetic "
            "from the style reference images. Follow any additional instructions in the prompt.\n\n"
        )
    else:
        preamble = (
            "Reference images showing the character design. "
            "Maintain EXACT character appearance, colors, and art style.\n\n"
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
            "X-Title": "ElizaOS Character Generator"
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


def create_preview_html(char_dir: Path, character: str):
    """Create or update the preview.html file."""
    preview_path = char_dir / "preview.html"

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="2">
    <title>{character} - Reference Sheet</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #1a1a2e;
            color: #eee;
        }}
        h1 {{
            color: #fff;
            border-bottom: 2px solid #ff6b35;
            padding-bottom: 10px;
        }}
        .sheet {{
            background: #16213e;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        img {{
            max-width: 100%;
            border-radius: 4px;
        }}
        .meta {{
            color: #888;
            font-size: 14px;
        }}
        .commands {{
            background: #0f3460;
            padding: 15px;
            border-radius: 4px;
            font-family: monospace;
            margin-top: 20px;
        }}
        .commands code {{
            display: block;
            margin: 5px 0;
            color: #e94560;
        }}
    </style>
</head>
<body>
    <h1>{character.title()} - Reference Sheet</h1>

    <div class="sheet">
        <img src="reference-sheet.png" alt="Reference Sheet" onerror="this.style.display='none'">
    </div>

    <p class="meta">Auto-refreshes every 2 seconds. Last check: <span id="time"></span></p>

    <div class="commands">
        <strong>Commands:</strong>
        <code>python scripts/posters/generate.py {character}</code>
        <code>python scripts/posters/generate.py {character} "adjustment here"</code>
        <code>python scripts/posters/generate.py {character} cyberpunk</code>
    </div>

    <script>
        document.getElementById('time').textContent = new Date().toLocaleTimeString();
    </script>
</body>
</html>"""

    preview_path.write_text(html)
    return preview_path


def get_output_path(char_dir: Path, theme: str = None, custom_output: str = None) -> Path:
    """Determine output path for the reference sheet."""
    if custom_output:
        return Path(custom_output)

    if theme and theme in THEMES:
        return char_dir / f"reference-sheet-{theme}.png"

    return char_dir / "reference-sheet.png"


def list_characters():
    """List available characters and themes."""
    print("AVAILABLE CHARACTERS:")
    print("-" * 50)
    for char_dir in sorted(CHARACTERS_DIR.iterdir()):
        if char_dir.is_dir() and not char_dir.name.startswith("."):
            manifest = char_dir / "manifest.json"
            ref_sheet = char_dir / "reference-sheet.png"
            status = []
            if manifest.exists():
                status.append("analyzed")
            else:
                status.append("needs analysis")
            if ref_sheet.exists():
                status.append("has ref sheet")
            print(f"  {char_dir.name:15} [{', '.join(status)}]")

    print()
    print("AVAILABLE THEMES:")
    print("-" * 50)
    for name, desc in THEMES.items():
        print(f"  {name:12} {desc[:50]}...")


# --------------- Main ---------------


def main():
    parser = argparse.ArgumentParser(
        description="Generate character reference sheets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "character",
        nargs="?",
        help="Character name (folder in posters/characters/)"
    )
    parser.add_argument(
        "modifier",
        nargs="?",
        help="Theme name (single word) or adjustment (quoted text)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Custom output path"
    )
    parser.add_argument(
        "-i", "--input",
        action="append",
        dest="extra_refs",
        help="Extra reference image(s) for inspiration (can use multiple times)"
    )
    parser.add_argument(
        "-t", "--text",
        dest="extra_text",
        help="Additional instructions to append to prompt (e.g., 'apply style only to shirt', 'more dramatic pose')"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available characters and themes"
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

    # Handle --list
    if args.list:
        list_characters()
        return 0

    # Validate character
    if not args.character:
        parser.error("character is required (or use --list)")

    # API key check
    if not OPENROUTER_API_KEY and not args.dry_run:
        logging.error("OPENROUTER_API_KEY not set")
        return 1

    try:
        # Determine if modifier is theme or adjustment
        theme = None
        adjustment = None
        if args.modifier:
            if args.modifier in THEMES:
                theme = args.modifier
                logging.info(f"Using theme: {theme}")
            else:
                adjustment = args.modifier
                logging.info(f"Using adjustment: {adjustment}")

        # Load manifest
        logging.info(f"Loading manifest for '{args.character}'...")
        manifest = load_manifest(args.character)
        char_dir = CHARACTERS_DIR / args.character

        # Create preview.html if it doesn't exist
        preview_path = char_dir / "preview.html"
        if not preview_path.exists():
            create_preview_html(char_dir, args.character)
            logging.info(f"Created preview: {preview_path}")

        # Select references
        refs = select_refs(manifest)
        if not refs:
            logging.error("No suitable reference images found")
            return 1

        # Add extra reference images if provided
        extra_ref_paths = []
        if args.extra_refs:
            for ref_path in args.extra_refs:
                p = Path(ref_path)
                if p.exists():
                    extra_ref_paths.append(p)
                    logging.info(f"Added extra reference: {p.name}")
                else:
                    logging.warning(f"Extra reference not found: {ref_path}")
            refs = refs + extra_ref_paths

        # Build prompt
        prompt = build_prompt(manifest, adjustment=adjustment, theme=theme, extra_text=args.extra_text)

        # Determine output path
        output_path = get_output_path(char_dir, theme=theme, custom_output=args.output)

        # Dry run
        if args.dry_run:
            print()
            print("=" * 60)
            print("DRY RUN - No API call will be made")
            print("=" * 60)
            print(f"Character: {args.character}")
            print(f"Theme: {theme or 'default'}")
            print(f"Adjustment: {adjustment or 'none'}")
            print(f"Character refs: {[r.name for r in refs if r not in extra_ref_paths]}")
            if extra_ref_paths:
                print(f"Extra refs: {[r.name for r in extra_ref_paths]}")
            if args.extra_text:
                print(f"Extra text: {args.extra_text}")
            print(f"Output: {output_path}")
            print()
            print("PROMPT:")
            print("-" * 60)
            print(prompt)
            print("-" * 60)
            return 0

        # Create collage
        logging.info("Creating reference collage...")
        collage_bytes = make_collage(refs)

        # Generate
        logging.info("Generating reference sheet...")
        has_style_refs = bool(extra_ref_paths)
        image_bytes = generate(collage_bytes, prompt, has_style_refs=has_style_refs)

        # Save
        output_path.write_bytes(image_bytes)
        logging.info(f"Saved: {output_path}")

        # Update preview.html
        create_preview_html(char_dir, args.character)

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
