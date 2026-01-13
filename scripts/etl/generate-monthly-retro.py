#!/usr/bin/env python3
"""
Generates a monthly retrospective council episode.
Aggregates the month's briefings, GitHub activity, and community themes,
then generates a special "State of ElizaOS" episode with strategic analysis.

Run on the 1st of each month to analyze the previous month.
"""

import os
import sys
import json
import requests
import argparse
from pathlib import Path
from datetime import datetime, timedelta, timezone
from calendar import monthrange
from collections import defaultdict
import logging

# --- Configuration ---
MODEL = "openai/gpt-5.2"
API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_API_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

SCRIPT_DIR = Path(__file__).parent.resolve()
SCRIPTS_ROOT = SCRIPT_DIR.parent  # scripts/
WORKSPACE_ROOT = SCRIPTS_ROOT.parent  # repository root

# Input directories
FACTS_DIR = WORKSPACE_ROOT / "the-council" / "facts"
COUNCIL_DIR = WORKSPACE_ROOT / "the-council" / "council_briefing"
GITHUB_SUMMARIES_DIR = WORKSPACE_ROOT / "github" / "summaries"

# Output
OUTPUT_DIR = WORKSPACE_ROOT / "the-council" / "retros"
EPISODES_DIR = WORKSPACE_ROOT / "the-council" / "episodes"

# Strategic context
NORTH_STAR_FILE = SCRIPTS_ROOT / "prompts" / "config" / "north-star.txt"

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(levelname)s - %(message)s')


def get_month_dates(year: int, month: int) -> tuple[str, str, list[str]]:
    """Get first day, last day, and all dates for a given month."""
    first_day = datetime(year, month, 1)
    last_day_num = monthrange(year, month)[1]
    last_day = datetime(year, month, last_day_num)

    all_dates = []
    current = first_day
    while current <= last_day:
        all_dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    return first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d"), all_dates


def load_month_facts(dates: list[str]) -> list[dict]:
    """Load all facts briefings for the given dates."""
    facts = []
    for date_str in dates:
        path = FACTS_DIR / f"{date_str}.json"
        if path.exists():
            try:
                data = json.loads(path.read_text())
                data["_date"] = date_str
                facts.append(data)
            except Exception as e:
                logging.warning(f"Failed to load facts for {date_str}: {e}")
    return facts


def load_month_council_briefings(dates: list[str]) -> list[dict]:
    """Load all council briefings for the given dates."""
    briefings = []
    for date_str in dates:
        path = COUNCIL_DIR / f"{date_str}.json"
        if path.exists():
            try:
                data = json.loads(path.read_text())
                data["_date"] = date_str
                briefings.append(data)
            except Exception as e:
                logging.warning(f"Failed to load briefing for {date_str}: {e}")
    return briefings


def load_github_monthly_summary(year: int, month: int) -> str | None:
    """Load the GitHub monthly summary if available."""
    path = GITHUB_SUMMARIES_DIR / "month" / f"{year}-{month:02d}-01.md"
    if path.exists():
        return path.read_text()
    return None


def compute_sentiment_baseline(facts: list[dict]) -> dict:
    """Compute sentiment statistics from the month's facts."""
    total_days = len(facts)
    if total_days == 0:
        return {
            "period_days": 0,
            "sentiment_distribution": {},
            "avg_negative_rate": 0.0,
            "context_frequency": {},
        }

    sentiment_counts = {"negative": 0, "positive": 0, "neutral": 0, "mixed": 0}
    context_counts = defaultdict(int)

    for fact in facts:
        tags = fact.get("tags", {})
        sentiment = tags.get("sentiment", {})

        # Handle both old (list) and new (dict) formats
        if isinstance(sentiment, list):
            for s in sentiment:
                if s in sentiment_counts:
                    sentiment_counts[s] += 1
        elif isinstance(sentiment, dict):
            overall = sentiment.get("overall", "neutral")
            if overall in sentiment_counts:
                sentiment_counts[overall] += 1
            for ctx in sentiment.get("context", []):
                context_counts[ctx] += 1

    return {
        "period_days": total_days,
        "sentiment_distribution": {
            k: round(v / total_days, 3) for k, v in sentiment_counts.items()
        },
        "avg_negative_rate": round(sentiment_counts["negative"] / total_days, 3),
        "context_frequency": dict(context_counts),
    }


def extract_themes(facts: list[dict], briefings: list[dict]) -> dict:
    """Extract recurring themes and statistics from the month's data."""
    themes = {
        "github_prs": [],
        "discord_topics": [],
        "strategic_themes": [],
        "user_concerns": [],
        "security_issues": [],
        "upcoming_launches": [],
    }

    for fact in facts:
        categories = fact.get("categories", {})

        # GitHub PRs
        github = categories.get("github_updates", {})
        for pr in github.get("new_issues_prs", []):
            themes["github_prs"].append({
                "title": pr.get("title"),
                "significance": pr.get("significance"),
                "status": pr.get("status"),
            })

        # Discord topics
        for update in categories.get("discord_updates", []):
            themes["discord_topics"].append({
                "channel": update.get("channel"),
                "summary": update.get("summary"),
            })

        # User concerns
        for feedback in categories.get("user_feedback", []):
            themes["user_concerns"].append(feedback.get("feedback_summary"))

        # Security
        for alert in categories.get("security_alerts", []):
            themes["security_issues"].append({
                "severity": alert.get("severity"),
                "issue": alert.get("issue"),
                "status": alert.get("status"),
            })

    for briefing in briefings:
        # Strategic themes from council
        for point in briefing.get("key_points", []):
            themes["strategic_themes"].append({
                "topic": point.get("topic"),
                "summary": point.get("summary"),
            })

    return themes


def load_north_star() -> str:
    """Load the current north star context."""
    if NORTH_STAR_FILE.exists():
        return NORTH_STAR_FILE.read_text()
    return ""


def generate_retro_prompt(year: int, month: int, themes: dict, github_summary: str | None, north_star: str) -> str:
    """Generate the prompt for the monthly retrospective."""
    month_name = datetime(year, month, 1).strftime("%B %Y")

    prompt = f"""You are generating a monthly retrospective episode for the JedAI Council - an AI council that debates strategic direction for the ElizaOS project.

## Context

**Month**: {month_name}
**Current North Star**:
{north_star}

## Month's Activity Summary

### GitHub Development
{github_summary if github_summary else "No GitHub summary available for this month."}

### Strategic Themes Discussed ({len(themes['strategic_themes'])} topics)
{json.dumps(themes['strategic_themes'][:15], indent=2)}

### Community Concerns ({len(themes['user_concerns'])} items)
{json.dumps(list(set(themes['user_concerns']))[:10], indent=2)}

### Security Issues
{json.dumps(themes['security_issues'], indent=2) if themes['security_issues'] else "No major security issues reported."}

### Key GitHub Activity ({len(themes['github_prs'])} PRs tracked)
Top PRs by significance:
{json.dumps(themes['github_prs'][:10], indent=2)}

## Your Task

Generate a special monthly retrospective episode where the council:

1. **Reviews the month** - What were the major developments, wins, and challenges?
2. **Identifies patterns** - What themes kept recurring? What's the community energy around?
3. **Debates strategic direction** - Given what happened, what should be the focus going forward?
4. **Proposes next month's focus** - Concrete recommendations for priorities

The council members are:
- **elizahost**: The moderator AI, neutral and synthesizing
- **aimarc**: Technical visionary, focused on architecture and AGI path
- **aishaw**: Pragmatic builder, focused on shipping and developer experience
- **peepo**: Community voice, meme-aware, cultural relevance
- **spartan**: Metrics-driven, focused on token economics and measurable outcomes

Output a JSON episode in this format:
{{
    "id": "RETRO-{year}-{month:02d}",
    "name": "Monthly Retro: {month_name}",
    "type": "retrospective",
    "premise": "...",
    "summary": "...",
    "month_reviewed": "{year}-{month:02d}",
    "key_developments": [
        {{"area": "...", "summary": "...", "impact": "high|medium|low"}}
    ],
    "recurring_themes": [
        {{"theme": "...", "frequency": "...", "council_take": "..."}}
    ],
    "wins": ["..."],
    "challenges": ["..."],
    "proposed_focus": [
        {{"priority": 1, "area": "...", "rationale": "...", "success_metric": "..."}}
    ],
    "north_star_assessment": {{
        "still_relevant": true/false,
        "suggested_updates": "..."
    }},
    "scenes": [
        {{
            "location": "council_chamber",
            "description": "...",
            "dialogue": [
                {{"actor": "elizahost", "line": "...", "action": "..."}}
            ]
        }}
    ]
}}

Make the dialogue feel natural and capture each council member's personality. The retrospective should be insightful and actionable.
"""
    return prompt


def call_llm(prompt: str) -> dict | None:
    """Call the LLM API and return parsed JSON response."""
    if not API_KEY:
        logging.error("OPENROUTER_API_KEY not set")
        return None

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/elizaOS/knowledge",
        "X-Title": "Monthly Council Retro"
    }

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(OPENROUTER_API_ENDPOINT, headers=headers, json=payload, timeout=300)
        response.raise_for_status()

        content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")

        # Clean up response
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        return json.loads(content.strip())

    except Exception as e:
        logging.error(f"LLM API call failed: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Generate monthly council retrospective episode")
    parser.add_argument("-y", "--year", type=int, help="Year to analyze (default: previous month's year)")
    parser.add_argument("-m", "--month", type=int, help="Month to analyze (default: previous month)")
    parser.add_argument("-o", "--output", type=Path, help="Output file path")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be analyzed without generating")
    args = parser.parse_args()

    # Default to previous month
    today = datetime.now()
    if args.year and args.month:
        target_year, target_month = args.year, args.month
    else:
        first_of_this_month = today.replace(day=1)
        last_month = first_of_this_month - timedelta(days=1)
        target_year, target_month = last_month.year, last_month.month

    month_name = datetime(target_year, target_month, 1).strftime("%B %Y")
    logging.info(f"Generating retrospective for {month_name}")

    # Get all dates for the month
    first_day, last_day, all_dates = get_month_dates(target_year, target_month)
    logging.info(f"Analyzing {len(all_dates)} days: {first_day} to {last_day}")

    # Load data
    facts = load_month_facts(all_dates)
    briefings = load_month_council_briefings(all_dates)
    github_summary = load_github_monthly_summary(target_year, target_month)
    north_star = load_north_star()

    logging.info(f"Loaded: {len(facts)} facts, {len(briefings)} briefings")

    if args.dry_run:
        print(f"\nDry run for {month_name}:")
        print(f"  Facts files: {len(facts)}")
        print(f"  Briefing files: {len(briefings)}")
        print(f"  GitHub summary: {'Yes' if github_summary else 'No'}")
        print(f"  North star: {'Loaded' if north_star else 'Missing'}")
        return

    # Extract themes
    themes = extract_themes(facts, briefings)
    logging.info(f"Extracted themes: {len(themes['strategic_themes'])} strategic, {len(themes['github_prs'])} PRs")

    # Compute sentiment baseline for daily extraction
    baseline = compute_sentiment_baseline(facts)
    logging.info(f"Baseline: {baseline['avg_negative_rate']:.1%} negative rate")

    # Generate prompt and call LLM
    prompt = generate_retro_prompt(target_year, target_month, themes, github_summary, north_star)

    logging.info("Calling LLM to generate retrospective...")
    episode = call_llm(prompt)

    if not episode:
        logging.error("Failed to generate retrospective")
        sys.exit(1)

    # Add metadata
    episode["_metadata"] = {
        "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
        "model": MODEL,
        "facts_analyzed": len(facts),
        "briefings_analyzed": len(briefings),
        "month": f"{target_year}-{target_month:02d}",
    }

    # Add sentiment baseline for reference
    episode["sentiment_baseline"] = baseline

    # Save output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = args.output or OUTPUT_DIR / f"{target_year}-{target_month:02d}-retro.json"
    output_file.write_text(json.dumps(episode, indent=2, ensure_ascii=True))
    logging.info(f"Retrospective saved to {output_file}")

    # Update latest.json symlink (used by daily extraction for baseline)
    latest_link = OUTPUT_DIR / "latest.json"
    if latest_link.exists() or latest_link.is_symlink():
        latest_link.unlink()
    latest_link.symlink_to(output_file.name)
    logging.info(f"Updated latest.json symlink -> {output_file.name}")

    # Also save as an episode
    EPISODES_DIR.mkdir(parents=True, exist_ok=True)
    episode_file = EPISODES_DIR / f"episode-retro-{target_year}-{target_month:02d}.json"
    episode_file.write_text(json.dumps(episode, indent=2, ensure_ascii=True))
    logging.info(f"Episode saved to {episode_file}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"Monthly Retrospective: {month_name}")
    print(f"{'='*60}")
    print(f"\nPremise: {episode.get('premise', 'N/A')}")
    print(f"\nKey Developments:")
    for dev in episode.get("key_developments", [])[:5]:
        print(f"  - [{dev.get('impact', '?').upper()}] {dev.get('area')}: {dev.get('summary')}")
    print(f"\nProposed Focus for Next Month:")
    for focus in episode.get("proposed_focus", [])[:3]:
        print(f"  {focus.get('priority')}. {focus.get('area')}: {focus.get('rationale')}")
    print(f"\nNorth Star Assessment:")
    ns = episode.get("north_star_assessment", {})
    print(f"  Still relevant: {ns.get('still_relevant', 'N/A')}")
    print(f"  Suggested updates: {ns.get('suggested_updates', 'None')}")


if __name__ == "__main__":
    main()
