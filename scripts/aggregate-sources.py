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
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR_BASE = WORKSPACE_ROOT / "the-council" / "aggregated"
LOG_LEVEL = logging.INFO

AI_NEWS_ELIZAOS_JSON_DIR = WORKSPACE_ROOT / "ai-news/elizaos/json"
AI_NEWS_ELIZAOS_MD_DIR = WORKSPACE_ROOT / "ai-news/elizaos/md"
AI_NEWS_ELIZAOS_DISCORD_JSON_DIR = WORKSPACE_ROOT / "ai-news/elizaos/discord/json"
AI_NEWS_ELIZAOS_DISCORD_MD_DIR = WORKSPACE_ROOT / "ai-news/elizaos/discord/md"
# AI_NEWS_ELIZAOS_DEV_JSON_DIR = WORKSPACE_ROOT / "ai-news/elizaos/dev/json"  # DEPRECATED: Directory no longer exists
# AI_NEWS_ELIZAOS_DEV_MD_DIR = WORKSPACE_ROOT / "ai-news/elizaos/dev/md"      # DEPRECATED: Directory no longer exists

AI_NEWS_HYPERFY_JSON_DIR = WORKSPACE_ROOT / "ai-news/hyperfy/json"
AI_NEWS_HYPERFY_MD_DIR = WORKSPACE_ROOT / "ai-news/hyperfy/md"

GITHUB_SUMMARIES_DAY_DIR = WORKSPACE_ROOT / "github/summaries/day"
GITHUB_SUMMARIES_WEEK_DIR = WORKSPACE_ROOT / "github/summaries/week"
GITHUB_SUMMARIES_MONTH_DIR = WORKSPACE_ROOT / "github/summaries/month"
GITHUB_STATS_MONTH_DIR = WORKSPACE_ROOT / "github/stats/month"
GITHUB_USER_SUMMARIES_FILE = WORKSPACE_ROOT / "github/user_summaries.ndjson"

AI_NEWS_SOURCES_CONFIG = {
    "elizaos_discord_md": {"dir": AI_NEWS_ELIZAOS_DISCORD_MD_DIR, "suffix": ".md", "days": 3, "is_json": False, "prefix": ""},
    # "elizaos_dev_md": {"dir": AI_NEWS_ELIZAOS_DEV_MD_DIR, "suffix": ".md", "days": 3, "is_json": False, "prefix": ""},  # DEPRECATED: Directory no longer exists
    "elizaos_daily_json": {"dir": AI_NEWS_ELIZAOS_JSON_DIR, "suffix": ".json", "is_json": True, "prefix": ""},
    "elizaos_daily_md": {"dir": AI_NEWS_ELIZAOS_MD_DIR, "suffix": ".md", "is_json": False, "prefix": ""},
    "elizaos_daily_discord_json": {"dir": AI_NEWS_ELIZAOS_DISCORD_JSON_DIR, "suffix": ".json", "is_json": True, "prefix": ""},
    "elizaos_daily_discord_md": {"dir": AI_NEWS_ELIZAOS_DISCORD_MD_DIR, "suffix": ".md", "is_json": False, "prefix": ""},
    # "elizaos_daily_dev_json": {"dir": AI_NEWS_ELIZAOS_DEV_JSON_DIR, "suffix": ".json", "is_json": True, "prefix": ""},    # DEPRECATED: Directory no longer exists
    # "elizaos_daily_dev_md": {"dir": AI_NEWS_ELIZAOS_DEV_MD_DIR, "suffix": ".md", "is_json": False, "prefix": ""},        # DEPRECATED: Directory no longer exists
    # Hyperfy sources temporarily disabled - data only available through 2025-07-03
    # "hyperfy_daily_json": {"dir": AI_NEWS_HYPERFY_JSON_DIR, "suffix": ".json", "is_json": True, "prefix": ""},
    # "hyperfy_daily_md": {"dir": AI_NEWS_HYPERFY_MD_DIR, "suffix": ".md", "is_json": False, "prefix": ""},
}

# --- Logging Setup ---
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Helper Functions ---

def read_text_file(file_path: Path) -> Optional[str]:
    if not file_path.is_file():
        logging.debug(f"Text file not found: {file_path}") # Changed to debug as it might be expected
        return None
    try:
        return file_path.read_text(encoding='utf-8')
    except Exception as e:
        logging.error(f"Error reading text file {file_path}: {e}")
        return None

def read_json_file(file_path: Path) -> Optional[Union[Dict[str, Any], List[Any]]]:
    if not file_path.is_file():
        logging.debug(f"JSON file not found: {file_path}") # Changed to debug
        return None
    try:
        with file_path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logging.warning(f"Error decoding JSON file {file_path}: {e}. Storing raw content.")
        try:
            return {"_error": "JSONDecodeError", "_raw_content": file_path.read_text(encoding='utf-8')}
        except Exception as read_e:
            logging.error(f"Could not even read {file_path} as text after JSON error: {read_e}")
            return {"_error": "ReadErrorAfterJSONDecodeError"}
    except Exception as e:
        logging.error(f"Error reading JSON file {file_path}: {e}")
        return None

def create_file_entry(file_path: Path, content_override: Optional[Union[str, Dict[str, Any], List[Any]]] = None) -> Dict[str, Any]:
    filename = file_path.name
    if content_override is not None:
        return {"filename": filename, "content": content_override}

    if not file_path.is_file():
        logging.debug(f"File not found for entry creation: {file_path}")
        return {"filename": filename, "error": "File not found"}

    content: Any
    if file_path.suffix.lower() == ".json":
        content = read_json_file(file_path)
        if content is None:
            return {"filename": filename, "error": "Failed to read JSON (None returned)"}
    else:
        content = read_text_file(file_path)
        if content is None:
             return {"filename": filename, "error": "Failed to read text file"}
    
    return {"filename": filename, "content": content}

def get_latest_file_entry(directory: Path) -> Optional[Dict[str, Any]]:
    if not directory.is_dir():
        logging.warning(f"Directory not found for latest file: {directory}")
        return None
    files = sorted([f for f in directory.iterdir() if f.is_file()], reverse=True)
    if not files:
        logging.warning(f"No files found in directory: {directory}")
        return None
    return create_file_entry(files[0])

def extract_github_monthly_stats(directory: Path, target_year_month: str) -> Optional[str]:
    file_name = f"stats_{target_year_month}.json"
    file_path = directory / file_name
    if not file_path.is_file():
        logging.warning(f"GitHub stats file not found: {file_path}")
        return None
    logging.debug(f"Reading GitHub stats file: {file_path}")
    return read_text_file(file_path)

def extract_user_summaries(ndjson_file: Path, target_date: datetime.date, days_to_include: int) -> Optional[str]:
    if not ndjson_file.is_file():
        logging.warning(f"User summaries file not found: {ndjson_file}")
        return None
    target_dates_str = { (target_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days_to_include) }
    logging.info(f"Filtering user summaries for dates: {target_dates_str}")
    relevant_lines = []
    try:
        with ndjson_file.open('r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, 1):
                stripped_line = line.strip()
                if not stripped_line: continue
                try:
                    data = json.loads(stripped_line)
                    summary_date_str = None
                    if isinstance(data, list) and len(data) > 3 and isinstance(data[3], str):
                        date_candidate = data[3]
                        try: summary_date_str = datetime.fromisoformat(date_candidate.replace('Z', '+00:00')).strftime('%Y-%m-%d')
                        except ValueError: 
                            try: 
                                datetime.strptime(date_candidate, '%Y-%m-%d'); summary_date_str = date_candidate
                            except ValueError: logging.debug(f"Date string at list index 3 ('{date_candidate}') unparseable in line {line_number}")
                    elif isinstance(data, dict):
                        date_val = data.get('date') or data.get('Date')
                        if isinstance(date_val, str):
                            try: summary_date_str = datetime.fromisoformat(date_val.replace('Z', '+00:00')).strftime('%Y-%m-%d')
                            except ValueError:
                                try: datetime.strptime(date_val, '%Y-%m-%d'); summary_date_str = date_val
                                except ValueError: logging.debug(f"Date string in dict ('{date_val}') unparseable in line {line_number}")
                    if summary_date_str and summary_date_str in target_dates_str:
                        relevant_lines.append(stripped_line)
                except json.JSONDecodeError: logging.debug(f"Skipping invalid JSON line {line_number} in {ndjson_file.name}")
                except Exception as e: logging.warning(f"Error processing line {line_number} in {ndjson_file.name}: {e}")
    except IOError as e:
        logging.error(f"Error reading user summaries file {ndjson_file}: {e}")
        return None
    logging.info(f"Extracted {len(relevant_lines)} user summaries.")
    return "\n".join(relevant_lines) if relevant_lines else None

def get_target_date(date_str_arg: str = None) -> datetime.date:
    if date_str_arg:
        try: return datetime.strptime(date_str_arg, "%Y-%m-%d").date()
        except ValueError: logging.error(f"Invalid date format: {date_str_arg}. Please use YYYY-MM-DD."); raise
    return datetime.today().date()

def main():
    parser = argparse.ArgumentParser(description="Aggregates content from various sources into a single JSON file.")
    parser.add_argument("target_date_str", nargs="?", type=str, help="Optional target date (YYYY-MM-DD). Defaults to today.")
    args = parser.parse_args()

    try: target_date = get_target_date(args.target_date_str)
    except ValueError: sys.exit(1)

    target_date_str = target_date.strftime("%Y-%m-%d")
    target_year_month_str = target_date.strftime("%Y-%m")
    logging.info(f"Generating aggregated context for date: {target_date_str}")

    final_context = {"date_generated_for": target_date_str}

    # AI News - Process based on config
    for name_prefix, config in AI_NEWS_SOURCES_CONFIG.items():
        source_dir = config["dir"]
        file_suffix = config["suffix"]
        is_json_content = config["is_json"]
        file_prefix_in_dir = config["prefix"]

        if "days" in config: # Handle multi-day sources (like _last_3_days)
            num_days = config["days"]
            for i in range(num_days):
                # AI News is fetched from previous days relative to the target_date of the report
                actual_file_date = target_date - timedelta(days=i + 1)
                actual_file_date_str = actual_file_date.strftime("%Y-%m-%d")
                file_path = source_dir / f"{file_prefix_in_dir}{actual_file_date_str}{file_suffix}"
                # Key in final_context should be unambiguous, including the actual date of the source file
                key = f"ai_news_{name_prefix}_{actual_file_date_str}"
                entry = create_file_entry(file_path)
                if entry and (entry.get("content") is not None or entry.get("error")):
                     final_context[key] = entry
        else: # Handle single-day sources (always T-1 for AI News)
            actual_file_date = target_date - timedelta(days=1)
            actual_file_date_str = actual_file_date.strftime("%Y-%m-%d")
            file_path = source_dir / f"{file_prefix_in_dir}{actual_file_date_str}{file_suffix}"
            key = f"ai_news_{name_prefix}_{actual_file_date_str}"
            entry = create_file_entry(file_path)
            if entry and (entry.get("content") is not None or entry.get("error")):
                final_context[key] = entry
    
    # GitHub Summaries - Daily (for target_date)
    gh_daily_path = GITHUB_SUMMARIES_DAY_DIR / f"{target_date_str}.md"
    entry = create_file_entry(gh_daily_path)
    if entry and (entry.get("content") is not None or entry.get("error")):
        final_context[f"github_summaries_daily_{target_date_str}"] = entry

    # GitHub Summaries - Week (latest)
    entry = get_latest_file_entry(GITHUB_SUMMARIES_WEEK_DIR)
    if entry and (entry.get("content") is not None or entry.get("error")):
        # Key includes filename to make it unique if multiple "latest" types exist
        final_context[f"github_summaries_week_latest_{entry['filename']}"] = entry 

    # GitHub Summaries - Month (latest)
    entry = get_latest_file_entry(GITHUB_SUMMARIES_MONTH_DIR)
    if entry and (entry.get("content") is not None or entry.get("error")):
        final_context[f"github_summaries_month_latest_{entry['filename']}"] = entry

    # GitHub Extracted Data
    monthly_stats_content = extract_github_monthly_stats(GITHUB_STATS_MONTH_DIR, target_year_month_str)
    if monthly_stats_content is not None:
        final_context[f"github_extracted_data_monthly_stats_text_{target_year_month_str}"] = monthly_stats_content
    
    user_summaries_content = extract_user_summaries(GITHUB_USER_SUMMARIES_FILE, target_date, 7)
    if user_summaries_content is not None:
        final_context[f"github_extracted_data_user_summaries_text_last_7_days_for_{target_date_str}"] = user_summaries_content

    OUTPUT_DIR_BASE.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR_BASE / f"{target_date_str}.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_context, f, indent=2, ensure_ascii=False)
        logging.info(f"Aggregated context saved to: {output_file}")
    except IOError as e:
        logging.error(f"Error writing output file {output_file}: {e}"); sys.exit(1)

if __name__ == "__main__":
    main() 