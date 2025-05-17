# elizaOS Knowledge Aggregation System

This repository serves as the central hub for aggregating, processing, and synthesizing knowledge for the elizaOS project. It employs a series of automated workflows and scripts to gather data from various sources, generate insights using LLMs, and disseminate information through different channels.

## Core Data Pipeline & Automation

The system follows a structured pipeline to transform raw data into actionable intelligence:

1.  **External Data Ingestion (`.github/workflows/sync.yml`)**:
    *   This workflow runs daily to synchronize data from external repositories and sources. This includes documentation from `elizaOS/eliza` and `madjin/daily-silk`, GitHub activity logs from `elizaos/elizaos.github.io`, and AI news from `M3-org/ai-news`.
    *   Raw synced data is stored in directories like `docs/`, `daily-silk/`, `github/`, and `ai-news/`.
    *   A `sync-report.md` is generated.

2.  **Daily Context Aggregation (`.github/workflows/generate_daily_context.yml`)**:
    *   This workflow runs `scripts/aggregate-sources.py` daily.
    *   `scripts/aggregate-sources.py` consolidates data from the synced external sources (e.g., `ai-news/`, `github/summaries/`) and internal structured data into a comprehensive daily JSON file: `the-council/aggregated/YYYY-MM-DD.json`.
    *   A permalink `the-council/aggregated/daily.json` is created, pointing to the latest daily aggregated file.

3.  **Council Context Generation (`.github/workflows/generate_council_context.yml`)**:
    *   Triggered daily after context aggregation, this workflow runs `scripts/generate_council_context.py`.
    *   This script takes `the-council/aggregated/daily.json` as input and uses an LLM (via OpenRouter) with strategic prompts (e.g., `scripts/prompts/strategy/north-star.txt`) to produce a high-level strategic briefing.
    *   The output is saved as `the-council/council_briefing/YYYY-MM-DD.json`, with a permalink `the-council/council_briefing/daily.json`.

4.  **HackMD Note Generation & Backup (`.github/workflows/update_hackmd_notes.yml`)**:
    *   This workflow runs weekly (and can be manually triggered) to manage topical insights on HackMD.
    *   It first executes `scripts/create-hackmd.py` which:
        *   Identifies prompt files in `scripts/prompts/` (organized by category in subdirectories).
        *   Ensures a corresponding HackMD note exists for each prompt, creating new ones if necessary.
        *   Updates the `book.json` file, which maps prompt names to HackMD note IDs and their `update_strategy` (defaulting to "overwrite" for new notes), serving as a state file.
        *   Creates an initial HackMD book index note if specified.
    *   Then, it runs `scripts/update-hackmd.py` which:
        *   Uses `the-council/aggregated/daily.json` (latest aggregated data) as context.
        *   For each prompt defined in `book.json`:
            *   It calls an LLM to generate content based on the prompt instructions (from the local `.txt` file) and the aggregated daily data.
            *   It updates the corresponding HackMD note's title (with the prompt name and current date) and its entire content.
            *   The new content includes the prompt details (from the local prompt file, wrapped in `<details>` tags) followed by the LLM-generated text for the day, effectively overwriting previous content as per the "overwrite" strategy.
        *   Saves the LLM-generated main content locally to `hackmd/[category]/[prompt_name]/YYYY-MM-DD.md`.
        *   Optionally (if the `-j` flag is used), saves a structured JSON object (including `prompt_name`, `category`, `date`, `generated_text`, and `source_references`) locally to `hackmd/[category]/[prompt_name]/YYYY-MM-DD.json`.
        *   Updates the main HackMD book index note with links to all content notes, categorized.
    *   Finally, changes to `book.json`, `hackmd/**/*.md`, and `hackmd/**/*.json` are committed to the repository.

5.  **Fact Extraction (Manual/Future Automation)**:
    *   The `scripts/extract_facts.py` script can be run on the output of `scripts/aggregate-sources.py` (`the-council/aggregated/YYYY-MM-DD.json`).
    *   It uses a specialized LLM prompt (`scripts/prompts/news_show/fact_extraction_prompt.txt`) to perform a deep analysis of the entire dataset in a single LLM call.
    *   Its goal is to distill significant information into a structured JSON output, organized by thematic categories (Twitter, GitHub, Discord, user feedback, strategic insights, market analysis), including source traceability.
    *   The output is typically saved to `the-council/extracted_facts/YYYY-MM-DD.json`.

## Key Directories

*   `.github/workflows/`: Contains GitHub Actions workflow configurations for automation.
*   `scripts/`: Houses all automation scripts (Python and shell).
    *   `scripts/prompts/`: Contains prompt templates for LLM interactions, organized by category.
*   `the-council/`: Stores daily aggregated data and generated contexts.
    *   `the-council/aggregated/`: Contains daily raw aggregated data (`YYYY-MM-DD.json`) and a `daily.json` permalink. Output of `scripts/aggregate-sources.py`.
    *   `the-council/council_briefing/`: Contains daily strategic council briefings (`YYYY-MM-DD.json`) and a `daily.json` permalink. Output of `scripts/generate_council_context.py`.
    *   `the-council/extracted_facts/`: Contains daily extracted facts and insights (`YYYY-MM-DD.json`). Output of `scripts/extract_facts.py`.
*   `hackmd/`: Stores local backups of content generated for HackMD notes, organized by category and prompt name, in both Markdown and JSON formats.
*   `ai-news/`: Contains synced data from the `M3-org/ai-news` repository.
*   `github/`: Contains synced GitHub activity logs and summaries.
*   `docs/`: Contains synced documentation from `elizaOS/eliza`.
*   `daily-silk/`: Contains synced documentation from `madjin/daily-silk`.
*   `book.json`: A state file mapping prompt names to HackMD note IDs and their update strategies (e.g., 'overwrite'), used by `create-hackmd.py` and `update-hackmd.py`.

## Primary Scripts Overview

*   **`scripts/aggregate-sources.py`**: The main data aggregation engine, creating `the-council/aggregated/YYYY-MM-DD.json`.
*   **`scripts/generate_council_context.py`**: Processes aggregated data from `the-council/aggregated/daily.json` to create strategic council briefings in `the-council/council_briefing/YYYY-MM-DD.json`.
*   **`scripts/create-hackmd.py`**: Initializes HackMD notes for prompts found in `scripts/prompts/`, creating new notes on HackMD if they don't exist. Manages `book.json` by storing HackMD note IDs and their update strategy (defaulting to 'overwrite' for new notes).
*   **`scripts/update-hackmd.py`**: Generates content daily for HackMD notes using prompts from `scripts/prompts/` and data from `the-council/aggregated/daily.json`. It updates each HackMD note's title (with the current date) and overwrites its content with the prompt details and new LLM-generated text. It also updates the main HackMD book index and saves local backups of the generated content.
*   **`scripts/extract_facts.py`**: Performs deep analysis on data from `the-council/aggregated/YYYY-MM-DD.json` to extract categorized facts and insights into `the-council/extracted_facts/YYYY-MM-DD.json`.

This system is designed to be modular and extensible, allowing for the integration of new data sources and processing steps as the project evolves.

## Repository Structure

The repository is organized into several main directories, each containing information from different sources:

```
.
├── archive/            # Archived discussions (legacy, to be deprecated)
├── docs/               # Documentation from elizaOS (from elizaOS/eliza repo)
├──── news/             # Daily AI news summaries
└──── partners/         # Information about elizaOS partners and integrations
├──── static/packages/  # Documentation from elizaOS plugin ecosystem
├── github/             # GitHub activity logs organized by day/week/month
├── daily-silk/         # Daily AI news from Discord channel using SILK
├── ai-news/            # AI News summaries from M3-org/ai-news
├──── elizaos/          # Summaries related to ElizaOS
└──── hyperfy/          # Summaries related to Hyperfy
├── scripts/            # Scripts for managing repository content
├──── prompts/          # Prompt templates for generating HackMD notes
├────── comms/          #   Communication-related prompts
├────── dev/            #   Development-related prompts
└────── strategy/       #   Strategy-related prompts
├── hackmd/             # Local backups of generated HackMD content
├──── comms/            #   Mirrors prompts/comms structure
├──── dev/              #   Mirrors prompts/dev structure
└──── strategy/         #   Mirrors prompts/strategy structure
└── book.json           # State file mapping prompts to HackMD note IDs
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

