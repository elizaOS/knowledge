# Poster Generation System

Character-driven visual content generation for the ElizaOS digital newsmagazine.

## Quick Start

```bash
# Generate a character turnaround sheet
python scripts/posters/generate.py eliza turnaround

# Generate a single pose
python scripts/posters/generate.py eliza pose happy

# See all options
python scripts/posters/generate.py --list
```

---

## Directory Structure

```
scripts/posters/
├── README.md                 # This file
│
├── ─── PRIMARY SCRIPTS ─────────────────────────────
├── generate.py               # Character assets (turnarounds, poses)
├── analyze-characters.py     # Analyze images → manifest.json
├── generate-ai-image.py      # Daily news posters from facts
│
├── config/                   # Configuration files
│   ├── style-presets.json    # 12 art style definitions
│   └── style-presets-v1.json # Archived v1 presets
│
├── assets/                   # Static reference images
│   ├── eliza.png             # Quick refs for news posters
│   ├── marc.png
│   ├── peepo.png
│   └── spartan.png
│
├── utils/                    # Utility scripts
│   ├── generate-sampler.py   # Generate all style variations
│   ├── backfill-ai-images.py # Backfill missing images
│   ├── posters-enhanced.sh   # Shell-based poster generation
│   └── run-poster-generation.sh
│
└── _deprecated/              # Experimental/replaced scripts
    ├── generate-character-poses.py  # Replaced by generate.py
    ├── test-reference-sheet.py      # Experimental
    ├── pose-presets.json.archived   # Archived config
    └── CHARACTER-ASSETS-README.md   # Superseded by this README
```

---

## Primary Workflow

### 1. Analyze Character Images

Creates `manifest.json` with metadata for each image (pose, angle, expression, costume details).

```bash
python scripts/posters/analyze-characters.py --character eliza
```

### 2. Generate Character Assets

Uses manifest metadata to intelligently select references and build rich prompts.

```bash
# Turnaround sheet (4 views)
python scripts/posters/generate.py eliza turnaround

# Expression sheet (6 expressions)
python scripts/posters/generate.py eliza expressions

# Single pose
python scripts/posters/generate.py eliza pose happy
python scripts/posters/generate.py eliza pose "waving at viewer" --angle 3/4_right

# Sketch mode (faster iteration)
python scripts/posters/generate.py eliza turnaround --sketch
```

### 3. Generate News Posters

Creates daily news illustrations from facts data.

```bash
python scripts/posters/generate-ai-image.py -d 2025-12-13 --style editorial
```

---

## Character Assets

Located in `posters/characters/{name}/`:

| Character | Status | Images | Description |
|-----------|--------|--------|-------------|
| eliza | Ready | 18 | 3D anime girl, orange/black, confident |
| marc | Needs analysis | 15 | Charlie Brown style cyborg analyst |
| peepo | Needs analysis | 10 | Green frog community mascot |
| spartan | Needs analysis | 15 | Warrior with red cyborg eye |
| shaw | Needs analysis | 15 | Chibi dev with elf ears |

---

## generate.py Reference

### Output Types

| Type | Description | Refs Used |
|------|-------------|-----------|
| `turnaround` | 4-view model sheet | full_body only |
| `expressions` | 6-expression grid | bust/portrait only |
| `pose` | Single character pose | 1 full_body + 1 face |

### Predefined Poses

| Pose | Use For |
|------|---------|
| `neutral` | Avatars, profile pics |
| `happy` | Positive news, wins |
| `serious` | Security alerts, announcements |
| `thinking` | Analysis, strategy |
| `explaining` | Tutorials, how-tos |
| `celebrating` | Milestones, achievements |
| `pointing` | Calls to action |
| `skeptical` | Due diligence |

### Options

```bash
--sketch          # Line art only (faster iteration)
--angle ANGLE     # front, 3/4_left, 3/4_right, side_left, side_right
--output PATH     # Custom output path
--dry-run         # Preview without API call
--verbose         # Debug logging
```

---

## Utility Scripts

### Style Sampler
Generate all 12 style variations for comparison:
```bash
python scripts/posters/utils/generate-sampler.py -d 2025-12-13
```

### Backfill Images
Fill in missing historical images:
```bash
python scripts/posters/utils/backfill-ai-images.py --days 7 --style editorial
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
| Analysis | `openai/gpt-5.2` (vision) |
| Generation | `google/gemini-3-pro-image-preview` |

### Style Presets

12 art styles defined in `config/style-presets.json`:

- editorial, risograph, tarot, collage
- ukiyo_e, synthwave, bauhaus, noir_ink
- paper_cutout, blueprint, pixel_art, council

---

## Output Locations

| Type | Location |
|------|----------|
| Character assets | `posters/characters/{name}/generated/` |
| News posters | `posters/` |
| Style samplers | `posters/sampler-{date}/` |

---

## Manifest Schema

Character manifests in `posters/characters/{name}/manifest.json`:

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
      "pose": "full_body",
      "angle": "front",
      "expression": "neutral",
      "action": "standing",
      "features_visible": ["face", "full_costume", "feet"],
      "usable_as_reference": true,
      "filename": "stand.png"
    }
  ]
}
```
