# elizaOS Knowledge Aggregation System

This repository serves as the central hub for aggregating, processing, and synthesizing knowledge for the elizaOS project. It employs a series of automated workflows and scripts to gather data from various sources, generate insights using LLMs, and disseminate information through different channels.

## 📚 Comprehensive Documentation

**All major directories now contain detailed README documentation!** Each README provides:
- **Technical specifications** and data formats
- **Integration patterns** and data flow diagrams  
- **Usage examples** with practical bash commands
- **Quality metrics** and performance characteristics
- **Troubleshooting guides** and best practices

**Directory Documentation:**
- **[Core Processing](the-council/README.md)**: Data aggregation, fact extraction, strategic analysis
- **[AI Intelligence](ai-news/README.md)**: Multi-source news aggregation (1,640+ files)
- **[GitHub Analytics](github/README.md)**: Development activity tracking (900+ files)
- **[Community Data](daily-silk/README.md)**: Discord AI news collection (25,000+ lines)
- **[Generated Content](hackmd/README.md)**: LLM-powered content creation and backup
- **[Visual Assets](posters/README.md)**: Automated poster generation (448+ images)
- **[Episode Database](clanktank/README.md)**: Business pitch show scripts (31 episodes)
- **[Historical Archive](archive/README.md)**: 7+ months of preserved data (1,813+ files)

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

## 🚀 Getting Started

**For Developers & Researchers:**
1. **Start with [the-council/README.md](the-council/README.md)** - Understand the core data processing pipeline
2. **Explore [ai-news/README.md](ai-news/README.md)** - Learn about multi-source intelligence gathering  
3. **Review [scripts/README.md](scripts/)** - See automation tools and deployment guides
4. **Check [CLAUDE.md](CLAUDE.md)** - Development guidelines and system architecture

**For Data Analysis:**
- **[github/README.md](github/README.md)** - 900+ files of development activity analytics
- **[daily-silk/README.md](daily-silk/README.md)** - 25,000+ lines of community AI news
- **[archive/README.md](archive/README.md)** - 7+ months of historical data (1,813+ files)

**For Content Creation:**
- **[hackmd/README.md](hackmd/README.md)** - LLM-generated content creation and management
- **[posters/README.md](posters/README.md)** - Automated visual content generation (448+ images)

---

## 🔌 MCP Server Integration

This repository includes a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that exposes the knowledge base to AI assistants like Claude. See **[mcp-server/README.md](mcp-server/README.md)** for full documentation.

### Quick Start

```bash
cd mcp-server && npm install && npm run build
```

### Claude Desktop Configuration

Add to your Claude Desktop MCP settings:

```json
{
  "mcpServers": {
    "elizaos-knowledge": {
      "command": "node",
      "args": ["/path/to/knowledge/mcp-server/dist/index.js"],
      "env": {
        "KNOWLEDGE_BASE_PATH": "/path/to/knowledge"
      }
    }
  }
}
```

### Available Tools

| Tool | Description |
|------|-------------|
| `get_daily_briefing` | Get aggregated intelligence from all sources |
| `get_facts` | Get LLM-extracted facts and insights |
| `get_council_briefing` | Get strategic analysis for leadership |
| `list_available_dates` | Discover available historical data |
| `search_knowledge` | Full-text search across all briefings |

### Example Queries

Once connected, you can ask Claude:
- "What happened in the ElizaOS community today?"
- "Search for discussions about MCP integration"
- "Get the council briefing from yesterday"

---

## Core Data Pipeline & Automation

The system follows a structured pipeline to transform raw data into actionable intelligence:

### Daily Automation Schedule (UTC)
- **01:00** - External Data Ingestion (`.github/workflows/sync.yml`)
- **01:15** - Daily Fact Extraction (`.github/workflows/extract_daily_facts.yml`)
- **01:30** - Context Aggregation (`.github/workflows/aggregate-daily-sources.yml`)
- **02:00** - Council Briefing Generation (`.github/workflows/generate-council-briefing.yml`)
- **02:30** - HackMD Note Updates (`.github/workflows/update_hackmd_notes.yml`)
- **04:00** - Poster Generation (`.github/workflows/generate-posters.yml`)
- **04:30** - Discord Briefing (`.github/workflows/daily_discord_briefing.yml`)

### Pipeline Details

1.  **External Data Ingestion (`.github/workflows/sync.yml`)**: (Runs at 01:00 UTC)
    *   This workflow runs daily to synchronize data from external repositories and sources. This includes documentation from `elizaOS/eliza` and `madjin/daily-silk`, GitHub activity logs from `elizaos/elizaos.github.io`, AI news from `M3-org/ai-news`, and episode data from `m3-org/clanktank` and `m3-org/the-council`.
    *   Raw synced data is stored in directories like `docs/`, `daily-silk/`, `github/`, `ai-news/`, `clanktank/episodes/`, and `the-council/episodes/`.

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

6.  **Enhanced Poster Generation (`.github/workflows/generate-posters.yml`)**: (Runs at 04:00 UTC)
    *   This workflow generates visual poster content using the enhanced `scripts/posters-enhanced.sh` script.
    *   Features multiple rendering engines (wkhtmltoimage, Chromium, ImageMagick) with robust fallback handling.
    *   Creates date-stamped posters (YYYY-MM-DD_category.png) to avoid Discord caching issues.
    *   Generates 16+ poster categories daily with ElizaOS branding and responsive layouts.
    *   All posters are hosted on GitHub Pages for reliable distribution.

7.  **Daily Discord Briefing (`.github/workflows/daily_discord_briefing.yml`)**: (Runs at 04:30 UTC)
    *   This workflow runs `scripts/webhook.py` daily after all data processing and poster generation are complete.
    *   Uses yesterday's date-stamped poster to avoid GitHub Pages deployment lag and Discord caching issues.
    *   Includes automatic poster cleanup and sends formatted briefings with LLM-generated summaries.
    *   Integrates rich Discord embeds with poster images hosted on GitHub Pages.
    *   Requires `OPENROUTER_API_KEY` and `DISCORD_BOT_TOKEN` secrets for LLM summarization and Discord posting.

## Key Directories

Each major directory contains comprehensive documentation. Click the links below to explore detailed information about each component:

### Core Processing Hub
*   **[`the-council/`](the-council/README.md)**: Central data processing hub containing daily aggregated data, strategic council briefings, and extracted facts
    *   `aggregated/`: Daily raw aggregated data (`YYYY-MM-DD.json`) from all sources
    *   `council_briefing/`: Strategic council briefings with high-level analysis  
    *   `facts/`: Daily extracted facts and insights with source tracing
    *   `episodes/`: Episode data from strategic discussions

### Data Sources & Intelligence
*   **[`ai-news/`](ai-news/README.md)**: Multi-source AI intelligence (1,640+ files) from elizaOS and Hyperfy ecosystems
*   **[`github/`](github/README.md)**: GitHub activity analytics (900+ files) with daily/weekly/monthly summaries and statistics  
*   **[`daily-silk/`](daily-silk/README.md)**: Daily AI news from Discord community (167+ files, 25,000+ lines)
*   **[`docs/`](docs/)**: Technical documentation synced from `elizaOS/eliza` repository

### Generated Content & Distribution
*   **[`hackmd/`](hackmd/README.md)**: LLM-generated content backups organized by category with HackMD synchronization
*   **[`posters/`](posters/README.md)**: Visual content generation (448+ date-stamped poster images) for Discord and social sharing

### Specialized Content
*   **[`clanktank/`](clanktank/README.md)**: Episode database for Clank Tank business pitch show (31 complete episode scripts)
*   **[`archive/`](archive/README.md)**: Historical data repository (1,813+ files) preserving 7+ months of elizaOS ecosystem evolution

### Automation & Configuration  
*   **[`.github/workflows/`](.github/workflows/)**: GitHub Actions workflow configurations for daily automation pipeline
*   **[`scripts/`](scripts/)**: All automation scripts (Python primary, shell secondary) with comprehensive tooling
    *   `prompts/`: LLM interaction templates organized by category (comms, dev, strategy)
*   **`book.json`**: HackMD state management file mapping prompts to note IDs and update strategies

## Primary Scripts Overview

*   **`scripts/aggregate-sources.py`**: The main data aggregation engine, creating `the-council/aggregated/YYYY-MM-DD.json`.
*   **`scripts/generate_council_context.py`**: Processes aggregated data from `the-council/aggregated/daily.json` to create strategic council briefings in `the-council/council_briefing/YYYY-MM-DD.json`.
*   **`scripts/create-hackmd.py`**: Initializes HackMD notes for prompts found in `scripts/prompts/`, creating new notes on HackMD if they don't exist. Manages `book.json` by storing HackMD note IDs and their update strategy (defaulting to 'overwrite' for new notes).
*   **`scripts/update-hackmd.py`**: Generates content daily for HackMD notes using prompts from `scripts/prompts/` and data from `the-council/aggregated/daily.json`. It updates each HackMD note's title (with the current date) and overwrites its content with the prompt details and new LLM-generated text. It also updates the main HackMD book index and saves local backups.
*   **`scripts/extract_facts.py`**: Performs deep analysis on aggregated data. As part of the `extract_daily_facts.yml` workflow, it outputs structured facts to `the-council/facts/YYYY-MM-DD.json` and a corresponding Markdown version to `hackmd/facts/YYYY-MM-DD.md`.
*   **`scripts/webhook.py`**: Called by `daily_discord_briefing.yml` to send the daily facts briefing from `the-council/facts/YYYY-MM-DD.json` to a specified Discord channel, with options for LLM summarization and a poster image.

This system is designed to be modular and extensible, allowing for the integration of new data sources and processing steps as the project evolves.

## Repository Structure

The repository is organized into several main directories with comprehensive documentation. Each directory README provides detailed technical specifications and usage examples:

```
elizaOS Knowledge Aggregation System
├── 📁 Core Processing Hub
│   └── the-council/            # 🔗 Central data processing (see README.md)
│       ├── aggregated/         #   Daily raw data aggregation (YYYY-MM-DD.json)
│       ├── council_briefing/   #   Strategic analysis & briefings  
│       ├── facts/              #   LLM-extracted insights & intelligence
│       └── episodes/           #   Strategic discussion archives
│
├── 📁 Data Sources & Intelligence  
│   ├── ai-news/                # 🔗 Multi-source AI intelligence (see README.md)
│   │   ├── elizaos/            #   ElizaOS ecosystem news (270+ files)
│   │   │   ├── dev/            #   Developer-focused content
│   │   │   ├── discord/        #   Community discussions  
│   │   │   └── json/ + md/     #   Daily summaries & reports
│   │   └── hyperfy/            #   VR/Web3 platform developments
│   ├── github/                 # 🔗 GitHub activity analytics (see README.md)
│   │   ├── stats/              #   Quantitative metrics (day/week/month)
│   │   └── summaries/          #   Human-readable reports (900+ files)
│   ├── daily-silk/             # 🔗 Discord AI news aggregation (see README.md)
│   └── docs/                   #   Technical docs from elizaOS/eliza
│
├── 📁 Generated Content & Distribution
│   ├── hackmd/                 # 🔗 LLM-generated content backups (see README.md)
│   │   ├── comms/              #   Communication & outreach content
│   │   ├── dev/                #   Development & technical content  
│   │   ├── strategy/           #   Strategic analysis & planning
│   │   └── facts/              #   Daily extracted facts (markdown)
│   └── posters/                # 🔗 Visual content generation (see README.md)
│       └── YYYY-MM-DD_*.png    #   Date-stamped poster images (448+ files)
│
├── 📁 Specialized Content
│   ├── clanktank/              # 🔗 Business pitch show episodes (see README.md)
│   │   └── episodes/           #   31 complete episode scripts (JSON)
│   └── archive/                # 🔗 Historical data preservation (see README.md)
│       ├── daily-elizaos/      #   Legacy daily reports (Oct 2024-Apr 2025)
│       └── elizaos/            #   Community collaboration archives
│
├── 📁 Automation & Configuration
│   ├── .github/workflows/      #   Daily automation pipeline (8 workflows)
│   ├── scripts/                #   Python automation scripts & tooling
│   │   └── prompts/            #   LLM interaction templates (comms/dev/strategy)
│   └── book.json               #   HackMD state management configuration
│
└── 📄 Documentation
    ├── README.md               #   This comprehensive system overview
    └── CLAUDE.md               #   Development guidelines & architecture notes
    
📊 System Scale: 5,000+ files • 50+ MB data • Daily automation • 7+ months history
🔗 All major directories contain detailed README.md documentation
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

### Episode Data
Structured episode content from M3-org repositories containing rich narrative and analytical content:

#### Clanktank Episodes
Episodes from the [m3-org/clanktank](https://github.com/m3-org/clanktank) repository. Contains JSON files with episode data covering various topics in AI, crypto, and technology. Each episode includes structured content with topics, discussions, and insights from the clanktank community.

#### The-Council Episodes  
Episodes from the [m3-org/the-council](https://github.com/m3-org/the-council) repository. Contains JSON files with strategic discussions and analysis from the council. This data is synced daily as part of the automated pipeline, providing ongoing strategic insights and community discussions.

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

