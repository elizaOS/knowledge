# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automating the elizaOS knowledge aggregation pipeline.

## Daily Pipeline Schedule (UTC)

The pipeline runs after upstream `M3-org/ai-news` completes its daily processing (~07:30 UTC):

| Time | Workflow | Description |
|------|----------|-------------|
| **08:00** | `sync.yml` | Sync external data sources |
| **08:30** | `aggregate-daily-sources.yml` | Aggregate all sources into daily JSON |
| **08:45** | `extract_daily_facts.yml` | Extract facts using LLM |
| **09:00** | `generate-council-briefing.yml` | Generate strategic council briefing |
| **09:30** | `update_hackmd_notes.yml` | Update HackMD documentation |
| **10:00** | `generate-posters.yml` | Generate visual content, enrich facts, generate RSS |
| **10:30** | `daily_discord_briefing.yml` | Send briefing to Discord |

### Periodic Retrospectives (`retro.yml`)
- **Monthly** (1st of each month @ 03:00 UTC) - Council retrospective episode
- **Quarterly** (1st of Jan/Apr/Jul/Oct @ 04:00 UTC) - Strategic summary
- **Annual** (Jan 2nd @ 05:00 UTC) - Year-in-review summary

---

## Workflow Details

### 1. `sync.yml` - Sync Knowledge Sources

**Trigger**: Daily at 08:00 UTC, manual dispatch

Synchronizes data from external repositories:
- **ElizaOS Docs**: `elizaOS/eliza` (develop branch) → `docs/`
- **Daily Silk**: `madjin/daily-silk` → `daily-silk/`
- **GitHub Activity**: `elizaos/elizaos.github.io` (_data branch) → `github/`
- **AI News**: `M3-org/ai-news` (gh-pages branch) → `ai-news/`
- **Clanktank Episodes**: `m3-org/clanktank` → `clanktank/episodes/`
- **Council Episodes**: `m3-org/the-council` → `the-council/episodes/`

### 2. `aggregate-daily-sources.yml` - Aggregate Daily Sources

**Trigger**: Daily at 08:30 UTC, manual dispatch

Runs `scripts/etl/aggregate-sources.py` to consolidate all synced data into a single JSON file at `the-council/aggregated/YYYY-MM-DD.json`. Creates `daily.json` permalink.

### 3. `extract_daily_facts.yml` - Extract Daily Facts

**Trigger**: Daily at 08:45 UTC, manual dispatch

Runs `scripts/etl/extract-facts.py` with LLM processing to extract key insights from aggregated data. Outputs:
- `the-council/facts/YYYY-MM-DD.json`
- `hackmd/facts/YYYY-MM-DD.md`
- `the-council/facts/daily.json` (permalink)

### 4. `generate-council-briefing.yml` - Generate Council Briefing

**Trigger**: Daily at 09:00 UTC, manual dispatch

Runs `scripts/etl/generate-council-context.py` to create strategic council briefings using LLM. Also generates RSS feeds. Outputs:
- `the-council/council_briefing/YYYY-MM-DD.json`
- `the-council/council_briefing/daily.json` (permalink)
- `rss/feed.xml` and `rss/council.xml`

### 5. `update_hackmd_notes.yml` - Update HackMD Notes

**Trigger**: Daily at 09:30 UTC, manual dispatch

Updates HackMD collaborative documentation:
- Runs `scripts/integrations/hackmd/create.py` to initialize new notes
- Runs `scripts/integrations/hackmd/update.py` to generate content using LLM
- Syncs content from source directories as configured in `book.json`
- Creates local backups in `hackmd/` directory

### 6. `generate-posters.yml` - Generate Content Posters

**Trigger**: Daily at 10:00 UTC, manual dispatch

Generates visual content using `scripts/posters/illustrate.py`:
- Creates illustrations from facts data with ElizaOS branding
- Uploads to Bunny CDN (if credentials available)
- Enriches facts and source files with media URLs
- Generates RSS feeds
- Cleans up media older than 7 days

### 7. `daily_discord_briefing.yml` - Daily Discord Facts Briefing

**Trigger**: Daily at 10:30 UTC, manual dispatch

Sends the daily facts briefing to Discord using `scripts/integrations/discord/webhook.py` with LLM-powered summarization and poster images.

### 8. `retro.yml` - Council Retrospectives

**Trigger**: Scheduled (monthly/quarterly/annual), manual dispatch

Generates retrospective content:
- **Monthly**: `scripts/etl/generate-monthly-retro.py`
- **Quarterly/Annual**: `scripts/etl/generate-quarterly-summary.py`

Outputs to `the-council/retros/` and `the-council/episodes/`.

### 9. `generate-illustrations.yml` - Generate Illustrations (Manual)

**Trigger**: Manual dispatch only

On-demand illustration generation with full configuration:
- Custom date selection
- Dry-run mode
- CDN upload toggle
- Facts enrichment toggle
- Icon sheet generation

### 10. `knowledge-gh-pages.yml` - Deploy to GitHub Pages

**Trigger**: Push to main branch, manual dispatch

Deploys repository content to GitHub Pages:
- Stages content from all data directories
- Filters posters to last 7 days (size optimization)
- Generates directory listing
- Uploads artifact and deploys

---

## Shared Components

### Composite Actions

Located in `.github/actions/`:

#### `setup-python-env`
Standardized Python environment setup:
```yaml
- uses: ./.github/actions/setup-python-env
  with:
    python-version: '3.12'  # default
    packages: 'requests'     # space-separated list
```

#### `alert-failure`
Standardized failure alerting to Discord:
```yaml
- uses: ./.github/actions/alert-failure
  with:
    webhook-url: ${{ secrets.ALERT_WEBHOOK_URL }}
    workflow-name: 'Workflow Name'
```

### Concurrency Control

Most ETL workflows use the same concurrency group to prevent simultaneous writes:
```yaml
concurrency:
  group: knowledge-repo-writes
  cancel-in-progress: false
```

---

## Environment Variables

| Secret | Used By | Purpose |
|--------|---------|---------|
| `OPENROUTER_API_KEY` | Most ETL workflows | LLM API access |
| `DISCORD_BOT_TOKEN` | daily_discord_briefing | Discord posting |
| `HMD_API_ACCESS_TOKEN` | update_hackmd_notes | HackMD API |
| `ALERT_WEBHOOK_URL` | All workflows | Failure alerts |
| `GH_PAT` | sync | Enhanced Git authentication |
| `BUNNY_STORAGE_PASSWORD` | generate-posters | CDN upload |
| `BUNNY_STORAGE_ZONE` | generate-posters | CDN configuration |

---

## Troubleshooting

### Common Issues

1. **Workflow fails at aggregation**: Check if sync.yml completed successfully
2. **Missing facts file**: Ensure extract_daily_facts ran after aggregation
3. **Discord posting fails**: Verify bot token and channel permissions
4. **CDN upload fails**: Check Bunny credentials and storage zone

### Manual Triggers

All workflows support `workflow_dispatch` for manual triggering via GitHub UI or CLI:
```bash
gh workflow run sync.yml
gh workflow run extract_daily_facts.yml
```

### Backfilling Data

Use the backfill scripts for missing data:
```bash
OPENROUTER_API_KEY=key ./scripts/etl/backfill-facts.sh 2026-01-09 2026-01-12
OPENROUTER_API_KEY=key ./scripts/etl/backfill-council.sh 2026-01-09 2026-01-12
```
