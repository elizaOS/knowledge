#!/usr/bin/env python3
"""
Generate character poses using Nano Banana Pro with chroma key background removal.

Usage:
  python scripts/posters/generate-character-poses.py eliza
  python scripts/posters/generate-character-poses.py eliza --pose happy
  python scripts/posters/generate-character-poses.py eliza --all-angles
  python scripts/posters/generate-character-poses.py eliza --dry-run
  python scripts/posters/generate-character-poses.py --list
"""

import os
import sys
import io
import json
import base64
import argparse
import logging
from pathlib import Path
from PIL import Image, ImageChops, ImageFilter

# --------------- Config ---------------

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
IMAGE_MODEL = "google/gemini-3-pro-image-preview"

SCRIPT_DIR = Path(__file__).parent.resolve()
CHARACTERS_DIR = SCRIPT_DIR.parent.parent / "posters" / "characters"

# 8 core poses - covers 90% of use cases
POSES = {
    "neutral":    "head and shoulders portrait, neutral expression, looking at viewer",
    "happy":      "head and shoulders portrait, warm genuine smile, friendly expression",
    "serious":    "head and shoulders portrait, serious focused expression, determined look",
    "thinking":   "head and shoulders portrait, thoughtful expression, slight head tilt",
    "explaining": "torso up, explaining with one hand raised, engaged teaching expression",
    "celebrating":"torso up, celebratory pose, fist raised, excited victorious expression",
    "pointing":   "dynamic pose pointing forward, engaged confident expression",
    "skeptical":  "skeptical pose, raised eyebrow, arms crossed, doubtful expression",
}

# When to use each pose (for reference)
POSE_HINTS = {
    "neutral":    "default, avatars, profile pics",
    "happy":      "positive news, wins, community",
    "serious":    "security alerts, important announcements",
    "thinking":   "analysis, strategy, planning",
    "explaining": "tutorials, documentation, how-tos",
    "celebrating":"milestones, achievements, market pumps",
    "pointing":   "calls to action, highlights, directions",
    "skeptical":  "due diligence, questioning claims, analysis",
}

GREEN_BG = "solid flat green background hex #00b140, no shadows"
STYLE = "character illustration, consistent with reference, maintain exact design and colors"
CONSTRAINTS = "high quality, clean lines, no text, no logos, no watermarks"

logging.basicConfig(level=logging.INFO, format='%(message)s')

# --------------- Core Functions ---------------

def load_manifest(char_dir: Path) -> dict | None:
    """Load character manifest if exists."""
    manifest = char_dir / "manifest.json"
    return json.load(open(manifest)) if manifest.exists() else None


def get_references(char_dir: Path, manifest: dict | None) -> list[Path]:
    """Get up to 3 reference images for character."""
    if manifest:
        usable = [
            char_dir / img["filename"]
            for img in manifest.get("images", [])
            if img.get("usable_as_reference", True)
        ]
        if usable:
            return [p for p in usable[:3] if p.exists()]

    # Fallback: first 3 images
    images = sorted([
        f for f in char_dir.iterdir()
        if f.suffix.lower() in {".png", ".jpg", ".jpeg"}
        and not f.name.startswith(("thumb-", "generated-"))
    ])
    return images[:3]


def image_to_base64(path: Path) -> str:
    """Convert image to base64 data URL."""
    mime = "image/png" if path.suffix == ".png" else "image/jpeg"
    data = base64.b64encode(path.read_bytes()).decode()
    return f"data:{mime};base64,{data}"


def generate_image(prompt: str, refs: list[Path]) -> bytes:
    """Call Nano Banana Pro to generate image."""
    import requests

    content = []
    # Images first (per Gemini feedback)
    for ref in refs:
        content.append({"type": "image_url", "image_url": {"url": image_to_base64(ref)}})

    content.append({"type": "text", "text": (
        "Reference images show the character. Maintain exact design, colors, style.\n\n"
        f"{prompt}"
    )})

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


def remove_green_screen(img_bytes: bytes) -> Image.Image:
    """Remove green background using HSV chroma key."""
    im = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    hsv = im.convert("HSV")
    H, S, V = hsv.split()

    # Sample border to find background hue
    w, h = im.size
    px = im.convert("RGB").load()
    hues = []
    for x in range(w):
        for y in [0, 1, h-1, h-2]:
            r, g, b = px[x, y]
            hue = Image.new("RGB", (1,1), (r,g,b)).convert("HSV").getpixel((0,0))[0]
            hues.append(hue)
    bg_hue = sorted(hues)[len(hues)//2]  # median

    # Create mask
    Hpx, Spx, Vpx = H.load(), S.load(), V.load()
    mask = Image.new("L", (w, h), 0)
    Mpx = mask.load()

    for y in range(h):
        for x in range(w):
            if Spx[x, y] > 38 and Vpx[x, y] > 38:  # saturation/value threshold
                hdist = min(abs(Hpx[x, y] - bg_hue), 255 - abs(Hpx[x, y] - bg_hue))
                if hdist <= 18:  # hue tolerance
                    Mpx[x, y] = 255

    # Blur edges, apply mask
    mask = mask.filter(ImageFilter.GaussianBlur(1.2))
    out = im.copy()
    out.putalpha(ImageChops.multiply(out.split()[3], Image.eval(mask, lambda p: 255-p)))
    return out


# --------------- Main ---------------

def main():
    parser = argparse.ArgumentParser(description="Generate character poses")
    parser.add_argument("character", nargs="?", help="Character folder name")
    parser.add_argument("-p", "--pose", help="Specific pose (default: all)")
    parser.add_argument("--all-angles", action="store_true", help="Generate front + 3/4 angles")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be generated")
    parser.add_argument("--list", action="store_true", help="List available poses")
    args = parser.parse_args()

    if args.list:
        print("Available poses:")
        for name, hint in POSE_HINTS.items():
            print(f"  {name:12} - {hint}")
        return 0

    if not args.character:
        parser.error("character required (or use --list)")

    char_dir = CHARACTERS_DIR / args.character
    if not char_dir.exists():
        logging.error(f"Not found: {char_dir}")
        return 1

    if not OPENROUTER_API_KEY and not args.dry_run:
        logging.error("OPENROUTER_API_KEY not set")
        return 1

    # Load character info
    manifest = load_manifest(char_dir)
    refs = get_references(char_dir, manifest)
    char_desc = manifest.get("description", args.character) if manifest else args.character

    logging.info(f"Character: {args.character}")
    logging.info(f"References: {[r.name for r in refs]}")

    # Determine what to generate
    poses = [args.pose] if args.pose else list(POSES.keys())
    angles = ["front", "3/4_left", "3/4_right"] if args.all_angles else ["front"]

    logging.info(f"Generating: {len(poses)} poses × {len(angles)} angles = {len(poses)*len(angles)} images\n")

    success, failed = 0, 0

    for pose in poses:
        if pose not in POSES:
            logging.warning(f"Unknown pose: {pose}")
            continue

        for angle in angles:
            suffix = f"-{angle}" if angle != "front" else ""
            outfile = char_dir / f"generated-{pose}{suffix}.png"

            if outfile.exists():
                logging.info(f"[skip] {outfile.name}")
                continue

            if args.dry_run:
                logging.info(f"[would create] {outfile.name}")
                continue

            # Build prompt
            angle_text = {"front": "front view", "3/4_left": "three-quarter left", "3/4_right": "three-quarter right"}[angle]
            prompt = f"Generate {char_desc}. {POSES[pose]}, {angle_text}. {STYLE}. {GREEN_BG}. {CONSTRAINTS}."

            logging.info(f"[generating] {outfile.name}")

            try:
                img_bytes = generate_image(prompt, refs)
                cutout = remove_green_screen(img_bytes)
                cutout.save(outfile, "PNG", optimize=True)
                logging.info(f"[saved] {outfile.name}")
                success += 1
            except Exception as e:
                logging.error(f"[failed] {outfile.name}: {e}")
                failed += 1

    logging.info(f"\nDone: {success} created, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
