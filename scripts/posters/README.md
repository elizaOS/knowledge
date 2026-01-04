# Poster Generation System

Character-driven visual content generation for the ElizaOS digital newsmagazine.

## Quick Start

```bash
# 1. Analyze character images (creates manifest.json)
python scripts/posters/analyze.py eliza

# 2. Generate reference sheet (creates reference-sheet-{character}.png)
python scripts/posters/character-reference.py eliza

# 3. Iterate
python scripts/posters/character-reference.py eliza "shorter hair"
python scripts/posters/character-reference.py eliza cyberpunk
```

---

## Workflow Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  ANALYZE    │ ──▶ │  GENERATE   │ ──▶ │ ILLUSTRATE  │
│             │     │             │     │             │
│ Images →    │     │ Manifest →  │     │ Ref sheet + │
│ manifest    │     │ ref sheet   │     │ story →     │
│             │     │             │     │ illustration│
└─────────────┘     └─────────────┘     └─────────────┘
   analyze.py         generate.py        (coming soon)
```

---

## Directory Structure

```
scripts/posters/
├── analyze.py            # Analyze images → manifest.json
├── generate.py           # Create reference sheets
├── illustrate.py         # Story illustrations from ref sheets
├── generate-ai-image.py  # Daily news posters from facts
│
├── config/               # Configuration files
│   └── style-presets.json
│
├── assets/               # Static reference images
│   └── *.png
│
├── utils/                # Utility scripts
│   ├── generate-sampler.py
│   ├── backfill-ai-images.py
│   ├── vision.py         # General-purpose image analysis
│   ├── screenshot.py     # Web page screenshots with anti-detection
│   ├── reality_context.py # Temporal context (crypto, weather, news)
│   └── icon_sheet.py     # Icon montage generation
│
└── _deprecated/          # Old/experimental scripts
```

---

## Scripts

### analyze.py - Character Analysis

Analyzes images in a character folder to create `manifest.json` with metadata.

```bash
python scripts/posters/analyze.py eliza
python scripts/posters/analyze.py marc --verbose
```

Creates metadata for each image: pose, angle, expression, costume details.

### vision.py - General Image Analysis

Simple, standalone image analysis following Unix philosophy. Outputs to stdout.

```bash
# Basic description
python scripts/posters/utils/vision.py image.png

# Custom prompt
python scripts/posters/utils/vision.py image.png -p "What data is shown in this chart?"

# JSON output
python scripts/posters/utils/vision.py image.png -p "List the main colors" --json

# From stdin (for piping)
cat image.png | python scripts/posters/utils/vision.py - -p "describe"

# Batch analysis
for f in media/*.png; do
  echo "=== $f ==="
  python scripts/posters/utils/vision.py "$f" -p "One sentence summary"
done

# Evaluate dataviz quality
python scripts/posters/utils/vision.py output.png -p "Rate clarity 1-10. What works?"
```

| Flag | Description |
|------|-------------|
| `-p, --prompt` | Analysis prompt (default: describe image) |
| `--json` | Request JSON output from model |
| `-m, --model` | Model override |

### screenshot.py - Web Page Screenshots

Take screenshots of web pages with anti-detection measures for sites that block bots.

```bash
# Basic screenshot
python scripts/posters/utils/screenshot.py https://cryptobubbles.net -o bubbles.png

# Custom viewport size
python scripts/posters/utils/screenshot.py https://dexscreener.com/solana --width 1280 --height 720

# Full page capture (scrollable content)
python scripts/posters/utils/screenshot.py https://defillama.com/ --full-page -o defi.png

# With custom timeout for slow-loading pages
python scripts/posters/utils/screenshot.py https://example.com --timeout 60000 -o slow-site.png
```

| Flag | Description |
|------|-------------|
| `-o, --output` | Output path (default: screenshot.png) |
| `--width` | Viewport width (default: 1920) |
| `--height` | Viewport height (default: 1080) |
| `--full-page` | Capture full scrollable page |
| `--timeout` | Navigation timeout in ms (default: 30000) |

**Dependencies:** Requires Playwright with Chromium:
```bash
pip install playwright
playwright install chromium
```

### generate.py - Reference Sheet Generator

Creates canonical reference sheets with full body views and expressions.

```bash
# Basic generation
python scripts/posters/generate.py eliza

# Iterate with adjustments (overwrites reference-sheet-{character}.png)
python scripts/posters/character-reference.py eliza "bigger eyes"
python scripts/posters/character-reference.py eliza "more orange in cap"

# Themed variations (creates reference-sheet-{theme}.png)
python scripts/posters/character-reference.py eliza cyberpunk
python scripts/posters/character-reference.py eliza formal

# Add extra reference images for inspiration
python scripts/posters/character-reference.py eliza -i outfit.png
python scripts/posters/character-reference.py eliza formal -i suit-ref.jpg

# Add extra instructions
python scripts/posters/character-reference.py eliza -t "more dynamic poses"
python scripts/posters/character-reference.py eliza -i watercolor.jpg -t "apply style only to clothing"

# Custom output path
python scripts/posters/character-reference.py eliza -o my-version.png

# Preview without API call
python scripts/posters/character-reference.py eliza --dry-run

# List characters and themes
python scripts/posters/character-reference.py --list
```

#### Options

| Flag | Description |
|------|-------------|
| `-i, --input` | Extra reference image(s) for inspiration |
| `-t, --text` | Additional instructions appended to prompt |
| `-o, --output` | Custom output path |
| `--dry-run` | Show prompt without generating |
| `--list` | List available characters and themes |
| `-v, --verbose` | Enable debug logging |

#### Built-in Themes

| Theme | Description |
|-------|-------------|
| cyberpunk | Neon lights, tech wear, glowing accents |
| formal | Business professional, elegant clothing |
| casual | Everyday clothes, relaxed style |
| fantasy | Medieval/magical RPG style |
| scifi | Futuristic uniform, space age |
| streetwear | Urban, trendy fashion |
| athletic | Sports clothing, activewear |
| vintage | Retro style, classic fashion |

---

## Character Assets

Located in `scripts/posters/characters/{name}/`:

| Character | Status | Description |
|-----------|--------|-------------|
| eliza | Ready | 3D anime girl, orange/black, confident |
| marc | Ready | Charlie Brown style cyborg analyst |
| peepo | Ready | Green frog community mascot |
| spartan | Ready | Warrior with red cyborg eye |
| shaw | Needs analysis | Chibi dev with elf ears |

Each character folder contains:
```
scripts/posters/characters/eliza/
├── *.png                       # Source reference images
├── manifest.json               # Analysis metadata
├── reference-sheet-eliza.png   # Generated canonical sheet (named for model context)
└── reference-sheet-{theme}.png # Themed variations
```

---

## Manifest Schema

`manifest.json` describes each character:

```json
{
  "character": "eliza",
  "description": "3D anime-like young woman...",
  "features": {
    "distinguishing": "Long black hair, red eyes, orange cap",
    "colors": ["orange", "black", "red"],
    "costume": "Orange backward cap, cropped top, black shorts, boots",
    "style": "3D-rendered anime/cartoon"
  },
  "images": [
    {
      "filename": "stand.png",
      "pose": "full_body",
      "angle": "front",
      "expression": "neutral",
      "action": "standing",
      "features_visible": ["face", "full_costume", "feet"],
      "usable_as_reference": true
    }
  ]
}
```

---

## Configuration

### Environment Variables

```bash
export OPENROUTER_API_KEY="your-key-here"
```

### API Models

| Purpose | Model |
|---------|-------|
| Analysis | `openai/gpt-4.1` (vision) |
| Generation | `google/gemini-3-pro-image-preview` |

---

## Output Locations

| Type | Location |
|------|----------|
| Reference sheets | `scripts/posters/characters/{name}/reference-sheet*.png` |
| News posters | `media/` |
| Style samplers | `media/sampler-{date}/` |

---

## illustrate.py - Story Illustrations

Generate illustrations using character reference sheets.

```bash
# Basic - character + scene
python scripts/posters/illustrate.py eliza "celebrating a product launch"

# With art style
python scripts/posters/illustrate.py eliza "presenting at conference" -s editorial

# Multiple characters
python scripts/posters/illustrate.py eliza marc "discussing code on whiteboard"

# From facts file (auto-generates scene from summary)
python scripts/posters/illustrate.py eliza -f the-council/facts/2025-12-14.json

# Custom output
python scripts/posters/illustrate.py eliza "happy moment" -o celebration.png

# List options
python scripts/posters/illustrate.py --list-styles
python scripts/posters/illustrate.py --list-characters
```

#### Options

| Flag | Description |
|------|-------------|
| `-s, --style` | Art style (default: editorial) |
| `-f, --facts` | Generate scene from facts JSON file |
| `-o, --output` | Custom output path |
| `--with-icons` | Include logo/icon sheet for entities in facts |
| `--batch` | Generate all category visuals from facts file |
| `--list-styles` | List available art styles |
| `--list-characters` | List characters with reference sheets |
| `--dry-run` | Show prompt without generating |

---

## Entity Icons

Generate icons for entities (projects, tokens, users) extracted from the knowledge base.

### Files

| File | Purpose |
|------|---------|
| `generate-icons.py` | Generate icons via AI with reference image pipeline |
| `validate-icons.py` | Validate icons, sync manifest, show coverage stats |
| `utils/icon_sheet.py` | Create icon sheet montages for poster composition |
| `assets/manifest.json` | Entity inventory with icon_paths |
| `assets/icons/` | Generated icon files |

### Reference Image Pipeline

Before AI generation, attempts to fetch real logos:
1. **Simple Icons** - 3300+ brand SVGs (with fuzzy matching)
2. **selfhst/icons** - 2300+ self-hosted app icons (PNG)
3. **gilbarbara/logos** - 1000+ tech brand logos (SVG)
4. **GitHub Avatars** - For GitHub users/orgs
5. **Google Favicon** - For entities with URLs
6. **CoinGecko** - Token logos for crypto assets

Configure local icon libraries via environment variables:
```bash
export SELFHST_ICONS_PATH=/path/to/selfhst/icons
export GILBARBARA_LOGOS_PATH=/path/to/gilbarbara/logos
```

### Usage

```bash
# Interactive mode - generate, review, repeat
python scripts/posters/generate-icons.py -i -t project

# Batch mode
python scripts/posters/generate-icons.py --batch project --limit 4

# Single entity
python scripts/posters/generate-icons.py --entity Discord

# List entities missing icons
python scripts/posters/generate-icons.py --list

# Validate icons and sync manifest
python scripts/posters/validate-icons.py

# Show coverage stats
python scripts/posters/validate-icons.py --stats
```

### Entity Status Flow

```
Entity extracted -> status: "keep" (curated)
                 -> status: "skip" (filtered out)
                 -> status: "review" (icon rejected)
```

### Icon Sheet Montages

Create icon sheets for use in poster composition:

```bash
# From entity names
python scripts/posters/utils/icon_sheet.py bitcoin ethereum discord -o tokens.png

# From facts file (auto-extract entities)
python scripts/posters/utils/icon_sheet.py -f the-council/facts/2025-12-21.json -o daily.png

# Filter by entity type
python scripts/posters/utils/icon_sheet.py -f facts.json -t token -o tokens.png

# Dry run (show what icons would be included)
python scripts/posters/utils/icon_sheet.py -f facts.json --dry-run
```

### Batch Mode (Multi-Story Generation)

Generate all category visuals for an HTML front page:

```bash
# Batch generate all visuals with icons
python scripts/posters/illustrate.py -f the-council/facts/2025-12-21.json --batch --with-icons

# Dry run to preview what will be generated
python scripts/posters/illustrate.py -f facts.json --batch --dry-run
```

Output structure (`media/{date}/`):
```
media/2025-12-21/
├── overall.png          (editorial - hero story)
├── github-updates.png   (dataviz)
├── discord-updates.png  (comic_panel)
├── strategic-insights.png (cinematic_anime)
├── market-analysis.png  (dataviz)
├── icons.png            (entity icon sheet)
└── manifest.json        (generation metadata)
```

#### Generation Manifest

Batch mode exports a `manifest.json` with metadata for pipeline review:

```json
{
  "version": "1.0",
  "generated_at": "2025-12-21T04:00:00+00:00",
  "source_facts": "the-council/facts/2025-12-21.json",
  "facts_date": "2025-12-21",
  "models": {"image": "google/gemini-3-pro-image-preview", "llm": "openai/gpt-4.1"},
  "generations": [
    {
      "category": "overall",
      "output_file": "overall.png",
      "style": "editorial",
      "characters": ["eliza"],
      "scene_or_viz_prompt": "Eliza presenting at a conference...",
      "full_prompt": "Create an illustration for a tech news magazine...",
      "success": true,
      "generation_time_seconds": 45.2
    }
  ],
  "icon_sheet": {"output_file": "icons.png", "entities_found": ["Discord", "GitHub"]},
  "stats": {"total_generations": 5, "successful": 5, "failed": 0}
}
```

Each category gets its appropriate style:
| Category | Style | Characters |
|----------|-------|------------|
| overall | editorial | eliza |
| github_updates | dataviz | shaw, eliza |
| discord_updates | comic_panel | eliza, peepo |
| strategic_insights | cinematic_anime | eliza, marc, spartan |
| market_analysis | dataviz | marc, spartan |

### Illustration with Icons

Use `--with-icons` flag to include entity logos:

```bash
# Interactive mode with icon sheet
python scripts/posters/illustrate.py -f the-council/facts/2025-12-21.json -i --with-icons

# Direct generation with icons
python scripts/posters/illustrate.py eliza -f facts.json --with-icons -o poster.png
```

---

## CDN Upload

Upload generated posters to Bunny CDN for hosting.

### Setup

```bash
export BUNNY_STORAGE_ZONE=m3tv
export BUNNY_STORAGE_PASSWORD=your-api-key
export BUNNY_CDN_URL=https://m3tv.b-cdn.net
```

### Usage

```bash
# Upload entire directory
python scripts/integrations/cdn/upload.py media/2025-12-25/

# With manifest update (adds cdn_url to manifest.json)
python scripts/integrations/cdn/upload.py media/2025-12-25/ --update-manifest

# Dry run first
python scripts/integrations/cdn/upload.py media/2025-12-25/ --dry-run

# Update facts.json with CDN URLs from manifest
python scripts/integrations/cdn/update_facts_media.py \
  -m media/2025-12-25/manifest.json \
  -f the-council/facts/2025-12-25.json
```

### Full Workflow

```bash
DATE=2025-12-25

# 1. Generate posters (creates manifest.json)
python scripts/posters/illustrate.py --batch -f the-council/facts/${DATE}.json --with-icons

# 2. Upload to Bunny CDN
python scripts/integrations/cdn/upload.py media/${DATE}/ --update-manifest

# 3. Update facts with CDN URLs
python scripts/integrations/cdn/update_facts_media.py \
  -m media/${DATE}/manifest.json \
  -f the-council/facts/${DATE}.json
```

---

## Organic Variation System

Batch mode uses date-seeded variation to produce unique outputs each day:

### Creative Brief Components

| Component | Options | Description |
|-----------|---------|-------------|
| **Lens** | 7 | Interpretive approach (emotion, journey, conflict, etc.) |
| **Composition** | 6 | Visual framing (bird's eye, close-up, silhouette, etc.) |
| **Mood** | 16 | Seasonal (4) + Holiday (12) atmospheric tone |

**Total combinations:** 7 × 6 × 16 = **672 unique briefs**

### Holiday Moods

Special moods override seasonal defaults on ~27 days/year:

| Holiday | Dates | Special Features |
|---------|-------|------------------|
| New Year's | Dec 31 - Jan 2 | Celebration, fireworks |
| Valentine's | Feb 13-15 | Warm pinks and reds |
| St. Patrick's | Mar 16-17 | Lucky green |
| Easter | Variable (3 days) | Pastel colors, renewal |
| April Fools | Apr 1 | Playful mischief |
| Bitcoin Pizza Day | May 22 | Crypto nostalgia |
| 4th of July | Jul 3-5 | Patriotic fireworks |
| Ethereum Birthday | Jul 30 | Blockchain celebration |
| Halloween | Oct 29-31 | **Characters wear costumes** |
| Thanksgiving | Variable (3 days) | Harvest warmth |
| Christmas | Dec 23-26 | **Characters wear Santa hats** |

### Style Rotation

Each category rotates through its `suggested_styles` from `config/style-presets.json`:

```
github_updates:    dataviz → blueprint → infographic → ...
discord_updates:   comic_panel → editorial → council → ...
strategic_insights: cinematic_anime → tarot → editorial → ...
```

### Reproducibility

All randomness is date-seeded: **same date = same output**.

---

## Testing & Validation Pipeline

Tools for testing illustration scripts and validating output quality.

### test-all-scripts.py - Comprehensive Test Runner

Runs all poster scripts with various configurations and generates a comparison gallery.

```bash
# Run all tests
python scripts/posters/test-all-scripts.py

# Use specific facts file
python scripts/posters/test-all-scripts.py -f the-council/facts/2025-05-15.json

# Regenerate HTML gallery only (skip image generation)
python scripts/posters/test-all-scripts.py --html-only

# Clean previous outputs first
python scripts/posters/test-all-scripts.py --clean
```

**Output:** `media/samples/`
- `results.json` - Test results with commands, status, and image paths
- `gallery.html` - Visual comparison of all test outputs
- `illustrate/` - Generated images organized by test name

**Test Coverage:**
| Script | Tests |
|--------|-------|
| illustrate.py | batch-all, with-icons, style variations (editorial, dataviz, cinematic-anime, etc.) |
| illustrate-adaptive.py | markdown input, retro JSON input |
| create-tag-icons.py | from-facts entity extraction |

### validate-illustrations.py - AI-Powered Quality Analysis

Evaluates generated illustrations from multiple reader perspectives using vision models.

```bash
# Validate all images in results.json
python scripts/posters/validate-illustrations.py

# Validate specific test folder
python scripts/posters/validate-illustrations.py --test style-editorial

# Limit images analyzed
python scripts/posters/validate-illustrations.py --limit 5

# Dry run - show what would be analyzed
python scripts/posters/validate-illustrations.py --dry-run
```

**Reader Perspectives:**
| Archetype | Description |
|-----------|-------------|
| Casual Scroller | 2-second attention span, drawn to eye-catching visuals |
| Community Member | Follows ElizaOS daily, wants progress updates |
| Developer | Wants technical substance, dislikes generic AI art |
| First-Time Visitor | Never heard of ElizaOS, trying to understand |

**Output:** `media/samples/validation-*.json`
- Per-image scores (1-5) and engagement predictions
- Consensus rate across perspectives
- Synthesized recommendations for improvement

### enrich-facts.py - Add CDN Image URLs to Facts

Enriches facts.json files with CDN URLs for generated illustrations.

```bash
# Dry run - see what URLs would be added
python scripts/posters/enrich-facts.py the-council/facts/2025-12-25.json --dry-run

# Enrich and overwrite
python scripts/posters/enrich-facts.py the-council/facts/2025-12-25.json

# Output to different file
python scripts/posters/enrich-facts.py the-council/facts/2025-12-25.json -o enriched.json
```

**CDN URL Format:** `https://cdn.elizaos.news/posters/{date}/{filename}.png`

---

## HTML Viewers

Interactive viewers for exploring generated content. Located in `media/viewers/`.

### gallery.html - Test Output Gallery

Visual comparison of all test outputs from `test-all-scripts.py`.

- Character reference sheets
- Side-by-side script comparisons
- Test status (success/error) indicators
- Exact commands used for each test
- Lightbox for full-size viewing

**URL:** `http://localhost:8000/media/samples/gallery.html`

### validation-viewer.html - Validation Report Viewer

Displays AI validation analysis with multi-perspective feedback.

- Source context and stories analyzed
- Character reference sheets
- 50/50 image + prompt layout
- Color-coded perspective cards (engaged/skipped)
- Copy Full Report button for JSON export
- Generation and validation commands

**URL:** `http://localhost:8000/media/samples/validation-viewer.html`

### facts-viewer.html - Daily Briefing Viewer

Magazine-style visualization of enriched facts.json files.

- Hero section with overall image
- Key facts, news highlights, GitHub updates
- Discord summaries, strategic insights
- Market analysis with observations
- Open questions and tags

**URL:** `http://localhost:8000/media/facts-viewer.html`

---

## Sample Gallery

The `media/samples/` directory contains committed test outputs showcasing the system's capabilities:

```
media/samples/
├── gallery.html              # Test comparison viewer
├── validation-viewer.html    # Validation report viewer
├── results.json              # Test execution results
├── validation-*.json         # AI validation reports
├── characters/               # Character reference sheets
│   ├── reference-sheet-eliza.png
│   ├── reference-sheet-marc.png
│   └── ...
└── illustrate/               # Generated illustrations
    ├── batch-all/
    ├── with-icons/
    ├── style-editorial/
    └── ...
```

**Sample Images:**

| Category | Description |
|----------|-------------|
| overall.png | Hero editorial illustration |
| github-updates.png | Data visualization of PR/issue activity |
| discord-updates.png | Comic panel of community discussions |
| strategic-insights.png | Cinematic scene of strategic themes |
| market-analysis.png | Market data visualization |
| icons.png | Entity logo montage |

---

## RSS Integration

Generated images can enhance RSS feeds by adding visual content to daily briefings:

```python
# In RSS generation pipeline
from scripts.posters.enrich_facts import enrich_facts

# Add CDN URLs to facts before RSS generation
enriched = enrich_facts(facts_path)
# enriched['images']['overall'] -> "https://cdn.elizaos.news/posters/2025-12-25/overall.png"
```

The `images` field in enriched facts can be used to:
- Add `<enclosure>` tags in RSS items
- Include `<media:content>` for podcast apps
- Generate Open Graph images for social sharing
