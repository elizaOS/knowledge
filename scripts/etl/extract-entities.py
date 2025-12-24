#!/usr/bin/env python3
"""
Extract named entities from files to identify what visual assets to source.

Usage:
  # Extract from single file
  python scripts/etl/extract-entities.py -i the-council/facts/2025-12-20.json

  # Batch extract from directory
  python scripts/etl/extract-entities.py -i the-council/facts/ --batch -o scripts/posters/assets/entity-inventory.json

  # Batch extract + normalize in one pass
  python scripts/etl/extract-entities.py -i the-council/facts/ --batch --normalize -o scripts/posters/assets/entity-inventory.json

  # Normalize existing inventory (no re-extraction, saves API calls)
  python scripts/etl/extract-entities.py -i scripts/posters/assets/entity-inventory.json --normalize-only
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
import requests

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_API_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-2.5-flash-lite"

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

CATEGORIES = ["tokens", "platforms", "tech", "projects", "plugins"]

EXTRACT_PROMPT = """Extract named entities from this content. Focus on things that could have icons/logos.

Content:
{content}

Return JSON with these categories:
- tokens: crypto tokens/coins AND their native chains (ETH, SOL, BTC, Solana, Ethereum, etc.)
- platforms: services/APIs (Discord, Twitter, GitHub, OpenAI, etc.)
- tech: technologies/standards (EVM, TEE, RAG, WebSocket, etc.)
- projects: named projects/protocols (elizaOS, Uniswap, etc.)
- plugins: plugin names (plugin-sql, plugin-twitter, etc.)

Only include explicitly mentioned entities. Normalize casing. Skip generic terms.

Output JSON only:
{{"tokens": [], "platforms": [], "tech": [], "projects": [], "plugins": []}}
"""

NORMALIZE_PROMPT = """Normalize and dedupe these entity lists. For each category:
1. Merge duplicates (e.g., "Discord", "discord", "Discord plugin" -> "Discord")
2. Use canonical names (e.g., "Ethereum" not "eth", "Solana" not "sol")
3. Remove generic terms that aren't specific entities
4. Keep the most recognizable form of each entity

Input:
{entities}

Return cleaned JSON with same structure:
{{"tokens": [], "platforms": [], "tech": [], "projects": [], "plugins": []}}
"""


def load_content(file_path: Path) -> str:
    """Load and extract text from file."""
    content = file_path.read_text(encoding='utf-8')

    if file_path.suffix == '.json':
        try:
            data = json.loads(content)
            texts = []
            if 'overall_summary' in data:
                texts.append(data['overall_summary'])
            for cat in data.get('categories', {}).values():
                if isinstance(cat, list):
                    for item in cat:
                        if isinstance(item, dict):
                            texts.extend(str(v) for v in item.values() if isinstance(v, str))
                elif isinstance(cat, dict):
                    texts.extend(str(v) for v in cat.values() if isinstance(v, str))
            content = "\n".join(texts)
        except json.JSONDecodeError:
            pass

    return content[:12000]  # Limit size


def call_llm(prompt: str) -> dict:
    """Call LLM with prompt, return parsed JSON."""
    if not OPENROUTER_API_KEY:
        logging.error("OPENROUTER_API_KEY not set")
        return {}

    try:
        response = requests.post(
            OPENROUTER_API_ENDPOINT,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"},
            },
            timeout=120
        )
        response.raise_for_status()

        result = response.json()["choices"][0]["message"]["content"]
        if result.startswith("```"):
            result = result.split("```")[1].lstrip("json\n")
        return json.loads(result.strip())

    except Exception as e:
        logging.error(f"LLM call failed: {e}")
        return {}


def extract_entities(content: str) -> dict:
    """Call LLM to extract entities from content."""
    return call_llm(EXTRACT_PROMPT.format(content=content))


def normalize_entities(entities: dict) -> dict:
    """Call LLM to normalize/dedupe merged entities."""
    logging.info("Normalizing entities via LLM...")
    entities_json = json.dumps(entities, indent=2)
    result = call_llm(NORMALIZE_PROMPT.format(entities=entities_json))
    if result:
        before = sum(len(v) for v in entities.values())
        after = sum(len(v) for v in result.values())
        logging.info(f"  Normalized: {before} -> {after} entities")
    return result if result else entities


def merge_entities(all_entities: list[dict]) -> dict:
    """Merge and dedupe entities from multiple extractions."""
    merged = {k: set() for k in CATEGORIES}

    for entities in all_entities:
        for cat in merged:
            items = entities.get(cat, [])
            if isinstance(items, list):
                merged[cat].update(items)
        # Migrate old 'chains' into 'tokens'
        chains = entities.get("chains", [])
        if isinstance(chains, list):
            merged["tokens"].update(chains)

    return {k: sorted(v) for k, v in merged.items()}


def main():
    parser = argparse.ArgumentParser(description="Extract entities for visual asset planning")
    parser.add_argument("-i", "--input", type=Path, required=True, help="Input file or directory")
    parser.add_argument("-o", "--output", type=Path, help="Output JSON file")
    parser.add_argument("--batch", action="store_true", help="Process all JSON files in directory")
    parser.add_argument("--normalize", action="store_true", help="Run LLM normalization pass on merged results")
    parser.add_argument("--normalize-only", action="store_true", help="Only normalize existing inventory (no extraction)")
    args = parser.parse_args()

    # Normalize-only mode: just process existing inventory
    if args.normalize_only:
        if not args.input.is_file():
            parser.error("--normalize-only requires -i to be an existing JSON file")

        logging.info(f"Loading {args.input}...")
        with open(args.input) as f:
            data = json.load(f)

        entities = data.get("entities", {})
        # Migrate chains to tokens if present
        if "chains" in entities:
            entities.setdefault("tokens", []).extend(entities.pop("chains"))
            entities["tokens"] = sorted(set(entities["tokens"]))

        normalized = normalize_entities(entities)

        output = {
            "entities": normalized,
            "_metadata": {
                "normalized_at": datetime.utcnow().isoformat() + "Z",
                "source": str(args.input),
            }
        }

        out_path = args.output or args.input
        out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
        logging.info(f"Saved to {out_path}")
        return

    files = []
    if args.input.is_dir() and args.batch:
        files = [f for f in sorted(args.input.glob("*.json")) if f.name != "daily.json"]
    elif args.input.is_file():
        files = [args.input]
    else:
        parser.error("Use --batch for directories")

    logging.info(f"Processing {len(files)} file(s)...")

    out_dir = args.output.parent if args.output else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    all_entities = []
    for f in files:
        logging.info(f"  {f.name}")
        content = load_content(f)
        entities = extract_entities(content)

        if entities:
            all_entities.append(entities)
            # Save individual file immediately
            if out_dir:
                (out_dir / f.name).write_text(json.dumps({
                    "source": f.name,
                    "entities": entities,
                    "_metadata": {"extracted_at": datetime.utcnow().isoformat() + "Z"}
                }, indent=2, ensure_ascii=True))

    merged = merge_entities(all_entities)

    # Optional LLM normalization pass
    if args.normalize:
        merged = normalize_entities(merged)

    output = {
        "entities": merged,
        "_metadata": {
            "extracted_at": datetime.utcnow().isoformat() + "Z",
            "files_processed": len(files),
            "normalized": args.normalize,
        }
    }

    if args.output:
        args.output.write_text(json.dumps(output, indent=2, ensure_ascii=True))
        logging.info(f"Saved {len(all_entities)} files + {args.output.name} to {out_dir}/")
    else:
        print(json.dumps(output, indent=2, ensure_ascii=True))

    # Summary
    for cat, items in merged.items():
        if items:
            logging.info(f"  {cat}: {', '.join(items[:5])}{'...' if len(items) > 5 else ''}")


if __name__ == "__main__":
    main()
