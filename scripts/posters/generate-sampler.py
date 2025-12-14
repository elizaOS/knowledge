#!/usr/bin/env python3
"""
Generate a sampler of all styles with a markdown report showing context.

Creates a folder with:
- One image per style
- A README.md with facts, prompts, and embedded images

Usage:
  python scripts/posters/generate-sampler.py
  python scripts/posters/generate-sampler.py -d 2025-12-12
  python scripts/posters/generate-sampler.py --styles editorial risograph noir_ink
  python scripts/posters/generate-sampler.py --include-characters
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

# Import from main generate-ai-image script
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from importlib.util import spec_from_file_location, module_from_spec
spec = spec_from_file_location("generate_ai_image", SCRIPT_DIR / "generate-ai-image.py")
generate_ai_image = module_from_spec(spec)
spec.loader.exec_module(generate_ai_image)

# Re-export needed functions and constants
OPENROUTER_API_KEY = generate_ai_image.OPENROUTER_API_KEY
OUTPUT_DIR = generate_ai_image.OUTPUT_DIR
DEFAULT_REFERENCES = generate_ai_image.DEFAULT_REFERENCES

load_facts = generate_ai_image.load_facts
load_style_presets = generate_ai_image.load_style_presets
get_available_styles = generate_ai_image.get_available_styles
get_style_prompt = generate_ai_image.get_style_prompt
style_requires_references = generate_ai_image.style_requires_references
generate_image_prompt = generate_ai_image.generate_image_prompt
generate_image = generate_ai_image.generate_image

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def generate_markdown_report(
    date_str: str,
    facts: dict,
    results: list[dict],
    output_dir: Path,
    include_characters: bool = False
) -> Path:
    """Generate a markdown report with all context and embedded images."""

    report_path = output_dir / "README.md"

    lines = [
        f"# Style Sampler: {date_str}",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        "",
        "## Source Facts",
        "",
        "### Overall Summary",
        "",
        f"> {facts.get('overall_summary', 'N/A')}",
        "",
    ]

    # Add category summaries
    categories = facts.get("categories", {})
    if categories:
        lines.append("### Category Highlights")
        lines.append("")

        for cat_name, cat_data in categories.items():
            if isinstance(cat_data, list) and cat_data:
                lines.append(f"**{cat_name}:**")
                for item in cat_data[:2]:  # First 2 items
                    if isinstance(item, dict):
                        summary = item.get("summary") or item.get("insight") or item.get("observation") or item.get("feedback_summary")
                        if summary:
                            lines.append(f"- {summary[:200]}...")
                lines.append("")
            elif isinstance(cat_data, dict) and "overall_focus" in cat_data:
                focus = cat_data.get("overall_focus", [])
                if focus:
                    lines.append(f"**{cat_name}:**")
                    for item in focus[:2]:
                        if isinstance(item, dict) and item.get("claim"):
                            lines.append(f"- {item['claim'][:200]}...")
                    lines.append("")

    lines.extend([
        "---",
        "",
        "## Generated Images",
        "",
    ])

    # Add each result
    for result in results:
        style_name = result["style"]
        status = result["status"]

        lines.append(f"### {style_name}")
        lines.append("")

        presets = load_style_presets()
        style_config = presets.get("styles", {}).get(style_name, {})
        lines.append(f"**Description:** {style_config.get('description', 'N/A')}")
        lines.append("")

        if status == "success":
            lines.append(f"![{style_name}](./{style_name}.png)")
            lines.append("")
            lines.append("<details>")
            lines.append("<summary>View Prompt</summary>")
            lines.append("")
            lines.append("```")
            lines.append(result.get("prompt", "N/A"))
            lines.append("```")
            lines.append("")
            lines.append("</details>")
        else:
            lines.append(f"**Status:** Failed - {result.get('error', 'Unknown error')}")

        if result.get("characters"):
            lines.append("")
            lines.append(f"**Characters used:** {', '.join(result['characters'])}")

        lines.append("")
        lines.append("---")
        lines.append("")

    # Summary table
    lines.extend([
        "## Summary",
        "",
        "| Style | Status | Characters |",
        "|-------|--------|------------|",
    ])

    for result in results:
        status_emoji = "✅" if result["status"] == "success" else "❌"
        chars = ", ".join(result.get("characters", [])) or "-"
        lines.append(f"| {result['style']} | {status_emoji} | {chars} |")

    lines.append("")

    # Write report
    report_path.write_text("\n".join(lines))
    return report_path


def main():
    available_styles = get_available_styles()

    parser = argparse.ArgumentParser(
        description="Generate a sampler of styles with markdown report",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("-d", "--date", help="Date in YYYY-MM-DD format (default: use daily.json)")
    parser.add_argument(
        "-o", "--output-dir",
        help="Output directory (default: posters/sampler-YYYY-MM-DD)"
    )
    parser.add_argument(
        "--styles",
        nargs="+",
        choices=available_styles,
        help=f"Specific styles to generate (default: all). Available: {', '.join(available_styles)}"
    )
    parser.add_argument(
        "--include-characters",
        action="store_true",
        help="Include council characters in all styles (not just 'council' style)"
    )
    parser.add_argument(
        "--journalistic",
        action="store_true",
        help="Only generate journalistically sensible styles (editorial, risograph, noir_ink, collage, ukiyo_e, paper_cutout)"
    )
    parser.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not OPENROUTER_API_KEY:
        logging.error("OPENROUTER_API_KEY environment variable not set")
        return 1

    # Load facts
    try:
        facts = load_facts(args.date)
        date_str = facts.get("briefing_date", datetime.now().strftime("%Y-%m-%d"))
    except FileNotFoundError as e:
        logging.error(f"Facts not found: {e}")
        return 1

    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = OUTPUT_DIR / f"sampler-{date_str}"

    output_dir.mkdir(parents=True, exist_ok=True)
    logging.info(f"Output directory: {output_dir}")

    # Determine styles to generate
    if args.styles:
        styles = args.styles
    elif args.journalistic:
        styles = ["editorial", "risograph", "noir_ink", "collage", "ukiyo_e", "paper_cutout"]
    else:
        styles = available_styles

    logging.info(f"Generating {len(styles)} styles: {', '.join(styles)}")
    logging.info(f"Facts summary: {facts.get('overall_summary', 'N/A')[:100]}...")

    # Generate each style
    results = []

    for style in styles:
        logging.info(f"\n{'='*50}")
        logging.info(f"Generating: {style}")
        logging.info(f"{'='*50}")

        result = {
            "style": style,
            "status": "pending",
            "prompt": None,
            "error": None,
            "characters": []
        }

        try:
            # Determine if we need character references
            reference_images = None
            character_names = []

            if style_requires_references(style) or args.include_characters:
                reference_images = [p for p in DEFAULT_REFERENCES.values() if p.exists()]
                character_names = [p.stem for p in reference_images]
                result["characters"] = character_names
                logging.info(f"  Using characters: {character_names}")

            # Generate prompt
            prompt = generate_image_prompt(facts, style=style, character_names=character_names)
            result["prompt"] = prompt
            logging.info(f"  Prompt: {prompt[:100]}...")

            # Generate image
            logging.info(f"  Calling Nano Banana Pro...")
            image_bytes = generate_image(prompt, reference_images=reference_images)

            # Save image
            output_path = output_dir / f"{style}.png"
            output_path.write_bytes(image_bytes)

            result["status"] = "success"
            logging.info(f"  Saved: {output_path}")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logging.error(f"  Failed: {e}")

        results.append(result)

    # Generate markdown report
    logging.info(f"\n{'='*50}")
    logging.info("Generating markdown report...")
    report_path = generate_markdown_report(
        date_str, facts, results, output_dir, args.include_characters
    )
    logging.info(f"Report saved: {report_path}")

    # Summary
    success = sum(1 for r in results if r["status"] == "success")
    failed = len(results) - success

    logging.info(f"\n{'='*50}")
    logging.info(f"COMPLETE: {success} succeeded, {failed} failed")
    logging.info(f"Output: {output_dir}")
    logging.info(f"Report: {report_path}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
