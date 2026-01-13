#!/usr/bin/env python3
"""
Generates quarterly or annual summaries from monthly retrospectives.
Analyzes patterns, tracks recurring issues, and produces strategic insights.
"""

import os
import sys
import json
import requests
import argparse
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
import logging

# --- Configuration ---
MODEL = "openai/gpt-5.2"
API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_API_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

SCRIPT_DIR = Path(__file__).parent.resolve()
SCRIPTS_ROOT = SCRIPT_DIR.parent  # scripts/
WORKSPACE_ROOT = SCRIPTS_ROOT.parent  # repository root
RETROS_DIR = WORKSPACE_ROOT / "the-council" / "retros"
OUTPUT_DIR = RETROS_DIR  # Consolidated: summaries now live alongside retros

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(levelname)s - %(message)s')


def load_retros_for_period(year: int, quarter: int = None) -> list[dict]:
    """Load retrospectives for a given year or quarter."""
    retros = []

    if quarter:
        # Q1=1-3, Q2=4-6, Q3=7-9, Q4=10-12
        start_month = (quarter - 1) * 3 + 1
        end_month = start_month + 2
        months = range(start_month, end_month + 1)
    else:
        months = range(1, 13)

    for month in months:
        path = RETROS_DIR / f"{year}-{month:02d}-retro.json"
        if path.exists():
            try:
                data = json.loads(path.read_text())
                retros.append(data)
                logging.info(f"Loaded retro for {year}-{month:02d}")
            except Exception as e:
                logging.warning(f"Failed to load {path}: {e}")

    return retros


def extract_patterns(retros: list[dict]) -> dict:
    """Extract patterns and recurring themes from retros."""
    patterns = {
        "all_developments": [],
        "all_wins": [],
        "all_challenges": [],
        "all_proposed_focus": [],
        "recurring_themes": defaultdict(int),
        "north_star_suggestions": [],
        "months_covered": [],
    }

    for retro in retros:
        month = retro.get("month_reviewed", "unknown")
        patterns["months_covered"].append(month)

        # Collect developments by impact
        for dev in retro.get("key_developments", []):
            patterns["all_developments"].append({
                "month": month,
                "area": dev.get("area"),
                "summary": dev.get("summary"),
                "impact": dev.get("impact"),
            })

        # Collect wins and challenges
        patterns["all_wins"].extend([{"month": month, "win": w} for w in retro.get("wins", [])])
        patterns["all_challenges"].extend([{"month": month, "challenge": c} for c in retro.get("challenges", [])])

        # Track proposed focus areas
        for focus in retro.get("proposed_focus", []):
            patterns["all_proposed_focus"].append({
                "month": month,
                "area": focus.get("area"),
                "rationale": focus.get("rationale"),
            })

        # Count recurring themes
        for theme in retro.get("recurring_themes", []):
            theme_name = theme.get("theme", "unknown")
            patterns["recurring_themes"][theme_name] += 1

        # Collect north star suggestions
        ns = retro.get("north_star_assessment", {})
        if ns.get("suggested_updates"):
            patterns["north_star_suggestions"].append({
                "month": month,
                "suggestion": ns["suggested_updates"],
            })

    return patterns


def generate_summary_prompt(period_name: str, patterns: dict) -> str:
    """Generate the prompt for the summary."""

    # Sort recurring themes by frequency
    sorted_themes = sorted(patterns["recurring_themes"].items(), key=lambda x: -x[1])

    # Get high-impact developments
    high_impact = [d for d in patterns["all_developments"] if d.get("impact") == "high"]

    prompt = f"""You are generating a strategic summary report for ElizaOS leadership.

## Period: {period_name}
## Months Covered: {', '.join(patterns['months_covered'])}

## High-Impact Developments ({len(high_impact)} items)
{json.dumps(high_impact, indent=2)}

## Recurring Themes (by frequency)
{json.dumps(sorted_themes[:10], indent=2)}

## All Wins ({len(patterns['all_wins'])} items)
{json.dumps(patterns['all_wins'][:20], indent=2)}

## All Challenges ({len(patterns['all_challenges'])} items)
{json.dumps(patterns['all_challenges'][:20], indent=2)}

## Proposed Focus Areas (across months)
{json.dumps(patterns['all_proposed_focus'], indent=2)}

## North Star Feedback (from monthly retros)
{json.dumps(patterns['north_star_suggestions'], indent=2)}

## Your Task

Generate a comprehensive strategic summary that:

1. **Executive Summary** - 2-3 paragraph overview of the period
2. **Key Achievements** - What was accomplished (grouped by theme)
3. **Persistent Challenges** - Issues that keep recurring and why
4. **Resolution Tracking** - What got better vs. what didn't
5. **Strategic Recommendations** - Based on patterns, what should leadership prioritize
6. **North Star Evolution** - How should the mission statement evolve based on learnings

Output as JSON:
{{
    "period": "{period_name}",
    "executive_summary": "...",
    "key_achievements": [
        {{"theme": "...", "accomplishments": ["..."], "impact": "..."}}
    ],
    "persistent_challenges": [
        {{"issue": "...", "months_affected": [...], "root_cause": "...", "recommendation": "..."}}
    ],
    "resolution_tracking": {{
        "improved": [{{"issue": "...", "progress": "..."}}],
        "stagnant": [{{"issue": "...", "blocker": "..."}}]
    }},
    "strategic_recommendations": [
        {{"priority": 1, "area": "...", "rationale": "...", "success_criteria": "..."}}
    ],
    "north_star_evolution": {{
        "current_gaps": ["..."],
        "suggested_additions": ["..."],
        "proposed_revision": "..."
    }},
    "metrics_to_track": [
        {{"metric": "...", "why": "...", "target": "..."}}
    ]
}}
"""
    return prompt


def call_llm(prompt: str) -> dict | None:
    """Call the LLM API."""
    if not API_KEY:
        logging.error("OPENROUTER_API_KEY not set")
        return None

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
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

        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]

        return json.loads(content.strip())
    except Exception as e:
        logging.error(f"LLM call failed: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Generate quarterly/annual summary from retros")
    parser.add_argument("-y", "--year", type=int, required=True, help="Year to summarize")
    parser.add_argument("-q", "--quarter", type=int, choices=[1, 2, 3, 4], help="Quarter (omit for full year)")
    parser.add_argument("--dry-run", action="store_true", help="Show patterns without generating")
    args = parser.parse_args()

    if args.quarter:
        period_name = f"Q{args.quarter} {args.year}"
        output_file = OUTPUT_DIR / f"{args.year}-Q{args.quarter}-summary.json"
    else:
        period_name = f"Year {args.year}"
        output_file = OUTPUT_DIR / f"{args.year}-annual-summary.json"

    logging.info(f"Generating summary for {period_name}")

    retros = load_retros_for_period(args.year, args.quarter)
    if not retros:
        logging.error("No retrospectives found for this period")
        sys.exit(1)

    logging.info(f"Loaded {len(retros)} retrospectives")

    patterns = extract_patterns(retros)

    if args.dry_run:
        print(f"\n=== Patterns for {period_name} ===")
        print(f"Months: {patterns['months_covered']}")
        print(f"Developments: {len(patterns['all_developments'])}")
        print(f"Wins: {len(patterns['all_wins'])}")
        print(f"Challenges: {len(patterns['all_challenges'])}")
        print(f"\nRecurring themes:")
        for theme, count in sorted(patterns['recurring_themes'].items(), key=lambda x: -x[1])[:10]:
            print(f"  {count}x - {theme}")
        return

    prompt = generate_summary_prompt(period_name, patterns)

    logging.info("Calling LLM to generate summary...")
    summary = call_llm(prompt)

    if not summary:
        logging.error("Failed to generate summary")
        sys.exit(1)

    summary["_metadata"] = {
        "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
        "model": MODEL,
        "retros_analyzed": len(retros),
        "months_covered": patterns["months_covered"],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(summary, indent=2, ensure_ascii=True))
    logging.info(f"Summary saved to {output_file}")

    # Print executive summary
    print(f"\n{'='*60}")
    print(f"Strategic Summary: {period_name}")
    print(f"{'='*60}")
    print(f"\n{summary.get('executive_summary', 'N/A')}")
    print(f"\nTop Strategic Recommendations:")
    for rec in summary.get("strategic_recommendations", [])[:3]:
        print(f"  {rec.get('priority')}. {rec.get('area')}: {rec.get('rationale')}")


if __name__ == "__main__":
    main()
