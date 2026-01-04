#!/usr/bin/env python3
"""
Generate simple icons from tags - just the word as the prompt.
1024x1024, 1:1 aspect ratio, nothing fancy.

Usage:
    # Single tag
    python generate-tag-icons.py "development"

    # Multiple tags
    python generate-tag-icons.py "development" "community" "strategy"

    # From file (one tag per line)
    python generate-tag-icons.py --from-file tags.txt

    # All unique tags from facts
    python generate-tag-icons.py --from-facts
"""

import os
import sys
import json
import base64
import argparse
import random
import requests
from pathlib import Path

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
IMAGE_MODEL = "google/gemini-2.5-flash-image-preview"

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR.parent.parent / "media" / "icons" / "tags"
FACTS_DIR = SCRIPT_DIR.parent.parent / "the-council" / "facts"


DEFAULT_PREFIX = "icon: "

# Prompt prefix options - organized by archetype
# Key insight: encode WHICH human mistake, not THAT it's wrong
PROMPT_PREFIXES = {
    # === PROVEN (user-tested, good results) ===
    "stock": "Stock photo misunderstanding of ",
    "intern": "Overconfident intern interpretation of ",
    "idiomatic": "Idiomatic literal interpretation of ",
    "literal": "Literal but wrong interpretation of ",

    # === EXPERIMENTAL (archetype-based) ===

    # === RETIRED (meta-instructions, less reliable) ===
    # "icon": "icon: ",
    # "linkedin": "LinkedIn-core interpretation of ",
    # "childrens": "Children's book literal interpretation of ",
    # "celebrity": "Celebrity-brained interpretation of ",
    # "misread": "Visually misread meaning of ",
    # "pun": "Pun-first interpretation of ",
    # "headline": "Headline-only interpretation of ",
    # "misinterpreted": "Deliberately misinterpreted version of ",
    # "boomer": "Boomer interpretation of ",
    # "wikipedia": "Wikipedia disambiguation gone wrong for ",
    # "misinterpreted": "Deliberately misinterpreted version of ",
    # "misread": "Visually misread meaning of ",
    # "common": "Common misinterpretation of the word ",
    # "surface": "Surface-level interpretation of ",
    # "wrong": "Intentionally wrong visual interpretation of ",
    # "comedic": "Comedically incorrect interpretation of ",
    # "pedantic": "Pedantically literal interpretation of ",
    # "semantic": "Semantically incorrect but visually literal take on ",
    # "lexical": "Lexical ambiguity exploited for humor: ",
    # "ambiguous": "Ambiguous term, wrong domain interpretation of ",
    # "homonym": "Homonym-based misinterpretation of ",
    # "stripped": "Context-stripped interpretation of ",
    # "aggressive": "Aggressively literal interpretation of ",
    # "malicious": "Maliciously literal interpretation of ",
    # "technical": "Technically correct, contextually wrong take on ",
    # "hr": "HR-approved misunderstanding of ",
}


def generate_icon(tag: str, prefix: str = None) -> tuple[bytes, str]:
    """Generate icon with just the tag as prompt. 1024x1024 square.

    Returns: (image_bytes, prompt_used)
    """
    prefix = prefix if prefix is not None else DEFAULT_PREFIX
    prompt = f"{prefix}{tag}"

    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": IMAGE_MODEL,
            "modalities": ["image", "text"],
            "messages": [{"role": "user", "content": prompt}],
            "image_config": {
                "aspect_ratio": "1:1",
                "image_size": "1K",
            },
        },
        timeout=120,
    )
    resp.raise_for_status()
    result = resp.json()

    # Extract image
    images = result["choices"][0]["message"].get("images", [])
    if not images:
        raise ValueError(f"No image generated for '{tag}'")

    image_url = images[0]["image_url"]["url"]
    if image_url.startswith("data:"):
        base64_data = image_url.split(",", 1)[1]
        return base64.b64decode(base64_data), prompt

    raise ValueError(f"Unexpected image format for '{tag}'")


def get_unique_tags_from_facts() -> list[str]:
    """Extract unique tags from all facts files."""
    tags = set()
    for f in FACTS_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text())
            tags_obj = data.get("tags", {})

            # Extract from nested structure
            # .tags.themes[], .tags.derived[], .tags.story_type[], etc.
            for key in ["themes", "derived", "story_type", "priority", "manual"]:
                for tag in tags_obj.get(key, []):
                    if isinstance(tag, str) and tag.strip():
                        # Split comma-separated tags and add individually
                        for t in tag.split(","):
                            t = t.strip()
                            if t:
                                tags.add(t)

            # .tags.sentiment.context[]
            sentiment = tags_obj.get("sentiment", {})
            for tag in sentiment.get("context", []):
                if isinstance(tag, str) and tag.strip():
                    for t in tag.split(","):
                        t = t.strip()
                        if t:
                            tags.add(t)

        except Exception:
            continue
    return sorted(tags)


def main():
    parser = argparse.ArgumentParser(description="Generate icons from tags")
    parser.add_argument("tags", nargs="*", help="Tags to generate icons for")
    parser.add_argument("--from-file", type=Path, help="Read tags from file")
    parser.add_argument("--from-facts", action="store_true", help="Use tags from facts/*.json")
    parser.add_argument("-o", "--output", type=Path, default=OUTPUT_DIR, help="Output directory")
    parser.add_argument("--skip-existing", action="store_true", help="Skip if icon already exists")
    parser.add_argument(
        "-p", "--prefix",
        choices=list(PROMPT_PREFIXES.keys()) + ["random"],
        default="icon",
        help=f"Prompt prefix style (use 'random' to rotate): {', '.join(PROMPT_PREFIXES.keys())}",
    )
    parser.add_argument("--list-prefixes", action="store_true", help="List all prefix options")
    args = parser.parse_args()

    if args.list_prefixes:
        print("Available prefix styles:\n")
        for key, prefix in PROMPT_PREFIXES.items():
            print(f"  {key:15} → \"{prefix}{{tag}}\"")
        sys.exit(0)

    if not OPENROUTER_API_KEY:
        print("Error: OPENROUTER_API_KEY not set")
        sys.exit(1)

    # Collect tags
    tags = []
    if args.from_facts:
        tags = get_unique_tags_from_facts()
        print(f"Found {len(tags)} unique tags from facts")
    elif args.from_file:
        tags = [line.strip() for line in args.from_file.read_text().splitlines() if line.strip()]
    else:
        tags = args.tags

    if not tags:
        print("No tags provided. Use --help for usage.")
        sys.exit(1)

    # Generate
    args.output.mkdir(parents=True, exist_ok=True)
    use_random = args.prefix == "random"
    prefix_list = list(PROMPT_PREFIXES.values())

    if use_random:
        print(f"Using random prefix rotation ({len(prefix_list)} styles)")
    else:
        prefix = PROMPT_PREFIXES[args.prefix]
        print(f"Using prefix: \"{prefix}...\"")

    for i, tag in enumerate(tags, 1):
        output_path = args.output / f"{tag}.png"
        prompt_path = args.output / f"{tag}.txt"

        if args.skip_existing and output_path.exists():
            print(f"[{i}/{len(tags)}] {tag} - skipped (exists)")
            continue

        # Pick prefix (random or fixed)
        if use_random:
            prefix = random.choice(prefix_list)

        print(f"[{i}/{len(tags)}] {tag} - generating...", end=" ", flush=True)

        try:
            image_bytes, prompt = generate_icon(tag, prefix)
            output_path.write_bytes(image_bytes)
            prompt_path.write_text(prompt)
            print(f"saved")
        except Exception as e:
            print(f"failed: {e}")
            continue

    print(f"\nOutput: {args.output}/")


if __name__ == "__main__":
    main()
