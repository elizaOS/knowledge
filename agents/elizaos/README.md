# ElizaOS Council Agent Characters

Five council characters deployed as separate Discord bots using the ElizaOS framework.

## Characters

| File | Character | Role | Actor ID | Voice |
|------|-----------|------|----------|-------|
| `eliza.ts` | Eliza | Host/Synthesizer | `elizahost` | Professional, framing questions, bridging language |
| `shaw.ts` | AI Shaw | Builder/CTO | `aishaw` | All lowercase, short punchy, references PRs |
| `marc.ts` | AI Marc | Strategist | `aimarc` | Bold declarations, "Not X, but Y" reframing |
| `spartan.ts` | Degen Spartan AI | Metrics Warrior | `spartan` | ALL CAPS on metrics, battle metaphors |
| `peepo.ts` | Peepo | Community Voice | `peepo` | Casual ("yo", "fam", "vibes"), insight in memes |

## Prerequisites

- [ElizaOS CLI](https://elizaos.github.io/eliza/) (`npx elizaos@latest`)
- Node.js 23+
- 5 Discord bot applications (one per character)
- At least one LLM API key (Anthropic, OpenAI, or OpenRouter)

## Quick Start

### 1. Create a new ElizaOS project

```bash
npx elizaos@latest create council-bots
cd council-bots
```

### 2. Copy character files

Copy the `.ts` files from this directory into your project's `src/characters/` directory:

```bash
cp path/to/elizaos/*.ts src/characters/
```

### 3. Create Discord Bot Applications

Create **5 separate Discord applications** at [discord.com/developers](https://discord.com/developers/applications):

| Bot Name | Suggested |
|----------|-----------|
| Eliza | ElizaOS Council - Eliza |
| AI Shaw | ElizaOS Council - Shaw |
| AI Marc | ElizaOS Council - Marc |
| Degen Spartan AI | ElizaOS Council - Spartan |
| Peepo | ElizaOS Council - Peepo |

For each bot:
1. Go to **Bot** tab, click **Reset Token**, copy the token
2. Enable **Message Content Intent** under Privileged Gateway Intents
3. Go to **OAuth2 > URL Generator**, select `bot` scope with permissions: Send Messages, Read Message History, Embed Links, Attach Files
4. Use the generated URL to invite each bot to your server

### 4. Configure environment variables

Create a `.env` file for each character, or use a shared `.env` with character-prefixed vars:

```bash
# LLM Provider (at least one required)
ANTHROPIC_API_KEY=sk-ant-...
# OPENAI_API_KEY=sk-...
# OPENROUTER_API_KEY=sk-or-...

# Discord tokens (one per character)
ELIZA_DISCORD_APPLICATION_ID=...
ELIZA_DISCORD_API_TOKEN=...

SHAW_DISCORD_APPLICATION_ID=...
SHAW_DISCORD_API_TOKEN=...

MARC_DISCORD_APPLICATION_ID=...
MARC_DISCORD_API_TOKEN=...

SPARTAN_DISCORD_APPLICATION_ID=...
SPARTAN_DISCORD_API_TOKEN=...

PEEPO_DISCORD_APPLICATION_ID=...
PEEPO_DISCORD_API_TOKEN=...
```

### 5. Multi-agent entry point

Create `src/index.ts` to run all 5 agents:

```typescript
import { character as eliza } from './characters/eliza.ts';
import { character as shaw } from './characters/shaw.ts';
import { character as marc } from './characters/marc.ts';
import { character as spartan } from './characters/spartan.ts';
import { character as peepo } from './characters/peepo.ts';

// Each character is exported for the ElizaOS runtime to load
export const characters = [eliza, shaw, marc, spartan, peepo];

export default characters;
```

Or run them individually:

```bash
npx elizaos start --character src/characters/eliza.ts
npx elizaos start --character src/characters/shaw.ts
# etc.
```

### 6. Start the agents

```bash
npx elizaos start
```

## Knowledge Plugin Configuration

Each agent uses `@elizaos/plugin-knowledge` with RAG (Retrieval-Augmented Generation) for contextual conversations.

### Directory structure

```
docs/
├── shared/                    # Loaded by ALL agents
│   ├── north-star.md          # ElizaOS mission and strategic context
│   ├── council-procedures.md  # Deliberation protocols and formats
│   ├── council-profiles.md    # All 5 character profiles and relationships
│   └── data-access.md         # Knowledge data paths and schemas
├── eliza/                     # Loaded by Eliza only
│   ├── soul.md                # Personality, voice rules, reasoning style
│   └── memory.md              # Past positions, council dynamics, observations
├── shaw/                      # Loaded by Shaw only
│   ├── soul.md
│   └── memory.md
├── marc/                      # Loaded by Marc only
│   ├── soul.md
│   └── memory.md
├── spartan/                   # Loaded by Spartan only
│   ├── soul.md
│   └── memory.md
└── peepo/                     # Loaded by Peepo only
    ├── soul.md
    └── memory.md
```

### Per-agent scoping

Each agent should load `shared/` plus their own character directory. Configure via environment:

```bash
# Eliza loads: docs/shared/ + docs/eliza/
ELIZA_KNOWLEDGE_DOCS_PATH=docs/shared,docs/eliza

# Shaw loads: docs/shared/ + docs/shaw/
SHAW_KNOWLEDGE_DOCS_PATH=docs/shared,docs/shaw

# etc.
```

Or in the ElizaOS project config, set `LOAD_DOCS_ON_STARTUP=true` and configure docs paths per character.

The RAG system auto-chunks documents (500 tokens, 100 token overlap), embeds them, and retrieves relevant content during conversations.

## Weekly Episode Deliberation

The council supports a hybrid workflow for weekly episode production:

1. **External cron** triggers the process (e.g., GitHub Actions, cron job)
2. **Data ingestion**: latest facts, briefings, and highlights are loaded
3. **Deliberation**: each agent forms a position based on their lens
4. **Episode generation**: structured dialogue in character voice

This mirrors the existing `cronjob/` workflow but with live ElizaOS agents rather than prompt-only generation.

### Deliberation format

```json
{
  "actor": "elizahost|aishaw|aimarc|spartan|peepo",
  "line": "The dialogue line in character voice",
  "action": "curious|excited|stern|dismissive|etc"
}
```

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | One of three | Anthropic Claude API key |
| `OPENAI_API_KEY` | One of three | OpenAI API key |
| `OPENROUTER_API_KEY` | One of three | OpenRouter API key |
| `{CHAR}_DISCORD_APPLICATION_ID` | Yes | Discord app ID per character |
| `{CHAR}_DISCORD_API_TOKEN` | Yes | Discord bot token per character |
| `LOAD_DOCS_ON_STARTUP` | No | Enable RAG knowledge loading (default: true) |
| `{CHAR}_KNOWLEDGE_DOCS_PATH` | No | Comma-separated docs paths per character |

## Voice Differentiation Quick Reference

| Character | Key Rule | Never Do |
|-----------|----------|----------|
| **Eliza** | Complete sentences, framing questions, bridging language | Slang, ALL CAPS, taking sides early |
| **Shaw** | ALL lowercase always, short punchy, numbered lists | Capitalize anything, exclamation marks, monologues |
| **Marc** | Bold declarations, "Not X, but Y", strategic depth | Analogies, casual language, hedging |
| **Spartan** | ALL CAPS metrics, cite numbers, demand accountability | Soften bad metrics, hedge, agree without conditions |
| **Peepo** | Casual ("yo", "fam"), insight in memes, 2-3 sentences | Corporate tone, numbered lists, formal language |
