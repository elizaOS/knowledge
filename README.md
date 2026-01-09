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
- **[Visual Assets](posters/README.md)**: Automated poster generation (rolling 7-day archive)
- **[Character System](scripts/posters/README.md)**: AI-powered character illustration pipeline
- **[Episode Database](clanktank/README.md)**: Business pitch show scripts (31 episodes)
- **[Historical Archive](archive/README.md)**: 7+ months of preserved data (1,813+ files)

**Quick Links to Explore Data:**

**Explore**
- Browse all content via GitHub Pages root: https://elizaos.github.io/knowledge/
- Eliza Daily HackMD Book: https://hackmd.io/@elizaos/book

**Updated daily**
(Data for these links is typically refreshed by 10:30 UTC each day.)
- Latest aggregated data: https://elizaos.github.io/knowledge/the-council/aggregated/daily.json
- Latest council briefing: https://elizaos.github.io/knowledge/the-council/council_briefing/daily.json
- Latest ElizaOS AI news summary: https://elizaos.github.io/knowledge/ai-news/elizaos/json/daily.json
- Latest extracted facts: https://elizaos.github.io/knowledge/the-council/facts/daily.json
- Contributor profiles: https://elizaos.github.io/knowledge/github/contributors/
- Eliza.how docs (llms-full.txt): https://eliza.how/llms-full.txt

**RSS Feeds** (self-rendering with XSLT - viewable in browser)
- Daily Intelligence Feed: https://elizaos.github.io/knowledge/rss/feed.xml
- Council Briefings Feed: https://elizaos.github.io/knowledge/rss/council.xml
- GitHub Activity Feed: https://elizaos.github.io/rss.xml

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

The pipeline runs after upstream `M3-org/ai-news` completes its daily processing (~07:30 UTC):

| Time | Workflow | Description |
|------|----------|-------------|
| **08:00** | `sync.yml` | Pull fresh data from ai-news (after upstream CDN upload) |
| **08:30** | `aggregate-daily-sources.yml` | Consolidate all sources into daily JSON |
| **08:45** | `extract_daily_facts.yml` | Extract key facts using LLM + generate RSS |
| **09:00** | `generate-council-briefing.yml` | Generate strategic council briefing + RSS |
| **09:30** | `update_hackmd_notes.yml` | Update HackMD documentation |
| **10:00** | `generate-posters.yml` | Generate visual content (skips if upstream has posters) |
| **10:30** | `daily_discord_briefing.yml` | Send daily briefing to Discord |

### Periodic Retrospectives (`.github/workflows/retro.yml`)
- **Monthly** (1st of each month @ 03:00 UTC) - Council retrospective episode analyzing the previous month
- **Quarterly** (1st of Jan/Apr/Jul/Oct @ 04:00 UTC) - Strategic summary across 3 months
- **Annual** (Manual trigger) - Comprehensive year-in-review summary

Retrospectives output to `the-council/retros/` and `the-council/summaries/`.

### Pipeline Details

1.  **External Data Ingestion (`.github/workflows/sync.yml`)**: (Runs at 08:00 UTC)
    *   This workflow runs daily to synchronize data from external repositories and sources. Scheduled after upstream `M3-org/ai-news` CDN upload (~07:30 UTC) to ensure fresh data.
    *   Sources include: documentation from `elizaOS/eliza` and `madjin/daily-silk`, GitHub activity logs from `elizaos/elizaos.github.io`, AI news from `M3-org/ai-news`, and episode data from `m3-org/clanktank` and `m3-org/the-council`.
    *   Raw synced data is stored in directories like `docs/`, `daily-silk/`, `github/`, `ai-news/`, `clanktank/episodes/`, and `the-council/episodes/`.

2.  **Daily Context Aggregation (`.github/workflows/aggregate-daily-sources.yml`)**: (Runs at 08:30 UTC)
    *   This workflow runs `scripts/aggregate-sources.py` daily after sync completes.
    *   Consolidates data from synced external sources (e.g., `ai-news/`, `github/summaries/`) and internal structured data into a comprehensive daily JSON file: `the-council/aggregated/YYYY-MM-DD.json`.
    *   Uses `ai-news/elizaos/json/` which contains CDN URLs for media.
    *   A permalink `the-council/aggregated/daily.json` is created, pointing to the latest daily aggregated file.

3.  **Daily Fact Extraction (`.github/workflows/extract_daily_facts.yml`)**: (Runs at 08:45 UTC)
    *   This workflow runs `scripts/extract-facts.py` daily after aggregation.
    *   Uses an LLM with a specialized prompt to distill significant information from the aggregated data.
    *   Outputs are structured JSON facts to `the-council/facts/YYYY-MM-DD.json` and a Markdown version to `hackmd/facts/YYYY-MM-DD.md`.
    *   Generates RSS feeds and creates permalink `the-council/facts/daily.json`.

4.  **Council Briefing Generation (`.github/workflows/generate-council-briefing.yml`)**: (Runs at 09:00 UTC)
    *   Triggered daily after fact extraction, this workflow runs `scripts/generate_council_context.py`.
    *   This script takes `the-council/aggregated/daily.json` as input and uses an LLM (via OpenRouter) with strategic prompts (e.g., `scripts/prompts/strategy/north-star.txt`) to produce a high-level strategic briefing.
    *   The output is saved as `the-council/council_briefing/YYYY-MM-DD.json`, with a permalink `the-council/council_briefing/daily.json`.

5.  **HackMD Note Generation & Backup (`.github/workflows/update_hackmd_notes.yml`)**: (Runs at 09:30 UTC)
    *   This workflow runs daily to manage topical insights on HackMD.
    *   It first executes `scripts/create-hackmd.py` which ensures HackMD notes exist for prompts and updates `book.json`.
    *   Then, it runs `scripts/update-hackmd.py` which uses `the-council/aggregated/daily.json` as context to generate content for each prompt, update HackMD notes, and save local backups.
    *   Changes to `book.json`, `hackmd/**/*.md`, and `hackmd/**/*.json` are committed.

6.  **Poster Generation (`.github/workflows/generate-posters.yml`)**: (Runs at 10:00 UTC)
    *   This workflow generates visual poster content using `scripts/posters/illustrate.py`.
    *   **Checks upstream first**: If `ai-news/elizaos/json/` already has poster URLs, generation is skipped to avoid duplicate work.
    *   When generating locally, creates illustrations with ElizaOS branding and uploads to Bunny CDN.
    *   Enriches facts with media URLs (respects existing upstream values).

7.  **Daily Discord Briefing (`.github/workflows/daily_discord_briefing.yml`)**: (Runs at 10:30 UTC)
    *   This workflow runs `scripts/webhook.py` daily after all data processing and poster generation are complete.
    *   Uses poster URLs from facts (either upstream CDN or locally generated).
    *   Includes automatic poster cleanup and sends formatted briefings with LLM-generated summaries.
    *   Integrates rich Discord embeds with poster images.
    *   Requires `OPENROUTER_API_KEY` and `DISCORD_BOT_TOKEN` secrets for LLM summarization and Discord posting.

## Key Directories

Each major directory contains comprehensive documentation. Click the links below to explore detailed information about each component:

### Core Processing Hub
*   **[`the-council/`](the-council/README.md)**: Central data processing hub containing daily aggregated data, strategic council briefings, and extracted facts
    *   `aggregated/`: Daily raw aggregated data (`YYYY-MM-DD.json`) from all sources
    *   `council_briefing/`: Strategic council briefings with high-level analysis
    *   `facts/`: Daily extracted facts and insights with source tracing
    *   `episodes/`: Episode data from strategic discussions (including monthly retros)
    *   `retros/`: Monthly retrospective analyses
    *   `summaries/`: Quarterly and annual strategic summaries

### Data Sources & Intelligence
*   **[`ai-news/`](ai-news/README.md)**: Multi-source AI intelligence (1,640+ files) from elizaOS and Hyperfy ecosystems
*   **[`github/`](github/README.md)**: GitHub activity analytics (900+ files) with daily/weekly/monthly summaries and statistics  
*   **[`daily-silk/`](daily-silk/README.md)**: Daily AI news from Discord community (167+ files, 25,000+ lines)
*   **[`docs/`](docs/)**: Technical documentation synced from `elizaOS/eliza` repository

### Generated Content & Distribution
*   **[`hackmd/`](hackmd/README.md)**: LLM-generated content backups organized by category with HackMD synchronization
*   **[`posters/`](posters/README.md)**: Visual content generation for Discord and social sharing (rolling 7-day archive)

### Specialized Content
*   **[`clanktank/`](clanktank/README.md)**: Episode database for Clank Tank business pitch show (31 complete episode scripts)
*   **[`archive/`](archive/README.md)**: Historical data repository (1,813+ files) preserving 7+ months of elizaOS ecosystem evolution

### Automation & Configuration  
*   **[`.github/workflows/`](.github/workflows/)**: GitHub Actions workflow configurations for daily automation pipeline
*   **[`scripts/`](scripts/)**: All automation scripts (Python primary, shell secondary) with comprehensive tooling
    *   `prompts/`: LLM interaction templates organized by category (comms, dev, strategy)
*   **`book.json`**: HackMD state management file mapping prompts to note IDs and update strategies

## Primary Scripts Overview

### ETL Pipeline (`scripts/etl/`)
*   **`aggregate-sources.py`**: The main data aggregation engine, creating `the-council/aggregated/YYYY-MM-DD.json`.
*   **`extract-facts.py`**: Performs deep analysis on aggregated data, outputs structured facts to `the-council/facts/YYYY-MM-DD.json` and markdown to `hackmd/facts/YYYY-MM-DD.md`.
*   **`generate-council-context.py`**: Processes aggregated data to create strategic council briefings in `the-council/council_briefing/YYYY-MM-DD.json`.
*   **`generate-monthly-retro.py`**: Generates monthly "State of ElizaOS" council episodes.
*   **`generate-quarterly-summary.py`**: Generates quarterly/annual strategic summaries.
*   **`generate-rss.py`**: Generates RSS feeds for facts and council briefings.

### Integrations (`scripts/integrations/`)
*   **`discord/webhook.py`**: Sends daily facts briefing to Discord with LLM summarization and poster images. Also handles poster cleanup (keeps last 7 days).
*   **`discord/bot.py`**: Council briefing Discord bot.
*   **`hackmd/create.py`**: Initializes HackMD notes for prompts, manages `book.json`.
*   **`hackmd/update.py`**: Generates daily content for HackMD notes using prompts and aggregated data.

### Character Illustration System (`scripts/posters/`)

A complete system for generating character-driven visual content:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  ANALYZE    │ ──▶ │  GENERATE   │ ──▶ │ ILLUSTRATE  │
│  analyze.py │     │ generate.py │     │illustrate.py│
│             │     │             │     │             │
│ Images →    │     │ Manifest →  │     │ Ref sheet + │
│ manifest    │     │ ref sheet   │     │ story →     │
│             │     │             │     │ illustration│
└─────────────┘     └─────────────┘     └─────────────┘
```

| Script | Purpose | Example |
|--------|---------|---------|
| `analyze.py` | Analyze character images → `manifest.json` | `python scripts/posters/analyze.py eliza` |
| `generate.py` | Create reference sheets from manifest | `python scripts/posters/generate.py eliza cyberpunk` |
| `illustrate.py` | Generate story illustrations with characters | `python scripts/posters/illustrate.py eliza "presenting at conference"` |
| `vision.py` | General-purpose image analysis (Unix-style) | `python scripts/posters/vision.py image.png -p "describe"` |
| `generate-ai-image.py` | Daily AI news poster generation | Automated via workflow |

**Available Characters**: eliza, marc, peepo, spartan, shaw

See **[scripts/posters/README.md](scripts/posters/README.md)** for detailed usage.

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
│   │   ├── summaries/          #   Human-readable reports (900+ files)
│   │   ├── api/                #   API endpoint data
│   │   └── contributors/       #   Contributor profiles & statistics
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
│       └── YYYY-MM-DD_*.png    #   Date-stamped poster images (last 7 days kept)
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
│   │   ├── etl/                #   Data pipeline (aggregate, extract, generate)
│   │   ├── integrations/       #   External services (Discord, HackMD)
│   │   ├── posters/            #   Character illustration system
│   │   │   ├── characters/     #   Character assets & manifests
│   │   │   └── config/         #   Style presets & configuration
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

**Synced directories:**
- `github/stats/` - Quantitative metrics (day/week/month JSON files)
- `github/summaries/` - Human-readable activity reports
- `github/api/` - API endpoint data
- `github/contributors/` - Contributor profiles and statistics

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

## Strategic Context (December 2025)

### North Star

To build the most reliable, developer-friendly open-source AI agent framework and cloud platform—enabling builders worldwide to deploy autonomous agents that work seamlessly across chains and platforms. We create infrastructure where agents and humans collaborate, forming the foundation for a decentralized AI economy that accelerates the path toward beneficial AGI.

### Core Principles

1. **Execution Excellence** - Reliability and seamless UX over feature quantity
2. **Developer First** - Great DX attracts builders; builders create ecosystem value
3. **Open & Composable** - Multi-agent systems that interoperate across platforms
4. **Trust Through Shipping** - Build community confidence through consistent delivery

### Current Product Focus

- **ElizaOS Framework** (v1.6.x) - Core TypeScript toolkit for building persistent, interoperable agents
- **ElizaOS Cloud** - Managed deployment platform with integrated storage and cross-chain capabilities
- **Flagship Agents** - Reference implementations demonstrating platform capabilities
- **Cross-Chain Infrastructure** - Native support for multi-chain agent operations

### Mission Summary

ElizaOS is an open-source "operating system for AI agents" aimed at decentralizing AI development. Built on three pillars:
1. **The Eliza Framework** - TypeScript toolkit for persistent agents
2. **AI-Enhanced Governance** - Building toward autonomous DAOs
3. **Eliza Labs** - R&D driving cloud, cross-chain, and multi-agent capabilities

The native token coordinates the ecosystem. The vision is an intelligent internet built on open protocols and collaboration.

### Taming Information

This repository addresses the challenge of information scattered across platforms (Discord, GitHub, X). It uses AI agents as "bridges" to collect, wrangle (summarize/tag), and distribute information in various formats (JSON, MD, RSS, dashboards, council episodes). Documentation is treated as a first-class citizen to empower AI assistants and streamline community operations.

