#!/usr/bin/env python3
"""
Test generating character reference sheets.
Run: python scripts/posters/test-reference-sheet.py
"""

import os
import sys
import base64
import json
from pathlib import Path
from datetime import datetime
import requests

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
IMAGE_MODEL = "google/gemini-3-pro-image-preview"

SCRIPT_DIR = Path(__file__).parent.resolve()
CHARACTERS_DIR = SCRIPT_DIR.parent.parent / "posters" / "characters"
OUTPUT_DIR = SCRIPT_DIR.parent.parent / "posters" / "test-sheets"

# Test prompts - we'll try different approaches
PROMPTS = {
    "turnaround_single": """character model sheet of {char_desc},
        showing the same character from 4 angles: front view, 3/4 view, side profile, back view,
        arranged horizontally left to right,
        neutral T-pose with arms slightly spread, standing straight,
        full body visible head to toe in each view,
        orthographic style, no perspective distortion,
        consistent character design across all views,
        clean white background, reference sheet style,
        professional character turnaround, game art style,
        no text, no labels""",

    "turnaround_grid": """professional character reference sheet for {char_desc},
        2x2 grid layout showing:
        top-left: front view full body,
        top-right: 3/4 angle full body,
        bottom-left: side profile full body,
        bottom-right: back view full body,
        all in neutral standing pose, arms relaxed at sides,
        consistent proportions and design in each panel,
        clean flat background, model sheet style,
        high quality character art, no text""",

    "expression_sheet": """character expression sheet for {char_desc},
        head and shoulders only,
        showing 6 different expressions in a horizontal row:
        neutral, happy/smiling, angry, sad, surprised, thinking,
        same character same angle (front view) for each expression,
        consistent art style across all expressions,
        clean background, reference sheet format,
        no text, no labels""",

    "front_neutral": """full body character illustration of {char_desc},
        front view, facing camera directly,
        neutral standing pose, arms relaxed at sides,
        full body visible from head to feet,
        neutral expression, looking at viewer,
        clean simple background,
        character reference style, consistent proportions,
        high quality, no text""",

    "side_neutral": """full body character illustration of {char_desc},
        side profile view, facing left,
        neutral standing pose,
        full body visible from head to feet,
        clean simple background,
        character reference style, consistent proportions,
        high quality, no text""",
}


def image_to_base64(path: Path) -> str:
    mime = "image/png" if path.suffix == ".png" else "image/jpeg"
    data = base64.b64encode(path.read_bytes()).decode()
    return f"data:{mime};base64,{data}"


def get_references(char_dir: Path) -> list[Path]:
    images = sorted([
        f for f in char_dir.iterdir()
        if f.suffix.lower() in {".png", ".jpg", ".jpeg"}
        and not f.name.startswith(("thumb-", "generated-", "test-"))
    ])
    return images[:2]  # Use fewer refs for this test


def generate(prompt: str, refs: list[Path]) -> bytes:
    content = []
    for ref in refs:
        content.append({"type": "image_url", "image_url": {"url": image_to_base64(ref)}})

    content.append({"type": "text", "text": (
        "These reference images show the character. "
        "Maintain exact character design, colors, costume, and art style.\n\n"
        f"{prompt}"
    )})

    print(f"  Calling {IMAGE_MODEL}...")
    resp = requests.post(
        OPENROUTER_ENDPOINT,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
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
    images = result["choices"][0]["message"].get("images", [])
    if not images:
        raise ValueError("No image in response")

    url = images[0]["image_url"]["url"]
    return base64.b64decode(url.split(",", 1)[1])


def main():
    if not OPENROUTER_API_KEY:
        print("ERROR: OPENROUTER_API_KEY not set")
        return 1

    character = sys.argv[1] if len(sys.argv) > 1 else "eliza"
    prompt_key = sys.argv[2] if len(sys.argv) > 2 else "turnaround_single"

    char_dir = CHARACTERS_DIR / character
    if not char_dir.exists():
        print(f"ERROR: Character not found: {char_dir}")
        return 1

    if prompt_key not in PROMPTS:
        print(f"ERROR: Unknown prompt. Available: {list(PROMPTS.keys())}")
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load character description from manifest if available
    manifest_path = char_dir / "manifest.json"
    if manifest_path.exists():
        manifest = json.load(open(manifest_path))
        char_desc = manifest.get("description", character)
    else:
        char_desc = character

    refs = get_references(char_dir)
    print(f"Character: {character}")
    print(f"Description: {char_desc}")
    print(f"References: {[r.name for r in refs]}")
    print(f"Prompt type: {prompt_key}")
    print()

    prompt = PROMPTS[prompt_key].format(char_desc=char_desc)
    print(f"Prompt:\n{prompt}\n")

    try:
        img_bytes = generate(prompt, refs)

        timestamp = datetime.now().strftime("%H%M%S")
        outfile = OUTPUT_DIR / f"{character}-{prompt_key}-{timestamp}.png"
        outfile.write_bytes(img_bytes)

        print(f"SUCCESS: {outfile}")
        print(f"Size: {len(img_bytes)} bytes")

    except Exception as e:
        print(f"FAILED: {e}")
        return 1

    return 0


if __name__ == "__main__":
    print("=" * 60)
    print("CHARACTER REFERENCE SHEET TEST")
    print("=" * 60)
    print()
    print("Usage: python test-reference-sheet.py [character] [prompt_type]")
    print()
    print("Prompt types:")
    for k in PROMPTS:
        print(f"  - {k}")
    print()
    print("=" * 60)
    print()
    sys.exit(main())
