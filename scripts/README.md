# Scripts

This directory contains various scripts for automating tasks related to content aggregation, generation, and publishing for the elizaOS knowledge system.

## Directory Structure

```
scripts/
├── etl/                      # Data processing pipeline scripts
│   ├── aggregate-sources.py  # Aggregates content from diverse sources
│   ├── extract-facts.py      # Extracts key facts using LLM
│   ├── generate-council-context.py  # Generates strategic council briefings
│   ├── generate-monthly-retro.py    # Monthly retrospective episodes
│   ├── generate-quarterly-summary.py # Quarterly/annual summaries
│   └── generate-rss.py       # Generates RSS feeds
├── integrations/
│   ├── discord/              # Discord integration scripts
│   │   ├── webhook.py        # Facts briefing to Discord
│   │   ├── bot.py            # Council briefing bot
│   │   └── summarize-episodes.py # Episode summaries for Discord
│   └── hackmd/               # HackMD integration scripts
│       ├── create.py         # Creates/manages HackMD notes
│       └── update.py         # Updates HackMD with LLM content
├── posters/                  # Visual content generation
│   ├── posters-enhanced.sh   # Markdown to PNG poster converter
│   └── run-poster-generation.sh # Batch poster generation
├── prompts/                  # LLM prompt templates
│   ├── config/               # Strategic configuration
│   │   └── north-star.txt    # Mission and strategic context
│   ├── extraction/           # Data extraction prompts
│   │   └── facts.txt         # Fact extraction prompt
│   └── hackmd/               # HackMD content prompts
│       ├── comms/            # Communication prompts
│       ├── dev/              # Developer update prompts
│       └── strategy/         # Strategic analysis prompts
└── archive/                  # Deprecated scripts (kept for reference)
```

---

## ETL Scripts (`etl/`)

### `aggregate-sources.py`

**Purpose**: Aggregates content from diverse data sources into a unified daily JSON file.

**Details**:
This Python script is the primary engine for collecting daily context. It navigates predefined paths within the workspace (e.g., `ai-news/` subfolders for elizaos, discord, and dev content, `github/summaries/` for activity summaries, and `github/stats/` for statistics).

**Usage**:
```bash
python scripts/etl/aggregate-sources.py [YYYY-MM-DD]
```
- If `[YYYY-MM-DD]` is provided, it generates the context for that specific date.
- If no date is provided, it defaults to the current date.

**Output**: `the-council/aggregated/YYYY-MM-DD.json`

---

### `extract-facts.py`

**Purpose**: Generates a categorized intelligence briefing by extracting key facts and insights from aggregated data.

**Details**:
Takes the comprehensive JSON output from `aggregate-sources.py` and uses a specialized LLM prompt (`scripts/prompts/extraction/facts.txt`) to perform deep analysis. Outputs structured JSON organized by thematic categories.

**Usage**:
```bash
python scripts/etl/extract-facts.py -i the-council/aggregated/YYYY-MM-DD.json -o the-council/facts/YYYY-MM-DD.json -md hackmd/facts/YYYY-MM-DD.md
```

**Output**: JSON facts file and optional Markdown version

---

### `generate-council-context.py`

**Purpose**: Generates strategic "council briefing" summaries from daily aggregated data.

**Details**:
Uses the North Star prompt (`scripts/prompts/config/north-star.txt`) combined with monthly goals to produce strategic briefings for leadership review.

**Usage**:
```bash
python scripts/etl/generate-council-context.py <input_file> <output_file>
```

**Environment Variables**:
- `OPENROUTER_API_KEY`: Required for LLM API access

---

### `generate-monthly-retro.py`

**Purpose**: Generates monthly retrospective council episodes analyzing the previous month's activity.

**Details**:
Aggregates a month's facts, briefings, and GitHub activity to produce "State of ElizaOS" episodes with strategic analysis and council dialogue.

**Usage**:
```bash
python scripts/etl/generate-monthly-retro.py -y 2025 -m 11
```

**Output**: `the-council/retros/YYYY-MM.json` and `the-council/episodes/episode-retro-YYYY-MM.json`

---

### `generate-quarterly-summary.py`

**Purpose**: Generates quarterly or annual summaries from monthly retrospectives.

**Usage**:
```bash
# Quarterly summary
python scripts/etl/generate-quarterly-summary.py -y 2025 -q 4

# Annual summary
python scripts/etl/generate-quarterly-summary.py -y 2025
```

**Output**: `the-council/summaries/YYYY-QN.json` or `the-council/summaries/YYYY-annual.json`

---

### `generate-rss.py`

**Purpose**: Generates RSS feeds from facts and council briefings.

**Usage**:
```bash
python scripts/etl/generate-rss.py
```

**Output**: `rss/feed.xml` (facts) and `rss/council.xml` (briefings)

---

## Integration Scripts

### Discord (`integrations/discord/`)

#### `webhook.py`

**Purpose**: Converts JSON facts data into rich Discord embeds with smart content processing.

**Key Features**:
- Smart budget allocation across sections
- LLM summarization for long content
- Rich Discord formatting with themed embeds
- Poster image integration

**Usage**:
```bash
python scripts/integrations/discord/webhook.py the-council/facts/YYYY-MM-DD.json -d -c CHANNEL_ID -s
```

**Environment Variables**:
- `DISCORD_BOT_TOKEN`: Required for Discord posting
- `OPENROUTER_API_KEY`: Required for LLM summarization (`-s` flag)

---

#### `bot.py`

**Purpose**: Enhanced Discord bot for posting council briefings with AI-generated dialogue.

---

#### `summarize-episodes.py`

**Purpose**: Generates Discord-optimized summaries of council episodes.

---

### HackMD (`integrations/hackmd/`)

#### `create.py`

**Purpose**: Manages HackMD notes - creates notes for prompts and handles directory mappings.

**Usage**:
```bash
python scripts/integrations/hackmd/create.py [-b BOOK_PERMALINK] [-i LOCAL_DIR_PATH]
```

---

#### `update.py`

**Purpose**: Generates daily content for HackMD notes using LLM or syncs from local files.

**Usage**:
```bash
python scripts/integrations/hackmd/update.py [-d YYYY-MM-DD] [-j] [-v]
```

**Environment Variables**:
- `OPENROUTER_API_KEY`: Required for LLM API calls
- `HMD_API_ACCESS_TOKEN`: Required for HackMD API

---

## Poster Scripts (`posters/`)

### `posters-enhanced.sh`

**Purpose**: Converts Markdown files to styled PNG posters with ElizaOS branding.

**Features**:
- ElizaOS branded styling with gradient headers
- Multiple fallback rendering engines (wkhtmltoimage, Chromium, ImageMagick)
- Improved typography and spacing

**Usage**:
```bash
./scripts/posters/posters-enhanced.sh input.md output.png
```

---

### `run-poster-generation.sh`

**Purpose**: Batch generates posters from multiple source directories.

**Usage**:
```bash
./scripts/posters/run-poster-generation.sh
```

---

## Prompts (`prompts/`)

The prompts directory houses all LLM prompt templates:

- **`config/`**: Strategic configuration files
  - `north-star.txt`: Mission, core principles, and strategic context

- **`extraction/`**: Data extraction prompts
  - `facts.txt`: Fact extraction and categorization prompt

- **`hackmd/`**: Content generation prompts for HackMD notes
  - `comms/`: Communication prompts (Discord announcements, tweets, newsletters)
  - `dev/`: Developer-focused prompts (updates, issue triage)
  - `strategy/`: Strategic analysis prompts (intel, team development)

---

## Archive (`archive/`)

Contains deprecated scripts kept for reference. These are no longer part of the active pipeline.

---

## Environment Variables Summary

| Variable | Required By | Purpose |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | Most ETL scripts | LLM API access |
| `DISCORD_BOT_TOKEN` | Discord integrations | Discord bot authentication |
| `HMD_API_ACCESS_TOKEN` | HackMD integrations | HackMD API access |

---

## Dependencies

- Python 3.x
- `requests` library
- `discord.py` library (for Discord integrations)
- System tools: `pandoc`, `wkhtmltoimage`, `chromium` (for poster generation)
