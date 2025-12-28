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

  # Incremental extraction (only files after date - for CI/CD)
  python scripts/etl/extract-entities.py -i the-council/facts/ --batch --since 2025-12-20 -o scripts/posters/assets/entity-inventory.json

  # Dedupe existing inventory (merge duplicates by name, resolve type conflicts)
  python scripts/etl/extract-entities.py -i scripts/posters/assets/entity-inventory.json --dedupe

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
from difflib import SequenceMatcher
import requests

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_API_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-2.5-flash-lite"

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent

# Entity types for flat schema (4 valid types only)
ENTITY_TYPES = ["token", "platform", "project", "user"]

# Type normalization for LLM outputs that don't follow instructions
TYPE_NORMALIZATION = {
    "person": "user",
    "developer": "user",
    "member": "user",
    "company": "project",
    "organization": "project",
    "event": "project",
}

# Types to skip entirely
SKIP_TYPES = {"date", "location", "security"}

EXTRACT_PROMPT = """Extract named entities from this content.

Content:
{content}

For each entity, provide:
- name: canonical name (properly cased)
- type: MUST be one of: token | platform | project | user
- description: 1-sentence explaining what it is
- aliases: other names/spellings used in the content

Type definitions (use ONLY these 4 types):
- token: cryptocurrencies, blockchains, L1/L2s (Bitcoin, Ethereum, Base, SOL)
- platform: services, APIs, apps, websites (Discord, GitHub, OpenAI, CoinGecko)
- project: software, protocols, plugins, DAOs, organizations (elizaOS, Uniswap, EVM)
- user: people, contributors, community members (Shaw, Jin, vitalik)

IMPORTANT: Do not create new types. Map everything to these 4 categories.
- Companies → project
- Organizations → project
- Developers → user
- Events → project
- Dates → omit entirely

Output JSON only:
{{"entities": [
  {{"name": "Example", "type": "token", "description": "...", "aliases": []}}
]}}
"""

NORMALIZE_PROMPT = """Normalize and dedupe these entities:
1. Merge duplicates (same entity with different names/casing)
2. Use canonical names (e.g., "Ethereum" not "eth")
3. Remove generic terms that aren't specific named entities
4. Combine descriptions from duplicates
5. Keep the most recognizable form of each entity

Input:
{entities}

Return cleaned JSON with same structure:
{{"entities": [...]}}
"""

RESOLVE_TYPES_PROMPT = """Resolve entity type conflicts. For each entity below, pick the BEST type.

Types (pick exactly one):
- token: cryptocurrencies, blockchains (Bitcoin, ETH, SOL)
- platform: services, APIs, websites (Discord, GitHub, CoinGecko)
- project: software, protocols, DAOs, organizations (elizaOS, Uniswap)
- user: people, contributors (Shaw, Jin, vitalik)

Entities with conflicting types:
{conflicts}

Return JSON mapping name to best type:
{{"Jin": "user", "ai16z": "token", ...}}
"""


def get_source_context(facts_data: dict) -> str:
    """Fetch additional context from original source files referenced in the facts."""
    source_paths = set()

    # Collect all source paths from the facts data
    def collect_sources(obj):
        if isinstance(obj, dict):
            if 'source' in obj and isinstance(obj['source'], list):
                source_paths.update(obj['source'])
            for v in obj.values():
                collect_sources(v)
        elif isinstance(obj, list):
            for item in obj:
                collect_sources(item)

    collect_sources(facts_data)

    # Read source files for additional context (limit to first 3 to avoid token explosion)
    context_parts = []
    for source_path in sorted(source_paths)[:3]:
        local_path = WORKSPACE_ROOT / source_path
        if local_path.exists():
            try:
                content = local_path.read_text(encoding='utf-8')[:3000]
                context_parts.append(f"--- Source: {source_path} ---\n{content}")
            except Exception:
                pass

    return "\n\n".join(context_parts)


def load_content(file_path: Path) -> tuple[str, dict]:
    """Load and extract text from file. Returns (text_content, raw_data)."""
    raw_content = file_path.read_text(encoding='utf-8')
    data = {}

    if file_path.suffix == '.json':
        try:
            data = json.loads(raw_content)
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
            text_content = "\n".join(texts)
        except json.JSONDecodeError:
            text_content = raw_content
    else:
        text_content = raw_content

    return text_content[:12000], data  # Limit size


def call_llm(prompt: str) -> tuple[dict, dict]:
    """Call LLM with prompt, return (parsed_result, usage_stats)."""
    empty_usage = {"input_tokens": 0, "output_tokens": 0}

    if not OPENROUTER_API_KEY:
        logging.error("OPENROUTER_API_KEY not set")
        return {}, empty_usage

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

        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]
        if content.startswith("```"):
            content = content.split("```")[1].lstrip("json\n")

        # Extract token usage from response
        usage = response_data.get("usage", {})
        usage_stats = {
            "input_tokens": usage.get("prompt_tokens", 0),
            "output_tokens": usage.get("completion_tokens", 0),
        }

        return json.loads(content.strip()), usage_stats

    except Exception as e:
        logging.error(f"LLM call failed: {e}")
        return {}, empty_usage


def extract_entities(content: str, source_context: str = "") -> tuple[dict, dict]:
    """Call LLM to extract entities from content with optional source context."""
    full_content = content
    if source_context:
        full_content = f"{content}\n\n--- Additional Context from Sources ---\n{source_context}"
    return call_llm(EXTRACT_PROMPT.format(content=full_content))


def normalize_entities(entities: list) -> tuple[list, dict]:
    """Call LLM to normalize/dedupe merged entities."""
    logging.info("Normalizing entities via LLM...")
    entities_json = json.dumps({"entities": entities}, indent=2)
    result, usage = call_llm(NORMALIZE_PROMPT.format(entities=entities_json))
    if result and "entities" in result:
        before = len(entities)
        after = len(result["entities"])
        logging.info(f"  Normalized: {before} -> {after} entities")
        return result["entities"], usage
    return entities, usage


def normalize_entity_type(entity: dict) -> dict:
    """Normalize entity type using fallback mapping."""
    raw_type = entity.get("type", "project")
    if raw_type in SKIP_TYPES:
        return None  # Signal to skip this entity
    entity["type"] = TYPE_NORMALIZATION.get(raw_type, raw_type)
    return entity


def merge_entities(all_extractions: list[dict], fuzzy: bool = True) -> list:
    """Merge and dedupe entities by name (with fuzzy matching), tracking type votes."""
    seen = {}  # canonical_key -> entity dict with type_votes
    key_map = {}  # all seen lowercase names -> canonical_key

    for extraction in all_extractions:
        entities = extraction.get("entities", [])
        if isinstance(entities, list):
            for entity in entities:
                if not isinstance(entity, dict) or "name" not in entity:
                    continue

                # Normalize type and skip unwanted types
                entity = normalize_entity_type(entity)
                if entity is None:
                    continue

                name_lower = entity["name"].lower().strip()
                entity_type = entity.get("type", "project")

                # Check for exact or fuzzy match
                match_key = None
                if name_lower in key_map:
                    match_key = key_map[name_lower]
                elif fuzzy:
                    match_key = find_fuzzy_match(name_lower, seen)
                    if match_key:
                        key_map[name_lower] = match_key

                if match_key is None:
                    # New entity
                    key_map[name_lower] = name_lower
                    seen[name_lower] = {
                        "name": entity["name"],
                        "type": entity_type,
                        "description": entity.get("description", ""),
                        "aliases": set(entity.get("aliases", [])),
                        "type_votes": {entity_type: 1},
                    }
                else:
                    existing = seen[match_key]
                    # Track type votes
                    existing["type_votes"][entity_type] = existing["type_votes"].get(entity_type, 0) + 1
                    # Merge aliases (including alternate name casings)
                    if entity["name"] != existing["name"]:
                        existing["aliases"].add(entity["name"])
                    existing["aliases"].update(entity.get("aliases", []))
                    # Keep longer description
                    if len(entity.get("description", "")) > len(existing.get("description", "")):
                        existing["description"] = entity["description"]

    # Convert sets to lists
    result = []
    for entity in seen.values():
        entity["aliases"] = list(entity["aliases"])
        result.append(entity)
    return result


def resolve_type_conflicts(entities: list) -> tuple[list, dict]:
    """Use LLM to resolve entities with multiple type votes."""
    conflicts = []
    for e in entities:
        votes = e.get("type_votes", {})
        if len(votes) > 1:
            conflicts.append({
                "name": e["name"],
                "types_seen": votes,
                "description": e.get("description", "")[:100]
            })

    if not conflicts:
        # No conflicts, clean up type_votes
        for e in entities:
            e.pop("type_votes", None)
        return entities, {"input_tokens": 0, "output_tokens": 0}

    logging.info(f"Resolving {len(conflicts)} type conflicts via LLM...")
    conflicts_json = json.dumps(conflicts, indent=2)
    result, usage = call_llm(RESOLVE_TYPES_PROMPT.format(conflicts=conflicts_json))

    # Apply resolutions
    resolutions = result if isinstance(result, dict) else {}
    for e in entities:
        if e["name"] in resolutions:
            resolved_type = resolutions[e["name"]]
            if resolved_type in ENTITY_TYPES:
                e["type"] = resolved_type
        elif len(e.get("type_votes", {})) > 1:
            # Fallback: pick most common type
            e["type"] = max(e["type_votes"], key=e["type_votes"].get)
        e.pop("type_votes", None)

    logging.info(f"  Resolved {len(resolutions)} conflicts")
    return entities, usage


def find_fuzzy_match(name: str, seen: dict, threshold: float = 0.85) -> str | None:
    """Find a fuzzy match for name in seen keys. Returns matching key or None."""
    name_lower = name.lower().strip()

    # Exact match first
    if name_lower in seen:
        return name_lower

    # Fuzzy match for short names (typos more likely)
    if len(name_lower) >= 3:
        for existing_key in seen:
            # Skip if lengths are too different (optimization)
            if abs(len(name_lower) - len(existing_key)) > 3:
                continue
            ratio = SequenceMatcher(None, name_lower, existing_key).ratio()
            if ratio >= threshold:
                return existing_key

    return None


def dedupe_entities(entities: list, fuzzy: bool = True) -> list:
    """Dedupe entities by name (with optional fuzzy matching), merge aliases and track type votes."""
    seen = {}  # canonical_key -> entity
    key_map = {}  # all seen lowercase names -> canonical_key

    for e in entities:
        name_lower = e["name"].lower().strip()

        # Check for exact or fuzzy match
        match_key = None
        if name_lower in key_map:
            match_key = key_map[name_lower]
        elif fuzzy:
            match_key = find_fuzzy_match(name_lower, seen)
            if match_key:
                key_map[name_lower] = match_key  # Remember this mapping

        if match_key is None:
            # New entity
            key_map[name_lower] = name_lower
            seen[name_lower] = {
                **e,
                "aliases": set(e.get("aliases", [])),
                "type_votes": {e["type"]: 1},
            }
        else:
            # Merge with existing
            existing = seen[match_key]
            existing["type_votes"][e["type"]] = existing["type_votes"].get(e["type"], 0) + 1
            # Add as alias if different spelling
            if e["name"] != existing["name"]:
                existing["aliases"].add(e["name"])
            existing["aliases"].update(e.get("aliases", []))
            # Keep longer description
            if len(e.get("description", "")) > len(existing.get("description", "")):
                existing["description"] = e["description"]

    # Convert sets to lists
    for e in seen.values():
        e["aliases"] = list(e["aliases"])
    return list(seen.values())


def main():
    parser = argparse.ArgumentParser(description="Extract entities for visual asset planning")
    parser.add_argument("-i", "--input", type=Path, required=True, help="Input file or directory")
    parser.add_argument("-o", "--output", type=Path, help="Output JSON file")
    parser.add_argument("--batch", action="store_true", help="Process all JSON files in directory")
    parser.add_argument("--normalize", action="store_true", help="Run LLM normalization pass on merged results")
    parser.add_argument("--normalize-only", action="store_true", help="Only normalize existing inventory (no extraction)")
    parser.add_argument("--dedupe", action="store_true", help="Dedupe existing inventory file by name, resolve type conflicts")
    parser.add_argument("--with-context", action="store_true", help="Follow source paths to fetch additional context")
    parser.add_argument("--since", type=str, help="Only process files dated after YYYY-MM-DD (for incremental runs)")
    args = parser.parse_args()

    # Dedupe mode: dedupe existing inventory by name
    if args.dedupe:
        if not args.input.is_file():
            parser.error("--dedupe requires -i to be an existing JSON file")

        logging.info(f"Loading {args.input}...")
        with open(args.input) as f:
            data = json.load(f)

        entities = data.get("entities", [])
        logging.info(f"Found {len(entities)} entities")

        # Dedupe by name
        deduped = dedupe_entities(entities)
        logging.info(f"Deduped to {len(deduped)} entities ({len(entities) - len(deduped)} merged)")

        # Resolve type conflicts via LLM
        deduped, usage = resolve_type_conflicts(deduped)

        output = {
            "entities": deduped,
            "_metadata": {
                **data.get("_metadata", {}),
                "deduped_at": datetime.utcnow().isoformat() + "Z",
                "dedupe_input_tokens": usage["input_tokens"],
                "dedupe_output_tokens": usage["output_tokens"],
            }
        }

        out_path = args.output or args.input
        out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
        logging.info(f"Saved to {out_path}")

        # Summary by type
        by_type = {}
        for entity in deduped:
            t = entity.get("type", "unknown")
            by_type[t] = by_type.get(t, 0) + 1
        logging.info(f"Types: {by_type}")
        return

    # Normalize-only mode: just process existing inventory
    if args.normalize_only:
        if not args.input.is_file():
            parser.error("--normalize-only requires -i to be an existing JSON file")

        logging.info(f"Loading {args.input}...")
        with open(args.input) as f:
            data = json.load(f)

        entities = data.get("entities", [])

        if not isinstance(entities, list):
            logging.error("Invalid format: entities should be a list (v2 schema)")
            sys.exit(1)

        normalized, usage = normalize_entities(entities)

        output = {
            "entities": normalized,
            "_metadata": {
                "normalized_at": datetime.utcnow().isoformat() + "Z",
                "source": str(args.input),
                "schema_version": 2,
                "input_tokens": usage["input_tokens"],
                "output_tokens": usage["output_tokens"],
            }
        }

        out_path = args.output or args.input
        out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
        logging.info(f"Saved to {out_path} (tokens: {usage['input_tokens']} in, {usage['output_tokens']} out)")
        return

    files = []
    if args.input.is_dir() and args.batch:
        files = [f for f in sorted(args.input.glob("*.json")) if f.name != "daily.json"]
        # Filter by date if --since is provided
        if args.since:
            files = [f for f in files if f.stem >= args.since]
            logging.info(f"Filtered to files since {args.since}")
    elif args.input.is_file():
        files = [args.input]
    else:
        parser.error("Use --batch for directories")

    logging.info(f"Processing {len(files)} file(s)...")

    out_dir = args.output.parent if args.output else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    all_extractions = []
    total_input_tokens = 0
    total_output_tokens = 0

    for f in files:
        logging.info(f"  {f.name}")
        content, raw_data = load_content(f)

        # Optionally follow source paths for additional context
        source_context = ""
        if args.with_context and raw_data:
            source_context = get_source_context(raw_data)
            if source_context:
                logging.info(f"    + added context from {len(source_context.split('---'))-1} source(s)")

        extraction, usage = extract_entities(content, source_context)
        total_input_tokens += usage["input_tokens"]
        total_output_tokens += usage["output_tokens"]

        if extraction and extraction.get("entities"):
            all_extractions.append(extraction)
            # Save individual file immediately
            if out_dir:
                (out_dir / f.name).write_text(json.dumps({
                    "source": f.name,
                    "entities": extraction.get("entities", []),
                    "_metadata": {"extracted_at": datetime.utcnow().isoformat() + "Z"}
                }, indent=2, ensure_ascii=True))

    merged = merge_entities(all_extractions)

    # Resolve type conflicts via LLM
    merged, resolve_usage = resolve_type_conflicts(merged)
    total_input_tokens += resolve_usage["input_tokens"]
    total_output_tokens += resolve_usage["output_tokens"]

    # Optional LLM normalization pass
    if args.normalize:
        merged, norm_usage = normalize_entities(merged)
        total_input_tokens += norm_usage["input_tokens"]
        total_output_tokens += norm_usage["output_tokens"]

    output = {
        "entities": merged,
        "_metadata": {
            "extracted_at": datetime.utcnow().isoformat() + "Z",
            "files_processed": len(files),
            "normalized": args.normalize,
            "schema_version": 2,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
        }
    }

    if args.output:
        args.output.write_text(json.dumps(output, indent=2, ensure_ascii=True))
        logging.info(f"Saved {len(all_extractions)} extractions to {args.output}")
        logging.info(f"  Tokens: {total_input_tokens:,} in, {total_output_tokens:,} out")
    else:
        print(json.dumps(output, indent=2, ensure_ascii=True))

    # Summary by type
    by_type = {}
    for entity in merged:
        t = entity.get("type", "unknown")
        by_type.setdefault(t, []).append(entity["name"])
    for entity_type, names in sorted(by_type.items()):
        sample = ", ".join(names[:5])
        suffix = f"... (+{len(names)-5})" if len(names) > 5 else ""
        logging.info(f"  {entity_type}: {sample}{suffix}")


if __name__ == "__main__":
    main()
