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
DATA_DIR = Path("the-council")
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

def generate_book_markdown(note_map: dict, prompt_to_category: dict) -> str:
    """Generates the markdown content for the index book, grouped by category."""
    header = f"# {BOOK_TITLE}\n\n<!-- Auto-generated index. Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} -->\n\n"
    content_sections = []

    # Group notes by category
    category_to_notes = {}
    for prompt_name, note_id in note_map.items():
        if prompt_name == BOOK_MAP_KEY or not note_id:
            continue
        # Use the map passed from main to find the category
        category = prompt_to_category.get(prompt_name, "uncategorized")
        if category not in category_to_notes:
            category_to_notes[category] = []
        category_to_notes[category].append((prompt_name, note_id))

    if not category_to_notes:
        return header + "*No content notes found in state file yet.*"

    # Sort categories alphabetically
    sorted_categories = sorted(category_to_notes.keys())

    for category in sorted_categories:
        # Create a capitalized H2 header for the category
        category_header = f"## {' '.join(word.capitalize() for word in category.split('-'))}\n"
        links = []
        # Sort notes alphabetically by prompt name within the category
        sorted_notes = sorted(category_to_notes[category], key=lambda item: item[0])
        for prompt_name, note_id in sorted_notes:
            display_title = ' '.join(word.capitalize() for word in prompt_name.split('-'))
            links.append(f"- [{display_title}]({HACKMD_BASE_URL}/{note_id})")
        content_sections.append(category_header + "\n".join(links))

    # Join category sections with double newlines
    return header + "\n\n".join(content_sections)

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
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # --- Check Prerequisites ---
    if not os.getenv("OPENROUTER_API_KEY"):
        logging.error("OPENROUTER_API_KEY environment variable not set.")
        sys.exit(1)
    get_api_token() # Check HackMD token early
    if not DATA_DIR.is_dir(): logging.error(f"Data dir not found: {DATA_DIR}"); sys.exit(1)
    if not PROMPTS_DIR.is_dir(): logging.error(f"Prompts dir not found: {PROMPTS_DIR}"); sys.exit(1)

    # --- Load State ---
    state = load_state()
    if not state:
        logging.error("State file is empty or failed to load.")
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
        logging.info(f"Attempting to update Book Index note (ID: {book_note_id}) with TEST content...")
        # book_content = generate_book_markdown(state) # Skip generating complex content for now
        test_content = "# Eliza Daily\n\nTest Update - $(date)"
        update_payload = {"content": test_content}
        patch_status_code, _ = make_api_request(f"/teams/{TEAM_PATH}/notes/{book_note_id}", method="PATCH", data=update_payload)
        if patch_status_code == 202:
            logging.info(f"   Successfully updated Book Index note content WITH TEST STRING.")
            # Now, immediately try with the real content (if the test worked)
            logging.info(f"   Attempting to update Book Index note with REAL content...")
            real_book_content = generate_book_markdown(state, prompt_to_category)
            real_update_payload = {"content": real_book_content}
            real_patch_status_code, _ = make_api_request(f"/teams/{TEAM_PATH}/notes/{book_note_id}", method="PATCH", data=real_update_payload)
            if real_patch_status_code == 202:
                logging.info(f"   Successfully updated Book Index note content with REAL content.")
            else:
                logging.warning(f"   WARNING: Failed to update Book Index note with REAL content (Status: {real_patch_status_code}). It might contain only the test string.")
        else:
            logging.warning(f"   WARNING: Failed to update Book Index note content EVEN WITH TEST STRING (Status: {patch_status_code}).")
        time.sleep(1) # Add delay after book update attempts
    else:
        logging.warning(f"Book index key '{BOOK_MAP_KEY}' not found in state. Skipping book update.")

    # --- Find and Aggregate Data ---
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

    # --- Create Output Directory ---
    logging.info(f"Ensuring base output directory '{OUTPUT_DIR}' exists...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- Process Prompts and Update Notes ---
    logging.info("Processing prompts and updating HackMD notes...")

    for prompt_name, note_id in state.items():
        if prompt_name == BOOK_MAP_KEY:
            logging.debug(f"Skipping book index key: {prompt_name}")
            continue

        if not note_id: # Skip if note_id is somehow empty/null
            logging.warning(f"Skipping prompt '{prompt_name}' due to missing note ID in state file.")
            continue

        logging.info(f"-- Processing: {prompt_name} (Note ID: {note_id})")
        # Get category for prompt path
        category_tag = prompt_to_category.get(prompt_name, None) # Get category from map
        if not category_tag:
            logging.error(f"   ERROR: Category not found for prompt '{prompt_name}' in mapping. Skipping.")
            continue

        # Construct the correct path using the category
        prompt_file_path = PROMPTS_DIR / category_tag / f"{prompt_name}.txt"

        if not prompt_file_path.is_file():
            logging.error(f"   ERROR: Prompt file '{prompt_file_path}' not found. Skipping.")
            continue

        # --- Generate LLM Content ---
        try:
            with open(prompt_file_path, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
        except Exception as e:
            logging.error(f"   ERROR: Failed to read prompt file '{prompt_file_path}': {e}")
            continue

        prompt_title_case = ' '.join(word.capitalize() for word in prompt_name.split('-'))
        prompt_instructions = f"Generate content suitable for a '{prompt_title_case}' document for the date {latest_date_str}, based on the provided aggregated data and the specific instructions in the template below. Output *only* the content requested by the template, without any preamble or extra formatting unless the template asks for it."
        final_llm_prompt = f"{prompt_instructions}\n\n**Template Instructions:**\n{prompt_template}\n\n**Aggregated Data for {latest_date_str}:**\n```\n{aggregated_content}\n```"

        logging.info(f"   Calling LLM ({LLM_MODEL})...")
        llm_payload = {
            "model": LLM_MODEL,
            "messages": [{"role": "user", "content": final_llm_prompt}]
        }
        openrouter_headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/elizaOS/knowledge", # Replace with your actual site/app URL
            "X-Title": f"Content Generator ({prompt_title_case})" # Optional
        }
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions", 
                headers=openrouter_headers, 
                json=llm_payload, 
                timeout=180 # Longer timeout for LLM
            )
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            llm_data = response.json()
            llm_content = llm_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        except requests.exceptions.RequestException as e:
            logging.error(f"   ERROR: LLM API request failed: {e}")
            continue
        except Exception as e:
             logging.error(f"   ERROR: Failed processing LLM response: {e}")
             continue

        if not llm_content:
            logging.error(f"   ERROR: Failed to generate content from LLM for '{prompt_name}'. Skipping update.")
            logging.debug(f"   LLM Raw Response: {llm_data}") # Log raw response if content is empty
            continue
        logging.info("   LLM content generated.")

        # --- Save Generated Content Locally ---
        # Get category for output path
        category_tag = prompt_to_category.get(prompt_name, "uncategorized") # Default if prompt somehow not found in scan
        prompt_output_dir = OUTPUT_DIR / category_tag / prompt_name
        prompt_output_dir.mkdir(parents=True, exist_ok=True)
        output_filename = prompt_output_dir / f"{latest_date_str}.md"
        logging.info(f"   Saving generated content to {output_filename}...")
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(llm_content)
            logging.info("   Content saved locally.")
        except Exception as e:
             logging.error(f"   ERROR: Failed to save content locally to {output_filename}: {e}")
             continue # Skip API update if we couldn't save locally

        # --- Get Current HackMD Note Content ---
        logging.info(f"   Fetching current content for note {note_id}...")
        get_status_code, get_response_data = make_api_request(f"/teams/{TEAM_PATH}/notes/{note_id}", method="GET")
        current_hackmd_content = ""
        if get_status_code == 200 and get_response_data:
            current_hackmd_content = get_response_data.get("content", "")
            logging.info(f"   Successfully fetched current content (length: {len(current_hackmd_content)}).")
        else:
            logging.warning(f"   WARNING: Failed to fetch current content for note {note_id} (Status: {get_status_code}). Will overwrite instead of appending.")
            # Proceeding will overwrite the note if PATCH succeeds

        # Log content being sent
        logging.debug(f"   DEBUG: Sending LLM content length: {len(llm_content)}")
        logging.debug(f"   DEBUG: Sending LLM content (start): {llm_content[:200]}...")

        # --- Construct Appended Content ---
        # Ensure newline separation, add date header
        new_content_block = f"{llm_content}"
        updated_hackmd_content = current_hackmd_content + new_content_block
        logging.debug(f"   DEBUG: Total updated content length: {len(updated_hackmd_content)}")

        # --- Update HackMD Note Content ---
        logging.info(f"   Attempting to update note {note_id} with appended content via API PATCH...")
        update_payload = {"content": updated_hackmd_content}
        content_patch_status, _ = make_api_request(f"/teams/{TEAM_PATH}/notes/{note_id}", method="PATCH", data=update_payload)

        if content_patch_status == 202:
            logging.info(f"   Successfully updated content for note {note_id}.")
            # --- Set Permissions via API --- 
            # Set permissions only after successful content update
            logging.info("   Attempting to set permissions via API (Read: guest, Write: signed_in)...")
            perm_payload = {"readPermission": "guest", "writePermission": "signed_in"}
            perm_patch_status, _ = make_api_request(f"/teams/{TEAM_PATH}/notes/{note_id}", method="PATCH", data=perm_payload)
            if perm_patch_status == 202:
                logging.info(f"   Successfully set permissions for note {note_id}.")
            else:
                 logging.warning(f"   WARNING: API PATCH call failed for permissions setting (Status: {perm_patch_status}).")

        else:
            logging.error(f"   ERROR: API PATCH call failed for content update (Status: {content_patch_status}). Skipping permissions and permalink update.")

        time.sleep(5) # Increased delay between notes

    logging.info("--- Script finished. ---")

if __name__ == "__main__":
    main() 