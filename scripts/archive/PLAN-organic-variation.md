# PR #36: Organic Variation & Story-Connected Visuals

## Goals

1. **Improve organic variation** in batch-generated illustrations
2. **Make images feel more connected to source stories** - not just generic mascot scenes
3. **Think like a professional tech newsroom** - match visual format to story type
4. **Maintain flexibility** for experimentation without locking into local maxima

---

## Current State

### Organic Variation System (Already Implemented)
- **Creative Brief System**: Date-seeded lens + composition + seasonal mood
- **Style Rotation**: Uses `suggested_styles` from `style-presets.json`
- **Character Shuffle**: Date-seeded randomization of character order/count
- **168 unique combinations** before repeating (7 lenses × 6 compositions × 4 seasons)

### Media Structure (Current)
```json
{
  "categories": {
    "discord_updates": [...],
    "github_updates": {...},
  },
  "media": {
    "posters": {
      "discord_updates": "https://cdn.../discord-updates.png",
      "github_updates": "https://cdn.../github-updates.png"
    }
  }
}
```

### Key Files
- `scripts/posters/illustrate.py` - Main generation logic
- `scripts/posters/config/style-presets.json` - Style definitions & category mappings
- `scripts/integrations/cdn/update_facts_media.py` - Links media to facts

---

## Proposed Improvements

### 1. LLM-Driven Visual Format Selection (with Guardrails)

**Concept**: Let the LLM decide the visual format based on actual story content, not rigid category rules.

**Why LLM judgment over config flags:**
- Context-aware: Reads actual content and judges what fits
- Avoids local maxima: Won't get locked into stale patterns
- Emergent creativity: May discover combinations we wouldn't hardcode
- Adapts to edge cases: Mixed themes, unusual content
- Keeps things fresh: Natural variation based on content nuances

**The guardrails:**
1. **Style vocabulary**: Config defines available styles, LLM picks from them
2. **Brand guidelines**: Prompt includes what we value aesthetically
3. **Category hints**: Soft suggestions, not rules (e.g., "github updates often work well as diagrams")
4. **Explain choice**: LLM outputs reasoning for reviewability
5. **Date-seeding**: Reproducibility when needed

**Implementation**: Add a "visual format decision" step to scene generation that:
```
Given this story content and category, decide:
- Visual approach: (abstract dataviz | conceptual metaphor | character scene)
- Style: (from available styles)
- Reasoning: (why this fits the content)

Category hint: {category} stories typically work well as {suggested_approach},
but judge based on today's content. Override if the story calls for something different.
```

### 2. Theme-to-Visual Mapping (Rejected)

Decided against hardcoded theme mappings - lets LLM judge based on actual content instead of category buckets. This avoids rigid patterns that become stale.

---

## Decided: Mesh Media Into Categories

**Decision**: Media should be meshed into category structures (next to stories)

### Current Structure
```json
{
  "categories": {
    "discord_updates": [...],
    "github_updates": {...}
  },
  "media": {
    "posters": {
      "overall": "url",
      "discord_updates": "url",
      "github_updates": "url"
    }
  }
}
```

### New Structure (Meshed)
```json
{
  "overall_summary": "...",
  "overall_media": {
    "poster_url": "https://cdn.../overall.png"
  },
  "categories": {
    "discord_updates": {
      "items": [...],
      "media": {
        "poster_url": "https://cdn.../discord-updates.png"
      }
    },
    "github_updates": {
      "content": {...},
      "media": {
        "poster_url": "https://cdn.../github-updates.png",
        "opengraph_preview": "https://opengraph.githubassets.com/..."
      }
    }
  }
}
```

**Note**: Media node is simple - just URLs. Style/generation metadata lives in the manifest (`media/{date}/manifest.json`). This allows media to include non-generated files (e.g., opengraph previews, external images).

### Impact Analysis (Low Risk)

| System | File | Action Needed |
|--------|------|---------------|
| CDN Updater | `update_facts_media.py` | **UPDATE** - Write to new locations |
| Discord Webhook | `webhook.py:213` | **UPDATE** - Read from `overall_media.poster_url` |
| RSS Generator | `generate-rss.py` | None - doesn't use media |
| HackMD | `update.py` | None - doesn't use media |
| Illustrations | `illustrate.py` | None - only writes manifest |

**Only 2 files need changes** - migration is feasible with low risk.

---

## Design Principles

### On Avoiding Local Maxima
- Keep configuration in `style-presets.json` (not hardcoded in Python)
- Make mappings soft preferences, not hard rules
- Allow CLI overrides for experimentation
- Start minimal, add complexity only when needed

### On Sentiment Modifiers (Rejected)
Initially proposed sentiment-based visual modifiers (positive → warm colors, etc.)
**Rejected** because: Risk of bias, self-fulfilling prophecy, departure from objective reporting

### Decisions Made

| Question | Decision |
|----------|----------|
| Media placement | **Mesh into categories** - better semantic cohesion |
| Visual format selection | **LLM judgment with guardrails** - not rigid config flags |
| Media format | **Simple objects** - `media.poster_url` not arrays |

---

## Implementation Plan

### Phase 1: LLM-Driven Visual Format Selection

**Goal**: Let LLM decide visual approach based on content, with soft category hints.

1. Update `style-presets.json`:
   - Add `visual_hint` to each category (soft suggestion, not rule)
   - Example: `"visual_hint": "often works well as data visualization or diagrams"`
   - Add `available_approaches`: `["abstract_dataviz", "conceptual_metaphor", "character_scene"]`

2. Update `illustrate.py`:
   - Add new function `decide_visual_format(content, category, category_hint)`
   - LLM returns: `{ "approach": "...", "style": "...", "reasoning": "..." }`
   - Use approach to determine whether to load character references
   - Log reasoning to manifest for review

3. Test with `--dry-run` to see LLM decisions and reasoning

### Phase 2: Mesh Media Structure

**Goal**: Move media URLs from separate node to alongside their stories.

1. Update `scripts/integrations/cdn/update_facts_media.py`:
   - Instead of `facts["media"]["posters"][category]`
   - Write to `facts["overall_media"]` for overall poster
   - Write to `facts["categories"][category]["media"]` for category posters

2. Update `scripts/integrations/discord/webhook.py`:
   - Change line 213 from: `data.get('media', {}).get('posters', {}).get('overall')`
   - To: `data.get('overall_media', {}).get('poster_url')`

3. Migrate existing facts files (optional - or let new ones use new structure)

### Phase 3: Iterate

Based on output quality, consider:
- Adding theme-to-format mappings
- Improving scene generation prompts with story-specific extraction
- A/B testing different visual approaches

---

## Files to Modify

| File | Changes |
|------|---------|
| `scripts/posters/config/style-presets.json` | Add `visual_hint` to categories, define `available_approaches` |
| `scripts/posters/illustrate.py` | Add `decide_visual_format()` LLM call, log reasoning to manifest |
| `scripts/integrations/cdn/update_facts_media.py` | Write media to meshed structure |
| `scripts/integrations/discord/webhook.py` | Read from new `overall_media` location |

---

## Testing Plan

1. `--dry-run` with `prefer_abstract` changes to verify prompt output
2. Generate sample posters for 2-3 dates with old vs new approach
3. Verify Discord webhook still receives poster URL after structure change
4. Manual review of visual quality improvement
