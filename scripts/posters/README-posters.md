# Poster Generation Scripts

This directory contains multiple approaches to generating editorial illustrations from daily briefings. Each script represents a different "artist" with its own philosophy and workflow.

## Quick Comparison

### Poster Generation

| Script | Lines | Philosophy | Best For |
|--------|-------|------------|----------|
| `generate-ai-image.py` | ~550 | Simple & direct | Quick single images, style previews |
| `illustrate.py` | ~1500 | Config-driven rules engine | Production batches, deterministic output |
| `illustrate-adaptive.py` | ~650 | LLM content analyzer | Adaptive generation, icon integration |
| `scene_director.py` | ~400 | LLM creative director | Editorial metaphors, cohesive day sets |

### Character & Icon Tools

| Script | Purpose |
|--------|---------|
| `character-reference.py` | Generate character reference sheets |
| `character-analyze.py` | Analyze character images → manifest.json |
| `create-tag-icons.py` | Create icons from tag words |
| `create-entity-icons.py` | Create icons for entities (projects, tokens) |
| `validate-entity-icons.py` | Validate entity icons and sync to manifest |

---

## generate-ai-image.py

**The Quick Sketch Artist**

Simple, straightforward image generation. Takes facts, generates a prompt, creates an image.

```bash
# Generate today's poster
python generate-ai-image.py

# Specific date and style
python generate-ai-image.py -d 2025-10-28 --style noir_ink

# Preview all styles
python generate-ai-image.py --preview-styles

# Generate per-category images
python generate-ai-image.py --by-category
```

**Features:**
- GPT-5.2 for prompt generation, Gemini 3 Pro for images
- Simple asset-based character references (`assets/*.png`)
- Style presets from `config/style-presets.json`
- Category-based batch generation
- Style preview mode

**When to use:** Quick iterations, testing styles, simple one-off images.

---

## illustrate.py

**The Staff Illustrator**

Comprehensive, config-driven system with many features. The most mature and feature-rich option.

```bash
# Interactive mode - choose what to generate
python illustrate.py the-council/facts/2025-10-28.json -i

# Batch mode - generate all categories
python illustrate.py the-council/facts/2025-10-28.json --batch

# Dry run to see what would be generated
python illustrate.py the-council/facts/2025-10-28.json --batch --dry-run

# List available styles/characters
python illustrate.py --list-styles
python illustrate.py --list-characters
```

**Features:**
- Interactive and batch modes
- Character reference sheets with full manifests (`characters/*/`)
- Holiday and seasonal mood detection
- Creative brief system (lens + composition + mood)
- Date-seeded style/character rotation for variety
- Category → style/character mappings
- Data visualization support for abstract content

**When to use:** Production daily briefings, when you want consistent deterministic output.

---

## illustrate-adaptive.py

**The Technical Artist**

Streamlined LLM-driven approach with content analysis and icon support.

```bash
# Run pipeline
python illustrate-adaptive.py the-council/facts/2025-10-28.json

# With icon/logo integration
python illustrate-adaptive.py the-council/facts/2025-10-28.json --with-icons

# Dry run
python illustrate-adaptive.py the-council/facts/2025-10-28.json --dry-run
```

**Features:**
- LLM analyzes content structure (fingerprinting)
- Generates scene descriptions dynamically
- Entity extraction for icon integration
- Simpler codebase than illustrate.py
- Single pipeline (no interactive mode)

**When to use:** When content varies significantly, when you want icons/logos in images.

---

## scene_director.py

**The Editorial Director**

LLM acts as creative director, planning visual metaphors for the whole day as a cohesive set.

```bash
# Generate 4-scene editorial set
python scene_director.py the-council/facts/2025-10-28.json

# Dry run - just generate plan and prompts
python scene_director.py the-council/facts/2025-10-28.json --dry-run

# Override the day's style
python scene_director.py the-council/facts/2025-10-28.json --style "Tech Noir"
python scene_director.py the-council/facts/2025-10-28.json -s "Warm Industrial"
```

**Features:**
- LLM picks unified day aesthetic (batch coherence)
- Visual metaphors, never literal descriptions
- Character casting based on story energy
- 4 scenes per day = mini graphic novel chapter
- Simplified prompts focused on reference sheet fidelity
- Style override option

**When to use:** Editorial/magazine feel, when you want cohesive visual storytelling.

---

## Key Differences

### Style Selection

| Script | How style is chosen |
|--------|---------------------|
| `generate-ai-image.py` | CLI flag or category mapping |
| `illustrate.py` | Category mapping + day-of-year rotation |
| `illustrate-adaptive.py` | LLM picks based on content analysis |
| `scene_director.py` | LLM picks ONE style for all 4 daily scenes |

### Character References

| Script | Reference approach |
|--------|-------------------|
| `generate-ai-image.py` | Simple PNGs in `assets/` |
| `illustrate.py` | Reference sheets + manifests in `characters/*/` |
| `illustrate-adaptive.py` | Same as illustrate.py |
| `scene_director.py` | Same as illustrate.py |

### Scene Generation

| Script | How scenes are described |
|--------|-------------------------|
| `generate-ai-image.py` | LLM generates prompt from summary |
| `illustrate.py` | Template-based with creative brief modifiers |
| `illustrate-adaptive.py` | LLM generates scene from content analysis |
| `scene_director.py` | LLM creates visual METAPHORS (never literal) |

---

## Shared Resources

All scripts share these resources:

```
scripts/posters/
├── config/
│   └── style-presets.json    # Style definitions, category mappings
├── characters/
│   ├── eliza/
│   │   ├── reference-sheet.png
│   │   └── manifest.json
│   ├── shaw/
│   ├── spartan/
│   ├── marc/
│   └── peepo/
├── assets/                    # Simple character PNGs (legacy)
└── icons/                     # Generated entity icons
```

---

## Choosing an Artist

**Need something quick?** → `generate-ai-image.py`

**Need reliable production output?** → `illustrate.py --batch`

**Content is unusual/varied?** → `illustrate-adaptive.py`

**Want editorial storytelling?** → `scene_director.py`

**Experimenting with styles?** → `generate-ai-image.py --preview-styles`

---

## Environment Variables

All scripts require:
```bash
export OPENROUTER_API_KEY="your-key"
```

---

## Output Locations

| Script | Default output |
|--------|---------------|
| `generate-ai-image.py` | `../../posters/` (workspace root) |
| `illustrate.py` | `media/{date}/` |
| `illustrate-adaptive.py` | `media/{date}/` |
| `scene_director.py` | `test_output/{date}_director/` |

---

## Prompt Logging

All scripts save prompts alongside generated images for quality control and iteration:

```
output/
├── 2025-10-28-discord-updates-editorial.png
├── 2025-10-28-discord-updates-editorial.txt  # ← prompt used
├── 2025-10-28-github-updates-noir_ink.png
└── 2025-10-28-github-updates-noir_ink.txt    # ← prompt used
```

This enables:
- **Quality control** - see what prompt produced what image
- **Iteration** - tweak prompts and regenerate
- **Debugging** - understand why an image looks a certain way
- **Learning** - build intuition for what prompts work best
