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
This script takes the comprehensive JSON output from `scripts/aggregate_sources.py` (e.g., `the-council/aggregated/YYYY-MM-DD.json`) and uses a specialized LLM prompt (`scripts/prompts/news_show/fact_extraction_prompt.txt`) to perform a deep analysis of the entire dataset in a single LLM call. It aims to distill the most significant information into a structured JSON output, organized by thematic categories such as Twitter news, GitHub updates (new issues/PRs, overall focus), Discord updates, user feedback, strategic insights, and market analysis. The output includes an overall summary and, for each extracted piece of information, `source_keys` tracing back to the original data in the input JSON. This script is designed to produce actionable intelligence for briefings or to power other content generation processes.

**Typical Usage**:
```bash
python scripts/extract-facts.py -i path/to/the-council/aggregated/YYYY-MM-DD.json -o path/to/the-council/extracted_facts/YYYY-MM-DD.json
```

---

## `create-hackmd.py`

**Purpose**: Manages HackMD notes corresponding to prompt files in `scripts/prompts/`. Ensures a HackMD note exists for each prompt, creating it if necessary with initial content (including the prompt itself). It populates/updates `book.json` to map prompt names to their HackMD note IDs and their update strategy (defaulting to 'overwrite' for new notes). Can also create/update a main book index note on HackMD.

**Details**:
This script iterates through all `*.txt` prompt files found recursively within the `scripts/prompts/` directory. For each prompt:
- It determines a `category_tag` based on the prompt file's parent directory (e.g., `comms`, `dev`, `strategy`).
- It checks `book.json` to see if a note already exists for the `prompt_name` (derived from the filename).
- If a note does not exist (or if its ID is missing in `book.json`), the script creates a new note on HackMD via the API.
    - The initial title of the new HackMD note includes the prompt name and the current date (e.g., "Developer Update - YYYY-MM-DD").
    - The initial content includes this title, the `category_tag`, and the full content of the prompt file itself, wrapped in HTML `<details>` tags.
    - The new note's ID and an `update_strategy` of "overwrite" are then saved to `book.json` for that `prompt_name`.
- If the `-b <permalink>` argument is provided, the script will also manage a main "Book Index" HackMD note:
    - If the Book Index note doesn't exist (ID not in `book.json` under `__BOOK_INDEX__`), it creates a new HackMD note with the title "Eliza Daily" (or as configured) and attempts to set its permalink to the one provided.
    - It then generates the content for this Book Index (a list of links to all other notes in `book.json`, grouped by category) and updates the Book Index note on HackMD or saves it locally.

**Usage**:
```bash
./scripts/create-hackmd.py [-b BOOK_PERMALINK] [-v]
```
- `-b BOOK_PERMALINK`, `--book BOOK_PERMALINK`: Optional. If provided, creates/updates the Book Index note on HackMD, attempting to set its permalink to `BOOK_PERMALINK`.
- `-v`, `--verbose`: Optional. Increases output verbosity for debugging.

**Dependencies**: Python 3, `requests` library.
**Environment Variables**:
- `HMD_API_ACCESS_TOKEN` (or `HACKMD_API_TOKEN` as fallback): Required for all HackMD API interactions.

---

## `update-hackmd.py`

**Purpose**: Generates daily content for HackMD notes based on prompts and aggregated data, then updates these notes on HackMD, including their titles and full content.

**Details**:
This script is central to the daily content update process for HackMD notes.
- It reads the `book.json` state file to get the list of `prompt_name`s and their corresponding HackMD `note_id`s and `update_strategy`.
- It uses the latest aggregated data from `the-council/aggregated/daily.json` as context (or a specific date's file if the `-d` flag is used).
- For each prompt listed in `book.json` (excluding `__BOOK_INDEX__`):
    1.  It reads the associated prompt template file from `scripts/prompts/[category]/[prompt_name].txt`.
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
- After processing all individual prompt notes, it regenerates the content for the main HackMD Book Index note (whose ID is stored under `__BOOK_INDEX__` in `book.json`) and updates it on HackMD.

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