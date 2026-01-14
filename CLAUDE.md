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
- `GILBARBARA_LOGOS_PATH` - (Optional) Path to gilbarbara/logos repo for SVG logos

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

## Backfill Process

When upstream data needs to be regenerated or pipeline gaps are discovered, follow this backfill process:

### Manual Backfill Steps

```bash
# 1. Resync upstream data from M3-org/ai-news (if needed)
for date in 2026-01-{01..13}; do
  curl -L -o "ai-news/elizaos/json/$date.json" \
    "https://raw.githubusercontent.com/M3-org/ai-news/gh-pages/elizaos/json/$date.json"
  curl -L -o "ai-news/elizaos/md/$date.md" \
    "https://raw.githubusercontent.com/M3-org/ai-news/gh-pages/elizaos/md/$date.md"
done

# 2. Reaggregate all affected dates
for date in 2026-01-{01..13}; do
  python scripts/etl/aggregate-sources.py $date
done

# 3. Re-extract facts (requires OPENROUTER_API_KEY)
for date in 2026-01-{01..13}; do
  python scripts/etl/extract-facts.py \
    -i the-council/aggregated/$date.json \
    -o the-council/facts/$date.json \
    -md hackmd/facts/$date.md
  sleep 5  # Rate limiting
done

# 4. Regenerate council briefings
for date in 2026-01-{01..13}; do
  python scripts/etl/generate-council-context.py \
    the-council/aggregated/$date.json \
    the-council/council_briefing/$date.json
  sleep 5  # Rate limiting
done

# 5. Update RSS feeds
python scripts/etl/generate-rss.py

# 6. (Optional) Regenerate posters - expensive and time-consuming
for date in 2026-01-{01..13}; do
  python scripts/posters/illustrate.py -f the-council/facts/$date.json --batch
  sleep 10
done
```

### Backfill Verification

```bash
# Check aggregation success rates
for date in 2026-01-{01..13}; do
  echo -n "$date: "
  jq -r '._metadata | "\(.sources_successful) successful, \(.sources_failed) failed"' \
    the-council/aggregated/$date.json
done

# Check facts extraction
for date in 2026-01-{01..13}; do
  echo -n "$date: "
  jq -r '._metadata | "\(.status) - \(.total_facts // 0) facts"' \
    the-council/facts/$date.json
done

# Check poster generation
for date in 2026-01-{01..13}; do
  echo -n "$date: "
  if [ -f "media/daily/$date/manifest.json" ]; then
    jq -r '.stats | "\(.successful)/\(.total_generations) successful"' \
      media/daily/$date/manifest.json
  else
    echo "NO MANIFEST"
  fi
done
```

## Known Issues

### Date Field Extraction (2026-01-14 Backfill)
**Issue**: `extract-facts.py` may infer wrong `briefing_date` when LLM sees T-1 (previous day) AI news data.

**Example**: Facts file `2026-01-13.json` contained `"briefing_date": "2026-01-12"`

**Root Cause**: The aggregator pulls `target_date - timedelta(days=1)` for AI news sources, but the LLM infers the date from the data content rather than the target filename.

**Workaround**: Manually verify `briefing_date` field in extracted facts matches expected date.

**Fix Planned**: Add explicit date validation to LLM prompt + post-process validation (see GitHub issue for details).

### API Rate Limiting (Poster Generation)
**Issue**: Batch poster generation can hit API rate limits (429 errors) when processing multiple dates.

**Example**: During 13-day backfill, poster generation hit "Resource exhausted" error on 2026-01-09.

**Impact**: Partial poster sets (4/5 instead of 5/5).

**Workaround**: Add `sleep 10` between dates, or regenerate failed posters individually.

**Fix Planned**: Implement exponential backoff retry logic with rate limit tracking (see GitHub issue for details).

### Upstream Schema Changes
**Issue**: Upstream data structure can change without notice (e.g., `images: []` → `images: null` or scalar strings).

**Impact**: Silent data quality degradation if not detected.

**Fix Planned**: Schema validation with baseline snapshots to detect breaking changes (see GitHub issue for details).

## Troubleshooting

### Common Issues
- **API Rate Limits**: Scripts include retry logic for OpenRouter and HackMD APIs. For poster generation, add delays between batch operations.
- **Missing Data**: Check if external sync workflows completed successfully. Verify upstream sources are available.
- **JSON Format Errors**: Validate input JSON structure before processing. Check for schema changes in upstream sources.
- **Discord Posting Failures**: Verify bot permissions and channel access.
- **Wrong Date Fields**: LLM may infer dates from content rather than target date. Verify `briefing_date` matches expected date.
- **Partial Poster Sets**: Check `media/daily/YYYY-MM-DD/manifest.json` for generation stats. API rate limits may cause partial generations.

### Debug Commands
```bash
# Verbose output for script debugging
python scripts/integrations/hackmd/update.py -v
python scripts/integrations/hackmd/create.py -v

# Test webhook without posting to Discord
python scripts/integrations/discord/webhook.py facts.json -o output.json

# Check aggregated data quality
jq '._metadata' the-council/aggregated/2026-01-13.json

# Verify facts extraction metadata
jq '._metadata' the-council/facts/2026-01-13.json

# Check poster generation stats
jq '.stats' media/daily/2026-01-13/manifest.json
```

### Pipeline Analysis (2026-01-14)
A comprehensive analysis of the pipeline identified improvements in:
- Data quality validation (schema validation, date field extraction)
- Error handling (retry logic, rate limiting, circuit breakers)
- Observability (metrics collection, health dashboard, alerting)
- Developer experience (setup automation, backfill tooling)

See GitHub issues for implementation roadmap and tracking.

The system is designed to be resilient and self-documenting through its comprehensive logging and structured data approach.
