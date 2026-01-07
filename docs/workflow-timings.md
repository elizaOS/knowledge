# Workflow Timings & Dependencies

This document maps the complete data pipeline across all upstream sources and the knowledge repo. Useful for debugging, optimization, or migration to orchestration tools like Dagster.

## Overview

The knowledge repo aggregates data from multiple upstream sources, each with their own automation schedules. Our pipeline is timed to run **after** all upstream sources complete their daily processing.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         UPSTREAM SOURCES                                │
├─────────────────────────────────────────────────────────────────────────┤
│  14:10 UTC (prev day)  madjin/daily-silk                               │
│  23:00 UTC (prev day)  elizaOS/elizaos.github.io                       │
│  00:00 UTC             M3-org/ai-news                                  │
│  00:30-07:30 UTC       M3-org/ai-news (CDN upload)                     │
├─────────────────────────────────────────────────────────────────────────┤
│                         KNOWLEDGE REPO                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  08:00 UTC             sync.yml                                        │
│  08:30 UTC             aggregate-daily-sources.yml                     │
│  08:45 UTC             extract_daily_facts.yml                         │
│  09:00 UTC             generate-council-briefing.yml                   │
│  09:30 UTC             update_hackmd_notes.yml                         │
│  10:00 UTC             generate-posters.yml                            │
│  10:30 UTC             daily_discord_briefing.yml                      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Upstream Sources

### 1. elizaOS/elizaos.github.io

**Repository**: https://github.com/elizaOS/elizaos.github.io

**Purpose**: GitHub activity tracking, contributor analytics, and AI-generated summaries for elizaOS repositories.

**Workflows**:

| Workflow | Schedule | Description |
|----------|----------|-------------|
| `run-pipelines.yml` | 23:00 UTC | Main pipeline: ingest GitHub data, process, export, generate summaries |
| `generate-summaries.yml` | workflow_run | Triggered after ingest/export; generates repo/overall/contributor summaries |

**Data Output**:
- Branch: `_data`
- Paths synced by knowledge repo:
  - `data/elizaos_eliza/` → `github/`
  - `data/dump/` → `github/`
  - `data/summaries/` → `github/summaries/`
  - `data/api/` → `github/api/`
  - `data/contributors/` → `github/contributors/`

**Completion Time**: ~23:30 UTC (30 min after start)

---

### 2. M3-org/ai-news

**Repository**: https://github.com/M3-org/ai-news

**Purpose**: Discord message aggregation, AI summarization, media CDN hosting, and daily news generation.

**Workflows**:

| Workflow | Schedule | Description |
|----------|----------|-------------|
| `elizaos.yml` | 00:00 UTC | Collect Discord data, generate JSON/MD summaries, deploy to gh-pages |
| `media-cdn-upload.yml` | workflow_run OR 07:30 UTC | Download media, upload to Bunny CDN, create json-cdn with swapped URLs |

**Data Output**:
- Branch: `gh-pages`
- Paths synced by knowledge repo:
  - `elizaos/json/` → `ai-news/elizaos/json/`
  - `elizaos/json-cdn/` → `ai-news/elizaos/json-cdn/` (CDN-enriched, has poster/meme URLs)
  - `elizaos/md/` → `ai-news/elizaos/md/`
  - `elizaos/discord/` → `ai-news/elizaos/discord/`
  - `hyperfy/` → `ai-news/hyperfy/`

**Key Files**:
- `json-cdn/{date}.json` - Contains `poster`, `meme`, and CDN-swapped media URLs
- `media-manifest.json` - Media file inventory with CDN URLs

**Completion Time**:
- `elizaos.yml`: ~00:30 UTC
- `media-cdn-upload.yml`: 00:30 UTC (workflow_run) or 07:30 UTC (backup)

**Important**: The `json-cdn/` directory may already contain poster/meme URLs from upstream. Knowledge repo should check for existing URLs before generating locally.

---

### 3. madjin/daily-silk

**Repository**: https://github.com/madjin/daily-silk

**Purpose**: Daily Discord message capture from AI news channels.

**Workflows**:

| Workflow | Schedule | Description |
|----------|----------|-------------|
| `discord-fetch.yml` | 14:10 UTC | Fetch Discord messages, save as JSON/MD |

**Data Output**:
- Branch: `main`
- Paths synced by knowledge repo:
  - `data/*.md` → `daily-silk/`

**Completion Time**: ~14:15 UTC

**Note**: This runs at 14:10 UTC, so at our 08:00 UTC sync, we get the **previous day's** data. This is expected behavior for daily summaries.

---

### 4. m3-org/clanktank

**Repository**: https://github.com/m3-org/clanktank

**Purpose**: Clank Tank episode scripts and metadata.

**Workflows**: None (manual updates)

**Data Output**:
- Branch: `main`
- Paths synced: `episodes/*.json` → `clanktank/episodes/`

---

### 5. m3-org/the-council

**Repository**: https://github.com/m3-org/the-council

**Purpose**: Council episode recordings and transcripts.

**Workflows**: None (manual updates)

**Data Output**:
- Branch: `main`
- Paths synced: `episodes/*.json` → `the-council/episodes/`

---

## Knowledge Repo Pipeline

### Daily Schedule (UTC)

| Time | Workflow | Depends On | Outputs |
|------|----------|------------|---------|
| **08:00** | `sync.yml` | All upstream sources | `ai-news/`, `github/`, `daily-silk/`, `docs/` |
| **08:30** | `aggregate-daily-sources.yml` | sync.yml | `the-council/aggregated/{date}.json` |
| **08:45** | `extract_daily_facts.yml` | aggregate | `the-council/facts/{date}.json`, `hackmd/facts/`, `rss/` |
| **09:00** | `generate-council-briefing.yml` | facts | `the-council/council_briefing/{date}.json` |
| **09:30** | `update_hackmd_notes.yml` | council briefing | `hackmd/**/*.md`, `book.json` |
| **10:00** | `generate-posters.yml` | hackmd, facts | `media/{date}/`, CDN upload |
| **10:30** | `daily_discord_briefing.yml` | posters | Discord messages |

### Periodic Workflows

| Schedule | Workflow | Description |
|----------|----------|-------------|
| 1st of month @ 03:00 | `retro.yml` | Monthly retrospective |
| 1st of Jan/Apr/Jul/Oct @ 04:00 | `retro.yml` | Quarterly summary |
| 2nd of Jan @ 05:00 | `retro.yml` | Annual summary |

---

## Dependency Graph

```
                    ┌──────────────────┐
                    │  elizaos.github  │
                    │  (23:00 prev)    │
                    └────────┬─────────┘
                             │
┌──────────────┐    ┌────────▼─────────┐    ┌──────────────┐
│  daily-silk  │    │    ai-news       │    │  clanktank   │
│ (14:10 prev) │    │ (00:00-07:30)    │    │  (manual)    │
└──────┬───────┘    └────────┬─────────┘    └──────┬───────┘
       │                     │                     │
       │    ┌────────────────┼────────────────┐    │
       │    │                │                │    │
       ▼    ▼                ▼                ▼    ▼
    ┌─────────────────────────────────────────────────┐
    │              sync.yml (08:00)                   │
    └─────────────────────┬───────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────────────┐
    │         aggregate-daily-sources (08:30)         │
    └─────────────────────┬───────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────────────┐
    │           extract_daily_facts (08:45)           │
    └─────────────────────┬───────────────────────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
    ┌─────────────────┐     ┌─────────────────┐
    │ council-briefing│     │   RSS feeds     │
    │    (09:00)      │     │                 │
    └────────┬────────┘     └─────────────────┘
             │
             ▼
    ┌─────────────────────────────────────────────────┐
    │            update_hackmd_notes (09:30)          │
    └─────────────────────┬───────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────────────┐
    │            generate-posters (10:00)             │
    │  [Checks upstream json-cdn for existing URLs]   │
    └─────────────────────┬───────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────────────┐
    │         daily_discord_briefing (10:30)          │
    └─────────────────────────────────────────────────┘
```

---

## Data Freshness at Sync (08:00 UTC)

| Source | Last Updated | Age | Notes |
|--------|--------------|-----|-------|
| elizaOS/elizaos.github.io | ~23:30 (prev) | ~8.5 hrs | GitHub activity from previous day |
| M3-org/ai-news | 00:30-07:30 | 0.5-7.5 hrs | Discord data, json-cdn ready |
| madjin/daily-silk | 14:10 (prev) | ~18 hrs | Previous day's Discord capture |
| m3-org/clanktank | Manual | Variable | Episode scripts |
| m3-org/the-council | Manual | Variable | Council recordings |

---

## Key Considerations for Orchestration Migration

### Current Limitations (Cron-based)

1. **No true dependency management** - Workflows use time-based scheduling, not completion triggers
2. **Fixed delays** - 15-30 min gaps between steps to ensure previous step completes
3. **No retry on upstream failure** - If ai-news fails, knowledge pipeline runs anyway
4. **Wasted compute** - Poster generation runs even if upstream already has posters

### Dagster Migration Benefits

1. **Asset-based dependencies** - Run downstream only when upstream assets materialize
2. **Cross-repo sensors** - Trigger on GitHub webhook events or file changes
3. **Conditional execution** - Skip poster generation if `json-cdn.poster` exists
4. **Backfill support** - Easily reprocess historical dates
5. **Observability** - Unified view of entire pipeline health

### Suggested Dagster Asset Graph

```python
# Upstream assets (external, sensor-triggered)
@asset(group="upstream")
def github_summaries(): ...  # Sensor: elizaos.github.io _data branch

@asset(group="upstream")
def ai_news_json_cdn(): ...  # Sensor: ai-news gh-pages branch

@asset(group="upstream")
def daily_silk(): ...  # Sensor: daily-silk main branch

# Knowledge repo assets
@asset(deps=[github_summaries, ai_news_json_cdn, daily_silk])
def aggregated_daily(): ...

@asset(deps=[aggregated_daily])
def daily_facts(): ...

@asset(deps=[daily_facts])
def council_briefing(): ...

@asset(deps=[council_briefing])
def hackmd_notes(): ...

@asset(deps=[daily_facts, ai_news_json_cdn])  # Check json-cdn first!
def posters():
    if ai_news_json_cdn.has_poster_urls():
        return skip()  # Use upstream posters
    return generate_posters()

@asset(deps=[posters, daily_facts])
def discord_briefing(): ...
```

### Sensor Examples

```python
@sensor(job=sync_job)
def ai_news_sensor(context):
    """Trigger sync when ai-news gh-pages updates."""
    last_commit = get_github_branch_sha("M3-org/ai-news", "gh-pages")
    if last_commit != context.cursor:
        yield RunRequest(run_key=last_commit)
        context.update_cursor(last_commit)
```

---

## Troubleshooting

### Pipeline ran but data is stale

1. Check upstream workflow runs:
   - https://github.com/elizaOS/elizaos.github.io/actions
   - https://github.com/M3-org/ai-news/actions
   - https://github.com/madjin/daily-silk/actions

2. Verify sync.yml pulled latest:
   ```bash
   git log --oneline ai-news/ | head -1
   git log --oneline github/ | head -1
   ```

### Poster generation overwrites upstream URLs

The `generate-posters.yml` workflow should check for existing URLs in `ai-news/elizaos/json-cdn/` before generating. If upstream already has `poster` field populated, skip local generation.

### Workflows running out of order

All workflows use the same concurrency group (`knowledge-repo-writes`) to prevent parallel execution. If timing drifts, increase gaps between cron schedules.

---

## Changelog

- **2026-01-07**: Rescheduled pipeline to run after sync (08:00-10:30 UTC)
  - Previously ran at 01:30-04:30 UTC on stale data
  - sync.yml was at 08:00 but pipeline ran before it
- **2025-12-31**: Added CDN media pipeline integration
- **2025-12-22**: Initial documentation
