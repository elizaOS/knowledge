#!/usr/bin/env python3
"""
Validate generated illustrations against source facts using vision analysis.

Evaluates from a reader's perspective: Does this image capture and communicate
the story it's meant to illustrate?

Usage:
  # Validate all images in results.json
  python scripts/posters/validate-illustrations.py

  # Validate specific test
  python scripts/posters/validate-illustrations.py --test style-editorial

  # Limit number of images
  python scripts/posters/validate-illustrations.py --limit 5

  # Output JSON report
  python scripts/posters/validate-illustrations.py --json -o validation-report.json

  # Dry run - show what would be analyzed
  python scripts/posters/validate-illustrations.py --dry-run
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add utils to path for vision module
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR / "utils"))

from vision import load_image_base64, analyze

# Config
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent
SAMPLES_DIR = WORKSPACE_ROOT / "media" / "samples"
FACTS_DIR = WORKSPACE_ROOT / "the-council" / "facts"
DEFAULT_MODEL = "google/gemini-3-flash-preview"

# Reader archetypes for multi-perspective evaluation
READER_ARCHETYPES = {
    "casual": {
        "name": "Casual Scroller",
        "context": """You're casually scrolling social media. You don't follow this project closely.
You have 2 seconds to decide if this is interesting. You're drawn to visuals that are
eye-catching, clear, and make you curious.""",
    },
    "invested": {
        "name": "Community Member",
        "context": """You follow ElizaOS and AI agents closely. You check updates daily.
You want to see progress, news, and developments. You recognize the characters and
care about the project's direction.""",
    },
    "technical": {
        "name": "Developer",
        "context": """You're a software developer evaluating AI tools. You want substance
over flash. You appreciate accurate technical representations and dislike misleading
or overly abstract imagery.""",
    },
    "newcomer": {
        "name": "First-Time Visitor",
        "context": """You've never heard of ElizaOS. You stumbled on this image.
You're trying to understand what this project is about from the image alone.
Does it communicate the core idea?""",
    },
}


def load_facts_summary(facts_path: Path) -> dict:
    """Extract key information from facts file for context."""
    with open(facts_path) as f:
        facts = json.load(f)

    summary = {
        "date": facts.get("briefing_date", "unknown"),
        "overall_summary": facts.get("overall_summary", ""),
        "stories": [],
    }

    # Extract key stories/claims
    cats = facts.get("categories", {})

    if "twitter_news_highlights" in cats:
        for item in cats["twitter_news_highlights"][:4]:
            if item.get("claim"):
                summary["stories"].append(item["claim"])

    if "github_updates" in cats:
        for item in cats["github_updates"].get("overall_focus", [])[:2]:
            if item.get("claim"):
                summary["stories"].append(item["claim"])

    if "discord_updates" in cats:
        for item in cats["discord_updates"][:2]:
            if item.get("summary"):
                summary["stories"].append(item["summary"])

    if "strategic_insights" in cats:
        for item in cats["strategic_insights"][:2]:
            if item.get("insight"):
                summary["stories"].append(item["insight"])

    return summary


def build_evaluation_prompt(facts_summary: dict) -> str:
    """Build multi-perspective evaluation prompt - single API call."""

    stories_text = "\n".join(f"- {s[:200]}" for s in facts_summary["stories"][:6])

    personas = "\n\n".join([
        f"**{key.upper()}** - {info['name']}: {info['context']}"
        for key, info in READER_ARCHETYPES.items()
    ])

    prompt = f"""Evaluate this illustration from multiple reader perspectives.

TODAY'S STORIES ({facts_summary['date']}):
{facts_summary['overall_summary']}

Key points:
{stories_text}

PERSONAS TO ROLEPLAY:
{personas}

For EACH persona, provide their honest gut reaction to this image:
- Would they engage (click, share, read more)?
- Does it connect to the stories?
- Score 1-5 for effectiveness

Respond as JSON:
{{
  "casual": {{
    "reaction": "<1-sentence gut reaction>",
    "would_engage": <true/false>,
    "score": <1-5>
  }},
  "invested": {{
    "reaction": "<1-sentence gut reaction>",
    "would_engage": <true/false>,
    "score": <1-5>
  }},
  "technical": {{
    "reaction": "<1-sentence gut reaction>",
    "would_engage": <true/false>,
    "score": <1-5>
  }},
  "newcomer": {{
    "reaction": "<1-sentence gut reaction>",
    "would_engage": <true/false>,
    "score": <1-5>
  }}
}}
"""
    return prompt


def synthesize_recommendations(report: dict, facts_summary: dict, model: str) -> dict:
    """Synthesize actionable recommendations from all perspective feedback."""
    import requests

    # Build summary of all feedback
    feedback_summary = []
    for ev in report["evaluations"]:
        img = ev["image"]
        feedback_summary.append(f"\n{img} (avg: {ev['avg_score']}/5, consensus: {ev['consensus']}):")
        for key, p in ev.get("perspectives", {}).items():
            engage = "engaged" if p.get("would_engage") else "skipped"
            feedback_summary.append(f"  - {p['name']} ({engage}): {p.get('reaction', '?')[:100]}")

    prompt = f"""You are an art director reviewing illustration feedback from multiple reader personas.

SOURCE CONTENT DATE: {facts_summary['date']}
SUMMARY: {facts_summary['overall_summary'][:200]}

FEEDBACK FROM READERS:
{''.join(feedback_summary)}

Based on this feedback, provide actionable recommendations for improving the illustration pipeline.

Respond as JSON:
{{
  "patterns": ["<recurring issues across images>"],
  "improvements": ["<specific actionable recommendations>"],
  "strongest": "<which image worked best and why>",
  "weakest": "<which image needs most work and why>",
  "priority": "<single most important thing to fix>"
}}
"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "reasoning": {"enabled": True}
        },
        timeout=120
    )
    response.raise_for_status()

    result = response.json()["choices"][0]["message"]["content"].strip()
    return parse_json_response(result)


def parse_json_response(result: str) -> dict:
    """Parse JSON from model response, handling markdown wrapping."""
    try:
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        return json.loads(result.strip())
    except json.JSONDecodeError:
        return {"error": "parse_failed", "raw": result[:200]}


def validate_image(image_path: Path, facts_summary: dict, model: str) -> dict:
    """Validate image from multiple reader perspectives - single API call."""

    image_url, _ = load_image_base64(image_path)
    prompt = build_evaluation_prompt(facts_summary)
    result = analyze(image_url, prompt, model, json_output=True, reasoning=True)
    ev = parse_json_response(result)

    # Process perspectives
    perspectives = {}
    scores = []
    engagements = 0

    for key in READER_ARCHETYPES.keys():
        if key in ev:
            p = ev[key]
            perspectives[key] = {
                "name": READER_ARCHETYPES[key]["name"],
                **p
            }
            if "score" in p and isinstance(p["score"], (int, float)):
                scores.append(p["score"])
            if p.get("would_engage"):
                engagements += 1

    return {
        "perspectives": perspectives,
        "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "engagement_rate": f"{engagements}/{len(READER_ARCHETYPES)}",
        "consensus": engagements >= len(READER_ARCHETYPES) // 2 + 1,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validate illustrations from a reader's perspective",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "-f", "--facts",
        help="Facts file to validate against (default: from results.json date)"
    )
    parser.add_argument(
        "-r", "--results",
        default=str(SAMPLES_DIR / "results.json"),
        help="Results JSON file"
    )
    parser.add_argument(
        "--test",
        help="Only validate specific test name"
    )
    parser.add_argument(
        "--skip",
        nargs="+",
        default=["create-tag-icons", "characters"],
        help="Skip these test folders (default: create-tag-icons characters)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit number of images (0=all)"
    )
    parser.add_argument(
        "-m", "--model",
        default=DEFAULT_MODEL,
        help=f"Vision model (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON report"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file for report"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be analyzed"
    )

    args = parser.parse_args()

    if not os.environ.get("OPENROUTER_API_KEY") and not args.dry_run:
        print("Error: OPENROUTER_API_KEY not set", file=sys.stderr)
        return 1

    # Load results
    results_path = Path(args.results)
    if not results_path.exists():
        print(f"Error: Results not found: {results_path}", file=sys.stderr)
        return 1

    with open(results_path) as f:
        results_data = json.load(f)

    results = results_data.get("results", [])
    date_str = results_data.get("date", "unknown")

    # Determine facts file
    facts_path = Path(args.facts) if args.facts else FACTS_DIR / f"{date_str}.json"
    if not facts_path.exists():
        print(f"Error: Facts not found: {facts_path}", file=sys.stderr)
        return 1

    facts_summary = load_facts_summary(facts_path)

    print(f"Reader Perspective Validation")
    print(f"=" * 50)
    print(f"Date: {facts_summary['date']}")
    print(f"Stories: {len(facts_summary['stories'])}")
    print(f"=" * 50)

    # Collect images
    images = []
    for result in results:
        if result.get("status") != "success":
            continue
        if args.test and result.get("test") != args.test:
            continue
        # Skip specified folders
        script_name = result.get("script", "")
        if any(skip in script_name for skip in args.skip):
            continue

        for img_rel in result.get("images", []):
            img_path = SAMPLES_DIR / img_rel
            if img_path.exists():
                images.append({
                    "path": img_path,
                    "test": result.get("test", "unknown"),
                    "script": script_name,
                })

    if args.limit > 0:
        images = images[:args.limit]

    print(f"Images: {len(images)}")

    if args.dry_run:
        print("\n[DRY RUN] Would analyze:")
        for img in images:
            print(f"  {img['test']}/{img['path'].name}")
        return 0

    # Validate
    report = {
        "generated_at": datetime.now().isoformat(),
        "date": facts_summary["date"],
        "source_facts": str(facts_path),
        "facts_summary": facts_summary["overall_summary"],
        "stories_analyzed": facts_summary["stories"][:8],
        "model": args.model,
        "archetypes": {k: v["name"] for k, v in READER_ARCHETYPES.items()},
        "skipped": args.skip,
        "evaluations": [],
        "summary": {"scores": [], "consensus_count": 0, "total": 0}
    }

    for i, img in enumerate(images, 1):
        print(f"\n[{i}/{len(images)}] {img['test']}/{img['path'].name}")

        try:
            ev = validate_image(img["path"], facts_summary, args.model)

            # Print compact multi-perspective results
            print(f"  Engagement: {ev['engagement_rate']} | Avg: {ev['avg_score']}/5 | Consensus: {'✓' if ev['consensus'] else '✗'}")
            for key, p in ev["perspectives"].items():
                emoji = "👍" if p.get("would_engage") else "👎"
                reaction = p.get("reaction", "?")[:60]
                print(f"    {emoji} {p['name']}: {reaction}")

            report["summary"]["scores"].append(ev["avg_score"])
            if ev["consensus"]:
                report["summary"]["consensus_count"] += 1
            report["summary"]["total"] += 1

            # Load prompt if available
            prompt_file = img["path"].with_suffix(".txt")
            prompt_used = prompt_file.read_text() if prompt_file.exists() else None

            # Path relative to samples dir (for HTML viewer)
            try:
                rel_path = str(img["path"].relative_to(SAMPLES_DIR))
            except ValueError:
                rel_path = img["path"].name

            report["evaluations"].append({
                "image": img["path"].name,
                "image_path": rel_path,
                "script": img.get("script", "unknown"),
                "test": img["test"],
                "prompt_used": prompt_used,
                **ev
            })

        except Exception as e:
            print(f"  Error: {e}")

    # Summary
    scores = report["summary"]["scores"]
    if scores:
        avg = sum(scores) / len(scores)
        consensus_pct = (report["summary"]["consensus_count"] / report["summary"]["total"]) * 100

        print(f"\n{'=' * 50}")
        print(f"SUMMARY ({len(READER_ARCHETYPES)} perspectives)")
        print(f"{'=' * 50}")
        print(f"Average score: {avg:.1f}/5")
        print(f"Majority consensus: {report['summary']['consensus_count']}/{report['summary']['total']} ({consensus_pct:.0f}%)")

        report["summary"]["average_score"] = round(avg, 2)
        report["summary"]["consensus_pct"] = round(consensus_pct, 1)

    # Synthesize recommendations
    if scores and not args.dry_run:
        print(f"\nSynthesizing recommendations...")
        recommendations = synthesize_recommendations(report, facts_summary, args.model)
        report["recommendations"] = recommendations

        print(f"\n{'=' * 50}")
        print("RECOMMENDATIONS")
        print(f"{'=' * 50}")
        for i, rec in enumerate(recommendations.get("improvements", [])[:3], 1):
            print(f"{i}. {rec}")
        if recommendations.get("strongest"):
            print(f"\n✓ Strongest: {recommendations['strongest']}")
        if recommendations.get("weakest"):
            print(f"✗ Needs work: {recommendations['weakest']}")

    # Auto-save report
    report_path = Path(args.output) if args.output else SAMPLES_DIR / "validation-report.json"
    report_path.write_text(json.dumps(report, indent=2))
    print(f"\nReport saved: {report_path}")

    # Also print JSON if requested
    if args.json:
        print(json.dumps(report, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
