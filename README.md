# elizaOS Knowledge Aggregation System

This repository serves as the central hub for aggregating, processing, and synthesizing knowledge for the elizaOS project. It employs a series of automated workflows and scripts to gather data from various sources, generate insights using LLMs, and disseminate information through different channels.

**Quick Links to Explore Data:**

**Explore**
- Browse all content via GitHub Pages root: https://elizaos.github.io/knowledge/
- Eliza Daily HackMD Book: https://hackmd.io/@elizaos/book

**Updated daily**
(Data for these links is typically refreshed by 02:30 UTC each day.)
- Latest aggregated data: https://elizaos.github.io/knowledge/the-council/aggregated/daily.json
- Latest council briefing: https://elizaos.github.io/knowledge/the-council/council_briefing/daily.json
- Latest ElizaOS AI news summary: https://elizaos.github.io/knowledge/ai-news/elizaos/json/daily.json
- Latest extracted facts: https://elizaos.github.io/knowledge/the-council/facts/daily.json
- Eliza.how docs (llms-full.txt): https://eliza.how/llms-full.txt

This repository serves as the central hub for aggregating, processing, and synthesizing knowledge for the elizaOS project. It employs a series of automated workflows and scripts to gather data from various sources, generate insights using LLMs, and disseminate information through different channels.

---

## Core Data Pipeline & Automation

The system follows a structured pipeline to transform raw data into actionable intelligence:

1.  **External Data Ingestion (`.github/workflows/sync.yml`)**: (Runs at 01:00 UTC)
    *   This workflow runs daily to synchronize data from external repositories and sources. This includes documentation from `elizaOS/eliza` and `madjin/daily-silk`, GitHub activity logs from `elizaos/elizaos.github.io`, and AI news from `M3-org/ai-news`.
    *   Raw synced data is stored in directories like `docs/`, `daily-silk/`, `github/`, and `ai-news/`.

2.  **Daily Fact Extraction (`.github/workflows/extract_daily_facts.yml`)**: (Runs at 01:15 UTC)
    *   This workflow runs `scripts/extract-facts.py` daily after data synchronization.
    *   `scripts/extract-facts.py` takes the daily aggregated data (from the previous day, or requires `aggregate-daily-sources.yml` to have run if processing current day's live data, though its schedule suggests it processes already aggregated data from a prior step if available, or just focuses on what `aggregate-sources.py` can provide it if it were to be run by this workflow directly) and uses an LLM with a specialized prompt to distill significant information.
    *   Outputs are structured JSON facts to `the-council/facts/YYYY-MM-DD.json` and a Markdown version to `hackmd/facts/YYYY-MM-DD.md`.
    *   A permalink `the-council/facts/daily.json` is also created.

3.  **Daily Context Aggregation (`.github/workflows/aggregate-daily-sources.yml`)**: (Runs at 01:30 UTC)
    *   This workflow runs `scripts/aggregate-sources.py` daily.
    *   `scripts/aggregate-sources.py` consolidates data from the synced external sources (e.g., `ai-news/`, `github/summaries/`) and internal structured data into a comprehensive daily JSON file: `the-council/aggregated/YYYY-MM-DD.json`.
    *   A permalink `the-council/aggregated/daily.json` is created, pointing to the latest daily aggregated file.

4.  **Council Briefing Generation (`.github/workflows/generate-council-briefing.yml`)**: (Runs at 02:00 UTC)
    *   Triggered daily after context aggregation, this workflow runs `scripts/generate_council_context.py`.
    *   This script takes `the-council/aggregated/daily.json` as input and uses an LLM (via OpenRouter) with strategic prompts (e.g., `scripts/prompts/strategy/north-star.txt`) to produce a high-level strategic briefing.
    *   The output is saved as `the-council/council_briefing/YYYY-MM-DD.json`, with a permalink `the-council/council_briefing/daily.json`.

5.  **HackMD Note Generation & Backup (`.github/workflows/update_hackmd_notes.yml`)**: (Runs at 02:30 UTC)
    *   This workflow runs daily to manage topical insights on HackMD.
    *   It first executes `scripts/create-hackmd.py` which ensures HackMD notes exist for prompts and updates `book.json`.
    *   Then, it runs `scripts/update-hackmd.py` which uses `the-council/aggregated/daily.json` as context to generate content for each prompt, update HackMD notes, and save local backups.
    *   Changes to `book.json`, `hackmd/**/*.md`, and `hackmd/**/*.json` are committed.

6.  **Daily Discord Briefing (`.github/workflows/daily_discord_briefing.yml`)**: (Runs at 02:35 UTC)
    *   This workflow runs `scripts/webhook.py` daily after all data processing and HackMD updates are complete.
    *   It takes the daily facts file (`the-council/facts/YYYY-MM-DD.json`) for the current date.
    *   It sends a formatted briefing, including summaries and an optional poster, to a specified Discord channel.
    *   Requires `OPENROUTER_API_KEY` and `DISCORD_BOT_TOKEN` secrets for LLM summarization and Discord posting.

## Key Directories

*   `.github/workflows/`: Contains GitHub Actions workflow configurations for automation.
*   `scripts/`: Houses all automation scripts (Python and shell).
    *   `scripts/prompts/`: Contains prompt templates for LLM interactions, organized by category.
*   `the-council/`: Stores daily aggregated data and generated contexts.
    *   `the-council/aggregated/`: Contains daily raw aggregated data (`YYYY-MM-DD.json`) and a `daily.json` permalink. Output of `scripts/aggregate-sources.py`.
    *   `the-council/council_briefing/`: Contains daily strategic council briefings (`YYYY-MM-DD.json`) and a `daily.json` permalink. Output of `scripts/generate_council_context.py`.
    *   `the-council/facts/`: Contains daily extracted facts and insights in JSON format (`YYYY-MM-DD.json`) and a `daily.json` permalink. Output of `scripts/extract-facts.py`.
    *   `the-council/old/`: Contains older council-related files.
*   `hackmd/`: Stores local backups of content generated for HackMD notes, organized by category and prompt name, in both Markdown and JSON formats.
    *   `hackmd/facts/`: Contains Markdown exports of extracted facts (`YYYY-MM-DD.md`).
*   `ai-news/`: Contains synced data from the `M3-org/ai-news` repository.
*   `github/`: Contains synced GitHub activity logs and summaries.
*   `docs/`: Contains synced documentation from `elizaOS/eliza`.
*   `daily-silk/`: Contains synced documentation from `madjin/daily-silk`.
*   `book.json`: A state file mapping prompt names to HackMD note IDs and their update strategies (e.g., 'overwrite'), used by `create-hackmd.py` and `update-hackmd.py`.

## Primary Scripts Overview

*   **`scripts/aggregate-sources.py`**: The main data aggregation engine, creating `the-council/aggregated/YYYY-MM-DD.json`.
*   **`scripts/generate_council_context.py`**: Processes aggregated data from `the-council/aggregated/daily.json` to create strategic council briefings in `the-council/council_briefing/YYYY-MM-DD.json`.
*   **`scripts/create-hackmd.py`**: Initializes HackMD notes for prompts found in `scripts/prompts/`, creating new notes on HackMD if they don't exist. Manages `book.json` by storing HackMD note IDs and their update strategy (defaulting to 'overwrite' for new notes).
*   **`scripts/update-hackmd.py`**: Generates content daily for HackMD notes using prompts from `scripts/prompts/` and data from `the-council/aggregated/daily.json`. It updates each HackMD note's title (with the current date) and overwrites its content with the prompt details and new LLM-generated text. It also updates the main HackMD book index and saves local backups.
*   **`scripts/extract_facts.py`**: Performs deep analysis on aggregated data. As part of the `extract_daily_facts.yml` workflow, it outputs structured facts to `the-council/facts/YYYY-MM-DD.json` and a corresponding Markdown version to `hackmd/facts/YYYY-MM-DD.md`.
*   **`scripts/webhook.py`**: Called by `daily_discord_briefing.yml` to send the daily facts briefing from `the-council/facts/YYYY-MM-DD.json` to a specified Discord channel, with options for LLM summarization and a poster image.

This system is designed to be modular and extensible, allowing for the integration of new data sources and processing steps as the project evolves.

## Repository Structure

The repository is organized into several main directories, each containing information from different sources:

```
.
├── .github/            # GitHub Actions workflows and configurations
│   └── workflows/
├── ai-news/            # AI News summaries from M3-org/ai-news & other specific feeds
│   ├── elizaos/        #   Summaries related to ElizaOS
│   │   ├── dev/
│   │   │   ├── json/
│   │   │   └── md/
│   │   ├── discord/
│   │   │   ├── json/
│   │   │   └── md/
│   │   ├── json/       #   (General ElizaOS json, if any)
│   │   └── md/         #   (General ElizaOS md, if any)
│   ├── hyperfy/        #   Summaries related to Hyperfy
│   │   ├── json/
│   │   └── md/
│   └── ...             #   (other specific ai-news feeds or top-level files)
├── archive/            # Archived discussions and older data (legacy)
│   ├── daily-elizaos/
│   └── ...
├── daily-silk/         # Daily AI news from Discord channel using SILK
├── docs/               # Documentation, blogs, community notes, and versioned docs
│   ├── blog/
│   ├── community/
│   ├── docs/           #   Core documentation (CLI, Core, REST)
│   ├── news/           #   (Potentially older news, distinct from ai-news)
│   ├── packages/
│   ├── partners/
│   ├── src/            #   (Source for Docusaurus if applicable)
│   └── versioned_docs/
├── github/             # GitHub activity logs and generated summaries/stats
│   ├── stats/
│   │   ├── day/
│   │   ├── week/
│   │   └── month/
│   └── summaries/
│       ├── day/
│       ├── week/
│       └── month/
├── hackmd/             # Local backups of generated HackMD content & specific notes
│   ├── comms/
│   ├── council/
│   ├── dev/
│   ├── facts/          #   Markdown exports of extracted facts
│   └── strategy/
├── scripts/            # Scripts for managing repository content & LLM interactions
│   ├── prompts/        #   Prompt templates for generating HackMD notes & other tasks
│   │   ├── comms/
│   │   ├── dev/
│   │   └── strategy/
│   └── special-prompts/
├── the-council/        # Aggregated data, council briefings, and extracted facts
│   ├── aggregated/     #   Daily raw aggregated data (YYYY-MM-DD.json)
│   ├── council_briefing/ # Daily strategic council briefings (YYYY-MM-DD.json)
│   └── facts/          #   Daily extracted facts (JSON) (YYYY-MM-DD.json)
├── book.json           # State file for HackMD notes (IDs, prompts, strategies)
├── README.md           # This file
```

## Data Sources

### Archive
Archive of Discord discussions from various channels related to AI development and communities. This section is being deprecated in favor of more structured data sources.

### Docs
Technical documentation from the [ElizaOS/eliza](https://github.com/elizaOS/eliza) repository, specifically from its `packages/docs` folder. These files contain guides, tutorials, API references, and technical specifications for the ElizaOS system.

### GitHub
Activity logs from [ElizaOS/elizaos.github.io](https://github.com/elizaos/elizaos.github.io) (`_data` branch), organized by day, week, and month. This provides a chronological view of development activities and changes.

Tip: here's a command to turn the JSON stats files into a single text file:

Stats
```bash
jq -r '                     
  "\n=== \(.interval.intervalStart) ===",
  .overview,
  "\nTop Issues:",
  (.topIssues[]? | "- #\(.number) [\(.state)] \(.title) by \(.author) (\(.commentCount) comments)"),
  "\nTop PRs:",
  (.topPRs[]? | "- #\(.number) \(.title) by \(.author) (\(.additions) +, \(.deletions) -)"),
  "\nCompleted Items:",
  (.completedItems[]? | "- \(.type): \(.title) (#\(.prNumber))"),
  "\nTop Contributors:",
  ([.topContributors[]? | "\(.username) (score: \(.totalScore | floor))"] | .[:3] | .[])
' github/stats/month/stats_2025-04*.json > monthly-github-stats.txt
```

User summaries
```bash
jq -r '                       
  map(select(.date | startswith("2025"))) |
  group_by(.date)[] |
  ("=== " + (.[0].date) + " ==="),
  (.[] | .summary, "---"),
  ""
' user_summaries.json > user_summaries.txt
```

### News
Daily AI news summaries generated by [M3-org/ai-news](https://github.com/M3-org/ai-news), an AI-powered news aggregation platform that collects, analyzes, and summarizes information from multiple sources in real-time. The news data is stored in the `gh-pages` branch of the original repository.

### Daily Silk
Daily AI news collected from a Discord channel using [SILK](https://github.com/madjin/daily-silk) and discord.py. The data is automatically fetched, processed, and stored in markdown format, with each file representing a day's worth of AI news and updates. The content is organized chronologically and includes timestamps for each entry. The data is collected daily and provides a comprehensive view of AI developments and announcements.

### AI News
Daily summaries and discussions related to AI, specifically from the ElizaOS and Hyperfy communities, sourced from the [M3-org/ai-news](https://github.com/M3-org/ai-news) repository (`gh-pages` branch). This includes:
- `ai-news/elizaos/`: Summaries and logs from ElizaOS related channels.
- `ai-news/hyperfy/`: Summaries and logs from Hyperfy related channels.

### Scripts & Prompts
The `scripts/` directory contains Python scripts used for automating content generation and updates.
- `scripts/prompts/`: Contains prompt templates categorized into subdirectories (`comms`, `dev`, `strategy`). These templates are used by `scripts/update-hackmd.py` along with daily context data to generate content for specific HackMD notes.
- `scripts/create-hackmd.py`: Creates new HackMD notes for prompts found in `scripts/prompts/` that are not already listed in `book.json`. It populates `book.json` with the note ID and an "overwrite" update strategy.
- `scripts/update-hackmd.py`: Reads the latest daily context data, generates content for each prompt (defined in `book.json`) using an LLM (via OpenRouter). It updates the corresponding HackMD note by overwriting its title (with the current date) and its entire content (placing the prompt details from the local file in `<details>` tags, followed by the LLM-generated text). It also updates the main Book Index note on HackMD and saves local backups.

### HackMD Backups
The `hackmd/` directory stores local backups of the content generated by `scripts/update-hackmd.py`. The structure mirrors the `scripts/prompts/` categories, with each prompt having its own subdirectory containing dated markdown files (e.g., `hackmd/comms/discord-announcement/2025-05-05.md`) and optionally JSON files.

### Packages
Documentation from the [ElizaOS package ecosystem](https://eliza.how/packages), which includes a collection of adapters, clients, and plugins that extend the functionality of the ElizaOS platform. This directory contains detailed information about each package's features, configuration, and integration methods.

### Partners
Information about [ElizaOS partners and integrations](https://eliza.how/partners), including details about official partnerships, supported platforms, and integration capabilities. This documentation helps users understand the broader ecosystem of services and platforms that work with ElizaOS.

## Usage

This repository is designed to be used as a knowledge source for RAG systems. The markdown files can be ingested into vector databases or other retrieval systems to provide context for AI agents.

### For AI Researchers and Developers

1. Clone this repository to your local machine or server
2. Use the files as a corpus for training or fine-tuning AI models
3. Index the content for retrieval in RAG systems
4. Reference specific sections in your AI prompts for domain-specific knowledge

## Contributing

### Adding New Sources

To add a new source to the knowledge repository:

1. Create a dedicated directory for the source
2. Ensure all files are in markdown (.md) format when possible
3. Update this README with information about the new source
4. Create a GitHub action to keep the source updated (see below)

### GitHub Actions

This repository uses GitHub Actions to automatically update content from various sources. To contribute a new action:

1. Create a new workflow file in `.github/workflows/`
2. Configure the action to fetch and format data from the source
3. Set an appropriate schedule for updates
4. Test the action to ensure it correctly updates the repository

#### Update HackMD Notes (`update_hackmd_notes.yml`)
This workflow runs weekly on Fridays at 18:00 UTC and can be triggered manually. It executes the following steps:
1.  **Install Dependencies**: Sets up Python, Node.js, and installs necessary packages (`requests`, `@hackmd/hackmd-cli`).
2.  **Create Notes**: Runs `scripts/create-hackmd.py` to check for new prompt files in `scripts/prompts/` and creates corresponding notes on HackMD if they don't exist in `book.json`. Requires `HMD_API_ACCESS_TOKEN` secret.
3.  **Update Notes**: Runs `scripts/update-hackmd.py` to generate content using the latest daily data and prompts, then updates the HackMD notes and the main book index. Requires `HMD_API_ACCESS_TOKEN` and `OPENROUTER_API_KEY` secrets.
4.  **Commit Changes**: Commits any modifications to `book.json` and the generated markdown files in the `hackmd/` directory back to the repository.

---

## Strategic Context Summaries (For AI Council & Background)

These summaries encapsulate the core mission, vision, and key initiatives, derived from project blog posts.

### Auto.fun Introduction Summary (`docs/blog/autofun-intro.mdx`)

Auto.fun is an AI-native, creator-first token launchpad designed for sustainable AI/crypto projects. It aims to balance fair community access with project funding needs through mechanisms like bonding curves and liquidity NFTs. Key features include a no-code agent builder, AI-generated marketing tools, and integration with the elizaOS ecosystem. It serves as a core product driving value back to the native token ($ai16z) through buybacks and liquidity pairing.

### ElizaOS Mission Summary (`docs/blog/mission.mdx`)

The elizaOS mission is to build an extensible, modular, open-source AI agent framework for Web2/Web3, seeing agents as steps toward AGI. Core values are Autonomy, Modularity, and Decentralization. Key products include the framework itself, DegenSpartanAI (trading agent), Autonomous Investor/Trust Marketplace (social trading intelligence), and the Agent Marketplace/auto.fun (launchpad).

### ElizaOS Reintroduction Summary (`docs/blog/reintroduction.mdx`)

elizaOS is an open-source "operating system for AI agents" aimed at decentralizing AI development away from corporate control. It's built on three pillars: 1) The Eliza Framework (TypeScript toolkit for persistent, interoperable agents), 2) AI-Enhanced Governance (building autonomous DAOs), and 3) Eliza Labs (R&D for future capabilities like v2, Trust Marketplace, auto.fun, DegenSpartanAI, Eliza Studios). The native Solana token coordinates the ecosystem and captures value. The vision is an intelligent internet built on open protocols and collaboration.

### Taming Information Summary (`docs/blog/taming_info.mdx`)

Addresses the challenge of information scattered across platforms (Discord, GitHub, X). Proposes using AI agents as "bridges" to collect, wrangle (summarize/tag), and distribute information in various formats (JSON, MD, RSS, dashboards, 3D shows). Showcases an AI News system and AI Assistants for tech support as examples. Emphasizes treating documentation as a first-class citizen to empower AI assistants and streamline community operations.

