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
*   **Purpose**: Updates HackMD notes by processing prompts, generates JSON backups, and updates `book.json`.
*   **Key Actions**:
    *   Sets up Python.
    *   Installs dependencies from `requirements.txt`.
    *   Ensures `scripts/update-hackmd.py` is executable.
    *   Runs `scripts/update-hackmd.py`: This script iterates through prompt files in `scripts/prompts/`, processes them with an LLM, and saves the output as both `.md` and structured `.json` files in the `hackmd/[category]/[prompt_name]/` directory structure. It also updates `book.json`.
    *   (The step to run `scripts/compile_show_context.py` needs review as this script was renamed/deleted. The original intent was to compile JSON files from `hackmd/` processing into `ai-news-show-feed/YYYY-MM-DD.json`.)
    *   Commits and pushes changes to `book.json`, `hackmd/**/*.md`, and `hackmd/**/*.json`.
    *   Includes `permissions: contents: write` to allow committing back to the repository.

### 5. `extract_daily_facts.yml`

*   **Name**: `Extract Daily Facts and Convert to Markdown`
*   **Trigger**: Daily at 01:15 UTC (after aggregation, before council briefing) and on `workflow_dispatch`.
*   **Purpose**: Runs fact extraction on aggregated data, outputting both JSON and Markdown. Creates permalinks.
*   **Key Actions**:
    *   Sets up Python.
    *   Installs dependencies.
    *   Gets yesterday's date.
    *   Runs `scripts/extract-facts.py` with inputs for aggregated data and outputs for JSON facts and Markdown facts.
    *   Creates `the-council/facts/daily.json` permalink.
    *   Commits `the-council/facts/*.json`, `hackmd/facts/*.md`, and `the-council/facts/daily.json`.

## Workflow Execution Order

While some workflows can be run manually (`workflow_dispatch`), the scheduled daily runs are now staggered as follows:

1.  **01:00 UTC**: `sync.yml` (Sync External Data Sources)
2.  **01:15 UTC**: `extract_daily_facts.yml` (Extract Daily Facts)
3.  **01:30 UTC**: `aggregate-daily-sources.yml` (Aggregate Daily Sources)
4.  **02:00 UTC**: `generate-council-briefing.yml` (Generate Council Briefing)
5.  **02:30 UTC**: `update_hackmd_notes.yml` (Update HackMD Notes)

This order ensures that data is first synced, then facts are extracted, then data is aggregated, then processed for council, and finally HackMD notes are updated based on the latest state.

## General Notes

-   All workflows require `contents: write` permissions to commit changes back to the repository.
-   Some workflows use a `GH_PAT` (Personal Access Token) or `GITHUB_TOKEN` for authenticated operations.
-   Scripts used by these workflows are generally located in the `scripts/` directory at the root of the repository. 
