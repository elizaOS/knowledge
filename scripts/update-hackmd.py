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

def generate_book_markdown(note_map: dict, prompt_to_category: dict) -> str:
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
                    custom_links_md.append(f"- [{link_item['text']}]({link_item['url']})")
                else:
                    logging.warning(f"Malformed custom link item: {link_item}. Skipping.")
        else:
            logging.warning(f"'{CUSTOM_HEADER_LINKS_KEY}' in state is not a list. Skipping custom links.")
        if custom_links_md:
            # Join custom links with single newlines, then add a double newline before this block
            header_parts.append("\n" + "\n".join(custom_links_md))

    # Join title, timestamp, and custom links block. Title/timestamp joined by single newline.
    # Custom links block (if present) separated by a double newline from timestamp.
    header = "\n".join(header_parts) 
    # If custom_links_md was added, header_parts has 3 elements. 
    # The join above correctly handles newlines between title and timestamp, 
    # and the extra \n added before custom_links_md ensures the double newline after timestamp.

    content_sections = []

    # Group notes by category
    category_to_notes = {}
    for prompt_name, config_val in note_map.items(): # config_val can be str or dict
        if prompt_name == BOOK_MAP_KEY or prompt_name == CUSTOM_HEADER_LINKS_KEY: # Exclude special keys
            continue

        actual_note_id = None
        if isinstance(config_val, str): # Legacy: value is note_id string
            actual_note_id = config_val
        elif isinstance(config_val, dict): # New: value is dict with "id"
            actual_note_id = config_val.get("id")

        if not actual_note_id: # If ID couldn't be extracted, skip
            logging.debug(f"Skipping note {prompt_name} in book generation due to missing ID.")
            continue
            
        category = prompt_to_category.get(prompt_name, "uncategorized")
        if category not in category_to_notes:
            category_to_notes[category] = []
        category_to_notes[category].append((prompt_name, actual_note_id)) 

    if not category_to_notes and not custom_links_md:
        # If no categories and no custom links, just return the basic header (Title + Timestamp)
        return f"# {BOOK_TITLE}\n<!-- Auto-generated index. Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} -->"
    elif not category_to_notes and custom_links_md:
        # If custom links but no categories, return header with custom links
        return header # Header already includes custom links correctly formatted

    sorted_categories = sorted(category_to_notes.keys())

    for category in sorted_categories:
        category_header_text = ' '.join(word.capitalize() for word in category.split('-'))
        category_section_parts = [f"## {category_header_text}"]
        links = []
        sorted_notes = sorted(category_to_notes[category], key=lambda item: item[0])
        for prompt_name, id_for_url in sorted_notes: 
            display_title = ' '.join(word.capitalize() for word in prompt_name.split('-'))
            links.append(f"- [{display_title}]({HACKMD_BASE_URL}/{id_for_url})")
        category_section_parts.append("\n".join(links))
        content_sections.append("\n".join(category_section_parts)) # Join header and links with single newline

    # Join the main header (title, timestamp, custom links) with category sections.
    # Each category section is separated by a double newline.
    # A double newline is also ensured between custom links (if any) and the first category.
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
        # Filter empty strings after extraction and join
        filtered_strings = [s for s in strings if s]
        return "\n---\n".join(filtered_strings)
    except Exception as e:
        logging.error(f"Error reading or processing JSON file '{json_file}': {e}")
        return ""

# --- New Function for Direct File Uploads from CUSTOM_HEADER_LINKS ---
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
        link_text = link_item.get("text", "Untitled Link") # Fallback for link text

        if source_dir_str and link_url:
            logging.info(f"-- Checking '{link_text}' for direct file upload from '{source_dir_str}'")
            
            # Extract note ID from URL
            try:
                note_id = link_url.split('/')[-1]
                if not note_id: # Handle cases like trailing slash in URL
                    raise ValueError("Extracted note ID is empty")
            except (IndexError, ValueError) as e:
                logging.error(f"   ERROR: Could not extract note ID from URL '{link_url}' for '{link_text}'. Skipping. Error: {e}")
                continue

            source_dir = Path(source_dir_str)
            if not source_dir.is_dir():
                logging.warning(f"   WARNING: source_directory '{source_dir}' for '{link_text}' is not a valid directory. Skipping.")
                continue

            markdown_files = list(source_dir.glob("*.md"))
            if not markdown_files:
                logging.info(f"   INFO: No markdown files (*.md) found in '{source_dir}' for '{link_text}'. Skipping update.")
                continue

            latest_md_file = max(markdown_files, key=lambda p: p.stat().st_mtime)
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
            if not hackmd_title: # Fallback if filename is empty or unusual
                 hackmd_title = ' '.join(word.capitalize() for word in link_text.split('-')) # Use link_text as a further fallback
            
            logging.info(f"   Attempting to update note {note_id} with content from '{latest_md_file}' and title '{hackmd_title}'...")
            update_payload = {"title": hackmd_title, "content": file_content}
            patch_status, _ = make_api_request(f"/teams/{team_path}/notes/{note_id}", method="PATCH", data=update_payload)

            if patch_status == 202:
                logging.info(f"   Successfully updated title and content for note {note_id} from '{latest_md_file}'.")
                logging.info("   Attempting to set permissions via API (Read: guest, Write: signed_in)...")
                perm_payload = {"readPermission": "guest", "writePermission": "owner"}
                perm_patch_status, _ = make_api_request(f"/teams/{team_path}/notes/{note_id}", method="PATCH", data=perm_payload)
                if perm_patch_status == 202:
                    logging.info(f"   Successfully set permissions for note {note_id}.")
                else:
                    logging.warning(f"   WARNING: API PATCH call failed for permissions setting (Status: {perm_patch_status}).")
            else:
                logging.error(f"   ERROR: API PATCH call failed for content update from file (Status: {patch_status}). Skipping permissions.")
            time.sleep(2) # Short delay between these updates
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
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # --- Check HackMD Token (Needed for all modes that interact with API) ---
    get_api_token() 

    # --- Handle --update-all-note-permissions mode ---
    if args.perms:
        logging.info("--- Mode: Update All Note Permissions ---")
        state = load_state()
        if not state:
            logging.error("State file is empty or failed to load. Cannot update permissions.")
            sys.exit(1)

        notes_to_update_perms = []
        for key, value in state.items():
            note_id_to_check = None
            note_name_for_log = key

            if key == BOOK_MAP_KEY:
                note_id_to_check = value
                note_name_for_log = "Book Index Page"
            elif key == CUSTOM_HEADER_LINKS_KEY:
                if isinstance(value, list):
                    for link_item in value:
                        if isinstance(link_item, dict) and "url" in link_item:
                            try:
                                extracted_id = link_item["url"].split('/')[-1]
                                if extracted_id: # Make sure it's not an empty string
                                    notes_to_update_perms.append({
                                        "id": extracted_id, 
                                        "name": f"Custom Link: {link_item.get('text', extracted_id)}"
                                    })
                            except Exception as e:
                                logging.warning(f"Could not parse note ID from custom link URL '{link_item['url']}': {e}")
                continue # Skip further processing of the CUSTOM_HEADER_LINKS_KEY itself
            elif isinstance(value, str): # Legacy format (value is note_id string)
                note_id_to_check = value
            elif isinstance(value, dict): # New format (value is dict with "id")
                note_id_to_check = value.get("id")
            
            if note_id_to_check:
                notes_to_update_perms.append({"id": note_id_to_check, "name": note_name_for_log})

        if not notes_to_update_perms:
            logging.info("No notes found to update permissions for.")
        else:
            logging.info(f"Found {len(notes_to_update_perms)} notes to update permissions for.")
            perm_payload = {"readPermission": "guest", "writePermission": "owner"}
            for note_info in notes_to_update_perms:
                note_id = note_info["id"]
                note_name = note_info["name"]
                logging.info(f"Attempting to set permissions for note '{note_name}' (ID: {note_id})...")
                perm_patch_status, _ = make_api_request(f"/teams/{TEAM_PATH}/notes/{note_id}", method="PATCH", data=perm_payload)
                if perm_patch_status == 202:
                    logging.info(f"   Successfully set permissions for note '{note_name}' (ID: {note_id}).")
                else:
                    logging.warning(f"   WARNING: API PATCH call failed for permissions setting on note '{note_name}' (ID: {note_id}) (Status: {perm_patch_status}).")
                time.sleep(1) # API rate limiting
        
        logging.info("--- Finished updating all note permissions. ---")
        sys.exit(0)

    # --- Full Processing Mode (if --update-all-note-permissions is not set) ---
    
    # --- Check Prerequisites (for full mode) ---
    if not os.getenv("OPENROUTER_API_KEY"): # Only check if not in permissions-only mode
        logging.error("OPENROUTER_API_KEY environment variable not set.")
        sys.exit(1)
    # get_api_token() # Already called
    if not DATA_DIR.is_dir(): logging.error(f"Data dir not found: {DATA_DIR}"); sys.exit(1)
    if not PROMPTS_DIR.is_dir(): logging.error(f"Prompts dir not found: {PROMPTS_DIR}"); sys.exit(1)

    # --- Load State (already loaded if in permissions mode, but safe to call again or ensure it's loaded) ---
    state = load_state() # Ensure state is loaded if not in perm-only mode path
    if not state:
        logging.error("State file is empty or failed to load for full processing.")
        sys.exit(1)

    # --- Build Prompt-to-Category Mapping (Moved Before Book Update) ---
    logging.info(f"Scanning '{PROMPTS_DIR}' to map prompts to categories...")
    prompt_to_category = {}
    for prompt_file in PROMPTS_DIR.rglob("*.txt"):
        prompt_name = prompt_file.stem
        relative_path = prompt_file.relative_to(PROMPTS_DIR)
        category_tag = relative_path.parent.name if relative_path.parent != Path('.') else "uncategorized"
        prompt_to_category[prompt_name] = category_tag
        logging.debug(f"Mapped prompt '{prompt_name}' to category '{category_tag}'")
    logging.info(f"Found {len(prompt_to_category)} prompts in category structure.")

    # --- Update Book Index First ---
    book_note_id = state.get(BOOK_MAP_KEY)
    if book_note_id:
        logging.info(f"Attempting to update Book Index note (ID: {book_note_id}) with latest content...")
        book_content = generate_book_markdown(state, prompt_to_category)
        update_payload = {"content": book_content}
        patch_status_code, _ = make_api_request(f"/teams/{TEAM_PATH}/notes/{book_note_id}", method="PATCH", data=update_payload)
        if patch_status_code == 202:
            logging.info(f"   Successfully updated Book Index note content.")
            # Now, set permissions for the Book Index note
            logging.info(f"   Attempting to set permissions for Book Index note {book_note_id} (Read: guest, Write: owner)...")
            perm_payload = {"readPermission": "guest", "writePermission": "owner"}
            perm_patch_status, _ = make_api_request(f"/teams/{TEAM_PATH}/notes/{book_note_id}", method="PATCH", data=perm_payload)
            if perm_patch_status == 202:
                logging.info(f"   Successfully set permissions for Book Index note {book_note_id}.")
            else:
                logging.warning(f"   WARNING: API PATCH call failed for Book Index note permissions setting (Status: {perm_patch_status}).")
        else:
            logging.warning(f"   WARNING: Failed to update Book Index note content (Status: {patch_status_code}). Skipping permissions update.")
        time.sleep(1)
    else:
        logging.warning(f"Book index key '{BOOK_MAP_KEY}' not found in state. Skipping book update.")

    # --- Find and Aggregate Data (Moved earlier to define latest_date_str) ---
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
        latest_data_file = max(json_files, key=lambda p: p.stat().st_mtime)
        latest_date_str = latest_data_file.stem
        logging.info(f"Using latest data file: {latest_data_file} (Date: {latest_date_str})")

    logging.info(f"Aggregating content from {latest_data_file}...")
    aggregated_content = aggregate_json_data(latest_data_file)
    if not aggregated_content:
        logging.warning(f"No text content extracted from {latest_data_file}. Some updates might be empty.")
    logging.info("Aggregated content prepared.")

    # --- Process Direct File Uploads from CUSTOM_HEADER_LINKS (Now latest_date_str is defined) ---
    process_direct_file_uploads(state, latest_date_str, TEAM_PATH, OUTPUT_DIR)

    # --- Create Output Directory (Ensure it exists before LLM processing saves files there) ---
    logging.info(f"Ensuring base output directory '{OUTPUT_DIR}' exists...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- Process Prompts and Update Notes (LLM-based) ---
    logging.info("Processing LLM prompts and updating HackMD notes...")

    for prompt_name, prompt_config_val in state.items():
        # Explicitly skip special keys that are not individual notes for LLM processing or direct upload
        if prompt_name == BOOK_MAP_KEY or prompt_name == CUSTOM_HEADER_LINKS_KEY:
            logging.debug(f"Skipping special key: {prompt_name}")
            continue

        note_id = None
        update_strategy = "append" # Default for LLM, direct upload usually overwrites content & title

        if isinstance(prompt_config_val, str): # Legacy format (note_id is a string)
            note_id = prompt_config_val
        elif isinstance(prompt_config_val, dict): # New format
            note_id = prompt_config_val.get("id")
            update_strategy = prompt_config_val.get("update_strategy", "append").lower()
        
        if not note_id: # Skip if note_id is somehow empty/null
            logging.warning(f"Skipping item '{prompt_name}' due to missing note ID in state file config.")
            continue

        # Check if a prompt file exists for this item
        category_tag = prompt_to_category.get(prompt_name)

        if category_tag: # Prompt exists, use LLM generation path
            logging.info(f"-- Processing LLM prompt: {prompt_name} (Note ID: {note_id}, Strategy: {update_strategy})")
            prompt_file_path = PROMPTS_DIR / category_tag / f"{prompt_name}.txt"

            if not prompt_file_path.is_file(): # Should not happen if category_tag is found from prompt_to_category map
                logging.error(f"   ERROR: Prompt file '{prompt_file_path}' expected for '{prompt_name}' but not found. Skipping.")
                continue

            # --- Generate LLM Content (Existing Logic) ---
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

            # --- Save Generated Content Locally (Markdown and JSON) ---
            # Category_tag is already known from prompt_to_category map
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
            content_patch_status, _ = make_api_request(f"/teams/{TEAM_PATH}/notes/{note_id}", method="PATCH", data=update_payload)

            if content_patch_status == 202:
                logging.info(f"   Successfully updated title and content for note {note_id}.")
                logging.info("   Attempting to set permissions via API (Read: guest, Write: signed_in)...")
                perm_payload = {"readPermission": "guest", "writePermission": "signed_in"}
                perm_patch_status, _ = make_api_request(f"/teams/{TEAM_PATH}/notes/{note_id}", method="PATCH", data=perm_payload)
                if perm_patch_status == 202:
                    logging.info(f"   Successfully set permissions for note {note_id}.")
                else:
                     logging.warning(f"   WARNING: API PATCH call failed for permissions setting (Status: {perm_patch_status}).")
            else:
                logging.error(f"   ERROR: API PATCH call failed for content update (Status: {content_patch_status}). Skipping permissions.")

        else: # No prompt file found, try direct file upload from source_directory
            logging.info(f"-- No prompt for '{prompt_name}'. Checking for direct file source (Note ID: {note_id}).")
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

                latest_md_file = max(markdown_files, key=lambda p: p.stat().st_mtime)
                logging.info(f"   Found latest file to upload: {latest_md_file}")

                try:
                    with open(latest_md_file, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                except Exception as e:
                    logging.error(f"   ERROR: Failed to read content from '{latest_md_file}': {e}. Skipping update.")
                    continue
                
                # Determine title for HackMD note
                # Priority: 1. title from book.json, 2. Capitalized filename stem, 3. Capitalized prompt_name
                hackmd_title = prompt_config_val.get("title")
                if not hackmd_title:
                    hackmd_title = ' '.join(word.capitalize() for word in latest_md_file.stem.split('-'))
                if not hackmd_title: # Fallback if filename is empty or unusual
                    hackmd_title = ' '.join(word.capitalize() for word in prompt_name.split('-'))
                
                logging.info(f"   Attempting to update note {note_id} with content from '{latest_md_file}' and title '{hackmd_title}'...")
                update_payload = {"title": hackmd_title, "content": file_content}
                patch_status, _ = make_api_request(f"/teams/{TEAM_PATH}/notes/{note_id}", method="PATCH", data=update_payload)

                if patch_status == 202:
                    logging.info(f"   Successfully updated title and content for note {note_id} from '{latest_md_file}'.")
                    # Set permissions, similar to LLM notes
                    logging.info("   Attempting to set permissions via API (Read: guest, Write: signed_in)...")
                    perm_payload = {"readPermission": "guest", "writePermission": "signed_in"}
                    perm_patch_status, _ = make_api_request(f"/teams/{TEAM_PATH}/notes/{note_id}", method="PATCH", data=perm_payload)
                    if perm_patch_status == 202:
                        logging.info(f"   Successfully set permissions for note {note_id}.")
                    else:
                        logging.warning(f"   WARNING: API PATCH call failed for permissions setting (Status: {perm_patch_status}).")
                else:
                    logging.error(f"   ERROR: API PATCH call failed for content update from file (Status: {patch_status}). Skipping permissions.")
            else:
                logging.warning(f"   Skipping '{prompt_name}': No prompt file found and no 'source_directory' specified in its book.json configuration.")

        time.sleep(5) # Increased delay between notes

    logging.info("--- Script finished. ---")

if __name__ == "__main__":
    main() 