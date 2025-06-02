# GitHub Actions Workflows

This directory contains GitHub Actions workflows used to automate various tasks for the `knowledge` repository.

## Workflow Overview

This directory contains GitHub Actions workflows to automate various aspects of knowledge aggregation, processing, and synchronization for the elizaOS project.

### 1. `sync.yml`

*   **Name**: `Sync External Data Sources`
*   **Trigger**: Daily at 01:00 UTC and on `workflow_dispatch` (manual trigger).
*   **Purpose**: Synchronizes data from various external repositories and sources into the current repository. This includes:
    *   Documentation from `elizaOS/eliza` (v2-develop branch) into `docs/core` and `docs/rest`.
    *   Documentation from `madjin/daily-silk` into `daily-silk/docs`.
    *   GitHub activity logs from `elizaos/elizaos.github.io` into `github/activity_logs`.
    *   AI news content (`elizaos/` and `hyperfy/` folders) from the `gh-pages` branch of `M3-org/ai-news` into the local `ai-news/` directory.
*   **Key Actions**: Uses `actions/checkout` and `rsync` for file synchronization. Includes `continue-on-error: true` for individual sync steps to enhance robustness.

### 2. `aggregate-daily-sources.yml` (Formerly `generate_daily_context.yml`)

*   **Name**: `Aggregate Daily Sources`
*   **Trigger**: Daily at 01:30 UTC and on `workflow_dispatch`.
*   **Purpose**: Generates a comprehensive daily aggregated JSON context file.
*   **Key Actions**:
    *   Sets up Python.
    *   Ensures `scripts/aggregate-sources.py` is executable.
    *   Runs `scripts/aggregate-sources.py` to collect data from various local paths (populated by `sync.yml` and other processes) and saves it to `the-council/aggregated/YYYY-MM-DD.json`.
    *   Creates a permalink `the-council/aggregated/daily.json` pointing to the latest daily file.
    *   Commits and pushes the generated JSON file and its permalink.

### 3. `generate-council-briefing.yml` (Formerly `generate_council_context.yml`)

*   **Name**: `Generate Council Briefing`
*   **Trigger**: Daily at 02:00 UTC and on `workflow_dispatch`.
*   **Purpose**: Takes the aggregated daily context and generates a specialized briefing JSON output tailored for council review, using an LLM for synthesis.
*   **Key Actions**:
    *   Sets up Python.
    *   Ensures `scripts/aggregate-sources.py` and `scripts/generate_council_context.py` are executable.
    *   Runs `scripts/aggregate-sources.py` (as input for the council script, ensuring it has the latest aggregated data available if run independently or if there are intermediate changes).
    *   Runs `scripts/generate_council_context.py`, which takes the output of `aggregate-sources.py` (e.g., `the-council/aggregated/YYYY-MM-DD.json`) and a strategic prompt, processes it with an LLM (via `OpenRouter API`), and saves the result to `the-council/council_briefing/YYYY-MM-DD.json`.
    *   Creates a permalink `the-council/council_briefing/daily.json`.
    *   Commits and pushes the generated council briefing and its permalink.

### 4. `update_hackmd_notes.yml`

*   **Name**: `Update HackMD Notes`
*   **Trigger**: Daily at 02:30 UTC and on `workflow_dispatch`.
*   **Purpose**: Updates HackMD notes based on various configurations in `book.json`. This includes processing LLM prompts for some notes and syncing content from local source directories for others. It also generates local backups of LLM-generated content and updates `book.json` if new notes are created by helper scripts.
*   **Key Actions**:
    *   Sets up Python and Node.js.
    *   Installs dependencies (e.g., `requests` for Python, `@hackmd/hackmd-cli` globally).
    *   Ensures `scripts/update-hackmd.py` (and potentially `scripts/create-hackmd.py`) are executable.
    *   Optionally runs `scripts/create-hackmd.py` to initialize new notes in `book.json` if needed (this step seems to primarily check existing mappings).
    *   Runs `scripts/update-hackmd.py`:
        *   **LLM Prompt Processing**: For notes configured with prompts (typically found in `scripts/prompts/`), it processes these with an LLM, updates the corresponding HackMD note via API, and saves the generated content locally as `.md` and structured `.json` files in the `hackmd/[category]/[prompt_name]/` directory structure.
        *   **Direct Content Syncing**: For notes in `book.json` (including those under `CUSTOM_HEADER_LINKS`) that have a `source_directory` specified (e.g., `github/summaries/day/` or `ai-news/elizaos/md/`), the script reads the latest/relevant markdown file directly from that local `source_directory` and updates the content of the corresponding HackMD note via API using the title specified in `book.json` (e.g., `hackmd_note_title`). These source files are *not* copied into the `hackmd/` Git directory by this script.
        *   **Book Index Update**: Updates the main HackMD book index note (`__BOOK_INDEX__` in `book.json`) with links to all managed notes.
    *   Commits and pushes changes to `book.json` (if modified by `create-hackmd.py`) and any files created or changed within the `hackmd/**/*.md` and `hackmd/**/*.json` paths (primarily the local backups of LLM-generated content).
    *   Includes `permissions: contents: write` to allow committing back to the repository.

### 5. `extract_daily_facts.yml`

*   **Name**: `Extract Daily Facts and Convert to Markdown`
*   **Trigger**: Daily at 01:15 UTC (after aggregation, before council briefing) and on `workflow_dispatch`.
*   **Purpose**: Runs fact extraction on aggregated data, outputting both JSON and Markdown. This includes processing user feedback in a way that prepares it for sentiment analysis. Creates permalinks.
*   **Key Actions**:
    *   Sets up Python.
    *   Installs dependencies.
    *   Gets yesterday's date.
    *   Runs `scripts/extract-facts.py` with inputs for aggregated data and outputs for JSON facts and Markdown facts.
    *   Creates `the-council/facts/daily.json` permalink.
    *   Commits `the-council/facts/*.json`, `hackmd/facts/*.md`, and `the-council/facts/daily.json`.

### 6. `daily_discord_briefing.yml`

*   **Name**: `Daily Discord Facts Briefing`
*   **Trigger**: Daily at 02:35 UTC and on `workflow_dispatch`.
*   **Purpose**: Sends the daily facts briefing (from `the-council/facts/YYYY-MM-DD.json`) to a specified Discord channel using the `scripts/webhook.py` script. The briefing includes a visual representation of user sentiment.
*   **Key Actions**:
    *   Sets up Python.
    *   Installs `discord.py` and `