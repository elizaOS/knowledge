# Knowledge Data Access

## Primary: MCP Server (`elizaos-knowledge`)

The MCP server handles path resolution, date fallback, and output formatting. Use these tools when available.

| Tool | Description | Params |
|------|-------------|--------|
| `get_facts` | Extracted facts and insights (GitHub, Discord, strategic) | `date?` (YYYY-MM-DD), `format?` (markdown\|json) |
| `get_daily_briefing` | Full aggregated intelligence from all sources | `date?`, `format?` |
| `get_council_briefing` | Strategic briefing with deliberation items | `date?`, `format?` |
| `list_available_dates` | Discover what dates have data | `type?` (facts\|council\|aggregated), `limit?` (1-100) |
| `search_knowledge` | Full-text search across all facts history | `query`, `date_start?`, `date_end?`, `limit?` (1-50) |

**Startup pattern:** `list_available_dates` → `get_facts` → `get_council_briefing`

**MCP server source:** `mcp-server/src/index.ts` (Node.js, StdIO transport)

### mcporter (OpenClaw runtime)

In OpenClaw, MCP tools are accessed via the `mcporter` CLI bridge:

```bash
# Find latest available dates
mcporter call elizaos-knowledge.list_available_dates

# Get today's facts in markdown
mcporter call elizaos-knowledge.get_facts date=2026-02-21 format=markdown

# Get strategic council briefing
mcporter call elizaos-knowledge.get_council_briefing date=2026-02-21

# Get full aggregated intelligence
mcporter call elizaos-knowledge.get_daily_briefing date=2026-02-21

# Search across all historical facts
mcporter call elizaos-knowledge.search_knowledge query="token migration" limit=10
```

Format: `mcporter call <server>.<tool> param1=value1 param2=value2`

## Secondary: GitHub Pages API

Static JSON served at `https://elizaos.github.io/knowledge/`:

| URL | Description |
|-----|-------------|
| `api/latest.json` | Latest available date per data source |
| `api/manifest.json` | Full data inventory (all dates, sources, health stats, 550+ dates) |
| `rss/feed.xml` | Facts RSS feed |
| `rss/council.xml` | Council briefings RSS feed |

## Tertiary: Direct File Access

When running inside the knowledge repo, files can be read directly. All paths relative to repo root.

### Daily Pipeline Data

| Path | Content |
|------|---------|
| `the-council/facts/{YYYY-MM-DD}.json` | Extracted facts and insights |
| `the-council/council_briefing/{YYYY-MM-DD}.json` | Strategic council briefing |
| `the-council/aggregated/{YYYY-MM-DD}.json` | All sources consolidated |
| `the-council/highlights/{YYYY-MM-DD}.json` | 2-3 editorial top stories |

### Periodic Data

| Path | Content |
|------|---------|
| `the-council/retros/{YYYY-MM}-retro.json` | Monthly retrospective |
| `the-council/episodes/*.json` | Council episode dialogues (80+) |

### Raw Sources

| Path | Content |
|------|---------|
| `ai-news/elizaos/json/{YYYY-MM-DD}.json` | AI news data |
| `ai-news/elizaos/md/{YYYY-MM-DD}.md` | AI news readable |
| `daily-silk/{YYYY-MM-DD}.md` | Discord AI news |
| `github/stats/*.json` | Repository activity stats |
| `github/summaries/*.json` | GitHub activity summaries |
| `github/api/summaries/contributors/{username}/lifetime.json` | Contributor profiles (1500+) |

### Reference Data

| Path | Content |
|------|---------|
| `scripts/prompts/config/north-star.txt` | Mission and strategic context |
| `agents/*.json` | Character manifests |
| `agents/README.md` | Character profiles and relationships |

## JSON Schemas

### Facts File
```json
{
  "briefing_date": "YYYY-MM-DD",
  "overall_sentiment": "positive|negative|neutral|mixed",
  "categories": [
    {
      "category": "string",
      "facts": [
        {
          "claim": "string",
          "source": "string",
          "sentiment": "string",
          "confidence": "high|medium|low"
        }
      ]
    }
  ],
  "_metadata": { "status": "complete", "total_facts": 0, "model": "string" }
}
```

### Council Briefing
```json
{
  "briefing_date": "YYYY-MM-DD",
  "executive_summary": "string",
  "key_developments": [...],
  "strategic_implications": [...],
  "recommendations": [...],
  "council_commentary": {
    "eliza": "string", "aishaw": "string", "aimarc": "string",
    "spartan": "string", "peepo": "string"
  }
}
```

## Date Conventions
- All dates: `YYYY-MM-DD` format
- Pipeline runs daily ~01:00-04:30 UTC
- AI news data is T-1 (yesterday's data in today's aggregation)
