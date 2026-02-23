# Tools & Data Access

## Data Access Methods

### 1. mcporter (if enabled)

The `elizaos-knowledge` MCP server provides structured access to all knowledge data. Access via mcporter:

```bash
# Find latest available dates
mcporter call elizaos-knowledge.list_available_dates

# Get today's facts (defaults to latest if no date)
mcporter call elizaos-knowledge.get_facts date=2026-02-21 format=markdown

# Get strategic council briefing
mcporter call elizaos-knowledge.get_council_briefing date=2026-02-21

# Get full aggregated intelligence
mcporter call elizaos-knowledge.get_daily_briefing date=2026-02-21

# Search across all historical facts
mcporter call elizaos-knowledge.search_knowledge query="token migration" limit=10
```

### 2. File Reads (always available)

Read JSON files directly from the knowledge repo. Use `read` with these paths:

| Path | Content |
|------|---------|
| `the-council/facts/{YYYY-MM-DD}.json` | Extracted facts and insights |
| `the-council/council_briefing/{YYYY-MM-DD}.json` | Strategic briefing with deliberation items |
| `the-council/aggregated/{YYYY-MM-DD}.json` | Full raw consolidated data |
| `the-council/highlights/{YYYY-MM-DD}.json` | 2-3 editorial top stories |
| `the-council/retros/{YYYY-MM}-retro.json` | Monthly retrospective |
| `the-council/episodes/*.json` | Past council episode dialogues |
| `github/api/summaries/contributors/{username}/lifetime.json` | Contributor profiles |
| `api/latest.json` | Latest available date per data source |

### 3. Web Fetch (always available)

GitHub Pages hosts the knowledge data publicly:

| URL | Content |
|-----|---------|
| `https://elizaos.github.io/knowledge/api/latest.json` | Latest dates per source |
| `https://elizaos.github.io/knowledge/api/manifest.json` | Full data inventory |
| `https://elizaos.github.io/knowledge/rss/feed.xml` | Facts RSS feed |
| `https://elizaos.github.io/knowledge/rss/council.xml` | Briefings RSS feed |

## JSON Schemas (Quick Reference)

**Facts** (`the-council/facts/*.json`):
- `briefing_date`, `overall_sentiment` (positive/negative/neutral/mixed)
- `categories[].facts[].claim` — the fact itself
- `categories[].facts[].source` — where it came from
- `categories[].facts[].sentiment`, `categories[].facts[].confidence`

**Council briefing** (`the-council/council_briefing/*.json`):
- `executive_summary` — one-paragraph overview
- `key_developments[]` — major developments with impact ratings
- `strategic_implications[]`, `recommendations[]`
- `council_commentary.{eliza,aishaw,aimarc,spartan,peepo}` — per-character takes

## Date Conventions

- All dates: `YYYY-MM-DD` format
- Pipeline runs daily ~01:00-04:30 UTC
- AI news is T-1 (yesterday's news in today's data)
