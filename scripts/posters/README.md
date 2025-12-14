# Poster Generation System

Character-driven visual content generation for the ElizaOS digital newsmagazine.

## Quick Start

```bash
# 1. Analyze character images (creates manifest.json)
python scripts/posters/analyze.py eliza

# 2. Generate reference sheet (creates reference-sheet.png)
python scripts/posters/generate.py eliza

# 3. Iterate with live preview
open posters/characters/eliza/preview.html
python scripts/posters/generate.py eliza "shorter hair"
python scripts/posters/generate.py eliza cyberpunk
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
│   └── backfill-ai-images.py
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

### generate.py - Reference Sheet Generator

Creates canonical reference sheets with full body views and expressions.

```bash
# Basic generation
python scripts/posters/generate.py eliza

# Iterate with adjustments (overwrites reference-sheet.png)
python scripts/posters/generate.py eliza "bigger eyes"
python scripts/posters/generate.py eliza "more orange in cap"

# Themed variations (creates reference-sheet-{theme}.png)
python scripts/posters/generate.py eliza cyberpunk
python scripts/posters/generate.py eliza formal

# Add extra reference images for inspiration
python scripts/posters/generate.py eliza -i outfit.png
python scripts/posters/generate.py eliza formal -i suit-ref.jpg

# Add extra instructions
python scripts/posters/generate.py eliza -t "more dynamic poses"
python scripts/posters/generate.py eliza -i watercolor.jpg -t "apply style only to clothing"

# Custom output path
python scripts/posters/generate.py eliza -o my-version.png

# Preview without API call
python scripts/posters/generate.py eliza --dry-run

# List characters and themes
python scripts/posters/generate.py --list
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

#### Live Preview

Each character folder gets a `preview.html` that auto-refreshes:

```bash
# Terminal 1: Open in browser
open posters/characters/eliza/preview.html

# Terminal 2: Iterate
python scripts/posters/generate.py eliza
python scripts/posters/generate.py eliza "adjust the eyes"
# Browser updates automatically every 2 seconds
```

---

## Character Assets

Located in `posters/characters/{name}/`:

| Character | Status | Description |
|-----------|--------|-------------|
| eliza | Ready | 3D anime girl, orange/black, confident |
| marc | Ready | Charlie Brown style cyborg analyst |
| peepo | Ready | Green frog community mascot |
| spartan | Ready | Warrior with red cyborg eye |
| shaw | Needs analysis | Chibi dev with elf ears |

Each character folder contains:
```
posters/characters/eliza/
├── *.png              # Source reference images
├── manifest.json      # Analysis metadata
├── reference-sheet.png    # Generated canonical sheet
├── reference-sheet-*.png  # Themed variations
└── preview.html       # Auto-refreshing browser preview
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
| Reference sheets | `posters/characters/{name}/reference-sheet*.png` |
| News posters | `posters/` |
| Style samplers | `posters/sampler-{date}/` |

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
| `--list-styles` | List available art styles |
| `--list-characters` | List characters with reference sheets |
| `--dry-run` | Show prompt without generating |
