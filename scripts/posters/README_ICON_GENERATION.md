# Icon Generation System

## Overview

This system generates icons/logos for entities (projects, tokens, users) extracted from the knowledge base. It uses a multi-source reference image pipeline with AI generation fallback via Nano Banana Pro (Gemini 3 Pro Image Preview).

## Key Files

| File | Purpose |
|------|---------|
| `scripts/posters/generate-icons.py` | Main icon generation script |
| `scripts/posters/validate-icons.py` | Validate icons and sync manifest |
| `scripts/posters/assets/manifest.json` | Entity inventory with icon_paths |
| `scripts/posters/assets/icons/` | Generated icon files |
| `scripts/etl/extract-entities.py` | Entity extraction (upstream) |

## Features

### Reference Image Pipeline
Before AI generation, the system attempts to fetch real logos from multiple sources:

1. **Simple Icons** (3300+ brand icons) - SVG icons for tech brands
2. **GitHub Avatars** - For GitHub users/orgs
3. **Google Favicon API** - For entities with URLs
4. **CoinGecko** - Real token logos for crypto assets

### Simple Icons Matching (with False Positive Prevention)
The matching logic uses tiered confidence levels:

| Priority | Match Type | Confidence | Min Length |
|----------|-----------|------------|------------|
| 1 | Exact title match | HIGH | Any |
| 2 | Alias match (aka/old names) | HIGH | Any |
| 3 | Suffix-stripped ("Anthropic API" → "anthropic") | MEDIUM | Any |
| 4 | Word boundary substring | LOW | 4+ chars |

**Safeguards:**
- Names < 4 chars only match via exact/alias (prevents "Go" → "Google")
- Word boundary matching (prevents "gem" → "gemini")
- Domain verification as bonus (uses Simple Icons `source` field)

### Generation Modes
- **Interactive mode** (`-i`): Generate -> Curate -> Repeat loop
- **Batch generation**: Generate multiple icons in a grid
- **Single entity**: Generate one icon at a time

### Other Features
- **Grid slicing**: Splits grid image into individual icons
- **Manifest sync**: Updates icon_paths after generation
- **Status tracking**: Marks deleted icons as `status: "review"`
- **Numbered filenames**: `entity-1.png`, `entity-2.png` for variants

## Usage

```bash
# Interactive mode (recommended)
python scripts/posters/generate-icons.py -i -t project

# Batch mode
python scripts/posters/generate-icons.py --batch project --limit 4

# Single entity
python scripts/posters/generate-icons.py --entity Discord

# List missing
python scripts/posters/generate-icons.py --list

# With verbose logging
python scripts/posters/generate-icons.py -i -t project -v

# Sync manifest after manual changes
python scripts/posters/validate-icons.py --sync-only
```

## Entity Status Flow

```
Entity extracted -> status: "keep" (curated)
                 -> status: "skip" (junk, filtered out)
                 -> status: "review" (icon deleted during curation)

get_missing_entities() returns entities where:
- status == "keep"
- icon_paths is empty or missing
```

## API Configuration

```python
IMAGE_MODEL = "google/gemini-3-pro-image-preview"
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

{
    "model": IMAGE_MODEL,
    "modalities": ["image", "text"],
    "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    "image_config": {"aspect_ratio": "1:1"}
}
```

## Environment

```bash
OPENROUTER_API_KEY=your_key
```
