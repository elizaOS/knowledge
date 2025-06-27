# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the elizaOS Knowledge Aggregation System - a central hub for aggregating, processing, and synthesizing knowledge for the elizaOS project using automated workflows and scripts. The system transforms raw data from various sources into actionable intelligence through structured pipelines.

## Architecture

### Core Data Pipeline
The system follows a daily automated pipeline (scheduled via GitHub Actions):

1. **External Data Ingestion** (01:00 UTC) - Syncs from external repositories
2. **Daily Fact Extraction** (01:15 UTC) - Extracts key insights using LLM
3. **Context Aggregation** (01:30 UTC) - Consolidates all data sources
4. **Council Briefing Generation** (02:00 UTC) - Creates strategic summaries
5. **HackMD Note Updates** (02:30 UTC) - Updates documentation platform
6. **Enhanced Poster Generation** (04:00 UTC) - Creates visual content with ElizaOS branding
7. **Discord Briefing** (04:30 UTC) - Sends daily briefings with current posters

### Key Directories
- `scripts/` - All automation scripts (Python primary, some shell)
- `the-council/` - Processed daily data (aggregated/, council_briefing/, facts/)
- `hackmd/` - Local backups of generated content
- `ai-news/`, `daily-silk/`, `github/`, `docs/` - Raw data sources
- `.github/workflows/` - Automation workflows

## Development Commands

### Python Scripts (Primary Automation)
Run from repository root:

```bash
# Aggregate daily data sources
python scripts/aggregate-sources.py [YYYY-MM-DD]

# Extract facts and insights from aggregated data
python scripts/extract-facts.py -i the-council/aggregated/YYYY-MM-DD.json -o the-council/facts/YYYY-MM-DD.json

# Generate strategic council briefing
python scripts/generate_council_context.py

# Create new HackMD notes for prompts
python scripts/create-hackmd.py [-b BOOK_PERMALINK] [-i LOCAL_DIR_PATH]

# Update HackMD notes with daily content
python scripts/update-hackmd.py [-d YYYY-MM-DD] [-j] [-v]

# Send Discord briefing
python scripts/webhook.py path/to/facts.json -d -c CHANNEL_ID -s
```

### Enhanced Poster Generation
```bash
# Generate poster from markdown with ElizaOS branding
./scripts/posters-enhanced.sh input.md output.png

# The enhanced script provides:
# - ElizaOS branded styling with gradient headers
# - Multiple fallback rendering engines (wkhtmltoimage, Chromium, ImageMagick)
# - Improved typography and spacing
# - Responsive layouts for different content lengths
# - Robust error handling and logging
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

### Output Formats
- **JSON**: Structured data for API consumption
- **Markdown**: Human-readable documentation
- **Discord Embeds**: Rich formatted briefings
- **HackMD Notes**: Collaborative documentation

## Key Scripts Behavior

### `aggregate-sources.py`
Intelligently reads diverse data sources, handles date-specific content, and creates comprehensive daily JSON files. Primary data aggregation engine.

### `extract-facts.py` 
Uses specialized LLM prompts to perform deep analysis and extract categorized insights with source tracing. Outputs structured intelligence briefings.

### `webhook.py`
Optimized Discord bot with smart budget allocation, content summarization, and rich formatting. Processes facts JSON into engaging Discord messages.

### `generate_council_context.py`
Strategic analysis engine that creates high-level briefings for leadership using comprehensive prompts and monthly goal alignment.

## Prompt System

The `scripts/prompts/` directory contains LLM interaction templates organized by category:
- `comms/` - Communication and outreach
- `dev/` - Development and technical
- `strategy/` - Strategic planning and analysis

Prompts are automatically processed by `update-hackmd.py` to generate daily content for corresponding HackMD notes.

## Best Practices

### When Working with Data
- Use date format YYYY-MM-DD consistently
- Check `the-council/aggregated/daily.json` for latest data
- Verify file existence before processing

### When Modifying Scripts
- Test with sample data first
- Check error handling for API calls
- Maintain backward compatibility with existing JSON structures
- Follow the established naming conventions

### When Adding New Data Sources
1. Update sync workflows in `.github/workflows/sync.yml`
2. Modify `aggregate-sources.py` to include new source
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
python scripts/update-hackmd.py -v
python scripts/create-hackmd.py -v

# Test webhook without posting to Discord
python scripts/webhook.py facts.json -o output.json
```

The system is designed to be resilient and self-documenting through its comprehensive logging and structured data approach.