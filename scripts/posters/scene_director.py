#!/usr/bin/env python3
"""
Scene Director Pipeline - Dynamic editorial illustration generation.

Transforms daily briefings into cohesive visual narratives using an LLM
as the creative director, then generates illustrations from the plan.

Architecture:
    facts.json → Director LLM → scene_plan.json → Image Generator → illustrations/

Usage:
    # Dry run - just generate the plan
    python scene_director.py the-council/facts/2025-11-28.json --dry-run

    # Generate images
    python scene_director.py the-council/facts/2025-11-28.json

    # Use specific output directory
    python scene_director.py the-council/facts/2025-11-28.json -o output/my-test
"""

import json
import argparse
import os
import base64
import random
from pathlib import Path
from datetime import datetime

# Local imports
SCRIPT_DIR = Path(__file__).parent
import sys
sys.path.insert(0, str(SCRIPT_DIR))

from illustrate import (
    make_reference_collage,
    generate_illustration,
    get_available_characters,
    load_style_presets,
    CHARACTERS_DIR,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Director-specific variety (independent from illustrate.py for more variation)
DIRECTOR_LIGHTING = [
    "cinematic three-point lighting with strong key",
    "moody single-source dramatic shadows",
    "soft diffused editorial lighting",
    "high-contrast noir lighting",
    "warm practical lighting from scene elements",
    "cool backlit silhouette lighting",
]

DIRECTOR_ATMOSPHERE = [
    "intimate and focused",
    "epic and expansive",
    "tense and claustrophobic",
    "dreamy and ethereal",
    "gritty and grounded",
    "clean and minimal",
]

DIRECTOR_SYSTEM_PROMPT = """You are the Creative Director for 'ElizaOS Magazine'. Transform a daily briefing into 4 editorial illustrations.

## CHARACTERS
- **Eliza**: Leadership, building, guiding
- **Shaw**: Hacking, tricks, mischief
- **Spartan**: Conflict, markets, battles
- **Marc**: Analysis, skepticism, data
- **Peepo**: Community, waiting, reactions

## VISUAL METAPHORS
Transform stories into visual metaphors. Keep descriptions SHORT (3-4 sentences).
- BAD: "Users frustrated about migration delay"
- GOOD: "Peepo sitting alone at foggy subway station, checking a glitching departure board."

## DAY STYLE
Pick ONE unified aesthetic for all 4 scenes (e.g., "Tech Noir", "Neon Blueprint", "Warm Industrial").

## OUTPUT FORMAT
Return JSON:
{
  "briefing_date": "YYYY-MM-DD",
  "day_style": "Style name",
  "scenes": [
    {
      "id": "scene_1",
      "title": "Short title",
      "characters": ["name"],
      "scene": "3-4 sentence visual description. Environment, lighting, mood. No explanations."
    }
  ]
}

Generate 4 scenes. Keep scene descriptions SHORT and visual."""


def load_character_manifests() -> list[dict]:
    """Load all character manifests into a list."""
    manifests = []
    for char_dir in CHARACTERS_DIR.iterdir():
        if char_dir.is_dir():
            manifest_path = char_dir / "manifest.json"
            if manifest_path.exists():
                with open(manifest_path) as f:
                    manifest = json.load(f)
                    manifest["name"] = char_dir.name  # Ensure name field
                    manifests.append(manifest)
    return manifests


def get_director_plan(briefing_data: dict, character_manifests: list[dict]) -> dict:
    """
    Send briefing to LLM to generate the Scene Director plan.

    Returns structured JSON with day_style and scenes array.
    """
    import requests

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable required")

    # Build character summary for the prompt
    char_summaries = []
    for m in character_manifests:
        char_summaries.append({
            "name": m.get("character", m.get("name", "unknown")),
            "description": m.get("description", ""),
            "signature_action": m.get("signature_action", ""),
            "psychology": m.get("default_psychology", ""),
            "narrative_role": m.get("narrative_role", ""),
        })

    user_message = f"""HERE IS TODAY'S BRIEFING:
{json.dumps(briefing_data, indent=2)}

HERE ARE THE AVAILABLE CHARACTERS:
{json.dumps(char_summaries, indent=2)}

Generate the 4-scene editorial plan as JSON."""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "openrouter/auto",
            "messages": [
                {"role": "system", "content": DIRECTOR_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.7,
            "response_format": {"type": "json_object"},
        },
        timeout=60,
    )
    response.raise_for_status()

    result = response.json()

    # Debug: check what we got back
    if "choices" not in result or not result["choices"]:
        print(f"  [DEBUG] Unexpected API response: {json.dumps(result, indent=2)[:500]}")
        raise ValueError("No choices in API response")

    content = result["choices"][0]["message"].get("content", "")

    if not content or not content.strip():
        print(f"  [DEBUG] Empty content. Full response: {json.dumps(result, indent=2)[:500]}")
        raise ValueError("Empty response from Director LLM")

    # Strip markdown code fences if present
    content = content.strip()
    if content.startswith("```"):
        # Remove opening fence (```json or ```)
        first_newline = content.find("\n")
        if first_newline != -1:
            content = content[first_newline + 1:]
        # Remove closing fence
        if content.endswith("```"):
            content = content[:-3].strip()

    # Parse JSON response
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"  [DEBUG] Invalid JSON returned:\n{content[:1000]}")
        raise ValueError(f"Director LLM returned invalid JSON: {e}")


def build_editorial_prompt(
    manifests: list[dict],
    scene: dict,
    day_style: str,
    briefing_date: datetime = None,
) -> str:
    """Build simple prompt matching consultant's successful format.

    Uses date-seeded RNG for lighting/atmosphere variety (offset seed from illustrate.py).
    """
    # Date-seeded variety for lighting and atmosphere
    if briefing_date:
        seed = int(briefing_date.strftime("%Y%m%d")) + 1000  # Offset from illustrate.py
        rng = random.Random(seed)
        lighting = rng.choice(DIRECTOR_LIGHTING)
        atmosphere = rng.choice(DIRECTOR_ATMOSPHERE)
    else:
        lighting = "cinematic three-point lighting with strong key"
        atmosphere = "intimate and focused"

    # Build character sections - visual details only
    char_sections = []
    for m in manifests:
        name = m.get("character", m.get("name", "Unknown")).upper()
        features = m.get("features", {})
        colors = ', '.join(features.get('colors', []))

        char_block = f"""**{name}**
- Visual: {features.get('distinguishing', m.get('description', ''))}
- Costume: {features.get('costume', '')}
- Colors: {colors}"""
        char_sections.append(char_block)

    char_section = "\n\n".join(char_sections)

    # Get scene description (handle both old and new field names)
    scene_desc = scene.get('scene') or scene.get('scene_description', '')

    prompt = f"""{day_style} illustration with anime-influenced character rendering.

CHARACTERS (must match reference sheet exactly):

{char_section}

SCENE:
{scene_desc}

STYLE REQUIREMENTS:
- {lighting}
- {day_style} aesthetic throughout
- {atmosphere} mood
- Clean character rendering matching reference sheet
- Cinematic composition

OUTPUT: A single powerful editorial illustration. No text, no UI, no speech bubbles."""

    return prompt


def run_pipeline(
    facts_path: Path,
    output_dir: Path = None,
    dry_run: bool = False,
    save_plan: bool = True,
    style_override: str = None,
) -> dict:
    """
    Run the full Scene Director pipeline.

    Args:
        facts_path: Path to daily facts JSON
        output_dir: Where to save outputs (default: test_output/{date}_director/)
        dry_run: If True, only generate plan, don't create images
        save_plan: If True, save the scene plan JSON
        style_override: Override the LLM's day_style selection

    Returns:
        The scene plan dict
    """
    # Load briefing
    with open(facts_path) as f:
        briefing = json.load(f)

    date_str = briefing.get("briefing_date", "unknown")

    # Parse date for variety seeding
    try:
        briefing_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        briefing_date = None  # Fall back to default lighting/atmosphere

    # Set output directory
    if output_dir is None:
        output_dir = SCRIPT_DIR.parent.parent / "media" / "editorial" / date_str
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print(f"Scene Director Pipeline")
    print(f"Input: {facts_path}")
    print(f"Date: {date_str}")
    print("=" * 60)

    # Load character manifests
    manifests = load_character_manifests()
    print(f"\nLoaded {len(manifests)} character manifests")

    # Phase 1: Director generates the plan
    print(f"\n🎬 Director is analyzing briefing...")
    plan = get_director_plan(briefing, manifests)

    # Apply style override if provided
    if style_override:
        print(f"🎨 Day Style: {style_override} (override)")
        plan["day_style"] = style_override
    else:
        print(f"🎨 Day Style: {plan.get('day_style', 'Unknown')}")

    if save_plan:
        plan_path = output_dir / "scene_plan.json"
        with open(plan_path, "w") as f:
            json.dump(plan, f, indent=2)
        print(f"\n📋 Saved plan to: {plan_path}")

    # Phase 2: Generate images from plan
    print(f"\n{'='*60}")
    print(f"Scenes to generate: {len(plan.get('scenes', []))}")
    print("=" * 60)

    for i, scene in enumerate(plan.get("scenes", []), 1):
        print(f"\n--- Scene {i}: {scene.get('title', 'Untitled')} ---")
        print(f"Characters: {', '.join(scene.get('characters', []))}")

        if dry_run:
            # Build and save prompt for review
            scene_manifests = [
                m for m in manifests
                if m.get("character", m.get("name", "")).lower() in [c.lower() for c in scene.get("characters", [])]
            ]

            if scene_manifests:
                prompt = build_editorial_prompt(
                    scene_manifests,
                    scene,
                    plan.get("day_style", "Editorial"),
                    briefing_date,
                )

                prompt_path = output_dir / f"{i:02d}_{scene.get('id', 'scene')}_prompt.txt"
                prompt_path.write_text(prompt)
                print(f"  [DRY RUN] Saved prompt: {prompt_path.name}")
            else:
                print(f"  [WARNING] No manifests found for characters: {scene.get('characters')}")
            continue

        # Actual generation
        try:
            # Get manifests for this scene's characters
            scene_manifests = [
                m for m in manifests
                if m.get("character", m.get("name", "")).lower() in [c.lower() for c in scene.get("characters", [])]
            ]

            if not scene_manifests:
                print(f"  [ERROR] No manifests for: {scene.get('characters')}")
                continue

            # Create reference collage
            char_names = [m.get("character", m.get("name")) for m in scene_manifests]
            collage_bytes, _ = make_reference_collage(char_names)

            # Build prompt
            prompt = build_editorial_prompt(
                scene_manifests,
                scene,
                plan.get("day_style", "Editorial"),
                briefing_date,
            )

            # Generate
            print(f"  Generating...")
            image_bytes = generate_illustration(collage_bytes, prompt)

            if image_bytes:
                image_path = output_dir / f"{i:02d}_{scene.get('id', 'scene')}.png"
                image_path.write_bytes(image_bytes)
                # Save prompt alongside image
                prompt_path = image_path.with_suffix('.txt')
                prompt_path.write_text(prompt)
                print(f"  ✓ Saved: {image_path.name} (+prompt)")
            else:
                print(f"  [ERROR] Generation failed")

        except Exception as e:
            print(f"  [ERROR] {e}")

    print(f"\n{'='*60}")
    print(f"Output directory: {output_dir}")
    print("=" * 60)

    return plan


def main():
    parser = argparse.ArgumentParser(
        description="Scene Director - Dynamic editorial illustration pipeline"
    )
    parser.add_argument(
        "facts_file",
        type=Path,
        help="Path to daily facts JSON file",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output directory (default: test_output/{date}_director/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only generate plan and prompts, don't create images",
    )
    parser.add_argument(
        "--no-save-plan",
        action="store_true",
        help="Don't save the scene plan JSON",
    )
    parser.add_argument(
        "-s", "--style",
        type=str,
        help="Override day style (e.g., 'Tech Noir', 'Warm Industrial', 'Solarpunk')",
    )

    args = parser.parse_args()

    if not args.facts_file.exists():
        print(f"Error: File not found: {args.facts_file}")
        sys.exit(1)

    run_pipeline(
        facts_path=args.facts_file,
        output_dir=args.output,
        dry_run=args.dry_run,
        save_plan=not args.no_save_plan,
        style_override=args.style,
    )


if __name__ == "__main__":
    main()
