# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the elizaOS Knowledge Aggregation System - a central hub for aggregating, processing, and synthesizing knowledge for the elizaOS project using automated workflows and scripts. The system transforms raw data from various sources into actionable intelligence through structured pipelines.

## Architecture

### Core Data Pipeline
The system follows a daily automated pipeline (scheduled via GitHub Actions):

1. **External Data Ingestion** (01:00 UTC) - Syncs from external repositories
2. **Context Aggregation** (01:30 UTC) - Consolidates all data sources
3. **Daily Fact Extraction** (01:35 UTC) - Extracts key insights using LLM
4. **Council Briefing Generation** (01:50 UTC) - Creates strategic summaries
5. **HackMD Note Updates** (02:30 UTC) - Updates documentation platform
6. **Enhanced Poster Generation** (04:00 UTC) - Creates visual content with ElizaOS branding
7. **Discord Briefing** (04:30 UTC) - Sends daily briefings with current posters

### Key Directories
- `scripts/` - All automation scripts organized by function:
  - `scripts/etl/` - Data processing pipeline (aggregate, extract, generate)
  - `scripts/integrations/` - External service integrations (Discord, HackMD)
  - `scripts/posters/` - Visual content generation
  - `scripts/prompts/` - LLM prompt templates
  - `scripts/archive/` - Deprecated scripts (kept for reference)
- `the-council/` - Processed daily data (aggregated/, council_briefing/, facts/, retros/, summaries/)
- `hackmd/` - Local backups of generated content
- `ai-news/`, `daily-silk/`, `github/`, `docs/` - Raw data sources
- `.github/workflows/` - Automation workflows
- `rss/` - RSS feeds for facts and council briefings

## Development Commands

### Python Scripts (Primary Automation)
Run from repository root:

```bash
# Aggregate daily data sources
python scripts/etl/aggregate-sources.py [YYYY-MM-DD]

# Extract facts and insights from aggregated data
python scripts/etl/extract-facts.py -i the-council/aggregated/YYYY-MM-DD.json -o the-council/facts/YYYY-MM-DD.json -md hackmd/facts/YYYY-MM-DD.md

# Generate strategic council briefing
python scripts/etl/generate-council-context.py <input_file> <output_file>

# Generate monthly retrospective
python scripts/etl/generate-monthly-retro.py -y 2025 -m 11

# Generate quarterly/annual summary
python scripts/etl/generate-quarterly-summary.py -y 2025 -q 4

# Generate RSS feeds
python scripts/etl/generate-rss.py

# Create new HackMD notes for prompts
python scripts/integrations/hackmd/create.py [-b BOOK_PERMALINK] [-i LOCAL_DIR_PATH]

# Update HackMD notes with daily content
python scripts/integrations/hackmd/update.py [-d YYYY-MM-DD] [-j] [-v]

# Send Discord briefing
python scripts/integrations/discord/webhook.py path/to/facts.json -d -c CHANNEL_ID -s
```

### Enhanced Poster Generation
```bash
# Generate poster from markdown with ElizaOS branding
./scripts/posters/posters-enhanced.sh input.md output.png

# Batch generate all posters
./scripts/posters/run-poster-generation.sh
```

### Node.js Scripts
Limited to Discord bot functionality:

```bash
cd scripts/
npm install  # Only needed for Discord.js dependency
```

### Environment Variables Required
- `OPENROUTER_API_KEY` - For LLM API calls
- `HMD_API_ACCESS_TOKEN` or `HACKMD_API_TOKEN` - For HackMD API
- `DISCORD_BOT_TOKEN` - For Discord posting
- `SELFHST_ICONS_PATH` - (Optional) Path to selfhst/icons repo for reference images

## Data Flow

### Input Sources
- **ElizaOS Docs**: Technical documentation from `elizaOS/eliza` → `docs/`
- **Daily Silk**: AI news from Discord → `daily-silk/YYYY-MM-DD.md`
- **GitHub Activity**: Repository activity logs → `github/stats/` and `github/summaries/`
- **AI News**: Curated AI news → `ai-news/elizaos/`

### Processing Pipeline
1. Raw data aggregated to `the-council/aggregated/YYYY-MM-DD.json`
2. Facts extracted to `the-council/facts/YYYY-MM-DD.json`
3. Strategic briefing generated to `the-council/council_briefing/YYYY-MM-DD.json`
4. Content published to HackMD and Discord
5. RSS feeds generated to `rss/feed.xml` and `rss/council.xml`

### Output Formats
- **JSON**: Structured data for API consumption
- **Markdown**: Human-readable documentation
- **Discord Embeds**: Rich formatted briefings
- **HackMD Notes**: Collaborative documentation
- **RSS Feeds**: Syndication feeds for facts and briefings

## Key Scripts Behavior

### ETL Scripts (`scripts/etl/`)
- **`aggregate-sources.py`**: Reads diverse data sources, creates daily JSON files
- **`extract-facts.py`**: LLM-powered fact extraction with categorization
- **`generate-council-context.py`**: Strategic analysis using North Star alignment
- **`generate-monthly-retro.py`**: Monthly "State of ElizaOS" council episodes
- **`generate-quarterly-summary.py`**: Quarterly/annual pattern analysis
- **`generate-rss.py`**: RSS feed generation

### Integration Scripts (`scripts/integrations/`)
- **`discord/webhook.py`**: Facts to Discord with smart summarization
- **`discord/bot.py`**: Council briefing Discord bot
- **`hackmd/create.py`**: HackMD note creation and management
- **`hackmd/update.py`**: Daily HackMD content updates

### Entity & Icon Pipeline (`scripts/etl/` and `scripts/posters/`)
- **`extract-entities.py`**: Extract entities (tokens, projects, users) from facts with LLM classification
- **`generate-icons.py`**: Generate icons for entities using Nano Banana Pro (Gemini 3 Image)
- **`validate-icons.py`**: Validate icons and sync icon_paths to manifest

See `scripts/posters/README_ICON_GENERATION.md` for detailed icon generation documentation.

```bash
# Extract entities from facts (with deduplication)
python scripts/etl/extract-entities.py --dedupe

# Interactive icon generation
python scripts/posters/generate-icons.py -i -t project

# Batch icon generation
python scripts/posters/generate-icons.py --batch project --limit 4

# Validate and sync icons
python scripts/posters/validate-icons.py --sync-only
```

## Prompt System

The `scripts/prompts/` directory contains LLM interaction templates:
- `config/north-star.txt` - Mission, core principles, strategic context
- `extraction/facts.txt` - Fact extraction prompt
- `hackmd/comms/` - Communication prompts (Discord, tweets, newsletters)
- `hackmd/dev/` - Developer update prompts
- `hackmd/strategy/` - Strategic analysis prompts

## Best Practices

### When Working with Data
- Use date format YYYY-MM-DD consistently
- Check `the-council/aggregated/daily.json` for latest data
- Verify file existence before processing

### When Modifying Scripts
- Test with sample data first
- Check error handling for API calls
- Maintain backward compatibility with existing JSON structures
- Follow the established naming conventions (kebab-case for files)

### When Adding New Data Sources
1. Update sync workflows in `.github/workflows/sync.yml`
2. Modify `scripts/etl/aggregate-sources.py` to include new source
3. Update README.md with source documentation
4. Test full pipeline with new data

## Troubleshooting

### Common Issues
- **API Rate Limits**: Scripts include retry logic for OpenRouter and HackMD APIs
- **Missing Data**: Check if external sync workflows completed successfully
- **JSON Format Errors**: Validate input JSON structure before processing
- **Discord Posting Failures**: Verify bot permissions and channel access

### Debug Commands
```bash
# Verbose output for script debugging
python scripts/integrations/hackmd/update.py -v
python scripts/integrations/hackmd/create.py -v

# Test webhook without posting to Discord
python scripts/integrations/discord/webhook.py facts.json -o output.json
```

The system is designed to be resilient and self-documenting through its comprehensive logging and structured data approach.
