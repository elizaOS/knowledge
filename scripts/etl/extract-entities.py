#!/usr/bin/env python3
"""
Extract ICONIFIABLE entities from files for a digital asset library.

Usage:
  # Extract from single file
  python scripts/etl/extract-entities.py -i the-council/facts/2025-12-20.json

  # Batch extract from directory
  python scripts/etl/extract-entities.py -i the-council/facts/ --batch -o scripts/posters/assets/manifest.json

  # Reclassify existing manifest (LLM iconifiability check)
  python scripts/etl/extract-entities.py -i scripts/posters/assets/manifest.json --reclassify

  # Dedupe existing inventory (merge duplicates by name)
  python scripts/etl/extract-entities.py -i scripts/posters/assets/manifest.json --dedupe

  # Filter obvious non-entities (no LLM, fast)
  python scripts/etl/extract-entities.py -i scripts/posters/assets/manifest.json --filter-only
"""

import os
import sys
import re
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone
from difflib import SequenceMatcher
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_API_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-2.5-flash-lite"

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent

# Entity types for flat schema (3 types - platform merged into project)
ENTITY_TYPES = ["token", "project", "user"]

# Type normalization for LLM outputs that don't follow instructions
TYPE_NORMALIZATION = {
    "person": "user",
    "developer": "user",
    "member": "user",
    "company": "project",
    "organization": "project",
    "event": "project",
    "platform": "project",  # Merged into project
}

# Types to skip entirely
SKIP_TYPES = {"date", "location", "security"}

# Generic entity names to skip (not specific named entities)
SKIP_ENTITIES = {
    "crypto", "cryptocurrency", "token", "tokens", "nft", "nfts",
    "blockchain", "defi", "wallet", "exchange", "trading",
    "agent", "agents", "agent tokens", "ai agent", "ai agents",
    "eli5", "eli5 token", "meme", "memes", "memecoin", "memecoins",
}

# Split into system (cacheable) and user (dynamic) parts
EXTRACT_SYSTEM = """Extract ICONIFIABLE entities for a digital asset library.

ICONIFIABILITY TEST - Only extract if ALL are true:
1. Has visual identity - Could a designer create a recognizable logo/icon?
2. Is a proper noun - A brand, project, company, or person (not a descriptor)
3. Is reusable - Would this icon appear in multiple future articles?
4. Is searchable - Can you find reference images by Googling "[name] logo"?

For each entity, provide:
- name: canonical name (properly cased)
- type: MUST be one of: token | project | user
- description: 1-3 sentence DEFINITIONAL description (what it IS, not what it did)
- aliases: other names/spellings used in the content

CRITICAL for description:
- Describe WHAT the entity IS, not what it did or was mentioned for
- Include visual identity hints if known (logo colors, shape, style)
- BAD: "An individual who answered a question about migration"
- GOOD: "Fast JavaScript runtime, bundler, and package manager. Logo is a white bun/dumpling on black."
- BAD: "A project mentioned in discussion about token launches"
- GOOD: "Unified API gateway for accessing multiple LLM providers. Teal circular ring logo."
- If you cannot describe what it IS, DO NOT EXTRACT IT

Type definitions (use ONLY these 3 types):
- token: cryptocurrencies, blockchains, L1/L2s (Bitcoin, Ethereum, Base, SOL)
- project: software, services, platforms, protocols, DAOs (elizaOS, Discord, GitHub, Uniswap)
- user: people, contributors, community members (Shaw, Jin, vitalik)

IMPORTANT: Do not create new types. Map everything to these 3 categories.
- Companies → project
- Organizations → project
- Platforms → project
- Developers → user
- Events → project (only if named event with logo, e.g., "ETHDenver")

NOT ICONIFIABLE - OMIT ENTIRELY:
- Versions: v1.0.0, v2dev, v0.10.0, 1.0.0-beta (these are ATTRIBUTES, not entities)
- Dates/times: April 14th, Q4 2025, 11:40 UTC, 2025-01-15
- Numbers/metrics: 300+, $50k, 100k, 10x, $124.53
- IDs/hashes: 1253563209462448241, 0x5AM, 02c148ea-fb77...
- Durations: 1-2 weeks, 3 months, 7 days
- Episodes without context: "Episode 2" (unless full show name)
- Sizes: 0.4GB, 100MB
- Generic phrases: "the platform", "new feature", "migration challenge"
- Cryptic abbreviations: Short codes that aren't well-known brands

ASK YOURSELF: "Would a newspaper's art department create an icon for this?"
If no → don't extract it.

Output JSON only:
{"entities": [
  {"name": "Example", "type": "token", "description": "...", "aliases": []}
]}"""

EXTRACT_USER = """Content:
{content}"""

NORMALIZE_PROMPT = """Normalize and dedupe these entities:
1. Merge duplicates (same entity with different names/casing)
2. Use canonical names (e.g., "Ethereum" not "eth")
3. Remove generic terms that aren't specific named entities
4. Keep the most recognizable form of each entity
5. Fix descriptions to be DEFINITIONAL (1-3 sentences: what it IS, not what it did)

CRITICAL for descriptions:
- Rewrite contextual descriptions to be definitional
- Include visual identity hints if known (logo colors, shape, style)
- BAD: "An individual who answered a question about migration"
- GOOD: "Fast JavaScript runtime, bundler, and package manager. Logo is a white bun/dumpling on black."
- BAD: "A project mentioned in discussion about token launches"
- GOOD: "Unified API gateway for accessing multiple LLM providers. Teal circular ring logo."
- If unknown or ambiguous, write "Unknown - needs research"

Input:
{entities}

Return cleaned JSON with same structure:
{{"entities": [...]}}
"""

CLASSIFY_PROMPT = """Classify entities for a DIGITAL ASSET LIBRARY.

For type, pick ONE:
- token: cryptocurrencies, blockchains (Bitcoin, ETH, SOL)
- project: software, services, platforms, DAOs (Discord, elizaOS, GitHub)
- user: people (Shaw, vitalik)

For status, apply the ICONIFIABILITY TEST:
"Would a newspaper's art department create a reusable icon for this?"

- keep: YES - Has recognizable visual identity (Discord logo, Bitcoin symbol, person's avatar)
- skip: NO - NOT iconifiable:
  * Versions (v1.0.0, v2dev) - attributes, not entities
  * Dates (April 14th, Q4 2025) - temporal, not visual
  * Numbers/metrics (300+, $50k) - quantities, not brands
  * Generic phrases ("the platform", "new feature")
  * "Unknown - needs research" descriptions - if we can't define it, can't icon it
  * Cryptic abbreviations that aren't well-known
- review: Maybe - Has brand but icon would be complex/unclear

Input:
{entities}

Return JSON object mapping name to {{type, status}}:
{{"Discord": {{"type": "project", "status": "keep"}}, "v1.0.0": {{"type": "project", "status": "skip"}}, ...}}
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


# Content fields to extract (allowlist approach - more robust than blocklist)
CONTENT_FIELDS = {"claim", "title", "description", "significance", "summary",
                  "content", "text", "body", "message", "details", "notes"}


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
                            # Only extract known content fields (allowlist)
                            for k, v in item.items():
                                if k in CONTENT_FIELDS and isinstance(v, str):
                                    texts.append(v)
                elif isinstance(cat, dict):
                    for k, v in cat.items():
                        if k in CONTENT_FIELDS and isinstance(v, str):
                            texts.append(v)
            text_content = "\n".join(texts)
        except json.JSONDecodeError:
            text_content = raw_content
    else:
        text_content = raw_content

    return text_content[:12000], data  # Limit size


def call_llm(prompt: str, system_prompt: str = None) -> tuple[dict, dict]:
    """Call LLM with prompt, return (parsed_result, usage_stats).

    Uses system prompt separation for better prompt caching on OpenRouter.
    """
    empty_usage = {"input_tokens": 0, "output_tokens": 0}

    if not OPENROUTER_API_KEY:
        logging.error("OPENROUTER_API_KEY not set")
        return {}, empty_usage

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        response = requests.post(
            OPENROUTER_API_ENDPOINT,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": messages,
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
    return call_llm(EXTRACT_USER.format(content=full_content), system_prompt=EXTRACT_SYSTEM)


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


def is_obviously_not_iconifiable(name: str) -> bool:
    """Minimal code filter for the most obvious non-entities.

    Only catches things that are unambiguously not iconifiable.
    Let LLM classification handle nuanced cases.
    """
    name = name.strip()

    # Too short
    if len(name) < 2:
        return True

    # Purely numeric (obvious non-entity)
    stripped = name.replace('$', '').replace(',', '').replace('.', '').replace(' ', '')
    if stripped.isdigit():
        return True

    # Long hex/UUID strings (technical IDs, not brands)
    cleaned = name.replace('-', '')
    if len(cleaned) >= 20 and all(c in '0123456789abcdefABCDEF' for c in cleaned):
        return True

    return False


# Backward compatibility alias
is_invalid_entity_name = is_obviously_not_iconifiable


def normalize_entity_type(entity: dict) -> dict:
    """Normalize entity type and filter generic names."""
    raw_type = entity.get("type", "project")
    if raw_type in SKIP_TYPES:
        return None  # Signal to skip this entity

    # Skip invalid entity names (numbers, IDs, timestamps, etc.)
    name = entity.get("name", "").strip()
    if is_invalid_entity_name(name):
        return None

    # Skip generic entity names that aren't specific named entities
    name_lower = name.lower()
    if name_lower in SKIP_ENTITIES:
        return None

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


CLASSIFY_BATCH_SIZE = 200  # Process in batches to avoid token limits


def classify_entities(entities: list) -> tuple[list, dict]:
    """Classify entities via LLM in batches."""
    total_usage = {"input_tokens": 0, "output_tokens": 0}
    keep_count = skip_count = review_count = 0

    # Process in batches
    for batch_start in range(0, len(entities), CLASSIFY_BATCH_SIZE):
        batch = entities[batch_start:batch_start + CLASSIFY_BATCH_SIZE]
        batch_num = batch_start // CLASSIFY_BATCH_SIZE + 1
        total_batches = (len(entities) + CLASSIFY_BATCH_SIZE - 1) // CLASSIFY_BATCH_SIZE

        # Build input for this batch
        input_list = []
        for e in batch:
            entry = {"name": e["name"]}
            if "type_votes" in e and len(e["type_votes"]) > 1:
                entry["types_seen"] = e["type_votes"]
            else:
                entry["type"] = e.get("type", "project")
            # Include description for iconifiability judgment
            if e.get("description"):
                entry["description"] = e["description"][:100]
            input_list.append(entry)

        logging.info(f"Classifying batch {batch_num}/{total_batches} ({len(batch)} entities)...")
        result, usage = call_llm(CLASSIFY_PROMPT.format(
            entities=json.dumps(input_list, indent=2)
        ))

        total_usage["input_tokens"] += usage.get("input_tokens", 0)
        total_usage["output_tokens"] += usage.get("output_tokens", 0)

        # Apply classifications
        classifications = result if isinstance(result, dict) else {}
        for e in batch:
            if e["name"] in classifications:
                c = classifications[e["name"]]
                if c.get("type") in ENTITY_TYPES:
                    e["type"] = c["type"]
                if c.get("status") in ("keep", "skip", "review"):
                    e["status"] = c["status"]
                    if c["status"] == "keep":
                        keep_count += 1
                    elif c["status"] == "skip":
                        skip_count += 1
                    else:
                        review_count += 1
            elif len(e.get("type_votes", {})) > 1:
                e["type"] = max(e["type_votes"], key=e["type_votes"].get)
            e.pop("type_votes", None)

            if e.get("type") in TYPE_NORMALIZATION:
                e["type"] = TYPE_NORMALIZATION[e["type"]]

    logging.info(f"Total: {keep_count} keep, {skip_count} skip, {review_count} review")
    return entities, total_usage


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
    parser.add_argument("--filter-only", action="store_true", help="Only filter invalid entities (no LLM, fast)")
    parser.add_argument("--reclassify", action="store_true", help="Re-run LLM classification on existing manifest (iconifiability check)")
    parser.add_argument("--dedupe", action="store_true", help="Dedupe existing inventory file by name, resolve type conflicts")
    parser.add_argument("--no-context", action="store_true", help="Skip fetching additional context from source paths (faster, fewer tokens)")
    parser.add_argument("--since", type=str, help="Only process files dated after YYYY-MM-DD (for incremental runs)")
    parser.add_argument("--parallel", "-p", type=int, default=1, metavar="N", help="Process N files in parallel (default: 1)")
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

        # Classify entities (type + status) via LLM
        deduped, usage = classify_entities(deduped)

        output = {
            "entities": deduped,
            "_metadata": {
                "classified_at": datetime.now(timezone.utc).isoformat() + "Z",
                "classify_input_tokens": usage["input_tokens"],
                "classify_output_tokens": usage["output_tokens"],
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

    # Reclassify mode: re-run LLM classification for iconifiability
    if args.reclassify:
        if not args.input.is_file():
            parser.error("--reclassify requires -i to be an existing JSON file")

        logging.info(f"Loading {args.input}...")
        with open(args.input) as f:
            data = json.load(f)

        entities = data.get("entities", [])
        logging.info(f"Reclassifying {len(entities)} entities for iconifiability...")

        # Run LLM classification (this applies the iconifiability test)
        entities, usage = classify_entities(entities)

        # Count results
        by_status = {}
        for e in entities:
            s = e.get("status", "keep")
            by_status[s] = by_status.get(s, 0) + 1

        logging.info(f"Results: {by_status}")

        output = {
            "entities": entities,
            "_metadata": {
                "reclassified_at": datetime.now(timezone.utc).isoformat() + "Z",
                "classify_input_tokens": usage["input_tokens"],
                "classify_output_tokens": usage["output_tokens"],
            }
        }

        out_path = args.output or args.input
        out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
        logging.info(f"Saved to {out_path}")
        return

    # Filter-only mode: apply code-based filters (no LLM)
    if args.filter_only:
        if not args.input.is_file():
            parser.error("--filter-only requires -i to be an existing JSON file")

        logging.info(f"Loading {args.input}...")
        with open(args.input) as f:
            data = json.load(f)

        entities = data.get("entities", [])
        before = len(entities)

        # Filter invalid names and skip types
        filtered = []
        for entity in entities:
            if not isinstance(entity, dict) or "name" not in entity:
                continue
            name = entity.get("name", "").strip()
            if is_invalid_entity_name(name):
                continue
            if name.lower() in SKIP_ENTITIES:
                continue
            filtered.append(entity)

        after = len(filtered)
        logging.info(f"Filtered: {before} -> {after} entities ({before - after} removed)")

        output = {
            "entities": filtered,
            "_metadata": data.get("_metadata", {})
        }
        output["_metadata"]["filtered_at"] = datetime.now(timezone.utc).isoformat() + "Z"

        out_path = args.output or args.input
        out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
        logging.info(f"Saved to {out_path}")
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
                "normalized_at": datetime.now(timezone.utc).isoformat() + "Z",
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

    logging.info(f"Processing {len(files)} file(s) with {args.parallel} worker(s)...")

    out_dir = args.output.parent if args.output else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    all_extractions = []
    total_input_tokens = 0
    total_output_tokens = 0

    def process_file(f):
        """Process a single file and return (extraction, usage, filename)."""
        content, raw_data = load_content(f)

        # Follow source paths for additional context (default: on)
        source_context = ""
        if not args.no_context and raw_data:
            source_context = get_source_context(raw_data)

        extraction, usage = extract_entities(content, source_context)
        return extraction, usage, f

    if args.parallel > 1:
        # Parallel processing
        with ThreadPoolExecutor(max_workers=args.parallel) as executor:
            futures = {executor.submit(process_file, f): f for f in files}
            for future in as_completed(futures):
                extraction, usage, f = future.result()
                logging.info(f"  {f.name} ({usage['input_tokens']} in, {usage['output_tokens']} out)")
                total_input_tokens += usage["input_tokens"]
                total_output_tokens += usage["output_tokens"]

                if extraction and extraction.get("entities"):
                    all_extractions.append(extraction)
                    if out_dir:
                        (out_dir / f.name).write_text(json.dumps({
                            "source": f.name,
                            "entities": extraction.get("entities", []),
                            "_metadata": {"extracted_at": datetime.now(timezone.utc).isoformat() + "Z"}
                        }, indent=2, ensure_ascii=True))
    else:
        # Sequential processing
        for f in files:
            extraction, usage, _ = process_file(f)
            logging.info(f"  {f.name} ({usage['input_tokens']} in, {usage['output_tokens']} out)")
            total_input_tokens += usage["input_tokens"]
            total_output_tokens += usage["output_tokens"]

            if extraction and extraction.get("entities"):
                all_extractions.append(extraction)
                if out_dir:
                    (out_dir / f.name).write_text(json.dumps({
                        "source": f.name,
                        "entities": extraction.get("entities", []),
                        "_metadata": {"extracted_at": datetime.now(timezone.utc).isoformat() + "Z"}
                    }, indent=2, ensure_ascii=True))

    merged = merge_entities(all_extractions)

    # Classify entities (type + status) via LLM
    merged, classify_usage = classify_entities(merged)
    total_input_tokens += classify_usage["input_tokens"]
    total_output_tokens += classify_usage["output_tokens"]

    # Optional LLM normalization pass
    if args.normalize:
        merged, norm_usage = normalize_entities(merged)
        total_input_tokens += norm_usage["input_tokens"]
        total_output_tokens += norm_usage["output_tokens"]

    output = {
        "entities": merged,
        "_metadata": {
            "extracted_at": datetime.now(timezone.utc).isoformat() + "Z",
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
