#!/usr/bin/env python3
"""
Processes an aggregated JSON context file (output from aggregate_sources.py),
recursively extracts text content, filters irrelevant data,
rephrases content using an LLM with a news anchor prompt,
and outputs a compiled JSON feed for the AI News Show.
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
LLM_MODEL = "anthropic/claude-3.7-sonnet" # Or your preferred model
NEWS_PROMPTS_DIR = Path(__file__).parent / "prompts" / "news_show"

# Keys to exclude from LLM processing at any depth
EXCLUDED_KEYS = ["date_generated_for", "filename", "sources", "url", "urls", "link", "links"]
# Add more keys if needed, e.g., "id", "timestamp", "user_id"

# Logging configuration
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def is_likely_url(text: str) -> bool:
    """Checks if a string is likely a URL."""
    if not text or not isinstance(text, str):
        return False
    # Simple check, can be made more sophisticated
    return text.startswith(("http://", "https://")) and " " not in text

def is_list_of_urls(data_list: list) -> bool:
    """Checks if a list consists predominantly of URLs."""
    if not data_list or not isinstance(data_list, list):
        return False
    url_count = sum(1 for item in data_list if isinstance(item, str) and is_likely_url(item))
    # Consider it a list of URLs if more than half are URLs and list is not very short
    return url_count > len(data_list) / 2 if len(data_list) > 0 else False

def flatten_and_extract_text(data: any, current_path: str = "", excluded_keys: list = None) -> list[tuple[str, str]]:
    """
    Recursively flattens the input data (dict or list) and extracts text content.
    Builds a path for each piece of text content to track its origin.
    Skips keys in excluded_keys and lists of URLs.
    """
    if excluded_keys is None:
        excluded_keys = []
    
    items_for_llm = []

    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{current_path}.{key}" if current_path else key
            if key.lower() in excluded_keys:
                logging.debug(f"Skipping excluded key: {new_path}")
                continue
            items_for_llm.extend(flatten_and_extract_text(value, new_path, excluded_keys))
    elif isinstance(data, list):
        if is_list_of_urls(data):
            logging.debug(f"Skipping list of URLs at path: {current_path or 'root list'}")
        else:
            for i, item in enumerate(data):
                # For items in a list, we might not want to append index to path unless necessary
                # or decide how to represent list items in the path.
                # For simplicity, let's pass the current_path to list items.
                # Consider if list items need unique paths or if their content is aggregated.
                # Current approach: if a list contains strings, they'll be associated with current_path.
                items_for_llm.extend(flatten_and_extract_text(item, current_path, excluded_keys))
    elif isinstance(data, str):
        if data.strip() and not is_likely_url(data): # Process non-empty strings that aren't just URLs
            items_for_llm.append((current_path, data.strip()))
        elif is_likely_url(data):
            logging.debug(f"Skipping string that is just a URL: {data} at path: {current_path}")

    return items_for_llm

def generate_type_from_path(path: str) -> str:
    """Generates a human-readable type string from a flattened path."""
    if not path:
        return "Generated General Update"
    # Replace underscores and dots with spaces, then title case
    parts = path.replace('_', ' ').replace('.', ' ').split()
    # Capitalize each part and join
    type_str = ' '.join(word.capitalize() for word in parts if word)
    return f"Generated {type_str} Update" if type_str else "Generated Update"

def main():
    parser = argparse.ArgumentParser(
        description="Process an aggregated JSON context file with a news anchor LLM."
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
        help="Full path for the output JSON file."
    )
    parser.add_argument(
        "-d", "--date",
        help="Optional: Specify the date (YYYY-MM-DD) for context/logging. If not provided, attempts to infer from input filename."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Increase output verbosity (DEBUG level)."
    )
    # --use-raw-source-references is removed
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

    # --- Determine Target Date for Logging ---
    target_date_str = args.date
    aggregated_data = {}
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            aggregated_data = json.load(f)
        if not isinstance(aggregated_data, dict):
            logging.error(f"Input file {args.input_file} does not contain a JSON object.")
            sys.exit(1)
        logging.info(f"Successfully read input data from {args.input_file}")
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from input file: {args.input_file}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error reading input file {args.input_file}: {e}")
        sys.exit(1)

    if not target_date_str: # Try to infer from filename if not provided
        # Regex to find YYYY-MM-DD in the filename
        match = re.search(r'(\d{4}-\d{2}-\d{2})', args.input_file.name)
        if match:
            try:
                datetime.strptime(match.group(1), "%Y-%m-%d") # Validate format
                target_date_str = match.group(1)
                logging.info(f"Inferred date from input filename: {target_date_str}")
            except ValueError:
                logging.info("Could not parse date from filename pattern despite match.")
    
    log_date_context = target_date_str if target_date_str else args.input_file.name
    logging.info(f"Processing for date context: '{log_date_context}'")

    # --- Flatten and Filter Data ---
    logging.info("Flattening and extracting text content from input data...")
    # Use lowercased EXCLUDED_KEYS for case-insensitive matching during flattening
    lower_excluded_keys = [key.lower() for key in EXCLUDED_KEYS]
    text_items_to_process = flatten_and_extract_text(aggregated_data, excluded_keys=lower_excluded_keys)
    
    if not text_items_to_process:
        logging.warning("No suitable text content found after flattening and filtering. Output will be empty.")
        # Write an empty list to the output file
        args.output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
        logging.info(f"Empty result written to {args.output_file}. Exiting.")
        sys.exit(0)

    logging.info(f"Found {len(text_items_to_process)} text items for LLM processing.")

    news_show_segments = []

    default_news_anchor_prompt_file = NEWS_PROMPTS_DIR / "default_anchor_prompt.txt"
    if not NEWS_PROMPTS_DIR.exists():
        logging.warning(f"News prompts directory not found: {NEWS_PROMPTS_DIR}.")
    elif not default_news_anchor_prompt_file.is_file() and aggregated_data:
        logging.warning(f"Default news anchor prompt '{default_news_anchor_prompt_file}' not found. LLM processing might be skipped if prompts aren't handled otherwise.")

    for source_path, input_for_llm in text_items_to_process:
        if not input_for_llm.strip():
            logging.warning(f"Input for LLM is empty for source path '{source_path}'. Skipping LLM processing for this item.")
            news_show_segments.append({
                "segment_id": f"data_source_{source_path}_skipped_empty_input",
                "anchor": "System",
                "type": "Skipped Segment (Empty Input)",
                "content": "Original content was empty or only whitespace.",
                "from_source": source_path
            })
            continue

        news_anchor_prompt_template = ""
        # TODO: Implement logic to select specific news anchor prompts based on source_path if needed
        # For now, always uses the default prompt.
        if default_news_anchor_prompt_file.is_file():
            try:
                news_anchor_prompt_template = default_news_anchor_prompt_file.read_text()
            except Exception as e:
                logging.error(f"Could not read default news anchor prompt {default_news_anchor_prompt_file}: {e}")
                news_show_segments.append({
                    "segment_id": f"data_source_{source_path}_raw_prompt_error",
                    "anchor": "System",
                    "type": "Raw Data Passthrough (Prompt Error)",
                    "content": input_for_llm,
                    "from_source": source_path
                })
                continue
        else:
            logging.info(f"No default news anchor prompt found. Passing through original text for '{source_path}'.")
            news_show_segments.append({
                "segment_id": f"data_source_{source_path}_raw_no_prompt",
                "anchor": "System",
                "type": "Raw Data Passthrough (No Prompt)",
                "content": input_for_llm,
                "from_source": source_path
            })
            continue
        
        # Using source_path as source_prompt_name for the template
        # Category is generic for now, derived from the first part of path if available
        category_for_prompt = source_path.split('.')[0] if '.' in source_path else "general_source"
        
        final_anchor_prompt = news_anchor_prompt_template.format(
            source_category=category_for_prompt,
            source_prompt_name=source_path, # Full path for detailed context in prompt if needed
            input_text=input_for_llm
        )

        logging.info(f"Processing source '{source_path}' with news anchor prompt...")
        
        llm_payload = {
            "model": LLM_MODEL,
            "messages": [{"role": "user", "content": final_anchor_prompt}]
        }
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/elizaOS/knowledge",
            "X-Title": f"News Show Segment Generator ({source_path})"
        }

        try:
            response = requests.post(OPENROUTER_API_ENDPOINT, headers=headers, json=llm_payload, timeout=180)
            response.raise_for_status()
            llm_response_data = response.json()
            anchor_output_content = llm_response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if not anchor_output_content.strip():
                logging.warning(f"LLM returned empty content for '{source_path}'. Using original input text.")
                anchor_output_content = input_for_llm
        except requests.exceptions.RequestException as e:
            logging.error(f"LLM API request failed for '{source_path}': {e}. Using original input text.")
            anchor_output_content = input_for_llm
        except Exception as e:
            logging.error(f"Error processing LLM response for '{source_path}': {e}. Using original input text.")
            anchor_output_content = input_for_llm

        segment_type = generate_type_from_path(source_path)
        news_show_segments.append({
            # "segment_id": f"data_source_{source_path.replace('.', '_')}_transformed", # Commented out
            # "anchor": "Generated Anchor", # Commented out
            "type": segment_type,
            "content": anchor_output_content,
            "from_source": source_path
        })

    # --- Prepare Output ---
    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    
    logging.info(f"Writing processed news show segments for '{log_date_context}' to: {args.output_file}")
    try:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            json.dump(news_show_segments, f, indent=2)
        logging.info(f"Successfully compiled {len(news_show_segments)} news segments into {args.output_file}.")
    except Exception as e:
        logging.error(f"Error writing compiled news show JSON to {args.output_file}: {e}")
        sys.exit(1)
        
    logging.info("--- News show feed generation finished. ---")

if __name__ == "__main__":
    main() 