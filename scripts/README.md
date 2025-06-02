# Scripts

This directory contains various scripts for automating tasks related to content aggregation, generation, and publishing for the elizaOS knowledge system.

## `aggregate-sources.py`

**Purpose**: Aggregates content from diverse data sources into a unified daily JSON file.

**Details**:
This Python script is the primary engine for collecting daily context. It navigates predefined paths within the workspace (e.g., `ai-news/` subfolders for elizaos, discord, and dev content in both Markdown and JSON formats, `github/summaries/` for daily, weekly, and monthly GitHub activity summaries, and `github/stats/month/` for monthly statistics). It also processes `github/user_summaries.ndjson` to extract recent user activity.
The script intelligently reads text and JSON files, handling potential errors gracefully. For date-specific content, it can fetch files for a given date or the latest available.
The final output is a structured JSON file named `YYYY-MM-DD.json` saved in the `the-council/aggregated/` directory. This file serves as the foundational input for other context generation and summarization scripts.

**Usage**:
```bash
./scripts/aggregate-sources.py [YYYY-MM-DD]
```
- If `[YYYY-MM-DD]` is provided, it generates the context for that specific date.
- If no date is provided, it defaults to the current date.

**Dependencies**: Python 3.

**Status**: Actively used. Replaces the older `aggregate-sources.sh`.

---

## `prompts/` Directory

**Purpose**: This directory houses all the prompt template files used by various scripts for interacting with Language Models (LLMs).

**Structure**:
- Prompt files are typically plain text (`.txt`) files.
- Subdirectories within `prompts/` (e.g., `prompts/comms/`, `prompts/dev/`, `prompts/strategy/`) are used by scripts like `create-hackmd.py` and `update-hackmd.py` to categorize the generated content and corresponding HackMD notes. The name of the subdirectory often becomes a category tag.
- Individual prompt files are named to reflect their specific purpose (e.g., `elizaos_prompt.txt`, `user_feedback_prompt.txt`). These names are also used by `create-hackmd.py` when generating titles or identifying notes.

**Usage**:
- Scripts such as `tweet-summarizer.sh`, `summarize.sh`, `process_prompts.sh`, `generate_council_context.py`, and `update-hackmd.py` utilize these files to provide specific instructions, context, and formatting guidance to the LLM for tasks like content generation, summarization, or reformatting.
- Some prompt files may contain placeholders (e.g., `{CONTENT}`, `{UPDATE_TYPE}`) that the calling script replaces with dynamic data before sending the complete prompt to the LLM.

---

## `generate_council_context.py`

**Purpose**: Generates a high-level "council context" summary from the daily aggregated data.

**Details**:
This Python script takes the `the-council/aggregated/YYYY-MM-DD.json` file (produced by `aggregate_sources.py`) as its main input. It uses a predefined prompt (or one implicitly embedded) to process this aggregated data through an AI model via the OpenRouter API (specifically `anthropic/claude-3.7-sonnet` by default).
The goal is to distill the extensive daily information into a more concise, high-level summary suitable for strategic review or "council" consumption.
The output is another JSON file, typically named `YYYY-MM-DD.json` and saved in `the-council/council_briefing/`.

**Environment Variables**:
- `OPENROUTER_API_KEY`: Required for API access.
- `HMD_API_ACCESS_TOKEN` or `HACKMD_API_TOKEN`: Required if the script interacts with HackMD (though current primary function seems to be local JSON to JSON processing).

**Dependencies**: Python 3, `requests` library.

This Python script takes the aggregated daily JSON (typically produced by `aggregate_sources.py`) and processes it with a sophisticated LLM prompt (defined in `scripts/prompts/strategy/north-star.txt` and combined with monthly goals) to produce a structured JSON briefing for the elizaOS Agent Council. It identifies key strategic themes, discussion points, and potential questions based on the day's operational data evaluated against strategic objectives. The script now uses a comprehensive text extraction method to gather all textual data from its input JSON, ensuring a richer context for the LLM. It also generates a Markdown version of the briefing suitable for HackMD.

---

## `extract_facts.py`

**Purpose**: Generates a categorized intelligence briefing by extracting key facts and insights from the aggregated daily JSON data.

**Details**:
This script takes the comprehensive JSON output from `scripts/aggregate_sources.py` (e.g., `the-council/aggregated/YYYY-MM-DD.json`) and uses a specialized LLM prompt (`scripts/prompts/news_show/fact_extraction_prompt.txt`) to perform a deep analysis of the entire dataset in a single LLM call. It aims to distill the most significant information into a structured JSON output, organized by thematic categories such as Twitter news, GitHub updates (new issues/PRs, overall focus), Discord updates, user feedback, strategic insights, and market analysis. The output includes an overall summary and, for each extracted piece of information, `source_keys` tracing back to the original data in the input JSON. Crucially, user feedback is structured to be easily consumable for sentiment analysis and visualization by downstream scripts like `webhook.py`. This script is designed to produce actionable intelligence for briefings or to power other content generation processes.

**Typical Usage**:
```bash
python scripts/extract-facts.py -i path/to/the-council/aggregated/YYYY-MM-DD.json -o path/to/the-council/extracted_facts/YYYY-MM-DD.json
```

---

## `webhook.py`

**Purpose**: Optimized Discord Facts Bot that converts JSON facts data into rich Discord embeds with smart content processing and budget allocation.

**Details**:
This Python script is the streamlined replacement for `extract-webhook.py`, reduced from 800+ lines to under 300 lines while adding more functionality. It processes JSON facts files (typically generated by `extract-facts.py`) to create engaging Discord messages with intelligent content management. Note: This handles **facts JSON** files - for council briefing JSON files, see `council-bot-enhanced.py`.

**Key Features**:
- **Smart Budget Allocation**: Automatically distributes character limits across sections based on content length and priority weighting (GitHub and Discord get higher priority)
- **Intelligent Content Processing**: 
  - Uses LLM summarization when content exceeds section budgets
  - Smart truncation at logical breakpoints (bullets, sentences, words) to avoid mid-word cuts
  - Bullet point detection for long or multi-item content
- **Rich Discord Formatting**:
  - Main embed with overall summary and thumbnail
  - Separate themed embeds for GitHub, Discord, and User Feedback sections
  - Single consolidated diff block for user feedback with sentiment-based coloring (`+` positive, `-` negative, neutral unmarked), providing a clear visual representation of community sentiment.
  - Clickable links for GitHub PRs/issues with author attribution
- **Visual Enhancements**: Includes AI-generated poster images and proper embed styling with section-specific colors
- **Robust Error Handling**: Proper Discord connection cleanup and graceful fallbacks when LLM summarization fails

**Core Sections**:
- **Main Embed**: Overall summary with key observations extracted from strategic insights
- **GitHub Section**: PRs and issues with `[Title](url) by @author - significance` format
- **Discord Section**: Channel summaries with participant information, intelligently consolidated
- **User Feedback Section**: Sentiment-colored feedback in a single diff block for efficient token usage, offering an at-a-glance view of community sentiment.
- **Visual Poster**: AI-generated daily summary image

**Content Processing**:
- **Proportional Budgeting**: Allocates 1600 total characters across sections based on raw content length and priority weights
- **LLM Integration**: Uses OpenRouter with `google/gemini-2.5-flash-preview` for intelligent summarization when content exceeds budgets
- **Smart Truncation**: Falls back to logical breakpoint truncation if LLM fails, preserving readability

**Usage**:
```bash
# Send to Discord with LLM summarization
export DISCORD_BOT_TOKEN="your_bot_token_here"
export OPENROUTER_API_KEY="your_key_here"
python scripts/webhook.py path/to/facts.json -d -c CHANNEL_ID -s

# Export to JSON for testing
python scripts/webhook.py the-council/facts/2024-01-15.json -o output.json -s

# Basic usage without summarization
python scripts/webhook.py the-council/facts/2024-01-15.json -d -c CHANNEL_ID
```

**Command-Line Arguments**:
- `json_file`: (Required) Path to the input JSON facts file (from extract-facts.py)
- `-d`, `--discord`: Send to Discord channels
- `-c`, `--channels`: Discord channel IDs (comma-separated). Required with `--discord`
- `-o`, `--out`: Export Discord payload to JSON file for testing
- `-s`, `--summarize`: Enable LLM summarization for long content
- `--poster`: Poster filename (default: `hackmd-facts-briefing.png`)

**Dependencies**:
- Python 3
- `discord.py` library (`pip install discord.py`)
- `requests` library (`pip install requests`)

**Environment Variables**:
- `DISCORD_BOT_TOKEN`: Required for Discord posting
- `OPENROUTER_API_KEY`: Required for LLM summarization (`-s` flag)

**Configuration**:
- **Colors**: GitHub (gray), Discord (blurple), User Feedback (purple), Default (orange)
- **Budget Limits**: 1600 total characters, 200 minimum per section, 1000 maximum per section
- **Priority Weights**: GitHub (1.5x), Discord (1.3x), User Feedback (1.0x)
- **Poster URL**: `https://elizaos.github.io/knowledge/posters/`

---

## `extract-webhook.py` (Deprecated)

> **Note:**  
> This script has been replaced by `webhook.py` which offers significantly improved functionality, better performance, and cleaner code architecture. The new script reduces complexity from 800+ lines to under 300 while adding smart content processing and budget allocation features.

---

## `create-hackmd.py`

**Purpose**: Manages HackMD notes. It ensures notes exist for prompt files in `scripts/prompts/` and can also map local directories to new HackMD notes for direct file synchronization. It populates/updates `book.json` to map note configurations (prompt-based or direct file sync) to their HackMD note IDs. Can also create/update a main book index note on HackMD.

**Details**:
This script has two main functionalities for setting up HackMD notes:

1.  **Prompt-Based Note Creation**:
    - It iterates through all `*.txt` prompt files found recursively within the `scripts/prompts/` directory.
    - For each prompt, it determines a `category_tag` based on the prompt file's parent directory (e.g., `comms`, `dev`, `strategy`).
    - It checks `book.json` to see if a note already exists for the `prompt_name` (derived from the filename).
    - If a note does not exist (or if its ID is missing in `book.json`), the script creates a new note on HackMD via the API.
        - The initial title of the new HackMD note includes the prompt name and the current date (e.g., "Developer Update - YYYY-MM-DD").
        - The initial content includes this title, the `category_tag`, and the full content of the prompt file itself, wrapped in HTML `<details>` tags.
        - The new note's ID and an `update_strategy` of "overwrite" are then saved to `book.json` for that `prompt_name`.

2.  **Direct Directory Mapping for File Sync (via `-i` or `--include` argument)**:
    - If the `-i LOCAL_DIR_PATH` argument is used (can be specified multiple times), the script processes each provided local directory path.
    - For each valid directory path not already configured in `book.json`'s `CUSTOM_HEADER_LINKS` (by checking `source_directory`):
        - It derives a link text and HackMD note title from the directory path (e.g., path `github/summaries/day/` might become link text "Github - Summaries - Day" and note title "Sync: Github - Summaries - Day").
        - It creates a new HackMD note with the derived title and placeholder content indicating it will be synced from the local directory.
        - If successful, it adds a new configuration object to the `CUSTOM_HEADER_LINKS` array in `book.json`. This object includes:
            - `text`: The derived link text (for the Book Index header).
            - `url`: The URL of the newly created HackMD note.
            - `source_directory`: The provided local directory path.
            - `hackmd_note_title`: The title given to the HackMD note.
        - This setup enables `update-hackmd.py` to later find this configuration and sync the latest `.md` file from the `source_directory` to this HackMD note.

3.  **Book Index Management (via `-b` argument)**:
    - If the `-b <permalink>` argument is provided, the script will also manage a main "Book Index" HackMD note:
        - If the Book Index note doesn't exist (ID not in `book.json` under `__BOOK_INDEX__`), it creates a new HackMD note with the title "Eliza Daily" (or as configured) and attempts to set its permalink to the one provided.
        - It then generates the content for this Book Index (a list of links based on `CUSTOM_HEADER_LINKS` and other notes in `book.json`, grouped by category) and updates the Book Index note on HackMD or saves it locally.

**`book.json` Structure and Usage**:
- `book.json` is a critical state file used by both `create-hackmd.py` and `update-hackmd.py`.
- For **prompt-based notes**, it stores mappings like: `"prompt-name": {"id": "hackmd_note_id", "update_strategy": "overwrite"}`.
- The `CUSTOM_HEADER_LINKS` key in `book.json` is an array of objects used to generate the header links in the Book Index page. Items here can now also include `source_directory` and `hackmd_note_title` fields to configure them for direct file sync by `update-hackmd.py` if no corresponding prompt file exists for that conceptual note.
- `update-hackmd.py` relies on these configurations to determine which notes to update and how: either by generating content using an LLM based on a prompt file, or by syncing content directly from a local file specified by a `source_directory` in a `CUSTOM_HEADER_LINKS` entry.

**Usage**:
```bash
./scripts/create-hackmd.py [-b BOOK_PERMALINK] [-i LOCAL_DIR_PATH]... [-v]
```
- `-b BOOK_PERMALINK`, `--book BOOK_PERMALINK`: Optional. If provided, creates/updates the Book Index note on HackMD, attempting to set its permalink to `BOOK_PERMALINK`.
- `-i LOCAL_DIR_PATH`, `--include LOCAL_DIR_PATH`: Optional. Can be used multiple times. For each local directory path provided, creates a new HackMD note and adds a configuration to `CUSTOM_HEADER_LINKS` in `book.json` to enable direct file sync from this directory by `update-hackmd.py`.
- `-v`, `--verbose`: Optional. Increases output verbosity for debugging.

**Dependencies**: Python 3, `requests` library.
**Environment Variables**:
- `HMD_API_ACCESS_TOKEN` (or `HACKMD_API_TOKEN` as fallback): Required for all HackMD API interactions.

---

## `update-hackmd.py`

**Purpose**: Generates daily content for HackMD notes or syncs them from local files, then updates these notes on HackMD, including their titles and full content.

**Details**:
This script is central to the daily content update process for HackMD notes.
- It reads the `book.json` state file to understand the notes to manage.
- It uses the latest aggregated data from `the-council/aggregated/YYYY-MM-DD.json` as context for LLM-generated notes (or a specific date's file if the `-d` flag is used).
- **Book Index Update**: First, it regenerates the content for the main HackMD Book Index note (ID from `__BOOK_INDEX__` in `book.json`, using link configurations from `CUSTOM_HEADER_LINKS` and other entries) and updates it on HackMD.
- **Direct File Sync from `CUSTOM_HEADER_LINKS`**: It then processes entries in `CUSTOM_HEADER_LINKS` in `book.json`. If an entry specifies a `source_directory`:
    - It extracts the HackMD note ID from the entry's `url`.
    - It finds the most recently modified `.md` file in the specified local `source_directory`.
    - It updates the HackMD note with the content of this local file and the title from `hackmd_note_title`.
    - It sets note permissions.
- **LLM-Based Content Generation**: For each remaining `prompt_name` in `book.json` that has a corresponding prompt file in `scripts/prompts/` (and is not a special key like `__BOOK_INDEX__` or `CUSTOM_HEADER_LINKS_KEY`):
    1.  It reads the associated prompt template file (e.g., `scripts/prompts/[category]/[prompt_name].txt`).
    2.  It calls an LLM (via the OpenRouter API, model typically `anthropic/claude-3.7-sonnet`) with the prompt template and the aggregated daily data to generate the main content for the note.
    3.  It constructs a new title for the HackMD note, combining the prompt's display name and the current processing date (e.g., "Developer Update - YYYY-MM-DD").
    4.  It constructs the new full content for the HackMD note. This includes:
        *   The full text of the prompt template (from the local file), wrapped in HTML `<details>` tags.
        *   A markdown separator (`---`).
        *   The LLM-generated main content for the day.
    5.  It updates the corresponding HackMD note via the API. This is an overwrite operation for both the `title` and the entire `content` of the note, based on the "overwrite" strategy typically set in `book.json`.
    6.  It sets the HackMD note permissions (e.g., read: guest, write: signed_in).
    7.  It saves the LLM-generated main content locally to `hackmd/[category]/[prompt_name]/YYYY-MM-DD.md`.
    8.  Optionally, if the `-j` or `--json` flag is used, it also saves a structured JSON file locally (`hackmd/[category]/[prompt_name]/YYYY-MM-DD.json`) containing the generated text and other metadata.

**Usage**:
```bash
./scripts/update-hackmd.py [-d YYYY-MM-DD] [-j] [-v]
```
- `-d YYYY-MM-DD`, `--date YYYY-MM-DD`: Optional. Specify the date for data aggregation. Defaults to the latest found `YYYY-MM-DD.json` file in `the-council/aggregated/`.
- `-j`, `--json`: Optional. Export JSON files (containing generated text and metadata) locally in addition to Markdown files.
- `-v`, `--verbose`: Optional. Increases output verbosity for debugging.

**Dependencies**: Python 3, `requests` library.
**Environment Variables**:
- `OPENROUTER_API_KEY`: Required for LLM API calls.
- `HMD_API_ACCESS_TOKEN` (or `HACKMD_API_TOKEN` as fallback): Required for all HackMD API interactions.

---

## `tweet-summarizer.sh` (Deprecated)

> **Note:**  
> This script is now deprecated and has been moved to `scripts/old/tweet-summarizer.sh`.  
> It is no longer maintained as part of the active pipeline.

The functionality for tweet summarization from GitHub activity logs is no longer supported in the main scripts directory. If you need to reference or reuse the old script, you can find it in the `scripts/old/` directory.
For up-to-date automation and content generation, please refer to the current Python-based workflows and scripts described above.