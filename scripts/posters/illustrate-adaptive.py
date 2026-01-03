#!/usr/bin/env python3
"""
LLM-first illustration pipeline - format agnostic.

Accepts any input file (JSON, markdown, text) and uses LLM to:
1. Analyze content structure
2. Identify illustratable sections
3. Suggest styles and characters for each

Usage:
  # Analyze any file
  python scripts/posters/illustrate2.py the-council/facts/2025-12-14.json
  python scripts/posters/illustrate2.py the-council/retros/2025-01-retro.json
  python scripts/posters/illustrate2.py hackmd/facts/2025-12-14.md

  # Dry run - show ideas without generating
  python scripts/posters/illustrate2.py input.json --dry-run

  # Generate specific number of illustrations
  python scripts/posters/illustrate2.py input.json -n 3

  # Interactive selection
  python scripts/posters/illustrate2.py input.json -i
"""

import os
import sys
import json
import argparse
import logging
import time
from pathlib import Path
from datetime import datetime, timezone

import requests

# Add script directory to path for imports
SCRIPT_DIR = Path(__file__).parent.resolve()
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

# Reuse image generation from original
from illustrate import (
    generate_illustration,
    generate_dataviz,
    make_reference_collage,
    build_illustration_prompt,
    build_dataviz_prompt,
    get_available_characters,
    get_style_description,
    is_data_visualization_style,
    generate_creative_brief,
    load_style_presets,
    CHARACTERS_DIR,
)
from utils.icon_sheet import make_icon_sheet, extract_entities_from_facts

# --------------- Config ---------------

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
LLM_MODEL = "openai/gpt-4.1"

WORKSPACE_ROOT = SCRIPT_DIR.parent.parent
OUTPUT_DIR = WORKSPACE_ROOT / "media"

logging.basicConfig(level=logging.INFO, format='%(message)s')


# --------------- Content Analysis ---------------


def read_input_file(path: Path) -> tuple[str, str]:
    """Read input file and return (content, format_hint).

    Format hint is based on extension, but LLM will analyze actual structure.
    """
    suffix = path.suffix.lower()
    content = path.read_text(encoding='utf-8')

    if suffix == '.json':
        return content, 'json'
    elif suffix in ('.md', '.markdown'):
        return content, 'markdown'
    else:
        return content, 'text'


def extract_date_hint(content: str, format_hint: str) -> str:
    """Try to extract a date from content for output naming."""
    import re

    # Look for common date patterns
    patterns = [
        r'"(?:briefing_)?date":\s*"(\d{4}-\d{2}-\d{2})"',  # JSON date field
        r'"month_reviewed":\s*"(\d{4}-\d{2})"',  # Retro month
        r'RETRO-(\d{4}-\d{2})',  # Retro ID
        r'(\d{4}-\d{2}-\d{2})',  # Any YYYY-MM-DD
    ]

    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            date_str = match.group(1)
            # Normalize to YYYY-MM-DD
            if len(date_str) == 7:  # YYYY-MM
                date_str += "-01"
            return date_str

    return datetime.now().strftime("%Y-%m-%d")


def get_available_styles_summary() -> str:
    """Get condensed summary of available styles for LLM context."""
    presets = load_style_presets()
    styles = presets.get("styles", {})

    lines = []
    for name, config in styles.items():
        is_dataviz = config.get("is_data_visualization", False)
        desc = config.get("description", "")[:60]
        tag = " [NO CHARACTERS - data viz]" if is_dataviz else ""
        lines.append(f"- {name}: {desc}{tag}")

    return "\n".join(lines)


def fingerprint_structure(content: str, format_hint: str) -> str:
    """Generate a structural fingerprint of the content to help LLM understand it."""
    if format_hint == 'json':
        try:
            data = json.loads(content)
            return _fingerprint_json(data)
        except json.JSONDecodeError:
            return "Invalid JSON"
    elif format_hint == 'markdown':
        return _fingerprint_markdown(content)
    return f"Plain text, {len(content)} characters"


def _fingerprint_json(data, depth=0, max_depth=2) -> str:
    """Recursively fingerprint JSON structure."""
    indent = "  " * depth
    lines = []

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str):
                preview = value[:100].replace('\n', ' ')
                lines.append(f"{indent}- {key}: \"{preview}{'...' if len(value) > 100 else ''}\"")
            elif isinstance(value, list):
                if value and isinstance(value[0], dict):
                    sample_keys = list(value[0].keys())[:4]
                    lines.append(f"{indent}- {key}: [{len(value)} items, each with: {', '.join(sample_keys)}]")
                else:
                    lines.append(f"{indent}- {key}: [{len(value)} items]")
            elif isinstance(value, dict) and depth < max_depth:
                lines.append(f"{indent}- {key}:")
                lines.append(_fingerprint_json(value, depth + 1, max_depth))
            else:
                lines.append(f"{indent}- {key}: {type(value).__name__}")
    elif isinstance(data, list):
        lines.append(f"{indent}[{len(data)} items]")

    return "\n".join(lines)


def _fingerprint_markdown(content: str) -> str:
    """Fingerprint markdown by extracting headers."""
    import re
    headers = re.findall(r'^(#{1,3})\s+(.+)$', content, re.MULTILINE)
    if headers:
        lines = [f"{'  ' * (len(h[0])-1)}- {h[1]}" for h in headers[:15]]
        return "Sections:\n" + "\n".join(lines)
    return f"Markdown, {len(content)} characters"


def analyze_content(content: str, format_hint: str) -> list[dict]:
    """Use LLM to analyze content and identify illustratable sections.

    Returns list of illustration ideas:
    [{
        "id": str,           # unique identifier
        "title": str,        # human readable title
        "content": str,      # the content to visualize
        "style": str,        # suggested style name
        "characters": list,  # suggested character names (empty for dataviz)
        "rationale": str,    # why this section is interesting
    }]
    """
    available_styles = get_available_styles_summary()
    available_chars = get_available_characters()

    # Generate structure fingerprint
    structure = fingerprint_structure(content, format_hint)

    system_prompt = f"""You are a creative director at a tech publication, analyzing content to plan illustrations.

INPUT FORMAT: {format_hint}

CONTENT STRUCTURE:
{structure}

AVAILABLE ART STYLES:
{available_styles}

AVAILABLE CHARACTERS (for non-dataviz styles):
{', '.join(available_chars)}

STORYTELLING FRAMEWORK - identify these narrative elements in the content:
1. THE HERO MOMENT - What's the main achievement or theme? (editorial/tarot styles)
2. THE CONFLICT - What tension, challenge, or struggle exists? (noir_ink/comic_panel styles)
3. THE JOURNEY - What transformation or process happened? (cinematic_anime/paper_cutout styles)
4. THE EVIDENCE - What data or metrics tell the story? (dataviz/infographic styles - no characters)
5. THE HUMAN ELEMENT - Where are the people, community, relationships? (council/comic_panel styles)
6. THE VISION - What are the implications or future directions? (blueprint/synthwave styles)

Not every piece of content has all six elements. Identify which ones are present and worth illustrating.

OUTPUT FORMAT - return a JSON array with one object per identified element:
[
  {{
    "id": "unique_slug",
    "title": "Human Readable Title",
    "content": "Extract the actual text (50-200 words) that supports this narrative element",
    "style": "style_name_from_available_list",
    "characters": ["char1"] or [] for dataviz styles,
    "rationale": "Which narrative element this represents and why it's visually compelling"
  }}
]

IMPORTANT:
- Return multiple items - one for each narrative element you identify
- Extract actual content text, don't just reference it
- For dataviz styles, characters array must be empty []

STORYBOARD VARIETY - these images will be viewed as a set:
- Vary styles - don't repeat the same style
- Vary character count - mix solo, duo, and ensemble scenes
- Vary composition energy - balance intimate close-ups with expansive wide shots
- Create visual rhythm - not all high-energy, not all contemplative

Output ONLY the JSON array."""

    response = requests.post(
        OPENROUTER_ENDPOINT,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this content and identify illustration opportunities:\n\n{content[:100000]}"}
            ]
        },
        timeout=90
    )
    response.raise_for_status()

    result = response.json()
    raw = result["choices"][0]["message"]["content"]

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        logging.warning(f"Invalid JSON from LLM: {raw[:200]}")
        return []

    # Find the list - could be top-level, nested in any key, or a single item
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        # Check if this dict IS a single item (has content key) vs a wrapper
        if "content" in data:
            items = [data]  # Single item, wrap in list
        else:
            # Try to find any list value
            items = next((v for v in data.values() if isinstance(v, list)), [])
            if not items:
                logging.debug(f"No list found in response. Keys: {list(data.keys())}")
    else:
        items = []

    if not items:
        logging.warning(f"No items extracted. Response type: {type(data).__name__}, preview: {str(data)[:500]}")
    else:
        logging.debug(f"Found {len(items)} raw items. First item keys: {list(items[0].keys()) if items else 'none'}")

    # Normalize each item - keep only dicts with content, fill defaults
    return [
        {
            "id": item.get("id", f"section_{i}"),
            "title": item.get("title", "Untitled"),
            "content": item.get("content", ""),
            "style": item.get("style", "editorial"),
            "characters": item.get("characters") or [],
            "rationale": item.get("rationale", ""),
        }
        for i, item in enumerate(items)
        if isinstance(item, dict) and item.get("content")
    ]


def generate_scene_description(
    content: str,
    characters: list[str],
    style: str,
    creative_brief: dict = None
) -> str:
    """Generate scene/visualization description from content."""

    if is_data_visualization_style(style):
        system_prompt = """You create data visualization descriptions.
Extract KEY METRICS and DATA RELATIONSHIPS from the content.
Output a visualization description (Sankey, dashboard, infographic, etc.).
Do NOT describe characters. Focus on DATA REPRESENTATION.
Keep under 100 words. Output ONLY the description."""
    else:
        brief_section = ""
        if creative_brief:
            brief_section = f"""
ATMOSPHERE: {creative_brief.get('mood', '')}

"""
        # Build character instruction
        if characters:
            if len(characters) == 1:
                char_instruction = f"Feature {characters[0]} as the focal character."
            else:
                char_instruction = f"Feature these characters TOGETHER in dynamic interaction: {', '.join(characters)}. Show their relationship/collaboration."
        else:
            char_instruction = "No characters - focus on visual metaphor."

        system_prompt = f"""You are a storyboard artist for a tech publication, creating one frame of a visual narrative.

{brief_section}{char_instruction}

STORYBOARD PRINCIPLES:
- If multiple characters listed, show them INTERACTING (not just standing together)
- Find the visual metaphor - don't be literal
- Vary composition based on content:
   - Conflict → dynamic angles, tension between figures
   - Achievement → expansive, upward energy
   - Collaboration → characters working together, shared focus
   - Data/metrics → abstract patterns, no characters needed
   - Community → ensemble, varied expressions and poses

OUTPUT: One scene description under 50 words.
Describe CHARACTER ACTIONS and SPATIAL RELATIONSHIPS, not just who's present."""

    response = requests.post(
        OPENROUTER_ENDPOINT,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ]
        },
        timeout=60
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


# --------------- Main Pipeline ---------------


def extract_entities_from_content(content: str) -> list[str]:
    """Extract entity names mentioned in any content.

    Searches for known entities from manifest in the content text.
    Works with any format (JSON, markdown, plain text).
    """
    import re
    from utils.icon_sheet import load_manifest

    manifest = load_manifest()

    # Build lookup of all entity names and aliases
    entity_lookup = {}  # lowercase name/alias -> entity name
    for entity in manifest.get("entities", []):
        if entity.get("status") in ("skip", "review"):
            continue
        if not entity.get("icon_paths"):
            continue

        name = entity.get("name", "")
        entity_lookup[name.lower()] = name
        for alias in entity.get("aliases", []):
            if len(alias) >= 2:
                entity_lookup[alias.lower()] = name

    # Search for entity mentions in content
    content_lower = content.lower()
    found = set()

    for lookup_key, entity_name in entity_lookup.items():
        # Word boundary match to avoid partial matches
        pattern = r'\b' + re.escape(lookup_key) + r'\b'
        if re.search(pattern, content_lower):
            found.add(entity_name)

    return sorted(found)


def run_pipeline(
    input_path: Path,
    num_illustrations: int = None,
    interactive: bool = False,
    dry_run: bool = False,
    with_icons: bool = False
) -> int:
    """Main pipeline: analyze → select → generate."""

    print(f"\n{'='*60}")
    print(f"LLM-First Illustration Pipeline")
    print(f"{'='*60}")
    print(f"Input: {input_path}")

    # Read input
    content, format_hint = read_input_file(input_path)
    date_str = extract_date_hint(content, format_hint)
    print(f"Format: {format_hint}, Date: {date_str}")

    # Parse date for creative brief
    try:
        content_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        content_date = datetime.now()

    creative_brief = generate_creative_brief(content_date)
    print(f"\nCreative direction:")
    print(f"  Mood: {creative_brief['mood']}")

    # Extract entities and create icon sheet if requested
    icon_sheet_bytes = None
    if with_icons:
        print(f"\nExtracting entities for icons...")
        entities = extract_entities_from_content(content)
        if entities:
            print(f"  Found {len(entities)} entities: {', '.join(entities[:8])}{'...' if len(entities) > 8 else ''}")
            icon_sheet_bytes, found = make_icon_sheet(entities[:12])  # Limit to 12 icons
            if icon_sheet_bytes:
                print(f"  Created icon sheet with {len(found)} icons")
            else:
                print(f"  No icons found in manifest for these entities")
        else:
            print(f"  No known entities found in content")

    # Analyze content
    print(f"\nAnalyzing content...")
    ideas = analyze_content(content, format_hint)

    if not ideas:
        print("No illustration ideas found.")
        return 1

    # Display ideas
    print(f"\nFound {len(ideas)} illustration opportunities:\n")
    print("-" * 60)

    for i, idea in enumerate(ideas, 1):
        chars = ", ".join(idea.get("characters", [])) or "(no characters)"
        print(f"{i}. [{idea['style']}] {idea['title']}")
        print(f"   Characters: {chars}")
        print(f"   {idea.get('rationale', '')}")
        print(f"   Content: {idea['content'][:80]}...")
        print()

    print("-" * 60)

    # Selection
    if interactive:
        print("Enter numbers to generate (e.g., '1 3'), 'all', or 'q' to quit:")
        try:
            response = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0

        if response in ('q', 'quit'):
            return 0
        elif response == 'all':
            selected_ideas = ideas
        else:
            try:
                indices = [int(x) - 1 for x in response.split()]
                selected_ideas = [ideas[i] for i in indices if 0 <= i < len(ideas)]
            except (ValueError, IndexError):
                print("Invalid selection")
                return 1
    elif num_illustrations:
        selected_ideas = ideas[:num_illustrations]
    else:
        selected_ideas = ideas

    if not selected_ideas:
        print("No ideas selected.")
        return 0

    print(f"\nGenerating {len(selected_ideas)} illustration(s)...")

    if dry_run:
        print("\n[DRY RUN - not generating images]\n")
        for idea in selected_ideas:
            scene = generate_scene_description(
                idea["content"],
                idea.get("characters", []),
                idea["style"],
                creative_brief
            )
            print(f"  {idea['title']}:")
            print(f"    Style: {idea['style']}")
            print(f"    Scene: {scene}")
            print()
        return 0

    # Create output directory
    output_dir = OUTPUT_DIR / date_str
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate
    generated = []
    for i, idea in enumerate(selected_ideas, 1):
        print(f"\n[{i}/{len(selected_ideas)}] {idea['title']} ({idea['style']})...")

        try:
            style = idea["style"]
            characters = idea.get("characters", [])

            # Generate scene description
            scene = generate_scene_description(
                idea["content"],
                characters,
                style,
                creative_brief
            )
            print(f"  Scene: {scene[:60]}...")

            # Generate image
            if is_data_visualization_style(style):
                prompt = build_dataviz_prompt(scene, style, idea["content"])
                image_bytes = generate_dataviz(prompt)
            else:
                if not characters:
                    characters = ["eliza"]  # fallback

                # Filter to available characters
                available = get_available_characters()
                characters = [c for c in characters if c in available] or ["eliza"]

                collage_bytes, manifests = make_reference_collage(characters)
                prompt = build_illustration_prompt(manifests, scene, style=style)
                image_bytes = generate_illustration(collage_bytes, prompt, icon_sheet_bytes)

            # Save
            slug = idea["id"].replace("_", "-")
            output_path = output_dir / f"{slug}.png"
            output_path.write_bytes(image_bytes)
            # Save prompt alongside image
            prompt_path = output_path.with_suffix('.txt')
            prompt_path.write_text(prompt)
            print(f"  Saved: {output_path} (+prompt)")
            generated.append(output_path)

        except Exception as e:
            print(f"  Error: {e}")
            continue

    print(f"\n{'='*60}")
    print(f"Generated {len(generated)}/{len(selected_ideas)} illustrations")
    print(f"Output: {output_dir}/")
    print(f"{'='*60}")

    return 0


# --------------- CLI ---------------


def main():
    parser = argparse.ArgumentParser(
        description="LLM-first illustration pipeline - works with any input format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Input file (JSON, markdown, or text)"
    )
    parser.add_argument(
        "-n", "--num",
        type=int,
        help="Number of illustrations to generate (default: all)"
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Interactive mode - select which ideas to generate"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze and show ideas without generating images"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--with-icons",
        action="store_true",
        help="Include entity icons (logos, tokens) extracted from content"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args.input.exists():
        logging.error(f"Input file not found: {args.input}")
        return 1

    if not OPENROUTER_API_KEY and not args.dry_run:
        logging.error("OPENROUTER_API_KEY not set")
        return 1

    return run_pipeline(
        args.input,
        num_illustrations=args.num,
        interactive=args.interactive,
        dry_run=args.dry_run,
        with_icons=args.with_icons
    )


if __name__ == "__main__":
    sys.exit(main())
