#!/usr/bin/env python3
"""
Processes an aggregated JSON context file (output from aggregate_sources.py),
passes the entire context to an LLM with a fact-extraction prompt,
and outputs a structured JSON list of extracted facts.
"""

import argparse
import json
import logging
from pathlib import Path
from datetime import datetime
import os
import sys
import re # For date parsing from filename
import requests
from typing import Optional

# Configuration
# HACKMD_OUTPUT_DIR = Path("hackmd") # No longer used
NEWS_SHOW_OUTPUT_DIR = Path("the-council") # Default parent for output if -o is just a filename, but -o allows full path
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_API_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
LLM_MODEL = "openai/gpt-5.2" # Or your preferred model, consider one with large context window
SCRIPTS_DIR = Path(__file__).parent.parent
WORKSPACE_ROOT = SCRIPTS_DIR.parent  # Repository root
DEFAULT_FACT_EXTRACTION_PROMPT_FILE = SCRIPTS_DIR / "prompts" / "extraction" / "facts.txt"

# Logging configuration
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def load_prompt_template(prompt_file: Path) -> str | None:
    """Loads the prompt template from the specified file."""
    if not prompt_file.is_file():
        logging.error(f"Prompt file not found: {prompt_file}")
        return None
    try:
        return prompt_file.read_text(encoding='utf-8')
    except Exception as e:
        logging.error(f"Could not read prompt file {prompt_file}: {e}")
        return None


# Tag generation prompt for backfilling existing files
TAG_GENERATION_PROMPT = """Analyze this fact briefing and generate semantic tags.

**Briefing Content:**
```json
{briefing_json}
```

**Tag Vocabularies (use ONLY these tags):**

**themes** (WHAT is happening - pick 2-5 most relevant):
- `token-migration`, `governance`, `tokenomics`
- `release`, `deployment`, `infrastructure`
- `developer-experience`, `documentation`, `onboarding`
- `security`, `vulnerability`, `audit`
- `community-growth`, `partnerships`, `ecosystem`
- `ai-agents`, `plugins`, `integrations`
- `performance`, `optimization`, `scaling`
- `ux-improvement`, `bug-fix`, `maintenance`
- `market-activity`, `trading`, `liquidity`

**sentiment** (structured object):
- `overall`: exactly one of `positive`, `negative`, `neutral`, `mixed`
- `context`: 1-3 domain tags from: `economic`, `technical`, `governance`, `social`

**story_type** (editorial classification - pick exactly 1):
- `crisis` - urgent issues, security incidents, breaking problems
- `progress` - features shipped, milestones reached, wins
- `maintenance` - routine updates, bug fixes, housekeeping
- `announcement` - official communications, launches, events
- `debate` - community discussions, governance decisions, differing opinions
- `analysis` - market insights, strategic observations, trends

**Output ONLY this JSON object, nothing else:**
```json
{{
  "themes": ["tag1", "tag2"],
  "sentiment": {{
    "overall": "positive|negative|neutral|mixed",
    "context": ["economic", "technical"]
  }},
  "story_type": ["tag"]
}}
```
"""


def derive_tags_from_categories(categories: dict) -> list[str]:
    """Derive rule-based tags from which categories have content."""
    derived = []

    # Map categories to derived tags
    category_tag_map = {
        "github_updates": "development",
        "discord_updates": "community",
        "market_analysis": "market",
        "user_feedback": "feedback",
        "strategic_insights": "strategy",
        "twitter_news_highlights": "social",
    }

    for cat_name, cat_data in categories.items():
        if cat_name in category_tag_map:
            # Check if category has meaningful content
            has_content = False
            if isinstance(cat_data, list) and len(cat_data) > 0:
                has_content = True
            elif isinstance(cat_data, dict):
                # github_updates has nested structure
                if cat_data.get("new_issues_prs") or cat_data.get("overall_focus"):
                    has_content = True

            if has_content:
                derived.append(category_tag_map[cat_name])

    return derived


def derive_priority_tags(data: dict) -> list[str]:
    """Derive priority/urgency tags from content signals."""
    priority = []

    overall_summary = data.get("overall_summary", "").lower()

    # Check for urgency signals
    urgent_keywords = ["urgent", "critical", "breaking", "emergency", "deadline", "immediately"]
    if any(kw in overall_summary for kw in urgent_keywords):
        priority.append("time-sensitive")

    # Check for high-attention signals
    attention_keywords = ["migration", "security", "vulnerability", "incident", "outage"]
    if any(kw in overall_summary for kw in attention_keywords):
        priority.append("high-attention")

    # Default to routine if no signals
    if not priority:
        priority.append("routine")

    return priority


def generate_tags_via_llm(briefing_data: dict) -> Optional[dict]:
    """Generate semantic tags for a briefing using LLM."""
    # Create a simplified version for the prompt (exclude _metadata)
    briefing_for_prompt = {k: v for k, v in briefing_data.items() if not k.startswith("_")}

    prompt = TAG_GENERATION_PROMPT.format(
        briefing_json=json.dumps(briefing_for_prompt, indent=2)[:8000]  # Limit size
    )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "google/gemini-2.5-flash-lite",  # Fast/cheap model for tag generation
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(OPENROUTER_API_ENDPOINT, headers=headers, json=payload, timeout=60)
        response.raise_for_status()

        content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")

        # Strip markdown code fences
        if content.startswith("```"):
            content = re.sub(r'^```(?:json)?\n?', '', content)
            content = re.sub(r'\n?```$', '', content)

        tags = json.loads(content.strip())

        # Validate structure
        if isinstance(tags, dict) and "themes" in tags:
            return tags
        else:
            logging.warning(f"Invalid tag structure from LLM: {content[:200]}")
            return None

    except Exception as e:
        logging.error(f"Failed to generate tags via LLM: {e}")
        return None


def build_complete_tags(llm_tags: Optional[dict], categories: dict, data: dict) -> dict:
    """Combine LLM tags with rule-based derived tags."""
    tags = {
        "themes": [],
        "sentiment": {"overall": "neutral", "context": []},
        "story_type": [],
        "derived": [],
        "priority": [],
        "manual": []
    }

    # Add LLM-generated tags
    if llm_tags:
        tags["themes"] = llm_tags.get("themes", [])
        # Normalize story_type to always be an array (LLM sometimes returns string)
        story_type = llm_tags.get("story_type", [])
        tags["story_type"] = [story_type] if isinstance(story_type, str) else story_type

        # Handle sentiment - support both old (list) and new (dict) formats
        llm_sentiment = llm_tags.get("sentiment", {})
        if isinstance(llm_sentiment, dict):
            tags["sentiment"] = {
                "overall": llm_sentiment.get("overall", "neutral"),
                "context": llm_sentiment.get("context", [])
            }
        elif isinstance(llm_sentiment, list):
            # Backwards compatibility: convert old list format
            overall = "neutral"
            for s in llm_sentiment:
                if s in ["positive", "negative", "neutral", "mixed"]:
                    overall = s
                    break
            tags["sentiment"] = {"overall": overall, "context": []}

    # Add rule-based derived tags
    tags["derived"] = derive_tags_from_categories(categories)

    # Add priority tags
    tags["priority"] = derive_priority_tags(data)

    return tags


def backfill_tags_for_file(file_path: Path, dry_run: bool = False, force: bool = False) -> bool:
    """Add tags to an existing facts JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Check if tags already exist
        if "tags" in data and not force:
            logging.info(f"  [skip] {file_path.name} - already has tags (use --force to overwrite)")
            return True

        # Check if _metadata.tags exists (old location)
        if data.get("_metadata", {}).get("tags") and not force:
            logging.info(f"  [skip] {file_path.name} - already has _metadata.tags (use --force to overwrite)")
            return True

        if "tags" in data and force:
            logging.info(f"  [force] {file_path.name} - overwriting existing tags")

        logging.info(f"  [process] {file_path.name}")

        # Generate LLM tags
        llm_tags = generate_tags_via_llm(data)

        # Build complete tag structure
        categories = data.get("categories", {})
        tags = build_complete_tags(llm_tags, categories, data)

        if dry_run:
            logging.info(f"    [dry-run] Would add tags: {json.dumps(tags, indent=2)}")
            return True

        # Add tags to data (at top level, after overall_summary)
        data["tags"] = tags

        # Update _metadata to note backfill
        if "_metadata" not in data:
            data["_metadata"] = {}
        data["_metadata"]["tags_backfilled_at"] = datetime.utcnow().isoformat() + "Z"

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=True)

        logging.info(f"    [done] Added {len(tags['themes'])} themes, story_type={tags['story_type']}")
        return True

    except Exception as e:
        logging.error(f"  [error] {file_path.name}: {e}")
        return False

def convert_briefing_to_markdown(briefing_data: dict) -> str:
    """Converts the structured JSON briefing data to a Markdown string."""
    md_lines = []
    date_str = briefing_data.get("briefing_date", "N/A")
    md_lines.append(f"# Fact Briefing: {date_str}\n")

    md_lines.append(f"## Overall Summary")
    md_lines.append(f"{briefing_data.get('overall_summary', 'No overall summary provided.')}\n")

    # Key Facts (simple strings)
    key_facts = briefing_data.get("key_facts", [])
    if key_facts:
        md_lines.append(f"## Key Facts\n")
        for fact in key_facts:
            md_lines.append(f"- {fact}")
        md_lines.append("")

    # Open Questions (simple strings)
    open_questions = briefing_data.get("open_questions", [])
    if open_questions:
        md_lines.append(f"## Open Questions\n")
        for question in open_questions:
            md_lines.append(f"- {question}")
        md_lines.append("")

    categories = briefing_data.get("categories", {})
    if not categories:
        md_lines.append("No detailed categories provided.")
        return "\n".join(md_lines)

    md_lines.append(f"## Categories")

    # Twitter News Highlights
    twitter_highlights = categories.get("twitter_news_highlights", [])
    if twitter_highlights:
        md_lines.append(f"\n### Twitter News Highlights")
        for item in twitter_highlights:
            sentiment_str = f" (Sentiment: {item.get('sentiment')})" if item.get('sentiment') else ""
            md_lines.append(f"- {item.get('claim', 'N/A')}{sentiment_str}")

    # GitHub Updates
    github_updates = categories.get("github_updates", {})
    if github_updates:
        md_lines.append(f"\n### GitHub Updates")
        new_issues_prs = github_updates.get("new_issues_prs", [])
        if new_issues_prs:
            md_lines.append(f"\n#### New Issues/PRs")
            for item in new_issues_prs:
                title = item.get('title', 'N/A')
                item_type = item.get('item_type', '').capitalize()
                number = item.get('number', '')
                url = item.get('url', '#')
                author = f" by {item.get('author', 'N/A')}" if item.get('author') else ""
                status = f" - Status: {item.get('status', 'N/A')}"
                significance = f" - Significance: {item.get('significance', 'N/A')}"
                md_lines.append(f"- [{item_type} #{number}: {title}]({url}){author}{status}{significance}")
        
        overall_focus_list = github_updates.get("overall_focus", [])
        if overall_focus_list:
            md_lines.append(f"\n#### Overall Focus")
            for item in overall_focus_list:
                md_lines.append(f"- {item.get('claim', 'N/A')}")

    # Discord Updates
    discord_updates = categories.get("discord_updates", [])
    if discord_updates:
        md_lines.append(f"\n### Discord Updates")
        for item in discord_updates:
            channel = item.get('channel', 'N/A')
            summary = item.get('summary', 'N/A')
            participants = ", ".join(item.get('key_participants', []))
            participants_str = f" (Key Participants: {participants})" if participants else ""
            md_lines.append(f"- **{channel}:** {summary}{participants_str}")

    # User Feedback
    user_feedback = categories.get("user_feedback", [])
    if user_feedback:
        md_lines.append(f"\n### User Feedback")
        for item in user_feedback:
            platform_str = f" (Platform: {item.get('source_platform')})" if item.get('source_platform') else ""
            sentiment_str = f" (Sentiment: {item.get('sentiment')})" if item.get('sentiment') else ""
            md_lines.append(f"- {item.get('feedback_summary', 'N/A')}{platform_str}{sentiment_str}")

    # Strategic Insights
    strategic_insights = categories.get("strategic_insights", [])
    if strategic_insights:
        md_lines.append(f"\n### Strategic Insights")
        for item in strategic_insights:
            theme = item.get('theme', 'Insight')
            md_lines.append(f"\n#### {theme}")
            md_lines.append(item.get('insight', 'N/A'))
            implications = item.get("implications_or_questions", [])
            if implications:
                md_lines.append(f"\n*Implications/Questions:*")
                for imp_q in implications:
                    md_lines.append(f"  - {imp_q}")
    
    # Market Analysis
    market_analysis = categories.get("market_analysis", [])
    if market_analysis:
        md_lines.append(f"\n### Market Analysis")
        for item in market_analysis:
            relevance_str = f" (Relevance: {item.get('relevance')})" if item.get('relevance') else ""
            md_lines.append(f"- {item.get('observation', 'N/A')}{relevance_str}")

    return "\n".join(md_lines)

def main():
    parser = argparse.ArgumentParser(
        description="Extracts structured facts from aggregated JSON using an LLM, or converts a fact JSON to Markdown."
    )
    parser.add_argument(
        "-i", "--input-file",
        type=Path,
        help="Input JSON file. For LLM mode: aggregated data. For Markdown mode (-m): fact JSON data."
    )
    parser.add_argument(
        "-o", "--output-file",
        type=Path,
        help="Output file. For LLM mode: fact JSON. For Markdown mode (-m): Markdown file."
    )
    parser.add_argument(
        "-d", "--date",
        help="Optional: Date (YYYY-MM-DD) for context/logging (primarily LLM mode)."
    )
    parser.add_argument(
        "-p", "--prompt-file",
        type=Path,
        default=DEFAULT_FACT_EXTRACTION_PROMPT_FILE,
        help=f"Path to fact extraction prompt file (LLM mode). Default: {DEFAULT_FACT_EXTRACTION_PROMPT_FILE}"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Increase output verbosity (DEBUG level)."
    )
    parser.add_argument(
        "-m", "--to-markdown",
        action="store_true",
        help="Convert input fact JSON (-i) to Markdown (-o). Skips LLM call."
    )
    parser.add_argument(
        "-md", "--markdown-export-file",
        type=Path,
        help="Optional: Simultaneously export a Markdown version of the extracted facts to this file "
             "during the primary LLM extraction process. Used in conjunction with -o (for JSON output)."
    )
    parser.add_argument(
        "--backfill-tags",
        action="store_true",
        help="Backfill mode: Add tags to existing facts JSON files without regenerating content. "
             "Use with -i for single file or --backfill-dir for directory."
    )
    parser.add_argument(
        "--backfill-dir",
        type=Path,
        help="Directory containing facts JSON files to backfill with tags."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes (for backfill mode)."
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Force overwrite existing tags (for backfill mode)."
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Verbose mode enabled.")

    if not OPENROUTER_API_KEY:
        logging.error("OPENROUTER_API_KEY environment variable not set.")
        sys.exit(1)

    # --- Backfill Tags Mode ---
    if args.backfill_tags:
        files_to_process = []

        if args.backfill_dir:
            if not args.backfill_dir.is_dir():
                logging.error(f"Backfill directory not found: {args.backfill_dir}")
                sys.exit(1)
            files_to_process = sorted(args.backfill_dir.glob("*.json"))
            # Exclude daily.json symlink
            files_to_process = [f for f in files_to_process if f.name != "daily.json"]
        elif args.input_file:
            if not args.input_file.is_file():
                logging.error(f"Input file not found: {args.input_file}")
                sys.exit(1)
            files_to_process = [args.input_file]
        else:
            parser.error("--backfill-tags requires either -i/--input-file or --backfill-dir")

        logging.info(f"Backfilling tags for {len(files_to_process)} file(s)...")
        if args.dry_run:
            logging.info("[DRY RUN MODE - no files will be modified]")

        success = 0
        failed = 0
        skipped = 0

        for file_path in files_to_process:
            result = backfill_tags_for_file(file_path, dry_run=args.dry_run, force=args.force)
            if result:
                success += 1
            else:
                failed += 1

        logging.info(f"\nBackfill complete: {success} processed, {failed} failed")
        sys.exit(0 if failed == 0 else 1)

    if not args.input_file or not args.output_file:
        # This check is primarily for LLM mode. For -m mode, specific checks are done later.
        if not args.to_markdown: 
            parser.error("-i/--input-file and -o/--output-file are required for LLM-based fact extraction.")

    prompt_template = load_prompt_template(args.prompt_file)
    if not prompt_template and not args.to_markdown: # Prompt only needed if not in to_markdown mode
        sys.exit(1) # Error already logged by load_prompt_template

    target_date_str = args.date
    # Infer date from input filename if not provided
    if not target_date_str and args.input_file: # Check if input_file is not None
        match = re.search(r'(\d{4}-\d{2}-\d{2})', args.input_file.name)
        if match:
            try:
                datetime.strptime(match.group(1), "%Y-%m-%d")
                target_date_str = match.group(1)
                logging.info(f"Inferred date from input filename: {target_date_str}")
            except ValueError:
                logging.info("Could not parse date from filename pattern despite match.")
    
    log_date_context = target_date_str if target_date_str else (args.input_file.name if args.input_file else "Unknown Context")
    logging.info(f"Processing for context: '{log_date_context}'")

    # --- Markdown Generation Mode (-m) ---
    if args.to_markdown:
        if not args.input_file or not args.output_file:
            parser.error("-i/--input-file (for fact JSON) and -o/--output-file (for Markdown) are required when using -m/--to-markdown.")
        if not args.input_file.is_file():
            logging.error(f"Error: Input fact JSON file not found: {args.input_file}")
            sys.exit(1)
        
        logging.info(f"Converting fact JSON '{args.input_file}' to Markdown '{args.output_file}'...")
        try:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                fact_json_data = json.load(f)
            markdown_content = convert_briefing_to_markdown(fact_json_data)
            args.output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            logging.info(f"Successfully wrote Markdown to {args.output_file}.")
            logging.info("--- Markdown generation finished. ---")
            sys.exit(0) # Exit after generating Markdown
        except Exception as e:
            logging.error(f"Error during JSON to Markdown conversion: {e}")
            sys.exit(1)

    # --- LLM-Based Fact Extraction Mode (Default if -m is not used) ---
    if not args.input_file:
        parser.error("-i/--input-file is required for LLM-based fact extraction.")
    if not args.input_file.is_file():
        logging.error(f"Error: Input aggregated JSON file not found: {args.input_file}")
        sys.exit(1)

    # aggregated_data_dict = None # Reverted: No longer creating legend here if source_keys are removed from output
    aggregated_data_json_string = ""
    try:
        aggregated_data_json_string = args.input_file.read_text(encoding='utf-8')
        # json.loads(aggregated_data_json_string) # Keep validation if desired, but dict not strictly needed if no legend
        json.loads(aggregated_data_json_string) # Validate JSON structure
        logging.info(f"Successfully read and validated input data from {args.input_file}")
    except json.JSONDecodeError:
        logging.error(f"Error: Input file {args.input_file} does not contain valid JSON.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error reading input file {args.input_file}: {e}")
        sys.exit(1)
    
    # Reverted: Removed source_key_legend creation and prompt modification logic
    # as per user decision to remove source_keys from LLM output requirement.
    final_llm_prompt = prompt_template.format(input_json_string=aggregated_data_json_string)

    logging.info(f"Sending context from '{args.input_file.name}' to LLM for fact extraction...")
    llm_payload = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": final_llm_prompt}],
        "response_format": {"type": "json_object"}
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/elizaOS/knowledge",
        "X-Title": f"Fact Extraction ({log_date_context})"
    }

    llm_output_data = None
    llm_metadata = {
        "model": LLM_MODEL,
        "extracted_at": datetime.utcnow().isoformat() + "Z",
    }
    extraction_start_time = datetime.utcnow()
    try:
        response = requests.post(OPENROUTER_API_ENDPOINT, headers=headers, json=llm_payload, timeout=300)
        response.raise_for_status()
        llm_response_data = response.json()

        # Capture token usage for cost tracking
        usage = llm_response_data.get("usage", {})
        if usage:
            llm_metadata["prompt_tokens"] = usage.get("prompt_tokens")
            llm_metadata["completion_tokens"] = usage.get("completion_tokens")
            llm_metadata["total_tokens"] = usage.get("total_tokens")
            logging.info(f"LLM Usage - Prompt: {usage.get('prompt_tokens')}, Completion: {usage.get('completion_tokens')}, Total: {usage.get('total_tokens')}")

        content_str = llm_response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        if not content_str.strip():
            logging.error("LLM returned empty content.")
        else:
            # Strip Markdown code fences if present
            if content_str.startswith("```json"):
                content_str = content_str[len("```json"):]
            if content_str.startswith("```"):
                content_str = content_str[len("```"):]
            if content_str.endswith("```"):
                content_str = content_str[:-len("```")]
            content_str = content_str.strip() # Clean up any surrounding whitespace

            try:
                parsed_content = json.loads(content_str)
                if isinstance(parsed_content, dict) and \
                   "briefing_date" in parsed_content and \
                   "overall_summary" in parsed_content and \
                   "categories" in parsed_content and isinstance(parsed_content["categories"], dict):
                    llm_output_data = parsed_content
                    logging.info(f"Successfully parsed categorized fact briefing from LLM response for date: {parsed_content.get('briefing_date')}")
                else:
                    logging.error(f"LLM response content is not in the expected categorized format. Content: {content_str[:500]}...")
            except json.JSONDecodeError as e_json:
                logging.error(f"Failed to parse LLM response content as JSON: {e_json}. Content: {content_str[:500]}...")

    except requests.exceptions.RequestException as e_req:
        logging.error(f"LLM API request failed: {e_req}")
    except Exception as e_gen:
        logging.error(f"Error processing LLM response: {e_gen}")

    # Calculate processing duration
    llm_metadata["processing_seconds"] = round((datetime.utcnow() - extraction_start_time).total_seconds(), 2)

    if not llm_output_data:
        logging.warning("No valid categorized briefing was extracted. The output JSON file might be incomplete or empty.")
        llm_output_data = {
            "briefing_date": target_date_str or "unknown",
            "overall_summary": "Error: Failed to generate briefing due to LLM or parsing issues.",
            "categories": {}
        }
        llm_metadata["status"] = "error"
    else:
        llm_metadata["status"] = "success"
        # Count facts extracted per category
        categories = llm_output_data.get("categories", {})
        llm_metadata["facts_by_category"] = {
            k: len(v) if isinstance(v, list) else (len(v.get("new_issues_prs", [])) if isinstance(v, dict) else 0)
            for k, v in categories.items()
        }
        # Include counts for key_facts and open_questions
        key_facts = llm_output_data.get("key_facts", [])
        open_questions = llm_output_data.get("open_questions", [])
        if key_facts:
            llm_metadata["facts_by_category"]["key_facts"] = len(key_facts)
        if open_questions:
            llm_metadata["facts_by_category"]["open_questions"] = len(open_questions)
        llm_metadata["total_facts"] = sum(llm_metadata["facts_by_category"].values())

        # Handle tags: merge LLM-generated tags with rule-based tags
        llm_tags = llm_output_data.get("tags", {})
        complete_tags = build_complete_tags(llm_tags, categories, llm_output_data)
        llm_output_data["tags"] = complete_tags
        sentiment = complete_tags.get('sentiment', {})
        sentiment_str = f"{sentiment.get('overall', '?')} ({', '.join(sentiment.get('context', []))})" if isinstance(sentiment, dict) else str(sentiment)
        logging.info(f"Tags: themes={complete_tags.get('themes', [])}, sentiment={sentiment_str}, story_type={complete_tags.get('story_type', [])}")

    # Add metadata to output
    llm_output_data["_metadata"] = llm_metadata

    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    logging.info(f"Writing categorized fact briefing for '{log_date_context}' to: {args.output_file}")
    try:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            json.dump(llm_output_data, f, indent=2, ensure_ascii=True)
        logging.info(f"Successfully wrote categorized fact briefing to {args.output_file}.")

        if args.markdown_export_file and llm_output_data:
            logging.info(f"Also exporting Markdown to: {args.markdown_export_file}")
            try:
                markdown_content = convert_briefing_to_markdown(llm_output_data)
                args.markdown_export_file.parent.mkdir(parents=True, exist_ok=True)
                with open(args.markdown_export_file, 'w', encoding='utf-8') as md_f:
                    md_f.write(markdown_content)
                logging.info(f"Successfully wrote Markdown export to {args.markdown_export_file}.")
            except Exception as e_md:
                logging.error(f"Error writing Markdown export to {args.markdown_export_file}: {e_md}")

    except Exception as e:
        logging.error(f"Error writing categorized fact briefing JSON to {args.output_file}: {e}")
        sys.exit(1)
        
    logging.info("--- Fact extraction finished. ---")

if __name__ == "__main__":
    main() 
