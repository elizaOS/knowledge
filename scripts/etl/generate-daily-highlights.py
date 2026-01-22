#!/usr/bin/env python3
"""
Generates daily editorial highlights by curating ai-news Full Stories.
Adds temporal perspective via Council character voices.
"""

import os
import sys
import json
import requests
import argparse
from pathlib import Path
from datetime import datetime, timedelta, timezone
import logging

# Configuration (matching other ETL scripts)
MODEL = "deepseek/deepseek-v3.2"
API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_API_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

SCRIPT_DIR = Path(__file__).parent.resolve()
SCRIPTS_ROOT = SCRIPT_DIR.parent
WORKSPACE_ROOT = SCRIPTS_ROOT.parent

# Input directories
AI_NEWS_DIR = WORKSPACE_ROOT / "ai-news" / "elizaos" / "json"
RETROS_DIR = WORKSPACE_ROOT / "the-council" / "retros"
CHARACTERS_FILE = WORKSPACE_ROOT / "characters.md"

# Output directory
OUTPUT_DIR = WORKSPACE_ROOT / "the-council" / "highlights"

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(levelname)s - %(message)s')


def normalize_categories(data: dict) -> dict:
    """Normalize categories field to always be an array.

    Handles schema inconsistency where some dates have:
    - Array: {"categories": [{"title": "..."}, ...]}
    - Object: {"categories": {"title": "..."}}
    """
    if "categories" in data:
        categories = data["categories"]
        # If categories is a dict (single object), wrap in array
        if isinstance(categories, dict):
            data["categories"] = [categories]
    return data


def load_ai_news(date_str: str) -> dict | None:
    """Load ai-news JSON for a single date."""
    path = AI_NEWS_DIR / f"{date_str}.json"
    if not path.exists():
        logging.warning(f"No ai-news for {date_str}")
        return None
    try:
        data = json.loads(path.read_text())
        data["_date"] = date_str
        return normalize_categories(data)
    except Exception as e:
        logging.error(f"Failed to load ai-news for {date_str}: {e}")
        return None


def load_ai_news_range(end_date_str: str, days: int = 7) -> list[dict]:
    """Load ai-news for the last N days."""
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    news_list = []

    for i in range(1, days + 1):
        date = end_date - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        news = load_ai_news(date_str)
        if news:
            news_list.append(news)

    return news_list


def load_recent_retro() -> dict | None:
    """Load most recent monthly retro."""
    # Find latest retro file
    retro_files = sorted(RETROS_DIR.glob("*-retro.json"), reverse=True)
    if not retro_files:
        logging.warning("No monthly retros found")
        return None

    try:
        latest = retro_files[0]
        data = json.loads(latest.read_text())
        logging.info(f"Loaded retro: {latest.name}")
        return data
    except Exception as e:
        logging.error(f"Failed to load retro: {e}")
        return None


def load_character_context() -> str:
    """Extract character voice guidelines from characters.md."""
    if not CHARACTERS_FILE.exists():
        logging.warning("characters.md not found")
        return ""

    try:
        content = CHARACTERS_FILE.read_text()
        # Extract Shaw, Marc, Eliza sections (lines up to 300 should cover all three)
        lines = content.split('\n')[:300]
        return '\n'.join(lines)
    except Exception as e:
        logging.error(f"Failed to load characters: {e}")
        return ""


def call_llm(prompt: str) -> dict | None:
    """Call OpenRouter API with JSON response format."""
    if not API_KEY:
        logging.error("OPENROUTER_API_KEY environment variable not set")
        return None

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/elizaOS/knowledge",
        "X-Title": "generate-daily-highlights.py"
    }

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(
            OPENROUTER_API_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=300
        )
        response.raise_for_status()

        response_json = response.json()
        content = response_json.get("choices", [{}])[0].get("message", {}).get("content", "")

        if not content:
            logging.error(f"Empty content in API response. Full response: {response_json}")
            return None

        # Clean markdown code fences
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

        if not content:
            logging.error("Content is empty after cleaning markdown fences")
            return None

        try:
            result = json.loads(content)
            return result
        except json.JSONDecodeError as je:
            logging.error(f"Failed to parse JSON. Error: {je}")
            logging.error(f"Content (first 500 chars): {content[:500]}")
            return None

    except requests.exceptions.Timeout:
        logging.error("LLM API call timed out after 300 seconds")
        return None
    except requests.exceptions.HTTPError as he:
        logging.error(f"HTTP error: {he}")
        try:
            error_detail = response.json()
            logging.error(f"Error details: {error_detail}")
        except:
            logging.error(f"Response text: {response.text[:500]}")
        return None
    except Exception as e:
        logging.error(f"LLM API call failed: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return None


def summarize_recent_coverage(last_7_days: list[dict]) -> str:
    """Create brief summary of last week's stories for prompt context."""
    if not last_7_days:
        return "No recent coverage available."

    summaries = []
    for news in last_7_days[:3]:  # Last 3 days only
        date = news.get("_date", "unknown")
        titles = [cat.get("title", "") for cat in news.get("categories", [])]
        summaries.append(f"- {date}: {', '.join(titles[:2])}")

    return '\n'.join(summaries)


def extract_retro_themes(retro: dict) -> list[str]:
    """Extract key themes from monthly retro."""
    if not retro:
        return []

    themes = []

    # Recurring themes
    for theme in retro.get("recurring_themes", []):
        themes.append(f"{theme.get('theme')}: {theme.get('council_take', '')}")

    # Proposed focus areas
    for focus in retro.get("proposed_focus", [])[:2]:  # Top 2 priorities
        themes.append(f"Priority: {focus.get('area')} - {focus.get('rationale', '')}")

    return themes


def build_curation_prompt(
    ai_news: dict,
    monthly_retro: dict | None,
    last_week: list[dict],
    character_context: str,
    date_str: str
) -> str:
    """Build editorial curation prompt."""

    # Extract Full Stories content
    stories = []
    for category in ai_news.get("categories", []):
        # Skip miscellaneous
        if category.get("topic") == "miscellaneous":
            continue

        title = category.get("title", "")
        content_items = category.get("content", [])

        for item in content_items:
            # Handle images field which can be array or null
            images = item.get("images")
            if isinstance(images, list) and images:
                image = images[0] if images else None
            else:
                image = None

            # Fallback to posters
            if not image:
                posters = item.get("posters")
                if isinstance(posters, list) and posters:
                    image = posters[0]
                else:
                    image = None

            stories.append({
                "category": title,
                "text": item.get("text", ""),
                "sources": item.get("sources"),
                "image": image
            })

    # Build temporal context
    retro_context = ""
    if monthly_retro:
        month = monthly_retro.get("month_reviewed", "recent")
        themes = extract_retro_themes(monthly_retro)
        retro_context = f"\n\n**{month} Retro Themes:**\n" + '\n'.join(f"- {t}" for t in themes)

    recent_coverage = summarize_recent_coverage(last_week)

    # Character voice excerpts
    character_guide = """
**Character Voices (5 mascots available):**
- Eliza (elizahost): curious moderator, synthesizes viewpoints, asks probing questions
- Shaw (aishaw): lowercase, pragmatic builder, "ship it", focuses on technical merit
- Marc (aimarc): bold declarations, binary framing, visionary contrarian, techno-optimist
- Spartan (spartan): ALL CAPS emphasis, profit-focused, battle metaphors, numbers-driven
- Peepo (peepo): "yo/fam/vibes", chill philosopher, meme wisdom, casual yet profound
"""

    prompt = f"""You are the ElizaOS Council editorial board (all 5 mascots) reviewing today's Full Stories for front-page placement.

**Today's Date:** {date_str}

**Full Stories Available:**
{json.dumps(stories, indent=2)}

**Recent Coverage (Last Week):**
{recent_coverage}
{retro_context}

{character_guide}

**Editorial Guidelines:**
1. Pick 2-5 stories that deserve front-page treatment (use all 5 mascots when warranted)
2. Skip if fewer than 2 stories meet the bar (some days are just incremental)
3. For each selected story:
   - Rewrite headline for impact (why this matters, not just what happened) - MAX 8 words
   - Consolidate narrative into 1 concise paragraph (75-100 words MAX)
   - Add ONE brief character quote or perspective (1 sentence)
   - Note temporal context in separate field (5-8 words)

**Selection Criteria (must meet 2+):**
- Represents shift or acceleration (not routine activity)
- Connects to retro themes or diverges significantly
- Has broader implications beyond the immediate update
- Would spark discussion in tomorrow's council meeting

**Output Format (JSON):**
{{
  "highlights": [
    {{
      "headline": "One-line headline (8 words max)",
      "body": "One concise paragraph (75-100 words). Include ONE brief character quote.",
      "character": "eliza" | "shaw" | "marc" | "spartan" | "peepo",
      "temporal_note": "Brief trend note (5-8 words)",
      "image": "URL if available from story",
      "sources": ["category names"]
    }}
  ],
  "summary": "Quiet day, incremental progress" OR null if highlights exist
}}

**Important:**
- BE CONCISE: Newspaper column style, not blog posts. Every word must earn its place.
- Character voices should feel natural in prose, not forced
- If today is quiet, output empty highlights array + summary explaining why
- Quality bar is high: only newsworthy developments, not status updates
- Target 75-100 words per highlight body (currently too verbose at 150-200 words)
"""

    return prompt


def generate_highlights(date_str: str) -> dict:
    """Generate 2-3 editorial highlights from ai-news."""

    logging.info(f"Generating highlights for {date_str}")

    # Load data
    ai_news = load_ai_news(date_str)
    if not ai_news:
        return {
            "date": date_str,
            "highlights": [],
            "summary": "No ai-news data available for this date.",
            "_metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "model": MODEL,
                "status": "no_data"
            }
        }

    monthly_retro = load_recent_retro()
    last_week = load_ai_news_range(date_str, days=7)
    character_context = load_character_context()

    # Build prompt
    prompt = build_curation_prompt(
        ai_news,
        monthly_retro,
        last_week,
        character_context,
        date_str
    )

    # Call LLM
    result = call_llm(prompt)

    if not result:
        return {
            "date": date_str,
            "highlights": [],
            "summary": "Failed to generate highlights (LLM error).",
            "_metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "model": MODEL,
                "status": "llm_error"
            }
        }

    # Add metadata
    highlights = result.get("highlights", [])

    output = {
        "date": date_str,
        "highlights": highlights,
        "summary": result.get("summary"),
        "_metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model": MODEL,
            "source": "ai-news",
            "editorial_pass": True,
            "stories_evaluated": len(ai_news.get("categories", [])),
            "highlights_generated": len(highlights),
            "status": "success"
        }
    }

    return output


def main():
    parser = argparse.ArgumentParser(
        description="Generate daily editorial highlights from ai-news Full Stories"
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Date to process (YYYY-MM-DD). Defaults to yesterday."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print prompt without calling LLM"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Custom output file path (overrides default)"
    )

    args = parser.parse_args()

    # Determine date
    if args.date:
        date_str = args.date
    else:
        # Default: yesterday (since pipeline runs early morning for previous day)
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        date_str = yesterday.strftime("%Y-%m-%d")

    logging.info(f"Processing date: {date_str}")

    # Generate highlights
    if args.dry_run:
        # Build and print prompt only
        ai_news = load_ai_news(date_str)
        if not ai_news:
            print(f"Error: No ai-news data for {date_str}")
            sys.exit(1)

        retro = load_recent_retro()
        last_week = load_ai_news_range(date_str, days=7)
        char_ctx = load_character_context()

        prompt = build_curation_prompt(ai_news, retro, last_week, char_ctx, date_str)
        print("\n=== DRY RUN: Prompt Preview ===\n")
        print(prompt)
        return

    output = generate_highlights(date_str)

    # Save output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.output:
        output_file = args.output
    else:
        output_file = OUTPUT_DIR / f"{date_str}.json"

    output_file.write_text(json.dumps(output, indent=2, ensure_ascii=False))

    # Log results
    highlights_count = len(output.get("highlights", []))
    logging.info(f"Generated {highlights_count} highlights")
    logging.info(f"Output saved to {output_file}")

    # Print summary to stdout
    if highlights_count > 0:
        print(f"\n✅ Generated {highlights_count} highlights for {date_str}")
        for h in output["highlights"]:
            print(f"  - {h['headline']}")
    else:
        summary = output.get("summary", "No highlights")
        print(f"\n⚪ {date_str}: {summary}")


if __name__ == "__main__":
    main()
