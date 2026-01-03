#!/usr/bin/env python3
"""
Test script for consultant's Scene Director prompt structure.
Tests the "Technical Noir" unified aesthetic approach for 2025-11-28 briefing.
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from illustrate import (
    generate_illustration, make_reference_collage,
    get_available_characters, load_style_presets
)

# Consultant's Scene Director prompts translated to our format
SCENE_DIRECTOR_PROMPTS = [
    {
        "title": "The Security Update: Row Level Protection",
        "narrative_element": "hero_moment",
        "characters": ["eliza"],
        "scene": """Eliza is welding a massive, glowing hexagonal bulkhead door into a dark server wall.
The door represents Entity-level Row Level Security - heavy, structural protection work.
Environment: Dark, industrial claustrophobic server tunnel with sparks flying.
Lighting: Deep shadows with harsh cyan rim light and bright orange welding sparks.
Camera: Low angle, looking up at the door to emphasize its weight and security.
Mood: Determined, protecting the core infrastructure.""",
        "style": "noir_ink",  # Tech Noir = noir_ink style
    },
    {
        "title": "Migration Limbo",
        "narrative_element": "conflict",
        "characters": ["peepo"],
        "scene": """Peepo sitting alone on a metal bench at a foggy, deserted futuristic subway station.
He's checking a wrist watch with a tired, bored expression - representing users waiting for token migration.
A digital sign above reads 'MIGRATION' but is glitching and partially illegible.
Environment: Heavy fog, empty platform, lonely atmosphere.
Lighting: Hazy monochromatic blue, single spotlight on Peepo.
Camera: Wide shot showing the emptiness and isolation of the station.
Mood: Sardonic patience, slight weariness from waiting.""",
        "style": "noir_ink",
    },
    {
        "title": "Polishing the Logs",
        "narrative_element": "journey",
        "characters": ["shaw"],
        "scene": """Shaw using a laser tool to organize a chaotic knot of neon cables into neat, parallel green lines.
The cables represent logging cleanup - JSON for production, readable single-line format for dev.
Environment: Dark crawlspace inside a mainframe, cramped technical space.
Lighting: Only light comes from the green laser tool and his teal goggles glowing.
Camera: Close up macro focus on the cables and his hands doing precise work.
Mood: Tech-savvy focus, the satisfaction of cleanup and organization.""",
        "style": "noir_ink",
    },
    {
        "title": "The Missing Evidence",
        "narrative_element": "evidence",
        "characters": ["marc", "spartan"],
        "scene": """Marc in foreground holding a magnifying lens to a floating, corrupted holographic document labeled 'SNAPSHOT'.
The document is half-burned/corrupted - representing users struggling to prove token holdings before the snapshot.
Spartan stands in the background, arms crossed, looking impatient and angry about lost tokens.
Environment: Dimly lit investigation room or data archive with filing systems.
Lighting: Noir shading - bright yellow from Marc's cybernetic eye against dark blue background.
Camera: Over-the-shoulder from Marc towards the document, with Spartan visible behind.
Mood: Skeptical scrutiny meets impatient intensity - investigation under pressure.""",
        "style": "noir_ink",
    },
]


def build_tech_noir_prompt(manifests: list, scene: str, characters: list) -> str:
    """Build prompt with Tech Noir style fusion using full manifest context."""

    # Build rich character descriptions from manifests
    char_sections = []
    for m in manifests:
        name = m.get('character', 'Unknown').upper()
        desc = m.get('description', '')
        features = m.get('features', {})
        signature = m.get('signature_action', '')
        psychology = m.get('default_psychology', '')
        role = m.get('narrative_role', '')

        # Visual details
        distinguishing = features.get('distinguishing', '')
        costume = features.get('costume', '')
        colors = ', '.join(features.get('colors', []))

        char_block = f"""**{name}**
- Visual: {distinguishing}
- Costume: {costume}
- Colors: {colors}
- Signature Action: {signature}
- Psychology: {psychology}
- Role: {role}"""
        char_sections.append(char_block)

    # Build relationship context if multiple characters
    relationship_context = ""
    if len(manifests) > 1:
        relationships = []
        for m in manifests:
            char_name = m.get('character', '')
            rels = m.get('relationships', {})
            for other_char in characters:
                if other_char != char_name and other_char in rels:
                    relationships.append(f"- {char_name.capitalize()} → {other_char.capitalize()}: {rels[other_char]}")
        if relationships:
            relationship_context = "\n\nCHARACTER DYNAMICS:\n" + "\n".join(relationships)

    char_section = "\n\n".join(char_sections)

    prompt = f"""Tech Noir illustration with anime-influenced character rendering.

CHARACTERS (must match reference sheet exactly):

{char_section}{relationship_context}

SCENE:
{scene}

STYLE REQUIREMENTS:
- Deep noir shadows with high contrast lighting
- Merge Tech Noir shadows with anime cel-shading on characters
- Industrial, cyberpunk environment aesthetic
- Dramatic rim lighting in cyan, orange, or green accents
- Gritty textures but clean character rendering
- Cinematic composition

OUTPUT: A single powerful editorial illustration. No text, no UI, no speech bubbles."""

    return prompt


def test_prompts(dry_run: bool = True, output_dir: Path = None):
    """Test the consultant's prompts."""

    if output_dir is None:
        output_dir = SCRIPT_DIR / "test_output" / "2025-11-28_tech_noir"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Testing Consultant's Scene Director Prompts")
    print("Unified Aesthetic: Technical Noir")
    print("=" * 60)

    for i, prompt_data in enumerate(SCENE_DIRECTOR_PROMPTS, 1):
        print(f"\n--- Scene {i}: {prompt_data['title']} ---")
        print(f"Narrative: {prompt_data['narrative_element']}")
        print(f"Characters: {', '.join(prompt_data['characters'])}")

        # Build character reference collage
        collage_bytes, manifests = make_reference_collage(prompt_data['characters'])

        if not collage_bytes:
            print(f"  WARNING: Could not create collage for {prompt_data['characters']}")
            continue

        print(f"  Created reference collage with {len(manifests)} character(s)")

        # Build the prompt
        full_prompt = build_tech_noir_prompt(manifests, prompt_data['scene'], prompt_data['characters'])

        print(f"\n  PROMPT:\n{'-'*40}")
        print(full_prompt[:500] + "..." if len(full_prompt) > 500 else full_prompt)
        print(f"{'-'*40}")

        if dry_run:
            print(f"  [DRY RUN] Would generate: {prompt_data['title']}")
            # Save prompt for review
            prompt_file = output_dir / f"{i:02d}_{prompt_data['title'].replace(' ', '_').replace(':', '')}_prompt.txt"
            prompt_file.write_text(full_prompt)
            print(f"  Saved prompt to: {prompt_file}")
        else:
            print(f"  Generating illustration...")
            image_bytes = generate_illustration(collage_bytes, full_prompt)

            if image_bytes:
                output_file = output_dir / f"{i:02d}_{prompt_data['title'].replace(' ', '_').replace(':', '')}.png"
                output_file.write_bytes(image_bytes)
                print(f"  Saved: {output_file}")
            else:
                print(f"  FAILED to generate image")

    print(f"\n{'='*60}")
    print(f"Output directory: {output_dir}")
    print(f"{'='*60}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test consultant Scene Director prompts")
    parser.add_argument("--generate", action="store_true", help="Actually generate images (default: dry run)")
    parser.add_argument("-o", "--output", type=Path, help="Output directory")
    args = parser.parse_args()

    test_prompts(dry_run=not args.generate, output_dir=args.output)
