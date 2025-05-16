#!/usr/bin/env python3

"""
Script to generate a JSON file containing aggregated content from relevant source files.
Usage: ./scripts/aggregate_sources.py [YYYY-MM-DD]
If no date is provided, defaults to the current date.
"""

import argparse
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union # For type hinting

# --- Configuration ---
# Using Path objects for easier manipulation
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent # Assumes script is in knowledge/scripts/
OUTPUT_DIR_BASE = WORKSPACE_ROOT / "the-council"
LOG_LEVEL = logging.INFO # Or logging.DEBUG for more verbose output

# Source File Paths (relative to WORKSPACE_ROOT)
AI_NEWS_ELIZAOS_JSON_DIR = WORKSPACE_ROOT / "ai-news/elizaos/json"
AI_NEWS_ELIZAOS_MD_DIR = WORKSPACE_ROOT / "ai-news/elizaos/md"
AI_NEWS_DISCORD_JSON_DIR = WORKSPACE_ROOT / "ai-news/elizaos/discord/json"
AI_NEWS_DISCORD_MD_DIR = WORKSPACE_ROOT / "ai-news/elizaos/discord/md"
AI_NEWS_DEV_JSON_DIR = WORKSPACE_ROOT / "ai-news/elizaos/dev/json"
AI_NEWS_DEV_MD_DIR = WORKSPACE_ROOT / "ai-news/elizaos/dev/md"

GITHUB_SUMMARIES_DAY_DIR = WORKSPACE_ROOT / "github/summaries/day"
GITHUB_SUMMARIES_WEEK_DIR = WORKSPACE_ROOT / "github/summaries/week"
GITHUB_SUMMARIES_MONTH_DIR = WORKSPACE_ROOT / "github/summaries/month"
GITHUB_STATS_MONTH_DIR = WORKSPACE_ROOT / "github/stats/month"
GITHUB_USER_SUMMARIES_FILE = WORKSPACE_ROOT / "github/user_summaries.ndjson"

# --- Logging Setup ---
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Helper Functions ---

def read_text_file(file_path: Path) -> Optional[str]:
    """Reads a text file and returns its content as a string."""
    if not file_path.is_file():
        logging.warning(f"Text file not found: {file_path}")
        return None
    try:
        return file_path.read_text(encoding='utf-8')
    except Exception as e:
        logging.error(f"Error reading text file {file_path}: {e}")
        return None

def read_json_file(file_path: Path) -> Optional[Union[Dict[str, Any], List[Any]]]:
    """Reads a JSON file and returns its parsed content."""
    if not file_path.is_file():
        logging.warning(f"JSON file not found: {file_path}")
        return None
    try:
        with file_path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON file {file_path}: {e}. Attempting to read as text.")
        # Fallback: return raw text if it can't be parsed as JSON, or an error marker
        try:
            # Return a dict that create_file_entry can understand as an error state if content is problematic
            return {"_error": "JSONDecodeError", "_raw_content": file_path.read_text(encoding='utf-8')}
        except Exception as read_e:
            logging.error(f"Could not even read {file_path} as text after JSON error: {read_e}")
            return {"_error": "ReadErrorAfterJSONDecodeError"}
    except Exception as e:
        logging.error(f"Error reading JSON file {file_path}: {e}")
        return None

def create_file_entry(file_path: Path, content_override: Optional[Union[str, Dict[str, Any], List[Any]]] = None) -> Dict[str, Any]:
    """
    Creates a dictionary entry for a file, including its name and content.
    If content_override is provided, it's used directly.
    Otherwise, reads the file. JSON files are parsed, others read as text.
    Returns an empty dict if the file path itself is invalid or an error occurs during reading.
    """
    filename = file_path.name
    if content_override is not None:
        return {"filename": filename, "content": content_override}

    if not file_path.is_file():
        logging.debug(f"File not found for entry creation: {file_path}")
        return {"filename": filename, "error": "File not found"} # Return error structure

    content: Any
    if file_path.suffix.lower() == ".json":
        content_data = read_json_file(file_path)
        if content_data is None: # Should ideally not happen if file_path.is_file() is true, but defensive
            return {"filename": filename, "error": "Failed to read JSON (None returned)"}
        # Check for our custom error structure from read_json_file
        if isinstance(content_data, dict) and "_error" in content_data:
            return {"filename": filename, "error": content_data["_error"], "raw_content": content_data.get("_raw_content")}
        content = content_data
    else:
        content = read_text_file(file_path)
        if content is None:
             return {"filename": filename, "error": "Failed to read text file"}
    
    return {"filename": filename, "content": content}


def get_specific_date_file_content(directory: Path, target_date: datetime.date, extension: str) -> Dict[str, Any]:
    """Gets content for a file named YYYY-MM-DD.ext in the given directory."""
    filename = f"{target_date.strftime('%Y-%m-%d')}.{extension.lstrip('.')}"
    file_path = directory / filename
    logging.debug(f"Attempting to get specific date file: {file_path}")
    return create_file_entry(file_path)

def get_latest_file_content(directory: Path) -> Dict[str, Any]:
    """Gets content for the most recent file (lexicographically) in a directory."""
    if not directory.is_dir():
        logging.warning(f"Directory not found for latest file: {directory}")
        return {"filename": str(directory), "error": "Directory not found"}
    
    files = sorted([f for f in directory.iterdir() if f.is_file()], reverse=True)
    if not files:
        logging.warning(f"No files found in directory: {directory}")
        return {"filename": str(directory), "error": "No files in directory"}
    
    latest_file_path = files[0]
    logging.debug(f"Attempting to get latest file: {latest_file_path} from {directory}")
    return create_file_entry(latest_file_path)

def get_recent_files_content(directory: Path, target_date: datetime.date, days: int, extension: str = "md") -> List[Dict[str, Any]]:
    """Gets content for files from the last N days with a specific extension."""
    if not directory.is_dir():
        logging.warning(f"Directory not found for recent files: {directory}")
        return []

    recent_files_data = []
    for i in range(days):
        current_date = target_date - timedelta(days=i)
        entry = get_specific_date_file_content(directory, current_date, extension)
        # Only add if it's not an empty dict or doesn't solely contain an error for file not found
        # (it will always have 'filename' from get_specific_date_file_content)
        if entry.get("error") != "File not found": # If other errors or success, include it.
             recent_files_data.append(entry)
        elif entry.get("content") is not None: # If somehow no error but content exists.
            recent_files_data.append(entry)

    # Sort by date, most recent first (filename will be YYYY-MM-DD.ext)
    return sorted(recent_files_data, key=lambda x: x.get("filename",""), reverse=True)

def extract_github_monthly_stats(directory: Path, target_year_month: str) -> str:
    """Extracts content of the stats_YYYY-MM.json file in the given directory."""
    file_name = f"stats_{target_year_month}.json"
    file_path = directory / file_name
    
    if not file_path.is_file():
        logging.warning(f"GitHub stats file not found: {file_path}")
        return ""
    
    logging.debug(f"Reading GitHub stats file: {file_path}")
    content = read_text_file(file_path) # Read as text
    
    return content if content else ""

def extract_user_summaries(ndjson_file: Path, target_date: datetime.date, days_to_include: int) -> str:
    """Extracts user summaries from the last N days from an NDJSON file."""
    if not ndjson_file.is_file():
        logging.warning(f"User summaries file not found: {ndjson_file}")
        return ""

    target_dates_str = set()
    for i in range(days_to_include):
        target_dates_str.add((target_date - timedelta(days=i)).strftime("%Y-%m-%d"))

    logging.info(f"Filtering user summaries for dates: {target_dates_str}")
    
    relevant_lines = []
    try:
        with ndjson_file.open('r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, 1):
                stripped_line = line.strip()
                if not stripped_line:  # Skip empty lines
                    continue
                try:
                    data = json.loads(stripped_line)
                    summary_date_str = None # This will store the YYYY-MM-DD string

                    if isinstance(data, list):
                        if len(data) > 3 and isinstance(data[3], str):
                            date_candidate = data[3]
                            try:
                                # Attempt ISO format first (e.g., YYYY-MM-DDTHH:MM:SSZ)
                                summary_date_str = datetime.fromisoformat(date_candidate.replace('Z', '+00:00')).strftime('%Y-%m-%d')
                            except ValueError:
                                # Attempt YYYY-MM-DD format next
                                try:
                                    datetime.strptime(date_candidate, '%Y-%m-%d') # Validate format
                                    summary_date_str = date_candidate # Already in correct string format
                                except ValueError:
                                    logging.debug(f"Date string at index 3 ('{date_candidate}') not in expected ISO or YYYY-MM-DD format in line {line_number}")
                        else:
                            logging.debug(f"Line {line_number} is a list but index 3 is not a suitable date string: {stripped_line}")
                    elif isinstance(data, dict):
                        # For dictionaries, try 'date' then 'Date' keys
                        date_val = data.get('date') or data.get('Date')
                        if isinstance(date_val, str):
                            try:
                                # Allow full ISO timestamps or just YYYY-MM-DD in dicts too
                                summary_date_str = datetime.fromisoformat(date_val.replace('Z', '+00:00')).strftime('%Y-%m-%d')
                            except ValueError:
                                try:
                                    datetime.strptime(date_val, '%Y-%m-%d') # Validate
                                    summary_date_str = date_val
                                except ValueError:
                                    logging.debug(f"Date string in dict ('{date_val}') not in expected ISO or YYYY-MM-DD format in line {line_number}")
                        elif date_val is not None:
                             logging.debug(f"Date value in dict is not a string: {date_val} in line {line_number}")
                    else:
                        logging.debug(f"Line {line_number} is not a list or dict: {stripped_line}")

                    if summary_date_str and summary_date_str in target_dates_str:
                        relevant_lines.append(stripped_line)
                except json.JSONDecodeError:
                    logging.debug(f"Skipping invalid JSON line in {ndjson_file.name} at line {line_number}: {stripped_line}")
                except Exception as e:
                    logging.warning(f"Error processing line {line_number} in {ndjson_file.name}: {stripped_line} - {e}")
    except IOError as e:
        logging.error(f"Error reading user summaries file {ndjson_file}: {e}")
        return ""
    
    logging.info(f"Extracted {len(relevant_lines)} user summaries.")
    return "\n".join(relevant_lines)

# --- End Helper Functions ---

def get_target_date(date_str_arg: str = None) -> datetime.date:
    """Determines the target date from argument or defaults to today."""
    if date_str_arg:
        try:
            return datetime.strptime(date_str_arg, "%Y-%m-%d").date()
        except ValueError:
            logging.error(f"Invalid date format: {date_str_arg}. Please use YYYY-MM-DD.")
            raise
    return datetime.today().date()

def main():
    parser = argparse.ArgumentParser(
        description="Aggregates content from various sources into a single JSON file for a target date."
    )
    parser.add_argument(
        "target_date_str",
        nargs="?",
        type=str,
        help="Optional target date in YYYY-MM-DD format. Defaults to today."
    )
    args = parser.parse_args()

    try:
        target_date = get_target_date(args.target_date_str)
    except ValueError:
        exit(1)

    target_date_str = target_date.strftime("%Y-%m-%d")
    target_year_month_str = target_date.strftime("%Y-%m")

    logging.info(f"Generating supreme context map for date: {target_date_str} (Month: {target_year_month_str})")

    output_file = OUTPUT_DIR_BASE / f"{target_date_str}.json"
    final_context = {"date_generated_for": target_date_str}

    # --- Data Aggregation Logic ---
    
    # Initialize structure
    final_context["ai_news"] = {"elizaos": {}}
    final_context["github"] = {"summaries": {}, "extracted_data": {}}

    # Populate using the new helper functions
    final_context["ai_news"]["elizaos"]["discord_md_last_3_days"] = get_recent_files_content(AI_NEWS_DISCORD_MD_DIR, target_date, 3, "md")
    final_context["ai_news"]["elizaos"]["dev_md_last_3_days"] = get_recent_files_content(AI_NEWS_DEV_MD_DIR, target_date, 3, "md")
    
    final_context["ai_news"]["elizaos"]["daily_elizaos_json"] = get_specific_date_file_content(AI_NEWS_ELIZAOS_JSON_DIR, target_date, "json")
    final_context["ai_news"]["elizaos"]["daily_elizaos_md"] = get_specific_date_file_content(AI_NEWS_ELIZAOS_MD_DIR, target_date, "md")
    final_context["ai_news"]["elizaos"]["daily_discord_json"] = get_specific_date_file_content(AI_NEWS_DISCORD_JSON_DIR, target_date, "json")
    final_context["ai_news"]["elizaos"]["daily_discord_md"] = get_specific_date_file_content(AI_NEWS_DISCORD_MD_DIR, target_date, "md")
    final_context["ai_news"]["elizaos"]["daily_dev_json"] = get_specific_date_file_content(AI_NEWS_DEV_JSON_DIR, target_date, "json")
    final_context["ai_news"]["elizaos"]["daily_dev_md"] = get_specific_date_file_content(AI_NEWS_DEV_MD_DIR, target_date, "md")

    final_context["github"]["summaries"]["daily"] = get_specific_date_file_content(GITHUB_SUMMARIES_DAY_DIR, target_date, "md")
    final_context["github"]["summaries"]["week"] = get_latest_file_content(GITHUB_SUMMARIES_WEEK_DIR)
    final_context["github"]["summaries"]["month"] = get_latest_file_content(GITHUB_SUMMARIES_MONTH_DIR)

    final_context["github"]["extracted_data"]["monthly_stats_text"] = extract_github_monthly_stats(GITHUB_STATS_MONTH_DIR, target_year_month_str)
    final_context["github"]["extracted_data"]["user_summaries_text"] = extract_user_summaries(GITHUB_USER_SUMMARIES_FILE, target_date, 7)

    # --- End Data Aggregation Logic ---

    # Ensure output directory exists
    OUTPUT_DIR_BASE.mkdir(parents=True, exist_ok=True)

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_context, f, indent=2, ensure_ascii=False)
        logging.info(f"Aggregated supreme context saved to: {output_file}")
    except IOError as e:
        logging.error(f"Error writing output file {output_file}: {e}")
        exit(1)

if __name__ == "__main__":
    main() 