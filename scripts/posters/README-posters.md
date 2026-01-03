# Poster Generation Scripts

This directory contains multiple approaches to generating editorial illustrations from daily briefings. Each script represents a different "artist" with its own philosophy and workflow.

## Quick Comparison

### Poster Generation

| Script | Lines | Philosophy | Best For |
|--------|-------|------------|----------|
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
| `illustrate.py` | Category mapping + day-of-year rotation |
| `illustrate-adaptive.py` | LLM picks based on content analysis |
| `scene_director.py` | LLM picks ONE style for all 4 daily scenes |

### Character References

| Script | Reference approach |
|--------|-------------------|
| `illustrate.py` | Reference sheets + manifests in `characters/*/` |
| `illustrate-adaptive.py` | Same as illustrate.py |
| `scene_director.py` | Same as illustrate.py |

### Scene Generation

| Script | How scenes are described |
|--------|-------------------------|
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

**Need reliable production output?** → `illustrate.py --batch`

**Content is unusual/varied?** → `illustrate-adaptive.py`

**Want editorial storytelling?** → `scene_director.py`

---

## Environment Variables

All scripts require:
```bash
export OPENROUTER_API_KEY="your-key"
```

---

## Output Locations

All scripts output to the `media/` directory with organized subfolders:

| Script | Default output |
|--------|---------------|
| `illustrate.py` | `media/daily/{date}/` |
| `illustrate-adaptive.py` | `media/daily/{date}/` |
| `scene_director.py` | `media/editorial/{date}/` |
| `create-tag-icons.py` | `media/icons/tags/` |
| `create-entity-icons.py` | `scripts/posters/assets/icons/` (permanent assets) |

---

## Testing & Comparison

Use `test-all-scripts.py` to generate samples from all scripts and create an HTML comparison gallery:

```bash
# Run all tests with latest facts
python scripts/posters/test-all-scripts.py

# Test specific script
python scripts/posters/test-all-scripts.py --only illustrate
python scripts/posters/test-all-scripts.py --only scene_director

# Dry run - see what would be generated
python scripts/posters/test-all-scripts.py --dry-run

# Just rebuild HTML gallery from existing samples
python scripts/posters/test-all-scripts.py --html-only
```

Output: `media/samples/gallery.html` - interactive lightbox gallery comparing all script outputs

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
