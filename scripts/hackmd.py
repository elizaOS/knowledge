#!/usr/bin/env python3
"""
Script to interact with the HackMD API for managing notes within the elizaOS content pipeline.

Handles uploading, pulling, publishing, and syncing notes, primarily for team workspaces.
Requires Python 3.x and the following packages:
- requests
- python-dotenv

Expects HACKMD_API_TOKEN to be set as an environment variable (e.g., via a .env file).
"""

import argparse
import os
import requests
import json
import logging
import re
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any

# --- Constants ---
HACKMD_API_URL = "https://api.hackmd.io/v1"
HACKMD_BASE_URL = "https://hackmd.io" # For viewing notes
TEAM_ID = "elizaos" # Hardcoded Team Path/ID as per PRD

# IMPORTANT: Replace these placeholders with the actual HackMD Note IDs for your book index notes!
# You can create them using the `create-book-note` command.
COUNCIL_BOOK_ID = "_uBNNBfeTIq3sx87nDW63w" # Hardcoded as per PRD - NEEDS ACTUAL ID
COMMUNITY_BOOK_ID = "lNf9HbwqSEqes_pyrtls_Q" # Hardcoded as per PRD - NEEDS ACTUAL ID

LOCAL_SYNC_DIR = "hackmd"

# Content types managed by this script
CONTENT_TYPES = ['newsletter', 'announcement', 'dev', 'council', 'feedback', 'strategic']
PUBLISHED_TAG = 'published'
TAG_LINE_PREFIX = "###### tags:"

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Helper Functions ---

def get_api_token() -> str:
    """Retrieves the HackMD API token from environment variables."""
    token = os.getenv("HACKMD_API_TOKEN")
    if not token:
        logging.error("HACKMD_API_TOKEN environment variable not set.")
        raise ValueError("HACKMD_API_TOKEN environment variable not set.")
    return token

def make_api_request(method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Optional[Any]:
    """Makes a request to the HackMD API with improved error reporting."""
    token = get_api_token()
    default_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    if headers:
        default_headers.update(headers)

    url = f"{HACKMD_API_URL}{endpoint}"
    logging.debug(f"Making API request: {method} {url} Data: {json.dumps(data) if data else 'None'}")

    try:
        response = requests.request(method, url, headers=default_headers, json=data)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        # Handle responses with no content (common for PATCH, DELETE)
        if response.status_code in [202, 204]:
            logging.debug(f"API Request successful ({response.status_code} No Content) for {method} {url}")
            return None # Indicate success with no body

        # For other successful responses, try to parse JSON
        return response.json()

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err} - Status: {http_err.response.status_code}")
        try:
            # Try to get more details from the response body
            error_details = http_err.response.json()
            logging.error(f"API Error Details: {error_details}")
        except json.JSONDecodeError:
            logging.error(f"API Error Body (non-JSON): {http_err.response.text}")
        return None # Indicate failure
    except requests.exceptions.RequestException as req_err:
        logging.error(f"Request exception occurred: {req_err}")
        return None # Indicate failure
    except json.JSONDecodeError:
        # This case should be less likely with the status code check above, but handle defensively
        logging.error(f"API Response JSON Decode Error for URL: {url}. Status: {response.status_code}. Response: {response.text}")
        return None # Indicate failure

def get_note_details(note_id: str) -> Optional[Dict[str, Any]]:
    """Gets details (including content) for a specific note."""
    logging.info(f"Fetching details for note ID: {note_id}")
    endpoint = f"/notes/{note_id}"
    note_data = make_api_request("GET", endpoint)
    if not note_data:
        logging.warning(f"Failed to retrieve details for note ID: {note_id}")
        return None
    return note_data

def get_book_content(team_path: str, book_note_id: str) -> Optional[str]:
    """Fetches the content of a specific book index note."""
    # Books are rendered from regular notes. Requires the Note ID of the index note.
    logging.info(f"Fetching content for book index note ID: {book_note_id} in team {team_path}")
    # Use the generic get_note_details function
    note_data = get_note_details(book_note_id)
    if note_data and 'content' in note_data:
        return note_data['content']
    else:
        logging.error(f"Could not fetch content for book index note ID: {book_note_id}")
        return None

def parse_links_from_book(book_content: str) -> List[Tuple[str, str]]:
    """Extracts markdown links (title, url) from book content."""
    # Simple regex for markdown links: - [Title](URL)
    # Assumes links are in list items starting with '- '
    links = re.findall(r"^\s*-\s*\[([^\]]+)\]\(([^\)]+)\)", book_content, re.MULTILINE)
    # Extract note ID from URL: https://hackmd.io/<note_id>
    parsed_links = []
    for title, url in links:
        match = re.search(r"https://hackmd\.io/([a-zA-Z0-9_-]+)", url)
        if match:
            note_id = match.group(1)
            parsed_links.append((title, note_id))
        else:
            logging.warning(f"Could not parse Note ID from URL: {url} in book content")
    return parsed_links

def update_book(team_path: str, book_note_id: str, note_title: str, note_url: str) -> bool:
    """Adds a markdown link for the new note to the specified book index note."""
    logging.info(f"Attempting to update book '{book_note_id}' in team '{team_path}' with note '{note_title}' ({note_url})")

    if not book_note_id or "YOUR_" in book_note_id: # Basic check for placeholder
        logging.error(f"Invalid or placeholder Book Note ID configured: {book_note_id}. Cannot update book.")
        logging.error("Please run 'create-book-note' and update the constants in the script.")
        return False

    try:
        current_content = get_book_content(team_path, book_note_id)
        if current_content is None:
            # Error already logged in get_book_content
            return False

        # Format the link: - [Title](URL)
        new_link = f"- [{note_title}]({note_url})"

        # Append the link, ensuring it's on a new line.
        # Avoids breaking existing markdown lists if the note doesn't end with a newline.
        if current_content.strip() and not current_content.endswith('\n'):
            updated_content = current_content + f"\n{new_link}"
        else:
             updated_content = current_content + new_link # Already ends with newline or is empty
        updated_content += "\n" # Ensure trailing newline

        # Update the book note content using the Team Notes API endpoint
        endpoint = f"/teams/{team_path}/notes/{book_note_id}"
        payload = {"content": updated_content}
        response = make_api_request("PATCH", endpoint, data=payload)

        # PATCH returns 202 (None here) on success
        if response is None:
            logging.info(f"Successfully requested update for book note {book_note_id}")
            return True
        else:
            # If PATCH returns something unexpected, log it (error handled in make_api_request)
            logging.warning(f"Book note {book_note_id} update requested, but received unexpected response: {response}")
            return False # Treat unexpected response as potential failure

    except Exception as e:
        logging.error(f"Unexpected error updating book {book_note_id}: {e}", exc_info=True)
        return False


# --- API Command Functions ---

def upload_note_cmd(file_path: str, content_type: str) -> Optional[Tuple[str, str]]:
    """Handles the 'upload' command: Uploads content from a file to HackMD."""
    logging.info(f"Uploading file: {file_path}, type: {content_type}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        logging.error(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}", exc_info=True)
        return None

    # Generate title and tags
    today_date = datetime.now().strftime("%Y-%m-%d")
    title = f"{content_type.capitalize()}-{today_date}"
    tags = [content_type]
    if content_type == "council":
        book_id_to_update = COUNCIL_BOOK_ID
        # tags.append("council") # Add specific tag if needed, auto type tag is added
    else:
        book_id_to_update = COMMUNITY_BOOK_ID
        # tags.append("community") # Add specific tag if needed

    # Determine permissions (default to team owner R/W, signed-in comment)
    read_permission = "owner"
    write_permission = "owner"
    comment_permission = "signed_in_users"

    # Prepare payload for creating a team note
    payload = {
        "title": title,
        "content": content,
        "readPermission": read_permission,
        "writePermission": write_permission,
        "commentPermission": comment_permission,
    }

    # Ensure tags line is present in content (HackMD API limitation)
    tag_line = f"{TAG_LINE_PREFIX} `{'` `'.join(tags)}`"
    if TAG_LINE_PREFIX not in content:
        payload["content"] = f"{tag_line}\n\n{content}"
        logging.debug("Prepended tags line to content.")
    else:
        logging.debug("Tags line potentially already exists in content.")
        # More complex logic could merge tags here if needed

    logging.info(f"Creating note with title: '{title}', tags: {tags}, type: {content_type}")
    endpoint = f"/teams/{TEAM_ID}/notes"
    response_data = make_api_request("POST", endpoint, data=payload)

    if response_data and isinstance(response_data, dict) and 'id' in response_data:
        note_id = response_data['id']
        # Construct the direct note URL (doesn't rely on publishLink which might not be set)
        note_url = f"{HACKMD_BASE_URL}/{note_id}"
        logging.info(f"Note created successfully: ID={note_id}, URL={note_url}")

        # Update the appropriate book index note
        book_updated = update_book(TEAM_ID, book_id_to_update, title, note_url)
        if not book_updated:
            # Log warning but proceed to publish attempt
            logging.warning(f"Failed to update book '{book_id_to_update}' with the new note link, but attempting to publish note anyway.")
        else:
            logging.info(f"Successfully updated book '{book_id_to_update}'.")

        # --- Immediately publish the note ---
        logging.info(f"Proceeding to immediately publish note ID: {note_id}")
        publish_success = publish_note_cmd(note_id)
        if not publish_success:
            logging.error(f"Failed to automatically publish note {note_id} after upload.")
            # Decide if this should cause the upload command to fail
            # return None # Uncomment if publish failure should mean upload failure
        else:
            logging.info(f"Successfully published note {note_id} immediately after upload.")
        # --- End Immediate Publish ---

        return note_id, note_url
    else:
        logging.error(f"Error creating note. API response: {response_data}")
        return None

def pull_note_cmd(note_id: str) -> bool:
    """Handles the 'pull' command: Pulls content and saves locally."""
    logging.info(f"Pulling content for note ID: {note_id}")
    note_data = get_note_details(note_id)

    if not note_data:
        # Error logged in get_note_details
        return False

    content = note_data.get('content')
    tags = note_data.get('tags', [])
    title = note_data.get('title', f"Untitled_{note_id}")

    if content is None:
        logging.error(f"Error: Note {note_id} content is empty or unavailable in API response.")
        return False

    # Determine type and date
    content_type = 'unknown'
    date_str = datetime.now().strftime("%Y-%m-%d") # Default date

    # 1. Check tags for known types
    found_type = next((tag for tag in tags if tag in CONTENT_TYPES), None)
    if found_type:
        content_type = found_type
    elif tags: # Fallback to first tag if no known type found
        content_type = tags[0].lower()
        logging.debug(f"Using first tag '{content_type}' as content type.")

    # 2. Try to extract date and potentially type from title (Format: Type-YYYY-MM-DD)
    try:
        parts = title.split('-')
        if len(parts) >= 4: # e.g., Council-2024-01-01
            maybe_date = "-".join(parts[-3:])
            datetime.strptime(maybe_date, "%Y-%m-%d") # Validate format
            date_str = maybe_date
            logging.debug(f"Extracted date {date_str} from title '{title}'.")
            # If type still unknown, try parsing from title prefix
            if content_type == 'unknown':
                potential_type_from_title = "-".join(parts[:-3]).lower()
                if potential_type_from_title in CONTENT_TYPES:
                    content_type = potential_type_from_title
                    logging.debug(f"Extracted type '{content_type}' from title.")
    except (ValueError, IndexError):
        logging.warning(f"Could not parse date/type from title '{title}'. Using defaults: Type='{content_type}', Date='{date_str}'.")

    # Ensure the local directory exists
    type_dir = os.path.join(LOCAL_SYNC_DIR, content_type)
    try:
        os.makedirs(type_dir, exist_ok=True)
    except OSError as e:
        logging.error(f"Error creating directory {type_dir}: {e}")
        return False

    # Save the file
    file_name = f"{date_str}.md"
    file_path = os.path.join(type_dir, file_name)

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"Successfully pulled note {note_id} to {file_path}")
        return True
    except IOError as e:
        logging.error(f"Error writing file {file_path}: {e}")
        return False

def publish_note_cmd(note_id: str) -> bool:
    """Handles the 'publish' command: Marks note as published by adding tag via content update."""
    logging.info(f"Marking note ID: {note_id} as published.")
    note_data = get_note_details(note_id)

    if not note_data:
        return False

    current_content = note_data.get('content', '')
    current_tags = note_data.get('tags', [])
    team_path = note_data.get('teamPath') # Required for team note PATCH endpoint

    if not team_path:
        # This should not happen if we only operate on team notes via TEAM_ID
        logging.error(f"Note {note_id} does not have a teamPath. Cannot update tags for non-team notes via this script.")
        return False

    # Check if already published
    if PUBLISHED_TAG in current_tags:
        logging.info(f"Note {note_id} is already marked as published.")
        return True

    # Add 'published' tag by modifying the content string
    # Ensure no duplicates in the final tag list
    new_tags_list = sorted(list(set(current_tags + [PUBLISHED_TAG])))
    new_tag_line = f"{TAG_LINE_PREFIX} `{'` `'.join(new_tags_list)}`"

    updated_content: str
    if TAG_LINE_PREFIX in current_content:
        # Replace existing tag line carefully
        lines = current_content.splitlines()
        found = False
        for i, line in enumerate(lines):
            if line.strip().startswith(TAG_LINE_PREFIX):
                lines[i] = new_tag_line
                found = True
                break
        if not found: # Should not happen if prefix is in content, but handle defensively
             logging.warning(f"Tag line prefix found in content of note {note_id}, but couldn't replace line.")
             # Prepend as fallback
             updated_content = f"{new_tag_line}\n\n{current_content}"
        else:
             updated_content = "\n".join(lines)
    else:
        # Add tag line to the beginning
        updated_content = f"{new_tag_line}\n\n{current_content}"

    # Use the Team Notes API endpoint for updating
    endpoint = f"/teams/{team_path}/notes/{note_id}"
    payload = {"content": updated_content}
    response = make_api_request("PATCH", endpoint, data=payload)

    # PATCH returns 202 (None here) on success
    if response is None:
        logging.info(f"Successfully marked note {note_id} as published.")
        return True
    else:
        logging.error(f"Error marking note {note_id} as published. API Response: {response}")
        return False

def create_book_note_cmd(title: str) -> Optional[str]:
    """Handles 'create-book-note': Creates a new note for use as a book index."""
    logging.info(f"Creating book note with title: '{title}' in team {TEAM_ID}")

    # Initial content for the book note
    content = f"# {title}\n\n<!-- This note serves as the index for the {title} book. Links will be added automatically. -->\n"

    # Set permissions (Team Owner R/W, Commenting disabled)
    # Changed from original PRD suggestion of 'everyone' read to 'owner' for safety.
    read_permission = "owner"
    write_permission = "owner"
    comment_permission = "disabled"

    payload = {
        "title": title,
        "content": content,
        "readPermission": read_permission,
        "writePermission": write_permission,
        "commentPermission": comment_permission
    }

    endpoint = f"/teams/{TEAM_ID}/notes"
    response_data = make_api_request("POST", endpoint, data=payload)

    if response_data and isinstance(response_data, dict) and 'id' in response_data:
        note_id = response_data['id']
        note_url = f"{HACKMD_BASE_URL}/{note_id}"
        logging.info(f"Book note created successfully: ID={note_id}, URL={note_url}")
        logging.warning(f"IMPORTANT: Update the script's constants (COUNCIL_BOOK_ID or COMMUNITY_BOOK_ID) with this ID: {note_id}")
        return note_id
    else:
        logging.error(f"Error creating book note '{title}'. API response: {response_data}")
        return None

# def sync_notes_cmd() -> None:
#     """Handles the 'sync' command: Pulls unpublished notes listed in configured books."""
#     logging.info("Starting sync process...")
#     book_ids_to_sync = {
#         "Council": COUNCIL_BOOK_ID,
#         "Community": COMMUNITY_BOOK_ID
#     }
#
#     notes_pulled = 0
#     notes_failed = 0
#
#     for book_name, book_note_id in book_ids_to_sync.items():
#         logging.info(f"-- Syncing notes from {book_name} book (Index Note ID: {book_note_id}) --")
#         if not book_note_id or "YOUR_" in book_note_id:
#             logging.error(f"Invalid or placeholder Book Note ID for {book_name}: {book_note_id}. Skipping sync.")
#             continue
#
#         book_content = get_book_content(TEAM_ID, book_note_id)
#         if not book_content:
#             logging.warning(f"Could not get content for {book_name} book index note. Skipping.")
#             continue
#
#         # Requires parse_links_from_book to extract ID from comment
#         # links = parse_links_from_book(book_content)
#         links = [] # Placeholder since parser is commented out
#         logging.info(f"Found {len(links)} note links in {book_name} book index. (Sync disabled)")
#
#         for note_title, note_id in links:
#             logging.debug(f"Checking note: '{note_title}' (ID: {note_id}) from {book_name} book.")
#             note_details = get_note_details(note_id)
#             if not note_details:
#                 logging.warning(f"Could not get details for note ID {note_id}. Skipping pull.")
#                 notes_failed += 1
#                 continue
#
#             tags = note_details.get('tags', [])
#             if PUBLISHED_TAG in tags:
#                 logging.debug(f"Note {note_id} ('{note_title}') is already published. Skipping pull.")
#                 continue
#             else:
#                 logging.info(f"Note {note_id} ('{note_title}') is not published. Pulling...")
#                 if pull_note_cmd(note_id):
#                     notes_pulled += 1
#                 else:
#                     notes_failed += 1
#
#     logging.info(f"Sync process finished. Notes pulled: {notes_pulled}. Notes failed/skipped: {notes_failed}.")


# --- Main Execution ---

def main():
    parser = argparse.ArgumentParser(description="HackMD Integration Script for elizaOS Content Pipeline", formatter_class=argparse.RawTextHelpFormatter)

    # Add verbose/debug flag
    parser.add_argument(
        "-v", "--verbose",
        help="Increase output verbosity (show DEBUG messages)",
        action="store_const", dest="loglevel", const=logging.DEBUG,
        default=logging.INFO,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True)

    # Upload command
    parser_upload = subparsers.add_parser("upload", help="Upload content file to HackMD")
    parser_upload.add_argument("--file", required=True, help="Path to the content file to upload")
    parser_upload.add_argument("--type", required=True, choices=CONTENT_TYPES, help="Type of content")

    # Pull command
    parser_pull = subparsers.add_parser("pull", help="Pull content from a HackMD note by ID and save locally (Utility, not part of main workflow)")
    parser_pull.add_argument("--id", required=True, help="HackMD Note ID to pull")

    # Publish command
    parser_publish = subparsers.add_parser("publish", help="Mark a HackMD note as published (adds 'published' tag)")
    parser_publish.add_argument("--id", required=True, help="HackMD Note ID to mark as published")

    # Sync command (Commented out)
    # parser_sync = subparsers.add_parser("sync", help="Sync all unpublished notes from configured book index notes (Currently Disabled)")

    # Create Book Note command
    parser_create_book = subparsers.add_parser("create-book-note", help="Create a new note to be used as a book index (outputs Note ID)")
    parser_create_book.add_argument("--title", required=True, help="Title for the new book index note (e.g., 'elizaOS Council')")


    args = parser.parse_args()

    # Set log level from command line
    logging.getLogger().setLevel(args.loglevel)

    # Load environment variables if .env file exists
    try:
        from dotenv import load_dotenv
        # Use find_dotenv to locate .env in parent directories if needed
        # from dotenv import find_dotenv
        # load_dotenv(find_dotenv())
        if load_dotenv():
             logging.debug("Loaded environment variables from .env file.")
        else:
             logging.debug(".env file not found, relying on environment variables.")
    except ImportError:
        logging.info("python-dotenv library not found, cannot load .env file. Ensure HACKMD_API_TOKEN is set in the environment.")

    # --- Command Dispatch ---
    exit_code = 0
    try:
        if args.command == "upload":
            result = upload_note_cmd(args.file, args.type)
            if not result:
                exit_code = 1
        elif args.command == "pull":
            if not pull_note_cmd(args.id):
                exit_code = 1
        elif args.command == "publish":
            if not publish_note_cmd(args.id):
                exit_code = 1
        # elif args.command == "sync":
        #     logging.info("Sync command is currently disabled.")
        #     # sync_notes_cmd()
        elif args.command == "create-book-note":
            note_id = create_book_note_cmd(args.title)
            if not note_id:
                exit_code = 1
        else:
            # Should not happen due to required=True in subparsers
            logging.error(f"Unknown command: {args.command}")
            parser.print_help()
            exit_code = 1

    except ValueError as ve:
        # Catch specific errors like missing API token
        logging.critical(f"Configuration Error: {ve}")
        exit_code = 2
    except Exception as e:
        # Catch unexpected errors
        logging.critical(f"An unexpected error occurred: {e}", exc_info=True)
        exit_code = 3

    if exit_code == 0:
        logging.info(f"Command '{args.command}' completed successfully.")
    else:
        logging.error(f"Command '{args.command}' failed with exit code {exit_code}.")

    exit(exit_code)


if __name__ == "__main__":
    main() 