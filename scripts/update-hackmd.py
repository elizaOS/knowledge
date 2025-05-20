#!/usr/bin/env python3
"""
Script to generate content based on prompts and update corresponding HackMD notes.
Reads state file, finds latest data, calls LLM for each prompt, 
updates note content and permissions via API.
Also updates the book index note and attempts to set content note permalinks.
"""

import argparse
import os
import sys
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
import requests
import time
import glob
import re

# --- Configuration ---
TEAM_PATH = "elizaos"
PROMPTS_DIR = Path("scripts/prompts")
STATE_FILE = Path("book.json")
DATA_DIR = Path("the-council/aggregated")
OUTPUT_DIR = Path("hackmd")
BOOK_MAP_KEY = "__BOOK_INDEX__"
LLM_MODEL = "anthropic/claude-3.7-sonnet"
API_BASE_URL = "https://api.hackmd.io/v1"

# Logging configuration
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# --- Helper Functions ---

def get_latest_md_file(markdown_files: list[Path]) -> Path | None:
    """
    Determines the latest markdown file to upload.
    Prioritizes YYYY-MM-DD.md files, then specific filenames (daily.md, etc.),
    then falls back to most recently modified.
    """
    if not markdown_files:
        return None

    date_pattern = re.compile(r"^\\d{4}-\\d{2}-\\d{2}$")
    dated_files = []
    other_files = []

    for f in markdown_files:
        if date_pattern.match(f.stem):
            dated_files.append(f)
        else:
            other_files.append(f)

    if dated_files:
        # If YYYY-MM-DD.md files exist, pick the latest among them by stem
        logging.debug(f"   Found dated files: {dated_files}. Picking max by stem.")
        return max(dated_files, key=lambda p: p.stem)
    elif other_files:
        # If no YYYY-MM-DD.md files, but other .md files exist
        # Prioritize 'daily.md', then 'index.md', then 'README.md' if they exist
        preferred_filenames = ["daily.md", "index.md", "README.md"]
        for preferred_name in preferred_filenames:
            for f_other in other_files:
                if f_other.name == preferred_name:
                    logging.info(f"   No YYYY-MM-DD files found. Using preferred file: {f_other}")
                    return f_other
        
        # If no preferred files, fallback to most recently modified of the 'other' files
        logging.info(f"   No YYYY-MM-DD or preferred files (daily.md, etc.) found. Using most recently modified of remaining files: {other_files}")
        return max(other_files, key=lambda p: p.stat().st_mtime)
    
    return None # Should not be reached if markdown_files is not empty initially

def get_api_token() -> str:
    """Retrieves the HackMD API token from environment variables."""
    token = os.getenv("HMD_API_ACCESS_TOKEN")
    if not token:
        token = os.getenv("HACKMD_API_TOKEN")
        if not token:
            logging.error("HMD_API_ACCESS_TOKEN or HACKMD_API_TOKEN environment variable not set.")
            sys.exit(1)
        else:
            logging.warning("Using fallback HACKMD_API_TOKEN env var.")
    return token

def get_clean_note_id(note_id_str: str | None) -> str | None:
    """Removes query parameters like ?view from a HackMD note ID string."""
    if not note_id_str:
        return None
    return note_id_str.split('?')[0]

def load_state() -> dict:
    """Loads the state from the JSON file."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
                logging.info(f"Loaded {len(state)} mappings from '{STATE_FILE}'.")
                return state
        except json.JSONDecodeError:
            logging.error(f"'{STATE_FILE}' is corrupted or empty. Cannot proceed.")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Error loading state file '{STATE_FILE}': {e}")
            sys.exit(1)
    else:
        logging.error(f"State file '{STATE_FILE}' not found. Cannot proceed.")
        sys.exit(1)

def make_api_request(endpoint: str, method: str = "GET", data: dict = None, headers: dict = None) -> tuple[int, dict | None]:
    """Makes an API request to HackMD."""
    token = get_api_token()
    default_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    if headers:
        default_headers.update(headers)

    url = f"{API_BASE_URL}{endpoint}"
    logging.debug(f"API Request: {method} {url} Payload: {json.dumps(data) if data else 'N/A'}")

    try:
        response = requests.request(method, url, headers=default_headers, json=data, timeout=60)
        response_data = None
        if response.text:
             try:
                 response_data = response.json()
             except json.JSONDecodeError:
                 if method == "PATCH" and response.status_code == 202 and "Accepted" in response.text:
                     logging.debug("PATCH request accepted (202), no JSON body.")
                 else:
                    logging.warning(f"API response for {method} {url} was not valid JSON. Status: {response.status_code}. Body: {response.text[:200]}...")
                 return response.status_code, None

        if not response.ok:
             logging.warning(f"API request failed: {method} {url} - Status: {response.status_code}")
             logging.warning(f"Response Body: {json.dumps(response_data) if response_data else response.text}")

        return response.status_code, response_data

    except requests.exceptions.Timeout:
        logging.error(f"Timeout error during API request: {method} {url}")
        return 408, None
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error during API request: {method} {url} - {e}")
        return 599, None
    except Exception as e:
        logging.error(f"Unexpected error during API request: {method} {url} - {e}")
        return 598, None

# Added back function and constants
BOOK_TITLE = "Eliza Daily"
HACKMD_BASE_URL = "https://hackmd.io"
CUSTOM_HEADER_LINKS_KEY = "CUSTOM_HEADER_LINKS" # New constant

def generate_book_markdown(note_map: dict, prompt_to_category: dict, link_mode: str = "view") -> str:
    """Generates the markdown content for the index book, grouped by category."""
    header_parts = [
        f"# {BOOK_TITLE}",
        f"<!-- Auto-generated index. Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} -->"
    ]

    custom_links_md = []
    if CUSTOM_HEADER_LINKS_KEY in note_map:
        custom_links_list = note_map.get(CUSTOM_HEADER_LINKS_KEY, [])
        if isinstance(custom_links_list, list): # Ensure it's a list
            for link_item in custom_links_list:
                if isinstance(link_item, dict) and "text" in link_item and "url" in link_item:
                    custom_links_md.append(f"- [{link_item['text']}]({link_item['url']})") # Custom links are used as-is
                else:
                    logging.warning(f"Malformed custom link item: {link_item}. Skipping.")
        else:
            logging.warning(f"'{CUSTOM_HEADER_LINKS_KEY}' in state is not a list. Skipping custom links.")
        if custom_links_md:
            header_parts.append("\n" + "\n".join(custom_links_md))

    header = "\n".join(header_parts) 
    content_sections = []
    category_to_notes = {}

    for prompt_name, config_val in note_map.items():
        if prompt_name == BOOK_MAP_KEY or prompt_name == CUSTOM_HEADER_LINKS_KEY:
            continue

        raw_note_id = None
        if isinstance(config_val, str):
            raw_note_id = config_val
        elif isinstance(config_val, dict):
            raw_note_id = config_val.get("id")

        clean_id_for_link = get_clean_note_id(raw_note_id)
        if not clean_id_for_link:
            logging.debug(f"Skipping note {prompt_name} in book generation due to missing or unparsable ID: {raw_note_id}.")
            continue
            
        category = prompt_to_category.get(prompt_name, "uncategorized")
        if category not in category_to_notes:
            category_to_notes[category] = []
        category_to_notes[category].append((prompt_name, clean_id_for_link)) 

    if not category_to_notes and not custom_links_md:
        return f"# {BOOK_TITLE}\n<!-- Auto-generated index. Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} -->"
    elif not category_to_notes and custom_links_md:
        return header

    sorted_categories = sorted(category_to_notes.keys())

    for category in sorted_categories:
        category_header_text = ' '.join(word.capitalize() for word in category.split('-'))
        category_section_parts = [f"## {category_header_text}"]
        links = []
        sorted_notes = sorted(category_to_notes[category], key=lambda item: item[0])
        for prompt_name, clean_id_for_url in sorted_notes: 
            display_title = ' '.join(word.capitalize() for word in prompt_name.split('-'))
            
            base_url = f"{HACKMD_BASE_URL}/{clean_id_for_url}"
            if link_mode == "view":
                url_suffix = "?view"
            elif link_mode == "edit":
                url_suffix = "?edit"
            elif link_mode == "both": # Example, could also be '?both' if HackMD supports it, or link to edit and mention view.
                url_suffix = "?both" # Assuming this is a valid HackMD parameter or for internal consistency.
                                      # Or,  f"- [{display_title} (View)]({base_url}?view) / [(Edit)]({base_url}?edit)" - more complex
            elif link_mode == "raw":
                url_suffix = ""
            else: # Default to view if mode is unrecognized
                url_suffix = "?view"
                logging.warning(f"Unrecognized link_mode '{link_mode}', defaulting to '?view'.")
            
            links.append(f"- [{display_title}]({base_url}{url_suffix})")
        category_section_parts.append("\n".join(links))
        content_sections.append("\n".join(category_section_parts))

    return header + "\n\n" + "\n\n".join(content_sections)

def aggregate_json_data(json_file: Path) -> str:
    """Reads a JSON file and aggregates all string values."""
    if not json_file.is_file():
        return ""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        strings = []
        def extract_strings(element):
            if isinstance(element, str):
                if element.lower() != 'null': # Exclude literal 'null' strings
                     strings.append(element)
            elif isinstance(element, list):
                for item in element:
                    extract_strings(item)
            elif isinstance(element, dict):
                for value in element.values():
                    extract_strings(value)
        
        extract_strings(data)
        filtered_strings = [s for s in strings if s]
        return "\n---\n".join(filtered_strings)
    except Exception as e:
        logging.error(f"Error reading or processing JSON file '{json_file}': {e}")
        return ""

def process_direct_file_uploads(state: dict, latest_date_str: str, team_path: str, output_dir: Path):
    """Processes items in CUSTOM_HEADER_LINKS for direct file uploads."""
    logging.info("--- Processing CUSTOM_HEADER_LINKS for direct file uploads ---")
    custom_links_config = state.get(CUSTOM_HEADER_LINKS_KEY, [])
    if not isinstance(custom_links_config, list):
        logging.warning(f"'{CUSTOM_HEADER_LINKS_KEY}' in state is not a list. Skipping direct file uploads.")
        return

    for link_item in custom_links_config:
        if not isinstance(link_item, dict):
            logging.warning(f"Skipping malformed item in CUSTOM_HEADER_LINKS (not a dict): {link_item}")
            continue

        source_dir_str = link_item.get("source_directory")
        link_url = link_item.get("url")
        link_text = link_item.get("text", "Untitled Link") 

        if source_dir_str and link_url:
            logging.info(f"-- Checking '{link_text}' for direct file upload from '{source_dir_str}'")
            
            raw_note_id_from_url = None
            try:
                raw_note_id_from_url = link_url.split('/')[-1]
                if not raw_note_id_from_url: 
                    raise ValueError("Extracted note ID part from URL is empty")
            except (IndexError, ValueError) as e:
                logging.error(f"   ERROR: Could not extract note ID part from URL '{link_url}' for '{link_text}'. Skipping. Error: {e}")
                continue
            
            api_note_id = get_clean_note_id(raw_note_id_from_url)
            if not api_note_id:
                logging.error(f"   ERROR: Could not obtain clean note ID from '{raw_note_id_from_url}' for '{link_text}'. Skipping.")
                continue

            source_dir = Path(source_dir_str)
            if not source_dir.is_dir():
                logging.warning(f"   WARNING: source_directory '{source_dir}' for '{link_text}' is not a valid directory. Skipping.")
                continue

            markdown_files = list(source_dir.glob("*.md"))
            if not markdown_files:
                logging.info(f"   INFO: No markdown files (*.md) found in '{source_dir}' for '{link_text}'. Skipping update.")
                continue

            latest_md_file = get_latest_md_file(markdown_files)
            if not latest_md_file:
                logging.warning(f"   WARNING: Could not determine latest file from non-empty list for '{link_text}' in '{source_dir}'. Skipping.")
                continue
            
            logging.info(f"   Found latest file to upload: {latest_md_file}")

            try:
                with open(latest_md_file, 'r', encoding='utf-8') as f:
                    file_content = f.read()
            except Exception as e:
                logging.error(f"   ERROR: Failed to read content from '{latest_md_file}': {e}. Skipping update.")
                continue
            
            hackmd_title = link_item.get("hackmd_note_title")
            if not hackmd_title:
                hackmd_title = ' '.join(word.capitalize() for word in latest_md_file.stem.split('-'))
            if not hackmd_title:
                 hackmd_title = ' '.join(word.capitalize() for word in link_text.split('-'))
            
            logging.info(f"   Attempting to update note {api_note_id} with content from '{latest_md_file}' and title '{hackmd_title}'...")
            update_payload = {"title": hackmd_title, "content": file_content}
            patch_status, _ = make_api_request(f"/teams/{team_path}/notes/{api_note_id}", method="PATCH", data=update_payload)

            if patch_status == 202:
                logging.info(f"   Successfully updated title and content for note {api_note_id} from '{latest_md_file}'.")
                logging.info("   Attempting to set permissions via API (Read: guest, Write: owner)...") # Changed from signed_in to owner
                perm_payload = {"readPermission": "guest", "writePermission": "owner"}
                perm_patch_status, _ = make_api_request(f"/teams/{team_path}/notes/{api_note_id}", method="PATCH", data=perm_payload)
                if perm_patch_status == 202:
                    logging.info(f"   Successfully set permissions for note {api_note_id}.")
                else:
                    logging.warning(f"   WARNING: API PATCH call failed for permissions setting (Status: {perm_patch_status}).")
            else:
                logging.error(f"   ERROR: API PATCH call failed for content update from file (Status: {patch_status}). Skipping permissions.")
            time.sleep(2)
        elif source_dir_str and not link_url:
            logging.warning(f"   Skipping '{link_text}': 'source_directory' provided but 'url' is missing.")
    logging.info("--- Finished processing CUSTOM_HEADER_LINKS for direct file uploads ---")

# --- Main Logic ---

def main():
    parser = argparse.ArgumentParser(description="Generate content from prompts and update HackMD notes.")
    parser.add_argument(
        "-d", "--date",
        help="Specify the date (YYYY-MM-DD) for data aggregation. Defaults to latest found."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Increase output verbosity (DEBUG level)."
    )
    parser.add_argument(
        "-j", "--json",
        action="store_true",
        help="Export JSON files in addition to Markdown. Defaults to False."
    )
    parser.add_argument(
        "--perms",
        action="store_true",
        help="Update permissions (read: guest, write: owner) for all HackMD notes listed in book.json. Skips all other processing."
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["view", "edit", "both", "raw"],
        default="view",
        help="Suffix mode for generated HackMD links in the book index (default: view)."
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    get_api_token() 

    if args.perms:
        logging.info("--- Mode: Update All Note Permissions ---")
        state = load_state()
        if not state:
            logging.error("State file is empty or failed to load. Cannot update permissions.")
            sys.exit(1)

        notes_to_update_perms = []
        for key, value in state.items():
            raw_note_id_val = None # This will hold the ID string that might have ?view etc.
            note_name_for_log = key

            if key == BOOK_MAP_KEY:
                raw_note_id_val = value
                note_name_for_log = "Book Index Page"
            elif key == CUSTOM_HEADER_LINKS_KEY:
                if isinstance(value, list):
                    for link_item in value:
                        if isinstance(link_item, dict) and "url" in link_item:
                            try:
                                # Extract the part that might be an ID from the URL
                                potential_id_part = link_item["url"].split('/')[-1]
                                clean_id = get_clean_note_id(potential_id_part)
                                if clean_id: # Ensure it's a valid ID after cleaning
                                    notes_to_update_perms.append({
                                        "id": clean_id, 
                                        "name": f"Custom Link: {link_item.get('text', clean_id)}"
                                    })
                                else:
                                    logging.debug(f"Custom link URL '{link_item['url']}' did not yield a clean ID part. Skipping for perms.")
                            except Exception as e:
                                logging.warning(f"Could not parse note ID from custom link URL '{link_item['url']}' for perms: {e}")
                continue 
            elif isinstance(value, str): 
                raw_note_id_val = value
            elif isinstance(value, dict): 
                raw_note_id_val = value.get("id")
            
            clean_api_id = get_clean_note_id(raw_note_id_val)
            if clean_api_id:
                notes_to_update_perms.append({"id": clean_api_id, "name": note_name_for_log})
            elif raw_note_id_val: # Log if original value was present but couldn't be cleaned
                 logging.warning(f"Could not obtain a clean API ID for '{note_name_for_log}' (raw value: {raw_note_id_val}). Skipping for perms.")


        if not notes_to_update_perms:
            logging.info("No notes found to update permissions for.")
        else:
            logging.info(f"Found {len(notes_to_update_perms)} notes to update permissions for.")
            perm_payload = {"readPermission": "guest", "writePermission": "owner"}
            for note_info in notes_to_update_perms:
                note_id_cleaned_for_api = note_info["id"] # Already cleaned
                note_name = note_info["name"]
                logging.info(f"Attempting to set permissions for note '{note_name}' (ID: {note_id_cleaned_for_api})...")
                perm_patch_status, _ = make_api_request(f"/teams/{TEAM_PATH}/notes/{note_id_cleaned_for_api}", method="PATCH", data=perm_payload)
                if perm_patch_status == 202:
                    logging.info(f"   Successfully set permissions for note '{note_name}' (ID: {note_id_cleaned_for_api}).")
                else:
                    logging.warning(f"   WARNING: API PATCH call failed for permissions setting on note '{note_name}' (ID: {note_id_cleaned_for_api}) (Status: {perm_patch_status}).")
                time.sleep(1) 
        
        logging.info("--- Finished updating all note permissions. ---")
        sys.exit(0)
    
    if not os.getenv("OPENROUTER_API_KEY"): 
        logging.error("OPENROUTER_API_KEY environment variable not set.")
        sys.exit(1)
    if not DATA_DIR.is_dir(): logging.error(f"Data dir not found: {DATA_DIR}"); sys.exit(1)
    if not PROMPTS_DIR.is_dir(): logging.error(f"Prompts dir not found: {PROMPTS_DIR}"); sys.exit(1)

    state = load_state() 
    if not state:
        logging.error("State file is empty or failed to load for full processing.")
        sys.exit(1)

    logging.info(f"Scanning '{PROMPTS_DIR}' to map prompts to categories...")
    prompt_to_category = {}
    for prompt_file in PROMPTS_DIR.rglob("*.txt"):
        prompt_name = prompt_file.stem
        relative_path = prompt_file.relative_to(PROMPTS_DIR)
        category_tag = relative_path.parent.name if relative_path.parent != Path('.') else "uncategorized"
        prompt_to_category[prompt_name] = category_tag
        logging.debug(f"Mapped prompt '{prompt_name}' to category '{category_tag}'")
    logging.info(f"Found {len(prompt_to_category)} prompts in category structure.")

    raw_book_note_id = state.get(BOOK_MAP_KEY)
    book_note_id_cleaned_api = get_clean_note_id(raw_book_note_id)

    if book_note_id_cleaned_api:
        logging.info(f"Attempting to update Book Index note (Clean ID: {book_note_id_cleaned_api}, Raw: {raw_book_note_id}) with latest content...")
        book_content = generate_book_markdown(state, prompt_to_category, args.mode) # Pass link_mode
        update_payload = {"content": book_content}
        patch_status_code, _ = make_api_request(f"/teams/{TEAM_PATH}/notes/{book_note_id_cleaned_api}", method="PATCH", data=update_payload)
        if patch_status_code == 202:
            logging.info(f"   Successfully updated Book Index note content.")
            logging.info(f"   Attempting to set permissions for Book Index note {book_note_id_cleaned_api} (Read: guest, Write: owner)...")
            perm_payload = {"readPermission": "guest", "writePermission": "owner"}
            perm_patch_status, _ = make_api_request(f"/teams/{TEAM_PATH}/notes/{book_note_id_cleaned_api}", method="PATCH", data=perm_payload)
            if perm_patch_status == 202:
                logging.info(f"   Successfully set permissions for Book Index note {book_note_id_cleaned_api}.")
            else:
                logging.warning(f"   WARNING: API PATCH call failed for Book Index note permissions setting (Status: {perm_patch_status}).")
        else:
            logging.warning(f"   WARNING: Failed to update Book Index note content (Status: {patch_status_code}). Skipping permissions update.")
        time.sleep(1)
    elif raw_book_note_id: # Log if raw_book_note_id was present but couldn't be cleaned
        logging.warning(f"Book index key '{BOOK_MAP_KEY}' had value '{raw_book_note_id}' which could not be cleaned to a valid ID. Skipping book update.")
    else:
        logging.warning(f"Book index key '{BOOK_MAP_KEY}' not found in state. Skipping book update.")

    latest_data_file = None
    if args.date:
        latest_data_file = DATA_DIR / f"{args.date}.json"
        if not latest_data_file.is_file():
            logging.error(f"Specified data file not found: {latest_data_file}")
            sys.exit(1)
        latest_date_str = args.date
        logging.info(f"Using specified data file: {latest_data_file}")
    else:
        logging.info(f"Finding latest daily data in {DATA_DIR}...")
        json_files = list(DATA_DIR.glob("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].json"))
        if not json_files:
            logging.error(f"No YYYY-MM-DD.json files found in {DATA_DIR}.")
            sys.exit(1)
        latest_data_file = max(json_files, key=lambda p: p.stem)
        latest_date_str = latest_data_file.stem
        logging.info(f"Using latest data file: {latest_data_file} (Date: {latest_date_str})")

    logging.info(f"Aggregating content from {latest_data_file}...")
    aggregated_content = aggregate_json_data(latest_data_file)
    if not aggregated_content:
        logging.warning(f"No text content extracted from {latest_data_file}. Some updates might be empty.")
    logging.info("Aggregated content prepared.")

    process_direct_file_uploads(state, latest_date_str, TEAM_PATH, OUTPUT_DIR)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    logging.info("Processing LLM prompts and updating HackMD notes...")

    for prompt_name, prompt_config_val in state.items():
        if prompt_name == BOOK_MAP_KEY or prompt_name == CUSTOM_HEADER_LINKS_KEY:
            logging.debug(f"Skipping special key: {prompt_name}")
            continue

        raw_note_id_from_config = None
        update_strategy = "append" 

        if isinstance(prompt_config_val, str): 
            raw_note_id_from_config = prompt_config_val
        elif isinstance(prompt_config_val, dict): 
            raw_note_id_from_config = prompt_config_val.get("id")
            update_strategy = prompt_config_val.get("update_strategy", "append").lower()
        
        api_note_id = get_clean_note_id(raw_note_id_from_config)
        if not api_note_id:
            logging.warning(f"Skipping item '{prompt_name}' due to missing or unparsable note ID in state file (raw: {raw_note_id_from_config}).")
            continue

        category_tag = prompt_to_category.get(prompt_name)

        if category_tag: 
            logging.info(f"-- Processing LLM prompt: {prompt_name} (API Note ID: {api_note_id}, Strategy: {update_strategy})")
            prompt_file_path = PROMPTS_DIR / category_tag / f"{prompt_name}.txt"

            if not prompt_file_path.is_file(): 
                logging.error(f"   ERROR: Prompt file '{prompt_file_path}' expected for '{prompt_name}' but not found. Skipping.")
                continue
            try:
                with open(prompt_file_path, 'r', encoding='utf-8') as f:
                    prompt_template = f.read()
            except Exception as e:
                logging.error(f"   ERROR: Failed to read prompt file '{prompt_file_path}': {e}")
                continue

            prompt_title_case = ' '.join(word.capitalize() for word in prompt_name.split('-'))
            prompt_instructions = (
                f"Generate content suitable for a '{prompt_title_case}' document for the date {latest_date_str}, "
                f"based on the provided aggregated data and the specific instructions in the template below.\n\n"
                f"Output *only* the main content as requested by the template. Do not include any other preamble or explanation "
                f"unless the template specifically asks for it within the main content part."
            )
            final_llm_prompt = f"{prompt_instructions}\n\n**Template Instructions:**\n{prompt_template}\n\n**Aggregated Data for {latest_date_str}:**\n```\n{aggregated_content}\n```"

            logging.info(f"   Calling LLM ({LLM_MODEL})...")
            llm_payload = {
                "model": LLM_MODEL,
                "messages": [{"role": "user", "content": final_llm_prompt}]
            }
            openrouter_headers = {
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/elizaOS/knowledge",
                "X-Title": f"Content Generator ({prompt_title_case})"
            }
            
            main_content_output = ""
            llm_data = None
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions", 
                    headers=openrouter_headers, 
                    json=llm_payload, 
                    timeout=180
                )
                response.raise_for_status()
                llm_data = response.json()
                main_content_output = llm_data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            except requests.exceptions.RequestException as e:
                logging.error(f"   ERROR: LLM API request failed: {e}")
                continue
            except Exception as e:
                 logging.error(f"   ERROR: Failed processing LLM response: {e}")
                 continue
                
            if not main_content_output:
                 logging.error(f"   ERROR: Main content from LLM is empty for '{prompt_name}'. Skipping update.")
                 if llm_data: logging.debug(f"   LLM Raw Response: {llm_data}")
                 continue
            logging.info("   LLM content generated and treated as main content.")

            prompt_output_dir = OUTPUT_DIR / category_tag / prompt_name
            prompt_output_dir.mkdir(parents=True, exist_ok=True)
            
            md_output_filename = prompt_output_dir / f"{latest_date_str}.md"
            logging.info(f"   Saving main generated content to {md_output_filename}...")
            try:
                with open(md_output_filename, 'w', encoding='utf-8') as f:
                    f.write(main_content_output)
                logging.info("   Main content saved locally to Markdown.")
            except Exception as e:
                 logging.error(f"   ERROR: Failed to save main content locally to {md_output_filename}: {e}")
            
            if args.json:
                json_output_filename = prompt_output_dir / f"{latest_date_str}.json"
                json_data_to_save = {
                    "prompt_name": prompt_name,
                    "category": category_tag,
                    "date": latest_date_str,
                    "generated_text": main_content_output,
                    "source_references": [aggregated_content]
                }
                logging.info(f"   Saving structured data to {json_output_filename} (JSON export enabled)...")
                try:
                    with open(json_output_filename, 'w', encoding='utf-8') as f:
                        json.dump(json_data_to_save, f, indent=2)
                    logging.info("   Structured data saved locally to JSON.")
                except Exception as e:
                    logging.error(f"   ERROR: Failed to save structured data locally to {json_output_filename}: {e}")
            else:
                logging.info("   JSON export disabled. Skipping JSON file saving.")

            new_hackmd_title = f"{prompt_title_case} - {latest_date_str}"
            details_block = f"<details><summary>Prompt Details ({prompt_name}.txt)</summary>\n\n```text\n{prompt_template}\n```\n\n</details>"
            updated_hackmd_content = f"{details_block}\n\n---\n\n{main_content_output}"
            
            update_payload = {"title": new_hackmd_title, "content": updated_hackmd_content}
            content_patch_status, _ = make_api_request(f"/teams/{TEAM_PATH}/notes/{api_note_id}", method="PATCH", data=update_payload)

            if content_patch_status == 202:
                logging.info(f"   Successfully updated title and content for note {api_note_id}.")
                logging.info("   Attempting to set permissions via API (Read: guest, Write: owner)...") # Changed from signed_in to owner
                perm_payload = {"readPermission": "guest", "writePermission": "owner"}
                perm_patch_status, _ = make_api_request(f"/teams/{TEAM_PATH}/notes/{api_note_id}", method="PATCH", data=perm_payload)
                if perm_patch_status == 202:
                    logging.info(f"   Successfully set permissions for note {api_note_id}.")
                else:
                     logging.warning(f"   WARNING: API PATCH call failed for permissions setting (Status: {perm_patch_status}).")
            else:
                logging.error(f"   ERROR: API PATCH call failed for content update (Status: {content_patch_status}). Skipping permissions.")

        else: # No prompt file found, this is where direct file upload from book.json top-level entries (non-CUSTOM_HEADER_LINKS) is handled.
            logging.info(f"-- No prompt for '{prompt_name}'. Checking for direct file source (API Note ID: {api_note_id}).")
            if not isinstance(prompt_config_val, dict):
                logging.warning(f"   Skipping '{prompt_name}': its configuration in book.json is not a dictionary, cannot check for 'source_directory'.")
                continue

            source_dir_path_str = prompt_config_val.get("source_directory")
            if source_dir_path_str:
                source_dir = Path(source_dir_path_str)
                if not source_dir.is_dir():
                    logging.warning(f"   WARNING: source_directory '{source_dir}' for '{prompt_name}' is not a valid directory. Skipping.")
                    continue

                markdown_files = list(source_dir.glob("*.md"))
                if not markdown_files:
                    logging.info(f"   INFO: No markdown files (*.md) found in '{source_dir}' for '{prompt_name}'. Skipping update.")
                    continue

                latest_md_file = get_latest_md_file(markdown_files)
                if not latest_md_file:
                    logging.warning(f"   WARNING: Could not determine latest file from non-empty list for '{prompt_name}' in '{source_dir}'. Skipping.")
                    continue
                
                logging.info(f"   Found latest file to upload: {latest_md_file}")

                try:
                    with open(latest_md_file, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                except Exception as e:
                    logging.error(f"   ERROR: Failed to read content from '{latest_md_file}': {e}. Skipping update.")
                    continue
                
                hackmd_title = prompt_config_val.get("title")
                if not hackmd_title:
                    hackmd_title = ' '.join(word.capitalize() for word in latest_md_file.stem.split('-'))
                if not hackmd_title: 
                    hackmd_title = ' '.join(word.capitalize() for word in prompt_name.split('-'))
                
                logging.info(f"   Attempting to update note {api_note_id} with content from '{latest_md_file}' and title '{hackmd_title}'...")
                update_payload = {"title": hackmd_title, "content": file_content}
                patch_status, _ = make_api_request(f"/teams/{TEAM_PATH}/notes/{api_note_id}", method="PATCH", data=update_payload)

                if patch_status == 202:
                    logging.info(f"   Successfully updated title and content for note {api_note_id} from '{latest_md_file}'.")
                    logging.info("   Attempting to set permissions via API (Read: guest, Write: owner)...") # Changed from signed_in to owner
                    perm_payload = {"readPermission": "guest", "writePermission": "owner"}
                    perm_patch_status, _ = make_api_request(f"/teams/{TEAM_PATH}/notes/{api_note_id}", method="PATCH", data=perm_payload)
                    if perm_patch_status == 202:
                        logging.info(f"   Successfully set permissions for note {api_note_id}.")
                    else:
                        logging.warning(f"   WARNING: API PATCH call failed for permissions setting (Status: {perm_patch_status}).")
                else:
                    logging.error(f"   ERROR: API PATCH call failed for content update from file (Status: {patch_status}). Skipping permissions.")
            else:
                logging.warning(f"   Skipping '{prompt_name}': No prompt file found and no 'source_directory' specified in its book.json configuration.")

        time.sleep(5) 

    logging.info("--- Script finished. ---")

if __name__ == "__main__":
    main() 