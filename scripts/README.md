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

**Purpose**: Generates a HackMD note from a template and a given content.

**Details**:
This Python script takes a template file and a content string as input, and generates a complete HackMD note from them. The template file is typically a plain text file with placeholders that are replaced with the provided content.

**Usage**:
```bash
./scripts/create-hackmd.py -t path/to/template.txt -c "This is the content to be inserted into the template."
```

**Dependencies**: Python 3.

---

## `tweet-summarizer.sh` (Deprecated)

> **Note:** This script is now deprecated and has been moved to `scripts/old/`.  
> It is no longer maintained or used in the main automation workflows.

The original `tweet-summarizer.sh` script generated tweets from GitHub activity logs in the elizaOS and auto.fun brand voices, using OpenRouter and prompt files.  
If you need to reference or reuse this functionality, please see `scripts/old/tweet-summarizer.sh`.