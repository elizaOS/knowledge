#!/usr/bin/env python3
"""
Generate story illustrations using character reference sheets.

Uses reference-sheet-{character}.png from each character folder to maintain consistency.

Usage:
  # Basic - character + prompt
  python scripts/posters/illustrate.py -c eliza -p "celebrating a product launch"

  # With art style
  python scripts/posters/illustrate.py -c eliza -p "presenting at conference" -s editorial

  # Multiple characters (comma-separated)
  python scripts/posters/illustrate.py -c eliza,marc -p "discussing code on whiteboard"

  # From facts file (generates prompt from summary)
  python scripts/posters/illustrate.py -c eliza -f the-council/facts/2025-12-14.json

  # Interactive mode - analyze facts and pick from multiple ideas
  python scripts/posters/illustrate.py -f the-council/facts/2025-12-14.json -i

  # Custom output
  python scripts/posters/illustrate.py -c eliza -p "happy moment" -o celebration.png

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
import time
from pathlib import Path
from datetime import datetime, timezone

import requests
from PIL import Image

# Icon sheet for entity logos
from utils.icon_sheet import make_icon_sheet, extract_entities_from_facts

# --------------- Config ---------------

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
LLM_MODEL = "openai/gpt-4.1"
IMAGE_MODEL = "google/gemini-3-pro-image-preview"

SCRIPT_DIR = Path(__file__).parent.resolve()
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent
CHARACTERS_DIR = SCRIPT_DIR / "characters"
OUTPUT_DIR = WORKSPACE_ROOT / "media" / "daily"
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
    """Get path to character's reference sheet.

    Filename includes character name for better model context.
    """
    char_dir = CHARACTERS_DIR / character
    ref_sheet = char_dir / f"reference-sheet-{character}.png"

    if not ref_sheet.exists():
        raise FileNotFoundError(
            f"No reference sheet for '{character}'. "
            f"Run: python scripts/posters/character-reference.py {character}"
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

# --------------- Organic Variation System ---------------
# Date-seeded creative briefs for natural variation in batch outputs

import random

# Interpretive lenses - HOW to see the story
DAILY_LENSES = [
    "Focus on the HUMAN EMOTION behind this news",
    "Show this as a JOURNEY or TRANSFORMATION",
    "Capture the TENSION or CONFLICT in this story",
    "Emphasize the COLLABORATION and TEAMWORK",
    "Frame this as a BREAKTHROUGH or DISCOVERY moment",
    "Show the SCALE and MAGNITUDE of this development",
    "Focus on the INDIVIDUAL IMPACT on one person",
]

# Compositional approaches - HOW to frame it visually
COMPOSITIONS = [
    "Bird's eye view looking down on the scene",
    "Intimate close-up on a meaningful detail",
    "Wide establishing shot showing full context",
    "Dynamic diagonal composition suggesting movement",
    "Silhouette against dramatic backdrop",
    "Split frame showing cause and effect",
]

# Lighting directions - HOW light shapes the scene
LIGHTING_DIRECTIONS = [
    "dramatic rim lighting from behind, subject edges glowing",
    "soft golden hour side-lighting, warm and nostalgic",
    "cool blue ambient light from above, calm and focused",
    "harsh chiaroscuro with deep contrasting shadows",
    "flat diffused lighting with soft gradients",
    "dramatic spotlight from upper left, theatrical",
    "backlighting creating silhouettes and halos",
    "neon-tinged atmospheric glow, cyberpunk mood",
]

# Environment depth - HOW space is rendered
ENVIRONMENT_DEPTH = [
    "shallow depth of field - sharp subject, dreamy blurred background",
    "deep focus - clear foreground object, subject, and detailed background",
    "atmospheric depth - fog/haze separating visual planes",
    "layered composition - distinct foreground, mid, and background elements",
    "minimal environment - subject isolated against simple backdrop",
    "environmental storytelling - rich contextual details throughout",
]

# Time of day - pure aesthetic choice (not tied to real-world seasonal daylight)
TIME_OF_DAY = [
    "dawn - soft pink/orange horizon, long shadows, quiet energy",
    "midday - bright overhead light, minimal shadows, high energy",
    "golden hour - warm directional light, long shadows, cinematic",
    "blue hour - cool twilight tones, city lights emerging",
    "night - artificial lighting, high contrast, intimate pools of light",
    "overcast - soft diffused light, muted colors, contemplative",
]

# Holiday moods - override seasonal mood on special days
# Format: (month, day): ("holiday_name", "mood description")
# Note: Deterministic holidays have minimal/no padding - the day is the day
HOLIDAY_MOODS = {
    # New Year's (Dec 31 - Jan 1 only, fireworks are over after NY Day)
    (12, 31): ("new_years", "new beginnings, celebration, fireworks and confetti"),
    (1, 1): ("new_years", "new beginnings, celebration, fireworks and confetti"),

    # Valentine's Day (Feb 14 only)
    (2, 14): ("valentines", "love and connection, romantic warmth, heartfelt moments"),

    # St. Patrick's Day (Mar 17 only)
    (3, 17): ("st_patricks", "lucky green, Irish charm, festive celebration"),

    # April Fools (Apr 1) - Easter takes priority if they overlap
    (4, 1): ("april_fools", "playful mischief, unexpected twists, lighthearted chaos"),

    # Bitcoin Pizza Day (May 22)
    (5, 22): ("bitcoin_pizza", "crypto nostalgia, pizza celebration, early adopter vibes"),

    # 4th of July (Jul 4 only, no padding needed)
    (7, 4): ("july_4th", "bold patriotic energy, fireworks, summer celebration"),

    # Ethereum Birthday (Jul 30)
    (7, 30): ("eth_birthday", "blockchain celebration, network anniversary, crypto milestone"),

    # Halloween (Oct 30-31) - 1 day buildup for spooky season
    (10, 30): ("halloween", "spooky and playful, orange and purple, eerie shadows, characters in creative Halloween costumes"),
    (10, 31): ("halloween", "peak spooky energy, haunted atmosphere, characters dressed in fun Halloween costumes"),

    # Christmas (Dec 24-25 only) - Christmas Eve + Christmas Day
    (12, 24): ("christmas", "Christmas Eve magic, warm glow, gift-giving anticipation, characters in Santa hats"),
    (12, 25): ("christmas", "Christmas joy, festive warmth, red and green, characters wearing Santa hats and holiday attire"),
}

# Variable holidays - hardcoded dates for 2025-2035
# Thanksgiving: 4th Thursday of November (Wed-Fri window)
THANKSGIVING_DATES = {
    2025: 27, 2026: 26, 2027: 25, 2028: 23, 2029: 22,
    2030: 28, 2031: 27, 2032: 25, 2033: 24, 2034: 23, 2035: 27,
}
THANKSGIVING_MOOD = "gratitude and abundance, harvest warmth, family gathering"

# Easter Sunday dates (Sat-Mon window)
EASTER_DATES = {
    2025: (4, 20), 2026: (4, 5), 2027: (3, 28), 2028: (4, 16), 2029: (4, 1),
    2030: (4, 21), 2031: (4, 13), 2032: (5, 2), 2033: (4, 24), 2034: (4, 9), 2035: (4, 29),
}
EASTER_MOOD = "renewal and rebirth, pastel colors, spring awakening"


def get_holiday_mood(date: datetime) -> str | None:
    """Check if date falls on a holiday, return mood if so.

    Priority: Easter > Thanksgiving > Fixed holidays > Seasonal
    """
    month, day, year = date.month, date.day, date.year

    # Check Easter first (takes priority over April Fools in 2029)
    if year in EASTER_DATES:
        easter_month, easter_day = EASTER_DATES[year]
        if month == easter_month and easter_day - 1 <= day <= easter_day + 1:
            return EASTER_MOOD

    # Check Thanksgiving (Wed-Fri window around Thursday)
    if month == 11 and year in THANKSGIVING_DATES:
        thurs = THANKSGIVING_DATES[year]
        if thurs - 1 <= day <= thurs + 1:
            return THANKSGIVING_MOOD

    # Check fixed holidays
    if (month, day) in HOLIDAY_MOODS:
        return HOLIDAY_MOODS[(month, day)][1]

    return None


def get_seasonal_mood(date: datetime) -> str:
    """Get atmospheric mood - holiday override or seasonal default."""
    # Holiday takes priority
    holiday_mood = get_holiday_mood(date)
    if holiday_mood:
        return holiday_mood

    # Fall back to seasonal
    month = date.month
    if month in [12, 1, 2]:
        return "winter stillness, contemplative, cool tones"
    if month in [3, 4, 5]:
        return "spring energy, renewal, fresh growth"
    if month in [6, 7, 8]:
        return "summer vibrancy, peak activity, warm light"
    return "autumn transition, harvest, golden hues"


def generate_creative_brief(date: datetime) -> dict:
    """Generate today's unique creative direction.

    Uses date-seeded RNG for reproducibility: same date = same brief.
    7 lenses × 6 compositions × 8 lighting × 6 depth × 6 time = 72,576 combinations.
    """
    seed = int(date.strftime("%Y%m%d"))
    rng = random.Random(seed)

    return {
        "lens": rng.choice(DAILY_LENSES),
        "composition": rng.choice(COMPOSITIONS),
        "mood": get_seasonal_mood(date),
        "lighting": rng.choice(LIGHTING_DIRECTIONS),
        "depth": rng.choice(ENVIRONMENT_DEPTH),
        "time_of_day": rng.choice(TIME_OF_DAY),
    }


def get_available_characters() -> list[str]:
    """Get list of characters with reference sheets."""
    chars = []
    for char_dir in CHARACTERS_DIR.iterdir():
        if char_dir.is_dir() and not char_dir.name.startswith("."):
            char_name = char_dir.name
            if (char_dir / f"reference-sheet-{char_name}.png").exists():
                chars.append(char_name)
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


def generate_illustration_ideas(facts_path: Path, facts_date: datetime = None) -> list[dict]:
    """Analyze facts file and generate multiple illustration ideas.

    Args:
        facts_path: Path to facts JSON file
        facts_date: Date for seeded randomness (style rotation, character shuffle).
                   If None, uses date from facts file or current date.
    """
    with open(facts_path) as f:
        facts = json.load(f)

    date_str = facts.get("briefing_date", "unknown")
    available_chars = get_available_characters()

    # Parse date for seeded randomness
    if facts_date is None:
        try:
            facts_date = datetime.strptime(date_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            facts_date = datetime.now()

    # Date-seeded RNG for reproducible variation
    date_seed = int(facts_date.strftime("%Y%m%d"))
    rng = random.Random(date_seed)
    day_of_year = facts_date.timetuple().tm_yday

    # Load category configs for style rotation
    presets = load_style_presets()
    category_configs = presets.get("categories", {})

    ideas = []

    # Always add overall summary as first option
    if facts.get("overall_summary"):
        # Rotate overall style by day
        overall_styles = ["editorial", "cinematic_anime", "tarot"]
        overall_style = overall_styles[day_of_year % len(overall_styles)]

        ideas.append({
            "category": "overall",
            "title": "Daily Overview",
            "content": facts["overall_summary"],
            "characters": ["eliza"],
            "style": overall_style,
        })

    # Add ideas for each category with content
    categories = facts.get("categories", {})

    for cat_name, cat_data in categories.items():
        content = extract_category_content(facts, cat_name)
        if not content or len(content) < 50:
            continue

        # Get suggested characters (filter to available)
        suggested = CATEGORY_CHARACTERS.get(cat_name, ["eliza"])
        chars = [c for c in suggested if c in available_chars]
        if not chars:
            chars = [available_chars[0]] if available_chars else ["eliza"]

        # Shuffle characters with date seed for varied arrangements
        chars_copy = chars.copy()
        rng.shuffle(chars_copy)
        # Vary character count: sometimes 1, sometimes 2, sometimes all
        char_count_options = [1, 2, len(chars_copy)]
        char_count = rng.choice([c for c in char_count_options if c <= len(chars_copy)])
        chars = chars_copy[:char_count]

        # Style rotation: use suggested_styles from config, rotate by day
        cat_config = category_configs.get(cat_name, {})
        suggested_styles = cat_config.get("suggested_styles", [CATEGORY_STYLES.get(cat_name, "editorial")])
        style = suggested_styles[day_of_year % len(suggested_styles)]

        ideas.append({
            "category": cat_name,
            "title": cat_name.replace("_", " ").title(),
            "content": content,
            "characters": chars,
            "style": style,
        })

    return ideas


def get_visual_approaches() -> dict:
    """Load visual approaches from config."""
    presets = load_style_presets()
    return presets.get("visual_approaches", {})


def get_category_visual_hint(category: str) -> str:
    """Get the visual hint for a category."""
    presets = load_style_presets()
    cat_config = presets.get("categories", {}).get(category, {})
    return cat_config.get("visual_hint", "")


def decide_visual_format(
    content: str,
    category: str,
    date_seed: int = None
) -> dict:
    """Use LLM to decide the best visual format for this content.

    Args:
        content: The story content to visualize
        category: Category name (github_updates, discord_updates, etc.)
        date_seed: Optional seed for reproducibility

    Returns:
        dict with:
            - approach: "abstract_dataviz" | "conceptual_metaphor" | "character_scene"
            - style: specific style name from available styles
            - reasoning: why this format fits the content
    """
    approaches = get_visual_approaches()
    visual_hint = get_category_visual_hint(category)

    # Build approach descriptions for the prompt
    approach_descriptions = []
    for name, config in approaches.items():
        if name.startswith("_"):
            continue
        styles = ", ".join(config.get("suggested_styles", []))
        approach_descriptions.append(
            f"- {name}: {config.get('description', '')} (styles: {styles})"
        )

    approaches_text = "\n".join(approach_descriptions)

    system_prompt = f"""You are a creative director for a tech news publication deciding how to visualize stories.

AVAILABLE VISUAL APPROACHES:
{approaches_text}

CATEGORY: {category}
CATEGORY HINT: {visual_hint}

Based on the story content, decide the best visual approach. The hint is a soft suggestion - override it if the content calls for something different.

Consider:
- Is this data-heavy content that would benefit from visualization?
- Is this about community/people where characters add personality?
- Is this conceptual/strategic where abstract metaphors work best?
- What would a reader find most informative and engaging?

Respond in JSON format:
{{
  "approach": "abstract_dataviz" | "conceptual_metaphor" | "character_scene",
  "style": "<specific style from the approach's suggested styles>",
  "reasoning": "<1-2 sentences explaining why this format fits>"
}}"""

    try:
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
                    {"role": "user", "content": f"Story content:\n{content[:1000]}"}
                ],
                "response_format": {"type": "json_object"}
            },
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        decision = json.loads(result["choices"][0]["message"]["content"])

        # Validate the response
        valid_approaches = [k for k in approaches.keys() if not k.startswith("_")]
        if decision.get("approach") not in valid_approaches:
            decision["approach"] = "conceptual_metaphor"  # safe default

        return decision

    except Exception as e:
        logging.warning(f"Visual format decision failed: {e}, using default")
        return {
            "approach": "conceptual_metaphor",
            "style": "editorial",
            "reasoning": "Default fallback due to decision error"
        }


def generate_scene_from_content(
    content: str,
    characters: list[str],
    style: str = None,
    creative_brief: dict = None
) -> str:
    """Use LLM to convert content into a scene/visualization description.

    Args:
        content: News content to visualize
        characters: List of character names for the scene
        style: Art style (affects prompt for dataviz styles)
        creative_brief: Optional dict with 'lens', 'composition', 'mood' keys
                       for organic variation in how the scene is interpreted
    """

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
        # Character-based scene with optional creative brief
        brief_section = ""
        if creative_brief:
            brief_section = f"""
TODAY'S CREATIVE DIRECTION:
- Interpretive lens: {creative_brief.get('lens', '')}
- Composition: {creative_brief.get('composition', '')}
- Atmosphere: {creative_brief.get('mood', '')}
- Lighting: {creative_brief.get('lighting', '')}
- Depth/Environment: {creative_brief.get('depth', '')}
- Time of day: {creative_brief.get('time_of_day', '')}

"""
        system_prompt = f"""Convert this news content into a brief scene description for an illustration.
{brief_section}The scene should feature: {', '.join(characters)}
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


def interactive_mode(facts_path: Path, dry_run: bool = False, with_icons: bool = False) -> int:
    """Run interactive mode - present ideas and generate selected ones."""
    print(f"\nAnalyzing {facts_path.name}...")

    # Parse date for creative brief
    with open(facts_path) as f:
        facts_data = json.load(f)
    date_str = facts_data.get("briefing_date", facts_path.stem)
    try:
        facts_date = datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        facts_date = datetime.now()

    # Generate creative brief for organic variation
    creative_brief = generate_creative_brief(facts_date)
    print(f"\nToday's creative direction:")
    print(f"  Lens: {creative_brief['lens']}")
    print(f"  Composition: {creative_brief['composition']}")
    print(f"  Mood: {creative_brief['mood']}")
    print(f"  Lighting: {creative_brief['lighting']}")
    print(f"  Depth: {creative_brief['depth']}")
    print(f"  Time: {creative_brief['time_of_day']}")

    # Generate icon sheet if requested
    icon_sheet_bytes = None
    if with_icons:
        entities = extract_entities_from_facts(facts_path)
        if entities:
            icon_sheet_bytes, found = make_icon_sheet(entities[:12])  # Limit to 12 icons
            if icon_sheet_bytes:
                print(f"Icon sheet: {len(found)} entities ({', '.join(found[:5])}{'...' if len(found) > 5 else ''})")
    ideas = generate_illustration_ideas(facts_path, facts_date)

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

    # Generate each selected idea (date_str already parsed from facts file above)
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
                    # Character-based illustration path - inject creative brief
                    collage_bytes, manifests = make_reference_collage(idea["characters"])

                    scene = generate_scene_from_content(
                        idea["content"], idea["characters"], style=gen_style,
                        creative_brief=creative_brief
                    )
                    print(f"   Scene: {scene[:60]}...")

                    if dry_run:
                        print(f"   [dry-run] Would generate with style '{gen_style}'")
                        continue

                    # Build and generate with character references
                    prompt = build_illustration_prompt(manifests, scene, style=gen_style)
                    image_bytes = generate_illustration(collage_bytes, prompt, icon_sheet_bytes)

                # Save with style in filename
                cat_str = idea["category"].replace("_", "-")
                output_path = OUTPUT_DIR / f"{date_str}-{cat_str}-{gen_style}.png"
                output_path.write_bytes(image_bytes)
                # Save prompt alongside image
                prompt_path = output_path.with_suffix('.txt')
                prompt_path.write_text(prompt)
                print(f"   Saved: {output_path} (+prompt)")
                generated.append(output_path)

            except Exception as e:
                print(f"   Error: {e}")
                continue

    print(f"\nGenerated {len(generated)} illustration(s)")
    return 0


def batch_mode(facts_path: Path, dry_run: bool = False, with_icons: bool = False, output_dir: Path = None) -> int:
    """Batch mode - generate all category visuals automatically.

    Outputs to media/{date}/ directory (or custom -o path):
      - overall.png (hero/editorial)
      - github-updates.png (dataviz)
      - discord-updates.png (comic_panel)
      - strategic-insights.png (cinematic_anime)
      - market-analysis.png (dataviz)
      - icons.png (entity icon sheet)
      - manifest.json (generation metadata)

    Uses organic variation system:
      - Style rotation from suggested_styles per category
      - Character shuffle with date-seeded RNG
      - Creative brief injection for interpretive variation
    """
    batch_start_time = time.time()
    print(f"\nBatch generating from {facts_path.name}...")

    # Extract date for output directory and creative brief
    with open(facts_path) as f:
        facts = json.load(f)
    date_str = facts.get("briefing_date", facts_path.stem)

    # Parse date for creative brief
    try:
        facts_date = datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        facts_date = datetime.now()

    # Generate today's creative brief for organic variation
    creative_brief = generate_creative_brief(facts_date)
    print(f"\nToday's creative direction:")
    print(f"  Lens: {creative_brief['lens']}")
    print(f"  Composition: {creative_brief['composition']}")
    print(f"  Mood: {creative_brief['mood']}")
    print(f"  Lighting: {creative_brief['lighting']}")
    print(f"  Depth: {creative_brief['depth']}")
    print(f"  Time: {creative_brief['time_of_day']}")

    # Generate ideas with date-seeded style rotation and character shuffle
    ideas = generate_illustration_ideas(facts_path, facts_date)
    if not ideas:
        print("No illustration ideas found.")
        return 1

    # Create output directory (use provided or default to media/daily/{date})
    if output_dir is None:
        output_dir = OUTPUT_DIR / date_str
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize manifest
    manifest = {
        "version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_facts": str(facts_path),
        "facts_date": date_str,
        "output_dir": str(output_dir),
        "models": {
            "image": IMAGE_MODEL,
            "llm": LLM_MODEL,
        },
        "options": {
            "with_icons": with_icons,
            "dry_run": dry_run,
        },
        "generations": [],
        "icon_sheet": None,
        "stats": {
            "total_generations": len(ideas),
            "successful": 0,
            "failed": 0,
            "total_time_seconds": 0,
        },
    }

    # Generate icon sheet once (shared across all illustrations)
    icon_sheet_bytes = None
    icon_sheet_info = None
    if with_icons:
        entities = extract_entities_from_facts(facts_path)
        if entities:
            icon_sheet_bytes, found = make_icon_sheet(entities[:12])
            if icon_sheet_bytes:
                # Save icon sheet
                icon_path = output_dir / "icons.png"
                icon_path.write_bytes(icon_sheet_bytes)
                print(f"Icon sheet: {icon_path} ({len(found)} entities)")
                icon_sheet_info = {
                    "output_file": "icons.png",
                    "entities_requested": entities[:12],
                    "entities_found": found,
                    "entity_count": len(found),
                }

    manifest["icon_sheet"] = icon_sheet_info

    print(f"\nGenerating {len(ideas)} visuals to {output_dir}/\n")

    generated = []
    for i, idea in enumerate(ideas, 1):
        cat_slug = idea["category"].replace("_", "-")
        style = idea["style"]
        output_path = output_dir / f"{cat_slug}.png"

        print(f"[{i}/{len(ideas)}] {idea['title']} ({style})...")

        # Track generation metadata
        gen_meta = {
            "category": idea["category"],
            "output_file": f"{cat_slug}.png",
            "style": style,
            "characters": idea["characters"],
            "content_context": idea["content"][:500],
            "is_dataviz": is_data_visualization_style(style),
            "scene_or_viz_prompt": None,
            "full_prompt": None,
            "success": False,
            "error": None,
            "generation_time_seconds": 0,
        }

        gen_start = time.time()

        try:
            if dry_run:
                chars = ", ".join(idea["characters"])
                print(f"   Style: {style}, Characters: {chars}")
                print(f"   Content: {idea['content'][:100]}...")
                print(f"   -> {output_path}")
                gen_meta["success"] = True
                gen_meta["generation_time_seconds"] = 0
                manifest["generations"].append(gen_meta)
                manifest["stats"]["successful"] += 1
                continue

            if is_data_visualization_style(style):
                # Data viz - no characters, no creative brief needed
                viz_desc = generate_scene_from_content(
                    idea["content"], idea["characters"], style=style
                )
                print(f"   Viz: {viz_desc[:60]}...")

                prompt = build_dataviz_prompt(viz_desc, style, idea["content"])
                image_bytes = generate_dataviz(prompt)

                gen_meta["scene_or_viz_prompt"] = viz_desc
                gen_meta["full_prompt"] = prompt
            else:
                # Character-based - inject creative brief for organic variation
                collage_bytes, manifests = make_reference_collage(idea["characters"])

                scene = generate_scene_from_content(
                    idea["content"], idea["characters"], style=style,
                    creative_brief=creative_brief
                )
                print(f"   Scene: {scene[:60]}...")

                prompt = build_illustration_prompt(manifests, scene, style=style)
                image_bytes = generate_illustration(collage_bytes, prompt, icon_sheet_bytes)

                gen_meta["scene_or_viz_prompt"] = scene
                gen_meta["full_prompt"] = prompt

            output_path.write_bytes(image_bytes)
            # Save prompt alongside image
            prompt_path = output_path.with_suffix('.txt')
            prompt_path.write_text(prompt)
            print(f"   Saved: {output_path} (+prompt)")
            generated.append(output_path)

            gen_meta["success"] = True
            manifest["stats"]["successful"] += 1

        except Exception as e:
            print(f"   Error: {e}")
            gen_meta["error"] = str(e)
            manifest["stats"]["failed"] += 1

        gen_meta["generation_time_seconds"] = round(time.time() - gen_start, 2)
        manifest["generations"].append(gen_meta)

    # Finalize manifest
    manifest["stats"]["total_time_seconds"] = round(time.time() - batch_start_time, 2)

    # Write manifest
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest: {manifest_path}")

    print(f"Batch complete: {len(generated)}/{len(ideas)} visuals in {output_dir}/")
    return 0


# --------------- Image Generation ---------------


def generate_illustration(
    collage_bytes: bytes,
    prompt: str,
    icon_sheet_bytes: bytes = None
) -> bytes:
    """Call image generation API.

    Args:
        collage_bytes: Character reference sheet PNG
        prompt: Generation prompt
        icon_sheet_bytes: Optional logo/icon sheet for brand references
    """
    collage_b64 = base64.b64encode(collage_bytes).decode("utf-8")

    # Build content with reference images
    content = [
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{collage_b64}"}
        }
    ]

    # Add icon sheet if provided
    if icon_sheet_bytes:
        icon_b64 = base64.b64encode(icon_sheet_bytes).decode("utf-8")
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{icon_b64}"}
        })
        preamble = (
            "IMAGE 1: Character reference sheet - use EXACT appearances.\n"
            "IMAGE 2: Logo/icon sheet - incorporate relevant logos as visual elements.\n\n"
        )
    else:
        preamble = (
            "Reference sheet showing character design(s). "
            "Use these EXACT character appearances in the illustration. "
            "Maintain colors, costume, and distinguishing features.\n\n"
        )

    content.append({
        "type": "text",
        "text": preamble + prompt
    })

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
            char_name = char_dir.name
            ref_sheet = char_dir / f"reference-sheet-{char_name}.png"
            if ref_sheet.exists():
                print(f"  {char_name} [ready]")
            else:
                print(f"  {char_name} [needs character-reference.py]")


def main():
    parser = argparse.ArgumentParser(
        description="Generate story illustrations using character reference sheets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "-c", "--characters",
        help="Character name(s), comma-separated (e.g., 'peepo' or 'eliza,marc')"
    )
    parser.add_argument(
        "-p", "--prompt",
        help="Scene description/prompt"
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
        "--batch",
        action="store_true",
        help="Batch mode: generate all category visuals from facts file"
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
        "--with-icons",
        action="store_true",
        help="Include logo/icon sheet for entities mentioned in facts"
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
        return interactive_mode(facts_path, dry_run=args.dry_run, with_icons=args.with_icons)

    # Batch mode
    if args.batch:
        if not args.facts:
            parser.error("Batch mode requires -f/--facts")
        facts_path = Path(args.facts)
        if not facts_path.exists():
            logging.error(f"Facts file not found: {facts_path}")
            return 1
        if not OPENROUTER_API_KEY and not args.dry_run:
            logging.error("OPENROUTER_API_KEY not set")
            return 1
        output_path = Path(args.output) if args.output else None
        return batch_mode(facts_path, dry_run=args.dry_run, with_icons=args.with_icons, output_dir=output_path)

    # API key check
    if not OPENROUTER_API_KEY and not args.dry_run:
        logging.error("OPENROUTER_API_KEY not set")
        return 1

    try:
        # Parse characters from -c flag
        characters = []
        scene = args.prompt

        if args.characters:
            characters = [c.strip() for c in args.characters.split(",")]
            # Validate characters exist
            for char in characters:
                char_dir = CHARACTERS_DIR / char
                if not char_dir.exists():
                    parser.error(f"Character '{char}' not found. Use --list-characters to see available.")

        if not characters:
            parser.error("No characters specified. Use -c/--characters (e.g., -c peepo or -c eliza,marc)")

        if not scene and not args.facts:
            parser.error("Provide a scene with -p/--prompt or use -f with a facts file")

        logging.info(f"Characters: {characters}")

        # Load reference sheets
        logging.info("Loading reference sheets...")
        collage_bytes, manifests = make_reference_collage(characters)
        logging.info(f"Loaded {len(manifests)} character(s)")

        # Generate icon sheet if requested
        icon_sheet_bytes = None
        if args.with_icons and args.facts:
            facts_path = Path(args.facts)
            if facts_path.exists():
                entities = extract_entities_from_facts(facts_path)
                if entities:
                    icon_sheet_bytes, found = make_icon_sheet(entities[:12])
                    if icon_sheet_bytes:
                        logging.info(f"Icon sheet: {len(found)} entities")

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
        image_bytes = generate_illustration(collage_bytes, prompt, icon_sheet_bytes)

        # Save
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(image_bytes)
        # Save prompt alongside image
        prompt_path = output_path.with_suffix('.txt')
        prompt_path.write_text(prompt)
        logging.info(f"Saved: {output_path} (+prompt)")

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
