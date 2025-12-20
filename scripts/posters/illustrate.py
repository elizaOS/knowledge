#!/usr/bin/env python3
"""
Generate story illustrations using character reference sheets.

Uses reference-sheet.png from each character folder to maintain consistency.

Usage:
  # Basic - character + prompt
  python scripts/posters/illustrate.py eliza "celebrating a product launch"

  # With art style
  python scripts/posters/illustrate.py eliza "presenting at conference" -s editorial

  # Multiple characters
  python scripts/posters/illustrate.py eliza marc "discussing code on whiteboard"

  # From facts file (generates prompt from summary)
  python scripts/posters/illustrate.py eliza -f the-council/facts/2025-12-14.json

  # Interactive mode - analyze facts and pick from multiple ideas
  python scripts/posters/illustrate.py -f the-council/facts/2025-12-14.json -i

  # Custom output
  python scripts/posters/illustrate.py eliza "happy moment" -o celebration.png

  # List available styles
  python scripts/posters/illustrate.py --list-styles
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
LLM_MODEL = "openai/gpt-4.1"
IMAGE_MODEL = "google/gemini-3-pro-image-preview"

SCRIPT_DIR = Path(__file__).parent.resolve()
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent
CHARACTERS_DIR = SCRIPT_DIR / "characters"
OUTPUT_DIR = WORKSPACE_ROOT / "posters"
STYLE_PRESETS_FILE = SCRIPT_DIR / "config" / "style-presets.json"

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

# --------------- Style System ---------------


def load_style_presets() -> dict:
    """Load style presets from JSON config file."""
    if not STYLE_PRESETS_FILE.exists():
        return {"styles": {}, "defaults": {"style": "editorial"}}

    with open(STYLE_PRESETS_FILE) as f:
        return json.load(f)


def get_available_styles() -> list[str]:
    """Get list of available style names."""
    presets = load_style_presets()
    return list(presets.get("styles", {}).keys())


def get_style_description(style_name: str) -> str:
    """Get style description for prompt building."""
    presets = load_style_presets()
    styles = presets.get("styles", {})

    if style_name not in styles:
        return "editorial illustration style"

    config = styles[style_name]
    return config.get("description", style_name)


def is_data_visualization_style(style_name: str) -> bool:
    """Check if style is a data visualization style (no characters needed)."""
    presets = load_style_presets()
    styles = presets.get("styles", {})
    if style_name not in styles:
        return False
    return styles[style_name].get("is_data_visualization", False)


def get_style_config(style_name: str) -> dict:
    """Get full style configuration."""
    presets = load_style_presets()
    styles = presets.get("styles", {})
    return styles.get(style_name, {})


# --------------- Reference Sheet Loading ---------------


def get_reference_sheet(character: str) -> Path:
    """Get path to character's reference sheet."""
    char_dir = CHARACTERS_DIR / character
    ref_sheet = char_dir / "reference-sheet.png"

    if not ref_sheet.exists():
        raise FileNotFoundError(
            f"No reference sheet for '{character}'. "
            f"Run: python scripts/posters/generate.py {character}"
        )

    return ref_sheet


def load_manifest(character: str) -> dict:
    """Load character manifest for description."""
    char_dir = CHARACTERS_DIR / character
    manifest_path = char_dir / "manifest.json"

    if not manifest_path.exists():
        return {"character": character, "description": character}

    with open(manifest_path) as f:
        return json.load(f)


def make_reference_collage(characters: list[str]) -> tuple[bytes, list[dict]]:
    """Create collage of reference sheets and return with manifests."""
    ref_sheets = []
    manifests = []

    for char in characters:
        ref_path = get_reference_sheet(char)
        ref_sheets.append(ref_path)
        manifests.append(load_manifest(char))

    if not ref_sheets:
        raise ValueError("No reference sheets found")

    # Load and combine images
    pil_images = []
    for ref in ref_sheets:
        img = Image.open(ref).convert("RGBA")
        pil_images.append(img)

    # Stack horizontally if multiple
    if len(pil_images) == 1:
        collage = pil_images[0]
    else:
        # Resize to consistent height
        target_height = 512
        resized = []
        for img in pil_images:
            ratio = target_height / img.height
            new_width = int(img.width * ratio)
            resized.append(img.resize((new_width, target_height), Image.LANCZOS))

        total_width = sum(img.width for img in resized)
        collage = Image.new("RGBA", (total_width, target_height), (255, 255, 255, 255))
        x = 0
        for img in resized:
            collage.paste(img, (x, 0))
            x += img.width

    buffer = io.BytesIO()
    collage.save(buffer, "PNG", optimize=True)
    return buffer.getvalue(), manifests


# --------------- Prompt Generation ---------------


def build_illustration_prompt(
    manifests: list[dict],
    scene: str,
    style: str = "editorial"
) -> str:
    """Build the illustration generation prompt."""
    # Character descriptions
    char_descriptions = []
    for m in manifests:
        name = m.get("character", "character")
        desc = m.get("description", name)
        char_descriptions.append(f"- {name.upper()}: {desc}")

    char_block = "\n".join(char_descriptions)

    # Style description
    style_desc = get_style_description(style)

    prompt = f"""Create an illustration for a tech news magazine.

CHARACTERS (use reference sheet for exact appearance):
{char_block}

SCENE: {scene}

ART STYLE: {style_desc}

REQUIREMENTS:
- Characters must match reference sheet EXACTLY (colors, costume, features)
- Dynamic composition suitable for editorial use
- Professional quality illustration
- No text or watermarks
- Scene should feel natural and engaging"""

    return prompt


def build_dataviz_prompt(viz_description: str, style: str, content: str) -> str:
    """Build prompt for data visualization (no characters)."""
    style_config = get_style_config(style)
    style_desc = style_config.get("description", "data visualization")
    style_suffix = style_config.get("style_suffix", "")

    prompt = f"""Create a professional data visualization for a tech news publication.

VISUALIZATION TYPE: {viz_description}

CONTENT CONTEXT:
{content[:500]}

STYLE: {style_desc}

REQUIREMENTS:
- Professional infographic/dashboard quality
- Clean, polished vector aesthetic
- Include section headers and labels where appropriate
- Strategic use of color to highlight key insights
- Editorial publication quality
- Modern, sophisticated design{style_suffix}"""

    return prompt


def generate_prompt_from_facts(facts_path: Path, manifests: list[dict]) -> str:
    """Generate a scene description from a facts file."""
    with open(facts_path) as f:
        facts = json.load(f)

    summary = facts.get("overall_summary", "")
    if not summary:
        raise ValueError("No overall_summary in facts file")

    # Use LLM to convert summary to scene
    char_names = [m.get("character", "character") for m in manifests]

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
                    "content": f"""Convert this news summary into a brief scene description for an illustration.
The scene should feature: {', '.join(char_names)}
Keep it under 50 words. Focus on a single compelling moment that captures the news.
Output ONLY the scene description, no explanation."""
                },
                {
                    "role": "user",
                    "content": summary
                }
            ]
        },
        timeout=60
    )
    response.raise_for_status()

    result = response.json()
    return result["choices"][0]["message"]["content"].strip()


# --------------- Interactive Mode ---------------

# Category to style mapping (first style is default)
CATEGORY_STYLES = {
    "github_updates": "dataviz",
    "discord_updates": "comic_panel",
    "user_feedback": "editorial",
    "strategic_insights": "cinematic_anime",
    "market_analysis": "dataviz",
    "twitter_news_highlights": "comic_panel",
}

# Category to suggested characters
CATEGORY_CHARACTERS = {
    "github_updates": ["shaw", "eliza"],
    "discord_updates": ["eliza", "peepo"],
    "user_feedback": ["peepo", "eliza"],
    "strategic_insights": ["eliza", "marc", "spartan"],
    "market_analysis": ["marc", "spartan"],
    "twitter_news_highlights": ["eliza", "peepo"],
}


def get_available_characters() -> list[str]:
    """Get list of characters with reference sheets."""
    chars = []
    for char_dir in CHARACTERS_DIR.iterdir():
        if char_dir.is_dir() and not char_dir.name.startswith("."):
            if (char_dir / "reference-sheet.png").exists():
                chars.append(char_dir.name)
    return sorted(chars)


def extract_category_content(facts: dict, category: str) -> str:
    """Extract readable content from a category."""
    categories = facts.get("categories", {})
    if category not in categories:
        return ""

    data = categories[category]

    if isinstance(data, list):
        # discord_updates, user_feedback, etc.
        texts = []
        for item in data[:3]:  # Limit to first 3
            if isinstance(item, dict):
                text = item.get("summary") or item.get("observation") or item.get("insight")
                if text:
                    texts.append(text[:200])
        return " ".join(texts)

    elif isinstance(data, dict):
        # github_updates has nested structure
        if "overall_focus" in data:
            focus = data.get("overall_focus", [])
            texts = [item.get("claim", "")[:200] for item in focus[:2] if isinstance(item, dict)]
            return " ".join(texts)

    return ""


def generate_illustration_ideas(facts_path: Path) -> list[dict]:
    """Analyze facts file and generate multiple illustration ideas."""
    with open(facts_path) as f:
        facts = json.load(f)

    date_str = facts.get("briefing_date", "unknown")
    available_chars = get_available_characters()

    ideas = []

    # Always add overall summary as first option
    if facts.get("overall_summary"):
        ideas.append({
            "category": "overall",
            "title": "Daily Overview",
            "content": facts["overall_summary"][:300],
            "characters": ["eliza"],
            "style": "editorial",
        })

    # Add ideas for each category with content
    categories = facts.get("categories", {})
    for cat_name, cat_data in categories.items():
        content = extract_category_content(facts, cat_name)
        if not content or len(content) < 50:
            continue

        # Get suggested characters (filter to available)
        suggested = CATEGORY_CHARACTERS.get(cat_name, ["eliza"])
        chars = [c for c in suggested if c in available_chars][:3]
        if not chars:
            chars = [available_chars[0]] if available_chars else ["eliza"]

        ideas.append({
            "category": cat_name,
            "title": cat_name.replace("_", " ").title(),
            "content": content[:300],
            "characters": chars,
            "style": CATEGORY_STYLES.get(cat_name, "editorial"),
        })

    return ideas


def generate_scene_from_content(content: str, characters: list[str], style: str = None) -> str:
    """Use LLM to convert content into a scene/visualization description."""

    # Check if this is a data visualization style
    if style and is_data_visualization_style(style):
        style_config = get_style_config(style)
        system_prompt = style_config.get(
            "scene_generation_prompt",
            """You are creating a data visualization. Extract KEY METRICS and DATA RELATIONSHIPS.
Output a visualization description (Sankey, dashboard, infographic, etc.).
Do NOT describe characters. Focus on DATA REPRESENTATION.
Keep under 100 words."""
        )
    else:
        # Character-based scene
        system_prompt = f"""Convert this news content into a brief scene description for an illustration.
The scene should feature: {', '.join(characters)}
Keep it under 50 words. Focus on a single compelling visual moment.
Output ONLY the scene description, no explanation."""

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
    result = response.json()
    return result["choices"][0]["message"]["content"].strip()


def get_style_alternatives(category: str) -> list[str]:
    """Get alternative styles for a category from presets."""
    presets = load_style_presets()
    cat_config = presets.get("categories", {}).get(category, {})
    return cat_config.get("suggested_styles", ["editorial", "risograph", "noir_ink"])


def display_styles_menu():
    """Display numbered list of all available styles."""
    styles = get_available_styles()
    print("\nAvailable styles:")
    for i, style in enumerate(styles, 1):
        desc = get_style_description(style)[:50]
        print(f"  {i:2}. {style}: {desc}...")
    return styles


def prompt_for_style(idea: dict, all_styles: list[str]) -> tuple[str, bool]:
    """Prompt user for style choice. Returns (style, generate_variations)."""
    default_style = idea["style"]

    try:
        prompt_text = f"  Style? [{default_style}] / # to pick / v for variations: "
        response = input(prompt_text).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return default_style, False

    if response == "":
        return default_style, False
    elif response == "v":
        return default_style, True  # Generate variations
    elif response == "?":
        display_styles_menu()
        return prompt_for_style(idea, all_styles)  # Ask again
    else:
        try:
            style_idx = int(response) - 1
            if 0 <= style_idx < len(all_styles):
                return all_styles[style_idx], False
        except ValueError:
            # Maybe they typed a style name directly
            if response in all_styles:
                return response, False
        print(f"  Invalid choice, using {default_style}")
        return default_style, False


def interactive_mode(facts_path: Path, dry_run: bool = False) -> int:
    """Run interactive mode - present ideas and generate selected ones."""
    print(f"\nAnalyzing {facts_path.name}...")
    ideas = generate_illustration_ideas(facts_path)

    if not ideas:
        print("No illustration ideas found in this facts file.")
        return 1

    # Get all available styles for reference
    all_styles = get_available_styles()

    # Display ideas
    print(f"\nFound {len(ideas)} illustration ideas:\n")
    print("-" * 60)

    for i, idea in enumerate(ideas, 1):
        chars = ", ".join(idea["characters"])
        print(f"{i}. [{idea['style']}] {idea['title']}")
        print(f"   Characters: {chars}")
        print(f"   {idea['content'][:100]}...")
        print()

    print("-" * 60)
    print("Enter numbers to generate (e.g., '1 3 5'), 'all', or 'q' to quit")
    print("Tip: Type '?' during style selection to see all styles")

    try:
        response = input("\nGenerate which? ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return 0

    if response in ("q", "quit", "exit"):
        return 0

    # Parse selection
    if response == "all":
        selected = list(range(len(ideas)))
    else:
        try:
            selected = [int(x) - 1 for x in response.split()]
            selected = [i for i in selected if 0 <= i < len(ideas)]
        except ValueError:
            print("Invalid selection")
            return 1

    if not selected:
        print("No valid selections")
        return 1

    # Prompt for style per idea
    print(f"\nStyle selection for {len(selected)} idea(s):")
    style_choices = []  # List of (idea_idx, style, generate_variations)

    for idx in selected:
        idea = ideas[idx]
        print(f"\n[{idx + 1}] {idea['title']}")
        style, variations = prompt_for_style(idea, all_styles)
        style_choices.append((idx, style, variations))

    # Calculate total generations
    total = sum(3 if v else 1 for _, _, v in style_choices)
    print(f"\nGenerating {total} illustration(s)...\n")

    # Generate each selected idea
    date_str = facts_path.stem  # e.g., "2025-12-01"
    generated = []
    gen_num = 0

    for idx, style, variations in style_choices:
        idea = ideas[idx]

        # Determine which styles to generate
        if variations:
            # Get alternatives from category config
            alt_styles = get_style_alternatives(idea["category"])
            styles_to_gen = [style]
            for alt in alt_styles:
                if alt != style and len(styles_to_gen) < 3:
                    styles_to_gen.append(alt)
            # Fill to 3 if needed
            while len(styles_to_gen) < 3:
                for s in all_styles:
                    if s not in styles_to_gen:
                        styles_to_gen.append(s)
                        break
        else:
            styles_to_gen = [style]

        for gen_style in styles_to_gen:
            gen_num += 1
            print(f"[{gen_num}/{total}] {idea['title']} ({gen_style})...")

            try:
                # Check if this is a data visualization style
                if is_data_visualization_style(gen_style):
                    # Data viz path - no character references
                    viz_desc = generate_scene_from_content(
                        idea["content"], idea["characters"], style=gen_style
                    )
                    print(f"   Viz: {viz_desc[:60]}...")

                    if dry_run:
                        print(f"   [dry-run] Would generate dataviz with style '{gen_style}'")
                        continue

                    # Build dataviz prompt and generate
                    prompt = build_dataviz_prompt(viz_desc, gen_style, idea["content"])
                    image_bytes = generate_dataviz(prompt)
                else:
                    # Character-based illustration path
                    collage_bytes, manifests = make_reference_collage(idea["characters"])

                    scene = generate_scene_from_content(
                        idea["content"], idea["characters"], style=gen_style
                    )
                    print(f"   Scene: {scene[:60]}...")

                    if dry_run:
                        print(f"   [dry-run] Would generate with style '{gen_style}'")
                        continue

                    # Build and generate with character references
                    prompt = build_illustration_prompt(manifests, scene, style=gen_style)
                    image_bytes = generate_illustration(collage_bytes, prompt)

                # Save with style in filename
                cat_str = idea["category"].replace("_", "-")
                output_path = OUTPUT_DIR / f"{date_str}-{cat_str}-{gen_style}.png"
                output_path.write_bytes(image_bytes)
                print(f"   Saved: {output_path}")
                generated.append(output_path)

            except Exception as e:
                print(f"   Error: {e}")
                continue

    print(f"\nGenerated {len(generated)} illustration(s)")
    return 0


# --------------- Image Generation ---------------


def generate_illustration(collage_bytes: bytes, prompt: str) -> bytes:
    """Call image generation API."""
    collage_b64 = base64.b64encode(collage_bytes).decode("utf-8")

    preamble = (
        "Reference sheet showing character design(s). "
        "Use these EXACT character appearances in the illustration. "
        "Maintain colors, costume, and distinguishing features.\n\n"
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
            "X-Title": "ElizaOS Illustrator"
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


def generate_dataviz(prompt: str) -> bytes:
    """Generate data visualization without character references."""
    logging.info(f"Calling {IMAGE_MODEL} for data visualization...")

    resp = requests.post(
        OPENROUTER_ENDPOINT,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/elizaOS/knowledge",
            "X-Title": "ElizaOS DataViz"
        },
        json={
            "model": IMAGE_MODEL,
            "modalities": ["image", "text"],
            "messages": [{"role": "user", "content": prompt}]
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


# --------------- CLI ---------------


def list_styles():
    """List available styles."""
    presets = load_style_presets()
    styles = presets.get("styles", {})

    print("Available styles:")
    for name, config in styles.items():
        desc = config.get("description", "No description")
        print(f"  {name}: {desc}")


def list_characters():
    """List available characters with reference sheets."""
    print("Characters with reference sheets:")
    for char_dir in sorted(CHARACTERS_DIR.iterdir()):
        if char_dir.is_dir() and not char_dir.name.startswith("."):
            ref_sheet = char_dir / "reference-sheet.png"
            if ref_sheet.exists():
                print(f"  {char_dir.name} [ready]")
            else:
                print(f"  {char_dir.name} [needs generate.py]")


def main():
    parser = argparse.ArgumentParser(
        description="Generate story illustrations using character reference sheets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "args",
        nargs="*",
        help="Character name(s) followed by scene description"
    )
    parser.add_argument(
        "-s", "--style",
        default="editorial",
        help="Art style (default: editorial). Use --list-styles to see options"
    )
    parser.add_argument(
        "-f", "--facts",
        help="Generate scene from facts JSON file"
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Interactive mode: analyze facts and pick from multiple ideas"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output path (default: posters/illustration-{timestamp}.png)"
    )
    parser.add_argument(
        "--list-styles",
        action="store_true",
        help="List available styles"
    )
    parser.add_argument(
        "--list-characters",
        action="store_true",
        help="List characters with reference sheets"
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

    # Handle list commands
    if args.list_styles:
        list_styles()
        return 0

    if args.list_characters:
        list_characters()
        return 0

    # Interactive mode
    if args.interactive:
        if not args.facts:
            parser.error("Interactive mode requires -f/--facts")
        facts_path = Path(args.facts)
        if not facts_path.exists():
            logging.error(f"Facts file not found: {facts_path}")
            return 1
        if not OPENROUTER_API_KEY and not args.dry_run:
            logging.error("OPENROUTER_API_KEY not set")
            return 1
        return interactive_mode(facts_path, dry_run=args.dry_run)

    # Validate args
    if not args.args:
        parser.error("Provide at least one character and a scene description")

    # API key check
    if not OPENROUTER_API_KEY and not args.dry_run:
        logging.error("OPENROUTER_API_KEY not set")
        return 1

    try:
        # Parse positional args: characters then scene
        # Last quoted arg or last arg is the scene
        characters = []
        scene = None

        for arg in args.args:
            char_dir = CHARACTERS_DIR / arg
            if char_dir.exists():
                characters.append(arg)
            else:
                # Not a character - must be the scene
                scene = arg
                break

        # If we found characters but no scene in args, remaining args are scene
        remaining_idx = len(characters)
        if remaining_idx < len(args.args):
            scene = " ".join(args.args[remaining_idx:])

        if not characters:
            parser.error("No valid characters found. Use --list-characters to see available.")

        if not scene and not args.facts:
            parser.error("Provide a scene description or use -f with a facts file")

        logging.info(f"Characters: {characters}")

        # Load reference sheets
        logging.info("Loading reference sheets...")
        collage_bytes, manifests = make_reference_collage(characters)
        logging.info(f"Loaded {len(manifests)} character(s)")

        # Get scene description
        if args.facts:
            facts_path = Path(args.facts)
            if not facts_path.exists():
                logging.error(f"Facts file not found: {facts_path}")
                return 1
            logging.info("Generating scene from facts...")
            scene = generate_prompt_from_facts(facts_path, manifests)
            logging.info(f"Scene: {scene}")

        # Build prompt
        prompt = build_illustration_prompt(manifests, scene, style=args.style)

        # Determine output path
        if args.output:
            output_path = Path(args.output)
        else:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            char_str = "-".join(characters)
            output_path = OUTPUT_DIR / f"illustration-{char_str}-{timestamp}.png"

        # Dry run
        if args.dry_run:
            print()
            print("=" * 60)
            print("DRY RUN")
            print("=" * 60)
            print(f"Characters: {characters}")
            print(f"Scene: {scene}")
            print(f"Style: {args.style}")
            print(f"Output: {output_path}")
            print()
            print("PROMPT:")
            print("-" * 60)
            print(prompt)
            print("-" * 60)
            return 0

        # Generate
        logging.info(f"Generating illustration (style: {args.style})...")
        image_bytes = generate_illustration(collage_bytes, prompt)

        # Save
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
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
