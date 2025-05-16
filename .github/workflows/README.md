# GitHub Actions Workflows

This directory contains GitHub Actions workflows used to automate various tasks for the `knowledge` repository.

## Available Workflows

### 1. Sync Knowledge Sources (`sync.yml`)

-   **Purpose**: Regularly synchronizes knowledge from various external sources into this repository.
-   **Triggers**:
    -   Scheduled: Daily at 4 AM UTC.
    -   Manual: Can be triggered via `workflow_dispatch`.
-   **Sources Synced**:
    -   ElizaOS Documentation (from `elizaOS/eliza` repository, `v2-develop` branch).
    -   Daily Silk Documentation (from `madjin/daily-silk` repository).
    -   GitHub Activity Logs (from `elizaos/elizaos.github.io` repository, `_data` branch).
    -   AI News (ElizaOS & Hyperfy) (from `M3-org/ai-news` repository, `gh-pages` branch).
-   **Output**: Updates directories like `docs/`, `github/`, `daily-silk/`, `ai-news/`, and generates a `sync-report.md`.
-   **Robustness**: Individual sync steps are configured with `continue-on-error: true` to prevent one failure from stopping the entire workflow.

### 2. Generate Daily Council Context (`generate_council_context.yml`)

-   **Purpose**: Generates a daily context file for "The Council," likely using AI to process aggregated data.
-   **Triggers**:
    -   Scheduled: Daily at 6 AM UTC (intended to run after `Sync Knowledge Sources`).
    -   Manual: Can be triggered via `workflow_dispatch`.
-   **Process**:
    1.  Runs `scripts/aggregate-sources.sh` to generate a daily aggregated data file (`the-council/YYYY-MM-DD.json`).
    2.  Runs `scripts/generate_council_context.py` using the aggregated data and an AI model (via OpenRouter) to produce `the-council/council_context_YYYY-MM-DD.json`.
    3.  Creates a permalink `the-council/council_daily.json`.
-   **Dependencies**: Requires `OPENROUTER_API_KEY` secret.

### 3. Generate Daily Context Map (`generate_daily_context.yml`)

-   **Purpose**: Aggregates data from various sources within the repository into a daily context map. This map is likely used by other processes (e.g., `Generate Daily Council Context`).
-   **Triggers**:
    -   Scheduled: Daily at 5 AM UTC.
    -   Manual: Can be triggered via `workflow_dispatch`.
-   **Process**:
    1.  Runs `scripts/aggregate-sources.sh`.
    2.  Creates `the-council/YYYY-MM-DD.json`.
    3.  Creates a permalink `the-council/daily.json`.

### 4. Update HackMD Notes Weekly (`update_hackmd_notes.yml`)

-   **Purpose**: Creates new HackMD notes (if needed) and updates existing ones weekly, then backs them up to the repository.
-   **Triggers**:
    -   Scheduled: Every Friday at 6 PM UTC.
    -   Manual: Can be triggered via `workflow_dispatch`.
-   **Process**:
    1.  Installs Python, Node.js, and dependencies (`requests`, `@hackmd/hackmd-cli`).
    2.  Runs `scripts/create-hackmd.py` to potentially create new notes on HackMD.
    3.  Runs `scripts/update-hackmd.py` to update content on HackMD and potentially pull updates locally.
    4.  Commits changes to `book.json` and files in `hackmd/**/*.md`.
-   **Dependencies**: Requires `HMD_API_ACCESS_TOKEN` and `OPENROUTER_API_KEY` secrets.

## General Notes

-   All workflows require `contents: write` permissions to commit changes back to the repository.
-   Some workflows use a `GH_PAT` (Personal Access Token) or `GITHUB_TOKEN` for authenticated operations.
-   Scripts used by these workflows are generally located in the `scripts/` directory at the root of the repository. 