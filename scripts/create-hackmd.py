#!/usr/bin/env python3
"""
Script to manage HackMD notes:
- Ensures a note exists for each prompt in PROMPTS_DIR.
- Populates initial content for new notes.
- Optionally creates/updates an index book note linking to all prompt notes.
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

# --- Configuration ---
TEAM_PATH = "elizaos"
PROMPTS_DIR = Path("scripts/prompts")
STATE_FILE = Path("book.json")
BOOK_MAP_KEY = "__BOOK_INDEX__"
BOOK_TITLE = "Eliza Daily"
API_BASE_URL = "https://api.hackmd.io/v1"
HACKMD_BASE_URL = "https://hackmd.io"
OUTPUT_DIR = "hackmd" # Directory to save generated files - Use string

# Logging configuration
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# --- Helper Functions ---

def get_api_token() -> str:
    """Retrieves the HackMD API token from environment variables."""
    token = os.getenv("HMD_API_ACCESS_TOKEN")
    if not token:
        logging.error("HMD_API_ACCESS_TOKEN environment variable not set.")
        sys.exit(1)
    return token

def load_state() -> dict:
    """Loads the state from the JSON file."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                logging.info(f"Loaded {len(state)} mappings from '{STATE_FILE}'.")
                return state
        except json.JSONDecodeError:
            logging.warning(f"'{STATE_FILE}' is corrupted or empty. Starting with empty state.")
            return {}
        except Exception as e:
            logging.error(f"Error loading state file '{STATE_FILE}': {e}")
            return {} # Treat as empty state on other errors
    else:
        logging.info(f"State file '{STATE_FILE}' not found. Starting with empty state.")
        return {}

def save_state(state: dict):
    """Saves the state to the JSON file."""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        logging.info(f"Saved state map to '{STATE_FILE}'.")
    except Exception as e:
        logging.error(f"Error saving state file '{STATE_FILE}': {e}")

def make_api_request(endpoint: str, method: str = "POST", data: dict = None, headers: dict = None) -> tuple[int, dict | None]:
    """Makes an API request to HackMD."""
    token = get_api_token()
    default_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    if headers:
        default_headers.update(headers)

    url = f"{API_BASE_URL}{endpoint}"
    logging.debug(f"API Request: {method} {url} Payload: {json.dumps(data)}")

    try:
        response = requests.request(method, url, headers=default_headers, json=data, timeout=30)
        response_data = None
        if response.text:
             try:
                 response_data = response.json()
             except json.JSONDecodeError:
                 logging.warning(f"API response for {method} {url} was not valid JSON. Status: {response.status_code}. Body: {response.text[:200]}...")
                 # Still return status code and None data
                 return response.status_code, None

        if not response.ok:
             logging.warning(f"API request failed: {method} {url} - Status: {response.status_code}")
             logging.warning(f"Response Body: {json.dumps(response_data) if response_data else response.text}")

        return response.status_code, response_data

    except requests.exceptions.RequestException as e:
        logging.error(f"Network error during API request: {method} {url} - {e}")
        return 599, None # Use 599 for network errors
    except Exception as e:
        logging.error(f"Unexpected error during API request: {method} {url} - {e}")
        return 598, None # Use 598 for other errors

def generate_book_markdown(note_map: dict, prompt_to_category: dict) -> str:
    """Generates the markdown content for the index book, grouped by category."""
    header = f"# {BOOK_TITLE}\n\n<!-- Auto-generated index. Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} -->\n\n"
    content_sections = []

    # Group notes by category
    category_to_notes = {}
    for prompt_name, note_id in note_map.items():
        if prompt_name == BOOK_MAP_KEY or not note_id:
            continue
        category = prompt_to_category.get(prompt_name, "uncategorized")
        if category not in category_to_notes:
            category_to_notes[category] = []
        category_to_notes[category].append((prompt_name, note_id))

    if not category_to_notes:
        return header + "*No content notes found in state file yet.*"

    # Sort categories and notes within categories
    sorted_categories = sorted(category_to_notes.keys())

    for category in sorted_categories:
        category_header = f"## {' '.join(word.capitalize() for word in category.split('-'))}\n"
        links = []
        # Sort notes by prompt name within the category
        sorted_notes = sorted(category_to_notes[category], key=lambda item: item[0])
        for prompt_name, note_id in sorted_notes:
            display_title = ' '.join(word.capitalize() for word in prompt_name.split('-'))
            links.append(f"- [{display_title}]({HACKMD_BASE_URL}/{note_id})")
        content_sections.append(category_header + "\n".join(links))

    return header + "\n\n".join(content_sections)

# --- Main Logic ---

def main():
    parser = argparse.ArgumentParser(description="Create/update HackMD notes and index book.")
    parser.add_argument(
        "-b", "--book",
        metavar="PERMALINK",
        help="Create/Update the Index Book note. Requires desired permalink target (used for API update)."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Increase output verbosity (DEBUG level)."
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # --- Load State ---
    current_state = load_state()
    updated_state = current_state.copy() # Work on a copy
    new_content_notes_created = False
    prompt_to_category = {} # <<< Add dictionary to store mapping

    # --- Process Prompt Files ---
    logging.info(f"Processing prompts in '{PROMPTS_DIR}' (**/*.txt)...")
    if not PROMPTS_DIR.is_dir():
        logging.error(f"Prompts directory not found: {PROMPTS_DIR}")
        sys.exit(1)

    # Use rglob for recursive search
    for prompt_file in PROMPTS_DIR.rglob("*.txt"):
        prompt_name = prompt_file.stem
        # Determine category tag from parent directory
        relative_path = prompt_file.relative_to(PROMPTS_DIR)
        category_tag = relative_path.parent.name if relative_path.parent != Path('.') else "uncategorized" # Use parent dir name or 'uncategorized' if in root
        prompt_to_category[prompt_name] = category_tag # <<< Store mapping

        if prompt_name not in updated_state:
            logging.info(f"-- No existing content note found for '{prompt_name}'. Creating...")
            new_content_notes_created = True

            # --- Prepare Details ---
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    file_content = f.read()
            except Exception as e:
                logging.error(f"   ERROR: Failed to read prompt file '{prompt_file}': {e}")
                continue # Skip this prompt

            note_title = f"{' '.join(word.capitalize() for word in prompt_name.split('-'))} - {datetime.now().strftime('%Y-%m-%d')}"
            note_tag = prompt_name
            # Wrap prompt in details and ensure final separator
            initial_content = f"# {note_title}\n\n###### tags: `{category_tag}`\n\n<details><summary>Prompt Details</summary>\n\n```text\n{file_content}\n```\n\n</details>\n\n---\n"

            # --- Create Note via API ---
            logging.info(f"   Creating note via API with Title: '{note_title}', Tag: '{category_tag}', Read: guest, Write: signed_in")
            create_payload = {
                "title": note_title,
                "content": initial_content,
                "readPermission": "guest",
                "writePermission": "signed_in",
                "commentPermission": "everyone"
            }
            status_code, response_data = make_api_request(f"/teams/{TEAM_PATH}/notes", method="POST", data=create_payload)

            if status_code == 201 and response_data and response_data.get("id"):
                new_note_id = response_data["id"]
                logging.info(f"   Note created for '{prompt_name}' with ID: {new_note_id}")
                updated_state[prompt_name] = new_note_id
                logging.warning(f"   WARNING: Note created. Please set its permalink manually in HackMD UI to '{prompt_name}'.")
            else:
                logging.error(f"   ERROR: Failed to create note for '{prompt_name}' via API (Status: {status_code}).")
                # Don't stop, just skip this one

    # --- Manage Book Index (if -b flag is provided) ---
    if args.book:
        book_permalink_target = args.book
        logging.info("Managing Book Index Note (Book Mode enabled)...")
        book_note_id = updated_state.get(BOOK_MAP_KEY)

        if not book_note_id:
            logging.info("-- Book index note ID not found in state file. Creating...")

            # --- Create Minimal Book Note via API ---
            logging.info(f"   Creating minimal book note via API with Title: '{BOOK_TITLE}', Read: guest, Write: owner")
            create_payload = {
                "title": BOOK_TITLE,
                "readPermission": "guest",
                "writePermission": "owner",
                "commentPermission": "disabled"
            }
            status_code, response_data = make_api_request(f"/teams/{TEAM_PATH}/notes", method="POST", data=create_payload)

            if status_code != 201 or not response_data or not response_data.get("id"):
                logging.error(f"   ERROR: Failed to create minimal book note via API (Status: {status_code}). Exiting.")
                sys.exit(1)

            new_book_note_id = response_data["id"]
            logging.info(f"   Minimal book note created with ID: {new_book_note_id}")
            updated_state[BOOK_MAP_KEY] = new_book_note_id
            new_content_notes_created = True # Mark map as updated

            # Generate and Save Book Content Locally (but don't update via API here)
            logging.info("   Generating actual book content (reading from state)...")
            # Pass prompt_to_category map here
            book_content = generate_book_markdown(updated_state, prompt_to_category)
            book_output_filename = os.path.join(OUTPUT_DIR, f"{book_permalink_target}.md")
            try:
                os.makedirs(OUTPUT_DIR, exist_ok=True)
                with open(book_output_filename, 'w', encoding='utf-8') as f:
                    f.write(book_content)
                logging.info(f"   Book content saved locally to: {book_output_filename}")
                logging.info(f"   Run update-hackmd.py script to upload this content.")
            except Exception as e:
                logging.warning(f"   Warning: Failed to save book content locally: {e}")

            # Add a short delay before setting permalink
            logging.info("   Waiting 2 seconds before setting permalink...")
            time.sleep(2)

            # --- Set Permalink via API PATCH (Separate) ---
            logging.info(f"   Attempting to set permalink '{book_permalink_target}' via API PATCH...")
            permalink_payload = {"permalink": book_permalink_target}
            permalink_patch_status_code, permalink_patch_response_data = make_api_request(f"/teams/{TEAM_PATH}/notes/{new_book_note_id}", method="PATCH", data=permalink_payload)
            logging.debug(f"   DEBUG: Permalink PATCH Response Body: {permalink_patch_response_data}")

            if permalink_patch_status_code == 202:
                logging.info(f"   Successfully set permalink '{book_permalink_target}'.")
            else:
                logging.warning(f"   WARNING: API PATCH call failed for permalink setting (Status: {permalink_patch_status_code}). Permalink might not be set.")
                logging.warning(f"   Please check the note '{BOOK_TITLE}' (ID: {new_book_note_id}) on HackMD.")

        elif new_content_notes_created:
            logging.info(f"-- New content notes were created. Updating existing book note (ID: {book_note_id})...")

            # --- Generate Updated Book Content ---
            logging.info("   Generating updated book content (reading from state)...")
             # Pass prompt_to_category map here too (though content update via API is not done here)
            book_content = generate_book_markdown(updated_state, prompt_to_category)
            # Save locally for reference/backup
            book_output_filename = os.path.join(OUTPUT_DIR, f"{book_permalink_target}.md")
            try:
                os.makedirs(OUTPUT_DIR, exist_ok=True)
                with open(book_output_filename, 'w', encoding='utf-8') as f:
                    f.write(book_content)
                logging.info(f"   Book content saved locally to: {book_output_filename}")
            except Exception as e:
                logging.warning(f"   Warning: Failed to save book content locally: {e}")

            # --- Update Book Note Content via API PATCH ---
            logging.info(f"   Attempting to update book content for note {book_note_id} via API PATCH...")
            update_payload = {"content": book_content}
            patch_status_code, _ = make_api_request(f"/teams/{TEAM_PATH}/notes/{book_note_id}", method="PATCH", data=update_payload)

            if patch_status_code == 202:
                logging.info(f"   Successfully updated book note {book_note_id} content.")
            else:
                logging.warning(f"   WARNING: API PATCH call failed for book content update (Status: {patch_status_code}). Book content may be stale.")
        else:
            logging.info(f"-- Book index note exists (ID: {book_note_id}) and no new content notes were created. No book update needed.")
    else:
        logging.info("Book management skipped (run with -b <permalink> to create/update book).")

    # --- Save Final State ---
    if new_content_notes_created:
        save_state(updated_state)
    else:
         logging.info("No notes created or book added. State file remains unchanged.")

    logging.info("--- Script finished. ---")

if __name__ == "__main__":
    main() 