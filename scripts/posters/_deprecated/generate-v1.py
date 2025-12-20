#!/usr/bin/env python3
"""
Consolidated character asset generator.

Uses manifest.json metadata to intelligently select reference images,
creates Pillow collages, and generates character sheets/poses with
full costume details in prompts.

Usage:
  # Reference sheets
  python scripts/posters/generate.py eliza turnaround
  python scripts/posters/generate.py eliza expressions

  # Single poses (predefined)
  python scripts/posters/generate.py eliza pose happy
  python scripts/posters/generate.py eliza pose serious --angle 3/4_right

  # Single poses (custom description)
  python scripts/posters/generate.py eliza pose "pointing excitedly at something"

  # Options
  python scripts/posters/generate.py eliza turnaround --sketch   # Line art first
  python scripts/posters/generate.py eliza pose happy --output custom.png
  python scripts/posters/generate.py --list                      # Show poses/types
  python scripts/posters/generate.py eliza turnaround --dry-run  # Preview without API call
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
from typing import Optional

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

# --------------- Predefined Poses ---------------

POSES = {
    "neutral": "head and shoulders portrait, neutral expression, looking at viewer",
    "happy": "head and shoulders portrait, warm genuine smile, friendly expression",
    "serious": "head and shoulders portrait, serious focused expression, determined look",
    "thinking": "head and shoulders portrait, thoughtful expression, slight head tilt",
    "explaining": "torso up, explaining with one hand raised, engaged teaching expression",
    "celebrating": "torso up, celebratory pose, fist raised, excited victorious expression",
    "pointing": "dynamic pose pointing forward, engaged confident expression",
    "skeptical": "skeptical pose, raised eyebrow, arms crossed, doubtful expression",
}

POSE_HINTS = {
    "neutral": "default, avatars, profile pics",
    "happy": "positive news, wins, community",
    "serious": "security alerts, important announcements",
    "thinking": "analysis, strategy, planning",
    "explaining": "tutorials, documentation, how-tos",
    "celebrating": "milestones, achievements, market pumps",
    "pointing": "calls to action, highlights, directions",
    "skeptical": "due diligence, questioning claims, analysis",
}

# --------------- Output Type Config ---------------

OUTPUT_TYPES = {
    "turnaround": {
        "description": "4-view character model sheet (front, 3/4, side, back)",
        "ref_filter": {"pose": ["full_body"], "limit": 3},
        "layout": "horizontal",
    },
    "expressions": {
        "description": "6-expression grid (neutral, happy, angry, sad, surprised, thinking)",
        "ref_filter": {"pose": ["bust", "portrait", "headshot"], "limit": 3},
        "layout": "horizontal",
    },
    "pose": {
        "description": "Single character pose",
        # For pose: always include 1 full_body + 1 bust/portrait for face detail
        "ref_filter": {"mixed": True, "limit": 2},
        "layout": "horizontal",
    },
}

OUTPUT_PROMPTS = {
    "turnaround": """professional character model sheet of {description},
showing the SAME character from 4 angles arranged horizontally: front view, 3/4 view, side profile, back view,
neutral T-pose with arms slightly spread, standing straight,
full body visible head to toe in each view,
orthographic style, no perspective distortion,
consistent character design across all views,

COSTUME (must appear in ALL views): {costume}
PRIMARY COLORS: {colors}
ART STYLE: {style}

clean white background, reference sheet style,
professional character turnaround, game art style,
no text, no labels, no watermarks""",

    "expressions": """professional character expression sheet for {description},
head and shoulders only,
showing 6 different expressions in a horizontal row: neutral, happy/smiling, angry, sad, surprised, thinking,
same character same angle (front view) for each expression,
consistent art style across all expressions,

COSTUME: {costume}
ART STYLE: {style}

clean background, reference sheet format,
no text, no labels, no watermarks""",

    "pose": """character illustration of {description},
{pose_description}, {angle},
{framing},

COSTUME: {costume}
PRIMARY COLORS: {colors}
ART STYLE: {style}

clean simple background,
character reference style, consistent proportions,
high quality, no text, no watermarks""",
}

COLLAGE_LAYOUTS = {
    "horizontal": (3, 1),  # cols, rows
    "grid_2x2": (2, 2),
    "vertical": (1, 3),
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
            f"Run: python scripts/posters/analyze-characters.py --character {character}"
        )

    with open(manifest_path) as f:
        return json.load(f)


def select_refs(manifest: dict, output_type: str) -> list[Path]:
    """Select reference images based on output type requirements.

    Queries manifest metadata semantically (by pose, angle) rather than alphabetically.

    Selection strategies:
    - pose filter: Only select images matching specific pose types
    - mixed filter: Select 1 full_body (for costume) + 1 face shot (for detail)
    - usable_as_reference: Filter by the usable flag
    """
    char_dir = CHARACTERS_DIR / manifest["character"]
    config = OUTPUT_TYPES.get(output_type, OUTPUT_TYPES["pose"])
    filters = config.get("ref_filter", {})
    limit = filters.get("limit", 3)

    all_images = manifest.get("images", [])

    # Strategy: "mixed" - pick 1 full_body + 1 face-focused image
    if filters.get("mixed"):
        selected = _select_mixed_refs(all_images, limit)
        images = selected
    else:
        images = all_images

        # Filter by pose type
        if "pose" in filters:
            pose_types = filters["pose"]
            images = [img for img in images if img.get("pose") in pose_types]
            logging.debug(f"After pose filter ({pose_types}): {len(images)} images")

        # Filter by usable_as_reference flag
        if filters.get("usable_as_reference"):
            images = [img for img in images if img.get("usable_as_reference", True)]
            logging.debug(f"After usable filter: {len(images)} images")

        # Prioritize angle variety for better reference coverage
        images = _prioritize_angle_variety(images)

        # Limit count
        images = images[:limit]

    # Convert to paths
    paths = []
    for img in images:
        path = char_dir / img["filename"]
        if path.exists():
            paths.append(path)
        else:
            logging.warning(f"Reference image not found: {path}")

    logging.info(f"Selected {len(paths)} reference(s): {[p.name for p in paths]}")
    return paths


def _select_mixed_refs(images: list[dict], limit: int) -> list[dict]:
    """Select a mix of full_body and face-focused references.

    This ensures the AI sees both:
    1. Full costume (from full_body images)
    2. Face details (from bust/portrait images)
    """
    selected = []

    # First: pick best full_body image (prefer front or 3/4 angle)
    full_body = [img for img in images if img.get("pose") == "full_body"]
    if full_body:
        # Prefer front-facing full body
        front_full = [img for img in full_body if img.get("angle") in ["front", "3/4_left", "3/4_right"]]
        if front_full:
            selected.append(front_full[0])
        else:
            selected.append(full_body[0])

    # Second: pick best face shot (bust or portrait)
    face_shots = [img for img in images if img.get("pose") in ["bust", "portrait", "headshot"]]
    if face_shots and len(selected) < limit:
        # Prefer different angle than full_body if possible
        already_angles = {img.get("angle") for img in selected}
        different_angle = [img for img in face_shots if img.get("angle") not in already_angles]
        if different_angle:
            selected.append(different_angle[0])
        else:
            selected.append(face_shots[0])

    # Fill remaining slots with any usable images
    remaining = [img for img in images
                 if img not in selected and img.get("usable_as_reference", True)]
    for img in remaining:
        if len(selected) >= limit:
            break
        selected.append(img)

    return selected


def _prioritize_angle_variety(images: list[dict]) -> list[dict]:
    """Reorder images to maximize angle variety in selection."""
    if len(images) <= 1:
        return images

    # Group by angle
    by_angle = {}
    for img in images:
        angle = img.get("angle", "unknown")
        if angle not in by_angle:
            by_angle[angle] = []
        by_angle[angle].append(img)

    # Round-robin from each angle group
    result = []
    angles = list(by_angle.keys())
    idx = 0
    while len(result) < len(images):
        angle = angles[idx % len(angles)]
        if by_angle[angle]:
            result.append(by_angle[angle].pop(0))
        idx += 1
        # Remove empty groups
        angles = [a for a in angles if by_angle[a]]
        if not angles:
            break

    return result


def make_collage(refs: list[Path], layout: str = "horizontal") -> bytes:
    """Create a single reference collage image using Pillow.

    Returns PNG bytes.
    """
    if not refs:
        raise ValueError("No reference images provided")

    cols, rows = COLLAGE_LAYOUTS.get(layout, (3, 1))

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

    # Normalize to consistent size (preserve aspect ratio, fit in box)
    target_size = (512, 512)
    resized = []
    for img in pil_images:
        # Thumbnail preserves aspect ratio
        img_copy = img.copy()
        img_copy.thumbnail(target_size, Image.LANCZOS)

        # Center on transparent canvas
        canvas = Image.new("RGBA", target_size, (0, 0, 0, 0))
        x = (target_size[0] - img_copy.width) // 2
        y = (target_size[1] - img_copy.height) // 2
        canvas.paste(img_copy, (x, y), img_copy if img_copy.mode == "RGBA" else None)
        resized.append(canvas)

    # Create collage canvas
    canvas_w = cols * target_size[0]
    canvas_h = rows * target_size[1]
    collage = Image.new("RGBA", (canvas_w, canvas_h), (255, 255, 255, 255))

    # Paste images
    for i, img in enumerate(resized):
        if i >= cols * rows:
            break
        x = (i % cols) * target_size[0]
        y = (i // cols) * target_size[1]
        collage.paste(img, (x, y), img)

    # Convert to bytes
    buffer = io.BytesIO()
    collage.save(buffer, "PNG", optimize=True)
    return buffer.getvalue()


def build_prompt(
    manifest: dict,
    output_type: str,
    sketch: bool = False,
    pose_name: str = None,
    pose_custom: str = None,
    angle: str = None,
) -> str:
    """Build generation prompt with full costume details from manifest."""
    template = OUTPUT_PROMPTS.get(output_type, OUTPUT_PROMPTS["pose"])

    features = manifest.get("features", {})

    # Determine pose description
    if pose_name and pose_name in POSES:
        pose_desc = POSES[pose_name]
    elif pose_custom:
        pose_desc = pose_custom
    else:
        pose_desc = "neutral standing pose, looking at viewer"

    # Determine framing from pose
    if any(word in pose_desc.lower() for word in ["full body", "standing", "walking"]):
        framing = "full body visible from head to feet"
    elif any(word in pose_desc.lower() for word in ["torso", "waist"]):
        framing = "visible from head to waist"
    else:
        framing = "head and shoulders visible"

    prompt = template.format(
        description=manifest.get("description", manifest["character"]),
        costume=features.get("costume", "character's typical outfit"),
        colors=", ".join(features.get("colors", ["characteristic colors"])),
        style=features.get("style", "stylized character art"),
        pose_description=pose_desc,
        angle=angle or "front view",
        framing=framing,
    )

    if sketch:
        prompt += "\n\nOUTPUT STYLE: Clean line art, black and white sketch, minimal shading, no color fill. Like a professional character design sketch."

    return prompt


def generate(collage_bytes: bytes, prompt: str) -> bytes:
    """Call Nano Banana Pro to generate image from collage + prompt.

    Returns PNG bytes.
    """
    collage_b64 = base64.b64encode(collage_bytes).decode("utf-8")

    content = [
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{collage_b64}"}
        },
        {
            "type": "text",
            "text": (
                "These reference images show the character design. "
                "Maintain EXACT character design, colors, costume, and art style throughout.\n\n"
                f"{prompt}"
            )
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

    # Extract image from response
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


def get_output_path(
    character: str,
    output_type: str,
    pose_name: str = None,
    sketch: bool = False,
    custom_output: str = None,
) -> Path:
    """Determine output path for generated image."""
    if custom_output:
        return Path(custom_output)

    char_dir = CHARACTERS_DIR / character
    gen_dir = char_dir / "generated"
    gen_dir.mkdir(exist_ok=True)

    if output_type == "pose" and pose_name:
        filename = f"pose-{pose_name}"
    else:
        filename = output_type

    if sketch:
        filename += "-sketch"

    filename += ".png"
    return gen_dir / filename


def list_info():
    """Print available poses and output types."""
    print("OUTPUT TYPES:")
    print("-" * 50)
    for name, config in OUTPUT_TYPES.items():
        print(f"  {name:15} {config['description']}")

    print()
    print("PREDEFINED POSES:")
    print("-" * 50)
    for name, desc in POSES.items():
        hint = POSE_HINTS.get(name, "")
        print(f"  {name:12} {desc[:50]}...")
        if hint:
            print(f"  {' '*12} Use for: {hint}")

    print()
    print("AVAILABLE CHARACTERS:")
    print("-" * 50)
    for char_dir in sorted(CHARACTERS_DIR.iterdir()):
        if char_dir.is_dir() and not char_dir.name.startswith("."):
            manifest = char_dir / "manifest.json"
            status = "ready" if manifest.exists() else "needs analysis"
            print(f"  {char_dir.name:15} [{status}]")


# --------------- Main ---------------


def main():
    parser = argparse.ArgumentParser(
        description="Generate character assets from manifest data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "character",
        nargs="?",
        help="Character name (folder in posters/characters/)"
    )
    parser.add_argument(
        "output_type",
        nargs="?",
        choices=list(OUTPUT_TYPES.keys()),
        help="Type of output to generate"
    )
    parser.add_argument(
        "pose",
        nargs="?",
        help="For 'pose' type: predefined pose name or custom description"
    )

    parser.add_argument(
        "--sketch",
        action="store_true",
        help="Generate line art sketch instead of full color"
    )
    parser.add_argument(
        "--angle",
        choices=["front", "3/4_left", "3/4_right", "side_left", "side_right"],
        default="front",
        help="Camera angle for pose output (default: front)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Custom output path (default: characters/{name}/generated/)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without calling API"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available poses, output types, and characters"
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
        list_info()
        return 0

    # Validate required args
    if not args.character:
        parser.error("character is required (or use --list)")
    if not args.output_type:
        parser.error("output_type is required (turnaround, expressions, pose)")

    # API key check
    if not OPENROUTER_API_KEY and not args.dry_run:
        logging.error("OPENROUTER_API_KEY not set")
        return 1

    try:
        # 1. Load manifest
        logging.info(f"Loading manifest for '{args.character}'...")
        manifest = load_manifest(args.character)
        logging.info(f"Character: {manifest.get('description', args.character)}")

        # 2. Select references
        refs = select_refs(manifest, args.output_type)
        if not refs:
            logging.error("No suitable reference images found")
            return 1

        # 3. Determine pose details
        pose_name = None
        pose_custom = None
        if args.output_type == "pose" and args.pose:
            if args.pose in POSES:
                pose_name = args.pose
            else:
                pose_custom = args.pose

        # 4. Build prompt
        prompt = build_prompt(
            manifest,
            args.output_type,
            sketch=args.sketch,
            pose_name=pose_name,
            pose_custom=pose_custom,
            angle=args.angle,
        )

        # 5. Determine output path
        output_path = get_output_path(
            args.character,
            args.output_type,
            pose_name=pose_name or (args.pose if pose_custom else None),
            sketch=args.sketch,
            custom_output=args.output,
        )

        # Dry run: show what would happen
        if args.dry_run:
            print()
            print("=" * 60)
            print("DRY RUN - No API call will be made")
            print("=" * 60)
            print()
            print(f"Character: {args.character}")
            print(f"Output type: {args.output_type}")
            print(f"References: {[r.name for r in refs]}")
            print(f"Output path: {output_path}")
            print(f"Sketch mode: {args.sketch}")
            print()
            print("PROMPT:")
            print("-" * 60)
            print(prompt)
            print("-" * 60)
            return 0

        # 6. Create collage
        logging.info("Creating reference collage...")
        layout = OUTPUT_TYPES[args.output_type].get("layout", "horizontal")
        collage_bytes = make_collage(refs, layout)
        logging.info(f"Collage size: {len(collage_bytes)} bytes")

        # 7. Generate
        logging.info("Generating image...")
        image_bytes = generate(collage_bytes, prompt)

        # 8. Save
        output_path.parent.mkdir(parents=True, exist_ok=True)
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
