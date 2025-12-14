#!/usr/bin/env python3
"""
Analyze character images using GPT-5.2 and generate manifest.json files.

Like a sculptor examining their reference material - describes what EXISTS
in each image (pose, angle, costume, distinguishing features) to build
a catalog for future pose generation.

Usage:
  # Analyze all characters (auto-discovers folders)
  python scripts/posters/analyze-characters.py

  # Analyze specific character
  python scripts/posters/analyze-characters.py --character eliza

  # Skip already analyzed images
  python scripts/posters/analyze-characters.py --skip-existing

  # Force re-analyze all
  python scripts/posters/analyze-characters.py --force
"""

import os
import sys
import json
import base64
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
import requests
import textwrap

# Config
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-5.2"

SCRIPT_DIR = Path(__file__).parent.resolve()
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent
CHARACTERS_DIR = WORKSPACE_ROOT / "posters" / "characters"

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Analysis prompt for GPT-5.2
ANALYSIS_PROMPT = """Analyze this character image for a digital asset catalog. Describe what you SEE, not what you imagine.

Return a JSON object with these exact fields:
{
  "pose": "full_body" | "bust" | "headshot" | "action" | "portrait",
  "angle": "front" | "3/4_left" | "3/4_right" | "side_left" | "side_right" | "back",
  "expression": "neutral" | "happy" | "serious" | "thinking" | "surprised" | "concerned" | "angry" | "confident" | "other",
  "action": "standing" | "sitting" | "walking" | "pointing" | "waving" | "arms_crossed" | "hands_on_hips" | "gesturing" | "typing" | "other",
  "background": "transparent" | "solid_color" | "gradient" | "scene" | "other",
  "background_color": "#hexcode or null if not solid",
  "features_visible": ["face", "hair", "full_costume", "hands", "feet", etc.],
  "quality": "high" | "medium" | "low",
  "usable_as_reference": true | false,
  "description": "One sentence describing this specific image for asset selection"
}

Be precise about what's actually visible. If expression is hard to determine, use "neutral".
Output ONLY valid JSON, no markdown code blocks."""

CHARACTER_SUMMARY_PROMPT = """Based on analyzing multiple images of this character, provide a summary.

Return a JSON object:
{
  "description": "Brief character description (role, personality vibe)",
  "features": {
    "distinguishing": "Key visual traits that define this character",
    "colors": ["primary colors associated with character"],
    "costume": "Description of typical outfit/attire",
    "style": "Art style (cartoon, semi-realistic, anime, etc.)"
  }
}

Output ONLY valid JSON, no markdown code blocks."""


def load_image_as_base64(path: Path) -> str:
    """Load image and return as base64 data URL."""
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


def analyze_image(image_path: Path) -> dict:
    """Use GPT-5.2 to analyze a single image."""
    logging.debug(f"Analyzing: {image_path.name}")

    image_url = load_image_as_base64(image_path)

    response = requests.post(
        OPENROUTER_ENDPOINT,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": image_url}},
                        {"type": "text", "text": ANALYSIS_PROMPT}
                    ]
                }
            ]
        },
        timeout=60
    )
    response.raise_for_status()

    result = response.json()
    content = result["choices"][0]["message"]["content"].strip()

    # Parse JSON from response (handle potential markdown code blocks)
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()

    try:
        analysis = json.loads(content)
    except json.JSONDecodeError as e:
        logging.warning(f"Failed to parse JSON for {image_path.name}: {e}")
        logging.debug(f"Raw content: {content}")
        analysis = {
            "pose": "unknown",
            "angle": "unknown",
            "expression": "neutral",
            "action": "unknown",
            "background": "unknown",
            "description": f"Analysis failed: {str(e)[:50]}",
            "usable_as_reference": False
        }

    return analysis


def generate_character_summary(character_name: str, image_analyses: list[dict]) -> dict:
    """Generate overall character summary from analyzed images."""
    # Create a text summary of all images for context
    image_summaries = "\n".join([
        f"- {img.get('filename', 'unknown')}: {img.get('description', 'No description')}"
        for img in image_analyses[:10]  # Limit context
    ])

    prompt = f"""Character: {character_name}

Analyzed images:
{image_summaries}

{CHARACTER_SUMMARY_PROMPT}"""

    response = requests.post(
        OPENROUTER_ENDPOINT,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}]
        },
        timeout=60
    )
    response.raise_for_status()

    result = response.json()
    content = result["choices"][0]["message"]["content"].strip()

    # Parse JSON
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()

    try:
        summary = json.loads(content)
    except json.JSONDecodeError:
        summary = {
            "description": f"{character_name} character",
            "features": {
                "distinguishing": "Unknown",
                "colors": [],
                "costume": "Unknown",
                "style": "Unknown"
            }
        }

    return summary


def get_character_folders() -> list[Path]:
    """Auto-discover character folders."""
    if not CHARACTERS_DIR.exists():
        logging.error(f"Characters directory not found: {CHARACTERS_DIR}")
        return []

    folders = [
        d for d in CHARACTERS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    ]
    return sorted(folders)


def get_image_files(character_dir: Path) -> list[Path]:
    """Get all image files in a character directory."""
    extensions = {".png", ".jpg", ".jpeg", ".webp"}
    images = [
        f for f in character_dir.iterdir()
        if f.is_file() and f.suffix.lower() in extensions
        and not f.name.startswith("thumb-")  # Skip thumbnails
    ]
    return sorted(images)


def load_existing_manifest(character_dir: Path) -> Optional[dict]:
    """Load existing manifest if present."""
    manifest_path = character_dir / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path) as f:
            return json.load(f)
    return None


def save_manifest(character_dir: Path, manifest: dict):
    """Save manifest to character directory."""
    manifest_path = character_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    logging.info(f"Saved: {manifest_path}")


def format_succinct_summary(manifest: dict) -> str:
    """Format manifest as succinct summary for human review."""
    name = manifest.get("character", "unknown").upper()
    desc = manifest.get("description", "No description")
    features = manifest.get("features", {})

    lines = [
        f"=== {name} ===",
        desc,
    ]

    if features.get("distinguishing"):
        lines.append(f"- {features['distinguishing']}")

    if features.get("colors"):
        colors = ", ".join(features["colors"])
        lines.append(f"- Colors: {colors}")

    if features.get("costume"):
        costume = features["costume"]
        # Truncate if too long
        if len(costume) > 80:
            costume = costume[:77] + "..."
        lines.append(f"- {costume}")

    if features.get("style"):
        lines.append(f"- Style: {features['style']}")

    lines.append(f"- {manifest.get('image_count', 0)} images analyzed")

    return "\n".join(lines)


def edit_manifest(manifest: dict, character_dir: Path) -> dict:
    """Open manifest in editor for user modification."""
    import subprocess
    import tempfile

    # Get editor from environment
    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL") or "nano"

    # Write manifest to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        json.dump(manifest, tmp, indent=2)
        tmp_path = tmp.name

    print(f"Opening in {editor}... (save and exit to continue)")

    try:
        subprocess.run([editor, tmp_path], check=True)

        # Reload edited manifest
        with open(tmp_path) as f:
            edited = json.load(f)

        print("Manifest updated.")
        return edited

    except subprocess.CalledProcessError:
        print("Editor exited with error, keeping original manifest.")
        return manifest
    except json.JSONDecodeError as e:
        print(f"Invalid JSON after edit: {e}")
        print("Keeping original manifest.")
        return manifest
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def confirm_manifest(manifest: dict, character_dir: Path) -> tuple[bool, dict]:
    """Display summary and ask for confirmation. Returns (confirmed, manifest)."""
    print()
    print(format_succinct_summary(manifest))
    print()

    while True:
        try:
            response = input("Correct? [Y/n/e]dit: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return False, manifest

        if response in ("", "y", "yes"):
            return True, manifest
        elif response in ("n", "no"):
            return False, manifest
        elif response in ("e", "edit"):
            manifest = edit_manifest(manifest, character_dir)
            print()
            print(format_succinct_summary(manifest))
            print()
            continue
        else:
            print("Please enter Y, n, or e")


def process_character(character_dir: Path, skip_existing: bool = False, force: bool = False) -> dict:
    """Process a single character directory."""
    character_name = character_dir.name
    logging.info(f"\n{'='*50}")
    logging.info(f"Processing: {character_name}")
    logging.info(f"{'='*50}")

    # Load existing manifest
    existing = load_existing_manifest(character_dir)
    existing_images = {}
    if existing and not force:
        existing_images = {img["filename"]: img for img in existing.get("images", [])}

    # Get all images
    image_files = get_image_files(character_dir)
    logging.info(f"Found {len(image_files)} images")

    # Analyze each image
    analyzed_images = []
    for img_path in image_files:
        filename = img_path.name

        # Skip if already analyzed
        if skip_existing and filename in existing_images:
            logging.info(f"  [skip] {filename} (already analyzed)")
            analyzed_images.append(existing_images[filename])
            continue

        logging.info(f"  [analyze] {filename}")
        try:
            analysis = analyze_image(img_path)
            analysis["filename"] = filename
            analyzed_images.append(analysis)
        except Exception as e:
            logging.error(f"  [error] {filename}: {e}")
            analyzed_images.append({
                "filename": filename,
                "error": str(e),
                "usable_as_reference": False
            })

    # Generate character summary
    logging.info(f"Generating character summary...")
    summary = generate_character_summary(character_name, analyzed_images)

    # Build manifest
    manifest = {
        "character": character_name,
        "description": summary.get("description", ""),
        "features": summary.get("features", {}),
        "analyzed_at": datetime.now().isoformat(),
        "image_count": len(analyzed_images),
        "images": analyzed_images
    }

    return manifest


def main():
    parser = argparse.ArgumentParser(
        description="Analyze character images and generate manifest.json files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "-c", "--character",
        help="Specific character to analyze (folder name)"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip images already in manifest"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-analyze all images, ignoring existing manifest"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be analyzed without making API calls"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Skip confirmation prompt, save automatically"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not OPENROUTER_API_KEY and not args.dry_run:
        logging.error("OPENROUTER_API_KEY environment variable not set")
        return 1

    # Get character folders to process
    if args.character:
        char_dir = CHARACTERS_DIR / args.character
        if not char_dir.exists():
            logging.error(f"Character folder not found: {char_dir}")
            return 1
        folders = [char_dir]
    else:
        folders = get_character_folders()

    if not folders:
        logging.error("No character folders found")
        return 1

    logging.info(f"Found {len(folders)} character(s): {[f.name for f in folders]}")

    if args.dry_run:
        logging.info("\nDRY RUN - showing what would be analyzed:")
        for folder in folders:
            images = get_image_files(folder)
            existing = load_existing_manifest(folder)
            existing_count = len(existing.get("images", [])) if existing else 0
            logging.info(f"  {folder.name}: {len(images)} images ({existing_count} already in manifest)")
        return 0

    # Process each character
    results = []
    for folder in folders:
        try:
            manifest = process_character(
                folder,
                skip_existing=args.skip_existing,
                force=args.force
            )

            # Confirm with user unless --auto
            if args.auto:
                save_manifest(folder, manifest)
                results.append((folder.name, "success", len(manifest["images"])))
            else:
                confirmed, manifest = confirm_manifest(manifest, folder)
                if confirmed:
                    save_manifest(folder, manifest)
                    results.append((folder.name, "success", len(manifest["images"])))
                else:
                    logging.info(f"Skipped {folder.name} (not confirmed)")
                    results.append((folder.name, "skipped", "not confirmed"))

        except Exception as e:
            logging.error(f"Failed to process {folder.name}: {e}")
            results.append((folder.name, "failed", str(e)))

    # Summary
    logging.info(f"\n{'='*50}")
    logging.info("SUMMARY")
    logging.info(f"{'='*50}")
    for name, status, info in results:
        if status == "success":
            logging.info(f"  {name}: {info} images cataloged")
        elif status == "skipped":
            logging.info(f"  {name}: skipped ({info})")
        else:
            logging.error(f"  {name}: FAILED - {info}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
