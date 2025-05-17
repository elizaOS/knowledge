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

# Configuration
# HACKMD_OUTPUT_DIR = Path("hackmd") # No longer used
NEWS_SHOW_OUTPUT_DIR = Path("the-council") # Default parent for output if -o is just a filename, but -o allows full path
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_API_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
LLM_MODEL = "anthropic/claude-3.7-sonnet" # Or your preferred model, consider one with large context window
FACT_EXTRACTION_PROMPT_DIR = Path(__file__).parent
DEFAULT_FACT_EXTRACTION_PROMPT_FILE = FACT_EXTRACTION_PROMPT_DIR / "special-prompts" / "fact_extraction_prompt.txt"

# Logging configuration
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def load_prompt_template(prompt_file: Path) -> str | None:
    """Loads the prompt template from the specified file."""
    if not prompt_file.is_file():
        logging.error(f"Prompt file not found: {prompt_file}")
        return None
    try:
        return prompt_file.read_text()
    except Exception as e:
        logging.error(f"Could not read prompt file {prompt_file}: {e}")
        return None

def convert_briefing_to_markdown(briefing_data: dict) -> str:
    """Converts the structured JSON briefing data to a Markdown string."""
    md_lines = []
    date_str = briefing_data.get("briefing_date", "N/A")
    md_lines.append(f"# Fact Briefing: {date_str}\n")

    md_lines.append(f"## Overall Summary")
    md_lines.append(f"{briefing_data.get('overall_summary', 'No overall summary provided.')}\n")

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
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Verbose mode enabled.")

    if not OPENROUTER_API_KEY:
        logging.error("OPENROUTER_API_KEY environment variable not set.")
        sys.exit(1)

    if not args.input_file or not args.output_file:
        parser.error("-i/--input-file and -o/--output-file are required for LLM-based fact extraction (if not using -m).")

    prompt_template = load_prompt_template(args.prompt_file)
    if not prompt_template:
        sys.exit(1) # Error already logged by load_prompt_template

    target_date_str = args.date
    aggregated_data_json_string = ""
    try:
        # Load the entire JSON content as a string for the prompt
        aggregated_data_json_string = args.input_file.read_text(encoding='utf-8')
        # Validate if it's a valid JSON object by trying to parse it (but we pass the string to LLM)
        json.loads(aggregated_data_json_string) 
        logging.info(f"Successfully read and validated input data from {args.input_file}")
    except json.JSONDecodeError:
        logging.error(f"Error: Input file {args.input_file} does not contain valid JSON.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error reading input file {args.input_file}: {e}")
        sys.exit(1)

    if not target_date_str:
        match = re.search(r'(\d{4}-\d{2}-\d{2})', args.input_file.name)
        if match:
            try:
                datetime.strptime(match.group(1), "%Y-%m-%d")
                target_date_str = match.group(1)
                logging.info(f"Inferred date from input filename: {target_date_str}")
            except ValueError:
                logging.info("Could not parse date from filename pattern despite match.")
    
    log_date_context = target_date_str if target_date_str else args.input_file.name
    logging.info(f"Processing for context: '{log_date_context}'")

    # --- Markdown Generation Mode ---
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

    # --- LLM-Based Fact Extraction Mode (Original Logic) ---
    # These checks are now effectively duplicated by the parser.error above if to_markdown is not set, 
    # but kept for clarity or if logic changes.
    if not args.input_file or not args.output_file:
        parser.error("-i/--input-file and -o/--output-file are required for LLM-based fact extraction (if not using -m).")

    # --- Prepare LLM call ---
    final_llm_prompt = prompt_template.format(input_json_string=aggregated_data_json_string)
    
    logging.info(f"Sending context from '{args.input_file.name}' to LLM for fact extraction...")
    llm_payload = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": final_llm_prompt}],
        "response_format": {"type": "json_object"} # Request JSON output
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/elizaOS/knowledge", # Replace with your actual repo/app URL
        "X-Title": f"Fact Extraction ({log_date_context})"
    }

    # extracted_facts_list = [] # No longer a flat list
    llm_output_data = None # Will store the entire JSON object from LLM
    try:
        response = requests.post(OPENROUTER_API_ENDPOINT, headers=headers, json=llm_payload, timeout=300) # Increased timeout for potentially long processing
        response.raise_for_status()
        llm_response_data = response.json()
        
        content_str = llm_response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        if not content_str.strip():
            logging.error("LLM returned empty content.")
        else:
            try:
                parsed_content = json.loads(content_str)
                # Validate the new expected structure (has briefing_date, overall_summary, categories)
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

    if not llm_output_data:
        logging.warning("No valid categorized briefing was extracted. The output file might be incomplete or empty.")
        # Create a minimal error structure or empty dict if preferred
        llm_output_data = {
            "briefing_date": target_date_str or "unknown",
            "overall_summary": "Error: Failed to generate briefing.",
            "categories": {}
        }

    # --- Prepare Output ---
    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # output_structure = {"extracted_facts": extracted_facts_list} # Old structure
    logging.info(f"Writing categorized fact briefing for '{log_date_context}' to: {args.output_file}")
    try:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            json.dump(llm_output_data, f, indent=2) # Write the whole parsed object
        logging.info(f"Successfully wrote categorized fact briefing to {args.output_file}.")

        # --- Also export Markdown if requested ---
        if args.markdown_export_file and llm_output_data:
            logging.info(f"Also exporting Markdown to: {args.markdown_export_file}")
            try:
                markdown_content = convert_briefing_to_markdown(llm_output_data)
                args.markdown_export_file.parent.mkdir(parents=True, exist_ok=True)
                with open(args.markdown_export_file, 'w', encoding='utf-8') as md_f:
                    md_f.write(markdown_content)
                logging.info(f"Successfully wrote Markdown export to {args.markdown_export_file}.")
            except Exception as e_md: # Use a different exception variable name
                logging.error(f"Error writing Markdown export to {args.markdown_export_file}: {e_md}")
                # Decide if this should be a critical error or just a warning.
                # For now, it's just a logged error, primary JSON output was successful.

    except Exception as e:
        logging.error(f"Error writing categorized fact briefing JSON to {args.output_file}: {e}")
        sys.exit(1)
        
    logging.info("--- Fact extraction finished. ---")

if __name__ == "__main__":
    main() 
