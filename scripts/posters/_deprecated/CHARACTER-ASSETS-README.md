# Character Asset System

## Overview

System for cataloging existing character images and generating new poses/reference sheets for AI-generated news illustrations.

## Current State (2025-12-13)

### What's Working

**1. Analysis Pipeline** (`analyze-characters.py`)
- Uses GPT-5.2 to analyze each image in a character folder
- Extracts: pose, angle, expression, action, background, features_visible
- Generates character summary (description, distinguishing features, colors, costume, style)
- Shows succinct summary for human confirmation before saving
- Outputs `manifest.json` per character

```bash
python scripts/posters/analyze-characters.py --character eliza
# Analyzes 18 images, shows summary, asks "Correct? [Y/n/edit]"
```

**2. Character Data**
- 5 characters in `posters/characters/`: eliza, marc, peepo, shaw, spartan
- Eliza has `manifest.json` (analyzed and confirmed)
- Other characters have images but no manifests yet

### What Needs Work

**Reference Sheet Generation** - Currently broken/suboptimal:

1. **Bad reference selection** - `test-reference-sheet.py` picks first 2 images alphabetically (1.png, 10.png = bust shots). Should pick `full_body` images from manifest.

2. **Missing costume details** - Prompts only use `description`, not `costume` field. Result: generated images missing pants/boots.

3. **Multiple image uploads** - Sending 2-3 separate refs. Better approach: combine into single Pillow collage.

## Planned Consolidation

Reduce to 2 scripts:

```
analyze-characters.py  →  manifest.json   (understand character)
generate.py            →  images          (create anything)
```

### generate.py Design

```bash
python scripts/posters/generate.py eliza turnaround
python scripts/posters/generate.py eliza turnaround --sketch
python scripts/posters/generate.py eliza expressions
python scripts/posters/generate.py eliza pose happy
```

**Internal flow:**
```python
def main(character, output_type, sketch=False):
    manifest = load_manifest(character)
    refs = select_refs(manifest, output_type)  # Smart: full_body for turnaround
    collage = make_collage(refs)               # Pillow: combine into 1 image
    prompt = build_prompt(manifest, output_type, sketch)  # Include costume!
    result = generate(collage, prompt)
    save(result, character, output_type)
```

**Key improvements:**
- `select_refs()` uses manifest metadata to pick appropriate images
- `make_collage()` combines refs into single image (Pillow 2x2 grid)
- `build_prompt()` includes full manifest data (description + costume + colors)
- `--sketch` flag for line art/B&W (cheaper iteration before color)

## File Inventory

| File | Status | Purpose |
|------|--------|---------|
| `analyze-characters.py` | ✅ Working | GPT-5.2 analysis → manifest.json |
| `generate-character-poses.py` | ⚠️ Keep for now | 8 poses + chroma key (to be replaced) |
| `test-reference-sheet.py` | ⚠️ Keep for now | Experimental sheets (to be replaced) |
| `generate-sampler.py` | ✅ Working | Style sampler with markdown report |
| `style-presets.json` | ✅ Working | 12 style definitions |
| `pose-presets.json.archived` | 📦 Archived | Was too complex, inlined into script |

## Next Steps

1. Create `generate.py` with:
   - Smart ref selection from manifest (filter by pose type)
   - Pillow collage creation
   - Rich prompts including costume details
   - `--sketch` mode

2. Test with eliza turnaround

3. Once working, clean up old scripts

## Useful Commands

```bash
# Analyze a character (creates manifest.json)
python scripts/posters/analyze-characters.py --character eliza

# Dry run to see what would be analyzed
python scripts/posters/analyze-characters.py --dry-run

# Current pose generation (has issues)
python scripts/posters/generate-character-poses.py eliza --dry-run

# Current sheet test (has issues with ref selection)
python scripts/posters/test-reference-sheet.py eliza turnaround_grid
```

## Key Insights

1. **Professional workflow**: sketch → review → color (not straight to final render)
2. **Reference selection matters**: full_body images for full body output
3. **Single collage > multiple images**: Pillow combine refs before API call
4. **Manifest is gold**: Contains everything needed for smart generation

## API Models Used

- **Analysis**: `openai/gpt-5.2` via OpenRouter (vision)
- **Generation**: `google/gemini-3-pro-image-preview` via OpenRouter (Nano Banana Pro)
