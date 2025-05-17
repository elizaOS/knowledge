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

def main():
    parser = argparse.ArgumentParser(
        description="Extract structured facts from an aggregated JSON context file using an LLM."
    )
    parser.add_argument(
        "-i", "--input-file",
        required=True,
        type=Path,
        help="Path to the input JSON file (output of aggregate_sources.py). Expected to be a JSON object."
    )
    parser.add_argument(
        "-o", "--output-file",
        required=True,
        type=Path,
        help="Full path for the output JSON file (e.g., the-council/fact_briefing_YYYY-MM-DD.json)."
    )
    parser.add_argument(
        "-d", "--date",
        help="Optional: Specify the date (YYYY-MM-DD) for context/logging. If not provided, attempts to infer from input filename."
    )
    parser.add_argument(
        "-p", "--prompt-file",
        type=Path,
        default=DEFAULT_FACT_EXTRACTION_PROMPT_FILE,
        help=f"Path to the fact extraction prompt file. Defaults to: {DEFAULT_FACT_EXTRACTION_PROMPT_FILE}"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Increase output verbosity (DEBUG level)."
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Verbose mode enabled.")

    if not OPENROUTER_API_KEY:
        logging.error("OPENROUTER_API_KEY environment variable not set.")
        sys.exit(1)

    if not args.input_file.is_file():
        logging.error(f"Input file not found: {args.input_file}")
        sys.exit(1)

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
    except Exception as e:
        logging.error(f"Error writing categorized fact briefing JSON to {args.output_file}: {e}")
        sys.exit(1)
        
    logging.info("--- Fact extraction finished. ---")

if __name__ == "__main__":
    main() 
