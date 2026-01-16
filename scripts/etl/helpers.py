#!/usr/bin/env python3
"""
Help-Reports ETL Pipeline

Unified script for extracting, analyzing, and backfilling help interactions from Discord data.

Usage:
    python helpers.py extract [-y YEAR] [-m MONTH] [--dry-run]
    python helpers.py analyze [-y YEAR] [-m MONTH] [--skip-llm]
    python helpers.py backfill [--force] [--start YYYY-MM] [--end YYYY-MM] [--limit N]

Commands:
    extract - Extract help interactions from Discord JSON files
    analyze - Generate contributor reports with network analysis and LLM perspectives
    backfill - Process all historical months through the pipeline
"""

import os
import sys
import json
import re
import requests
import argparse
import logging
import subprocess
from pathlib import Path
from datetime import datetime, timedelta, timezone
from calendar import monthrange
from collections import defaultdict, Counter
from typing import Optional
from string import Template

# Load environment variables from .env if available (for local testing)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, use system environment variables

try:
    import networkx as nx
except ImportError:
    print("ERROR: networkx is required. Install with: pip install networkx")
    sys.exit(1)

# --- Configuration ---
MODEL = "openai/gpt-5.2"
API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_API_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

SCRIPT_DIR = Path(__file__).parent.resolve()
SCRIPTS_ROOT = SCRIPT_DIR.parent  # scripts/
WORKSPACE_ROOT = SCRIPTS_ROOT.parent  # repository root

# Input/Output directories
DISCORD_JSON_DIR = WORKSPACE_ROOT / "ai-news" / "elizaos" / "discord" / "json"
HELPERS_DATA_DIR = WORKSPACE_ROOT / "media" / "data" / "helpers"  # Viz data (interactions, networks)
REPORTS_DIR = WORKSPACE_ROOT / "the-council" / "help-reports"  # Council intelligence (reports)
MARKDOWN_DIR = WORKSPACE_ROOT / "hackmd" / "helpers"

# Strategic context
NORTH_STAR_FILE = SCRIPTS_ROOT / "prompts" / "config" / "north-star.txt"
HELP_ANALYSIS_PROMPT_FILE = SCRIPTS_ROOT / "prompts" / "extraction" / "help-analysis.txt"

# Weighting configuration
NORTH_STAR_TRANSITION_DATE = "2025-12-01"  # When project goals shifted

CHANNEL_WEIGHTS = {
    "discussion": 1.0,          # Public, newcomer help
    "💬-discussion": 1.0,
    "coders": 1.0,              # Public, technical help
    "💻-coders": 1.0,
    "💬-coders": 1.0,
    "partners": 0.7,            # Semi-private
    "🥇-partners": 0.7,
    "tokenomics": 0.7,          # Semi-private
    "core-devs": 0.5,           # Private, internal collaboration
    "ideas-feedback-rants": 0.8,
    "spartan_holders": 0.6,
    "3d-ai-tv": 0.6,
}

DEFAULT_CHANNEL_WEIGHT = 1.0

# Temporal weights (alignment with project values)
TEMPORAL_WEIGHT_PRE_NORTH_STAR = 0.8    # Before Dec 2025
TEMPORAL_WEIGHT_POST_NORTH_STAR = 1.0   # Dec 2025 onwards

# Topic keywords for classification
TOPIC_KEYWORDS = {
    "Discord setup": ["discord", "bot", "integration", "voice", "channel"],
    "Plugin development": ["plugin", "custom", "development", "action", "provider"],
    "Troubleshooting": ["error", "bug", "fix", "debug", "issue", "problem"],
    "Deployment": ["deploy", "hosting", "server", "vps", "docker", "cloud"],
    "Migration support": ["migrate", "migration", "token", "wallet", "swap"],
    "API/Configuration": ["api", "config", "setup", "env", "key", "credential"],
    "Database": ["database", "postgres", "sqlite", "vector", "memory"],
    "Model/LLM": ["model", "llm", "openai", "anthropic", "ollama", "local"],
    "Twitter/Social": ["twitter", "tweet", "post", "social", "x.com"],
}

# Resolution quality indicators
RESOLUTION_SUCCESSFUL = ["confirmed working", "resolved", "fixed", "helped", "solved", "success"]
RESOLUTION_PARTIAL = ["suggested", "directed to", "recommended", "try", "check"]
RESOLUTION_UNANSWERED = ["unanswered"]

# Regex patterns for parsing help interactions
HELP_PATTERN_FULL = re.compile(
    r'Helper:\s*(.+?)\s*\|\s*Helpee:\s*(.+?)\s*\|\s*Context:\s*(.+?)\s*\|\s*Resolution:\s*(.+?)(?:\n|$)',
    re.IGNORECASE | re.DOTALL
)

HELP_PATTERN_NO_RESOLUTION = re.compile(
    r'Helper:\s*(.+?)\s*\|\s*Helpee:\s*(.+?)\s*\|\s*Context:\s*(.+?)(?:\n|$)',
    re.IGNORECASE | re.DOTALL
)

# Generic helpee patterns (get lower weight)
GENERIC_HELPEE_PATTERNS = [
    "multiple users", "community members", "several people", "several users",
    "community", "multiple", "channel members", "the community", "users"
]

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(levelname)s - %(message)s')


# ============================================================================
# Shared Utilities
# ============================================================================

def get_month_dates(year: int, month: int) -> tuple[str, str, list[str]]:
    """Get first day, last day, and all dates for a given month."""
    first_day = datetime(year, month, 1)
    last_day_num = monthrange(year, month)[1]
    last_day = datetime(year, month, last_day_num)

    all_dates = []
    current = first_day
    while current <= last_day:
        all_dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    return first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d"), all_dates


def get_target_month(year: Optional[int], month: Optional[int]) -> tuple[int, int, str]:
    """Get target year, month, and name. Defaults to previous month if not specified."""
    today = datetime.now()
    if year and month:
        target_year, target_month = year, month
    else:
        first_of_this_month = today.replace(day=1)
        last_month = first_of_this_month - timedelta(days=1)
        target_year, target_month = last_month.year, last_month.month

    month_name = datetime(target_year, target_month, 1).strftime("%B %Y")
    return target_year, target_month, month_name


# ============================================================================
# Extract Command - Help Interaction Extraction
# ============================================================================

def get_channel_weight(channel_name: str) -> float:
    """Get the weight for a given channel name."""
    # Try exact match first
    if channel_name in CHANNEL_WEIGHTS:
        return CHANNEL_WEIGHTS[channel_name]

    # Try case-insensitive match
    channel_lower = channel_name.lower()
    for known_channel, weight in CHANNEL_WEIGHTS.items():
        if known_channel.lower() == channel_lower:
            return weight

    # Try substring match (for emoji variants)
    for known_channel, weight in CHANNEL_WEIGHTS.items():
        if known_channel in channel_name or channel_name in known_channel:
            return weight

    return DEFAULT_CHANNEL_WEIGHT


def get_temporal_weight(date_str: str) -> float:
    """Get temporal weight based on date (pre/post North Star transition)."""
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        transition = datetime.strptime(NORTH_STAR_TRANSITION_DATE, "%Y-%m-%d")

        if date >= transition:
            return TEMPORAL_WEIGHT_POST_NORTH_STAR
        else:
            return TEMPORAL_WEIGHT_PRE_NORTH_STAR
    except ValueError:
        logging.warning(f"Invalid date format: {date_str}, using default weight")
        return TEMPORAL_WEIGHT_PRE_NORTH_STAR


def is_generic_helpee(helpee: str) -> bool:
    """Check if helpee is a generic reference rather than specific user."""
    helpee_lower = helpee.lower().strip()
    return any(pattern in helpee_lower for pattern in GENERIC_HELPEE_PATTERNS)


def parse_help_section(summary: str, channel_name: str, channel_id: str, date_str: str) -> list[dict]:
    """Extract help interactions from Discord summary text."""
    interactions = []

    # Look for "## 3. Help Interactions" section
    help_section_pattern = r'##\s*3\.\s*Help Interactions.*?(?=##|\Z)'
    match = re.search(help_section_pattern, summary, re.IGNORECASE | re.DOTALL)

    if not match:
        logging.debug(f"No Help Interactions section found for {channel_name} on {date_str}")
        return []

    help_section = match.group(0)

    # Check for explicit "no help" message
    if "no significant help" in help_section.lower():
        return []

    # Try to parse each line with full pattern (all 4 fields)
    for match in HELP_PATTERN_FULL.finditer(help_section):
        helper = match.group(1).strip()
        helpee = match.group(2).strip()
        context = match.group(3).strip()
        resolution = match.group(4).strip()

        if not helper or not helpee:
            continue

        # Calculate weights
        channel_weight = get_channel_weight(channel_name)
        temporal_weight = get_temporal_weight(date_str)
        helpee_modifier = 0.5 if is_generic_helpee(helpee) else 1.0
        combined_weight = channel_weight * temporal_weight * helpee_modifier

        interactions.append({
            "date": date_str,
            "channel_id": channel_id,
            "channel_name": channel_name,
            "helper": helper,
            "helpee": helpee,
            "context": context,
            "resolution": resolution,
            "is_generic_helpee": is_generic_helpee(helpee),
            "weights": {
                "channel": channel_weight,
                "temporal": temporal_weight,
                "helpee_modifier": helpee_modifier,
                "combined": round(combined_weight, 3)
            }
        })

    # Try fallback pattern for entries missing resolution
    for match in HELP_PATTERN_NO_RESOLUTION.finditer(help_section):
        helper = match.group(1).strip()
        helpee = match.group(2).strip()
        context = match.group(3).strip()

        if not helper or not helpee:
            continue

        # Skip if context contains "| Resolution:" - already handled by full pattern
        # (The no-resolution regex captures everything to EOL, including resolution text)
        if "| resolution:" in context.lower():
            continue

        # Skip if already matched by full pattern
        if any(i["helper"] == helper and
               i["helpee"] == helpee and
               i["context"] == context
               for i in interactions):
            continue

        # Calculate weights
        channel_weight = get_channel_weight(channel_name)
        temporal_weight = get_temporal_weight(date_str)
        helpee_modifier = 0.5 if is_generic_helpee(helpee) else 1.0
        combined_weight = channel_weight * temporal_weight * helpee_modifier

        interactions.append({
            "date": date_str,
            "channel_id": channel_id,
            "channel_name": channel_name,
            "helper": helper,
            "helpee": helpee,
            "context": context,
            "resolution": "Unanswered",
            "is_generic_helpee": is_generic_helpee(helpee),
            "weights": {
                "channel": channel_weight,
                "temporal": temporal_weight,
                "helpee_modifier": helpee_modifier,
                "combined": round(combined_weight, 3)
            }
        })

    return interactions


def process_discord_file(file_path: Path, date_str: str) -> tuple[list[dict], list[str]]:
    """Process a single Discord JSON file. Returns (interactions, errors)."""
    interactions = []
    errors = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        categories = data.get("categories", [])

        for category in categories:
            channel_id = category.get("channelId", "")
            channel_name = category.get("channelName", "unknown")
            summary = category.get("summary", "")

            if not summary:
                continue

            try:
                channel_interactions = parse_help_section(summary, channel_name, channel_id, date_str)
                interactions.extend(channel_interactions)
            except Exception as e:
                error_msg = f"Error parsing {channel_name} on {date_str}: {e}"
                errors.append(error_msg)
                logging.warning(error_msg)

    except FileNotFoundError:
        error_msg = f"File not found: {file_path}"
        errors.append(error_msg)
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in {file_path}: {e}"
        errors.append(error_msg)
        logging.error(error_msg)
    except Exception as e:
        error_msg = f"Error processing {file_path}: {e}"
        errors.append(error_msg)
        logging.error(error_msg)

    return interactions, errors


def extract_month_interactions(year: int, month: int) -> dict:
    """Extract all help interactions for a given month."""
    month_name = datetime(year, month, 1).strftime("%B %Y")
    logging.info(f"Extracting help interactions for {month_name}")

    first_day, last_day, all_dates = get_month_dates(year, month)
    logging.info(f"Processing {len(all_dates)} days: {first_day} to {last_day}")

    all_interactions = []
    days_with_data = []
    days_missing = []
    all_errors = []
    channels_seen = set()

    for date_str in all_dates:
        file_path = DISCORD_JSON_DIR / f"{date_str}.json"

        if not file_path.exists():
            days_missing.append(date_str)
            logging.debug(f"No data for {date_str}")
            continue

        interactions, errors = process_discord_file(file_path, date_str)

        if interactions:
            days_with_data.append(date_str)
            all_interactions.extend(interactions)
            channels_seen.update(i["channel_name"] for i in interactions)

        all_errors.extend(errors)

    # Calculate statistics
    helper_counts = defaultdict(int)
    helpee_counts = defaultdict(int)
    channel_counts = defaultdict(int)

    for interaction in all_interactions:
        helper_counts[interaction["helper"]] += 1
        if not interaction["is_generic_helpee"]:
            helpee_counts[interaction["helpee"]] += 1
        channel_counts[interaction["channel_name"]] += 1

    # Build output
    output = {
        "month": f"{year}-{month:02d}",
        "date_range": {
            "start": first_day,
            "end": last_day
        },
        "interactions": all_interactions,
        "_metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
            "days_processed": len(all_dates),
            "days_with_data": len(days_with_data),
            "days_missing": days_missing,
            "total_interactions": len(all_interactions),
            "unique_helpers": len(helper_counts),
            "unique_helpees": len(helpee_counts),
            "channels_tracked": sorted(channels_seen),
            "channel_distribution": dict(channel_counts),
            "north_star_transition": NORTH_STAR_TRANSITION_DATE,
            "parse_errors": len(all_errors),
            "error_details": all_errors[:10] if all_errors else []
        }
    }

    logging.info(f"Extracted {len(all_interactions)} interactions from {len(days_with_data)} days")
    logging.info(f"Unique helpers: {len(helper_counts)}, Unique helpees: {len(helpee_counts)}")
    logging.info(f"Channels: {sorted(channels_seen)}")

    if all_errors:
        logging.warning(f"Encountered {len(all_errors)} parse errors (see metadata for details)")

    return output


def cmd_extract(args):
    """Extract command handler."""
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    target_year, target_month, month_name = get_target_month(args.year, args.month)

    if args.dry_run:
        print(f"\nDry run for {month_name}:")
        print(f"  Would process: {DISCORD_JSON_DIR / f'{target_year}-{target_month:02d}-*.json'}")
        first_day, last_day, all_dates = get_month_dates(target_year, target_month)
        print(f"  Date range: {first_day} to {last_day} ({len(all_dates)} days)")

        # Count available files
        available = sum(1 for d in all_dates if (DISCORD_JSON_DIR / f"{d}.json").exists())
        print(f"  Files available: {available}/{len(all_dates)}")
        return

    # Extract interactions
    result = extract_month_interactions(target_year, target_month)

    # Determine output path
    HELPERS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_file = args.output or HELPERS_DATA_DIR / f"{target_year}-{target_month:02d}-interactions.json"

    # Write output
    logging.info(f"Writing output to {output_file}")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=True)
        logging.info(f"Successfully wrote {len(result['interactions'])} interactions to {output_file}")
    except Exception as e:
        logging.error(f"Error writing output file: {e}")
        sys.exit(1)

    # Print summary
    metadata = result["_metadata"]
    print(f"\n{'='*60}")
    print(f"Help Interaction Extraction: {month_name}")
    print(f"{'='*60}")
    print(f"Date range: {result['date_range']['start']} to {result['date_range']['end']}")
    print(f"Days processed: {metadata['days_processed']}")
    print(f"Days with data: {metadata['days_with_data']}")
    print(f"Days missing: {len(metadata['days_missing'])}")
    print(f"\nInteractions extracted: {metadata['total_interactions']}")
    print(f"Unique helpers: {metadata['unique_helpers']}")
    print(f"Unique helpees: {metadata['unique_helpees']}")
    print(f"\nChannels tracked: {', '.join(metadata['channels_tracked'])}")
    print(f"\nChannel distribution:")
    for channel, count in sorted(metadata['channel_distribution'].items(), key=lambda x: -x[1]):
        print(f"  {channel}: {count}")

    if metadata['parse_errors'] > 0:
        print(f"\nWarning: {metadata['parse_errors']} parse errors encountered")
        print("  See _metadata.error_details in output JSON for details")

    print(f"\nOutput: {output_file}")


# ============================================================================
# Analyze Command - Report Generation with LLM Analysis
# ============================================================================

def classify_topic(context: str) -> list[str]:
    """Classify the help context into topic categories."""
    context_lower = context.lower()
    topics = []

    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw in context_lower for kw in keywords):
            topics.append(topic)

    return topics if topics else ["General"]


def classify_resolution(resolution: str) -> str:
    """Classify resolution quality (successful, partial, unanswered)."""
    resolution_lower = resolution.lower()

    if any(indicator in resolution_lower for indicator in RESOLUTION_UNANSWERED):
        return "unanswered"

    if any(indicator in resolution_lower for indicator in RESOLUTION_SUCCESSFUL):
        return "successful"

    if any(indicator in resolution_lower for indicator in RESOLUTION_PARTIAL):
        return "partial"

    return "partial" if resolution else "unanswered"


def generate_contributor_profiles(interactions: list[dict]) -> dict:
    """Generate detailed contributor profiles from interactions."""
    profiles = defaultdict(lambda: {
        "total_helps": 0,
        "weighted_helps": 0.0,
        "unique_helpees": set(),
        "channels": Counter(),
        "topics": Counter(),
        "resolution_quality": Counter(),
        "interactions_by_date": [],
        "examples": []
    })

    for interaction in interactions:
        helper = interaction["helper"]
        profile = profiles[helper]

        profile["total_helps"] += 1
        profile["weighted_helps"] += interaction["weights"]["combined"]

        if not interaction["is_generic_helpee"]:
            profile["unique_helpees"].add(interaction["helpee"])

        profile["channels"][interaction["channel_name"]] += 1

        topics = classify_topic(interaction["context"])
        for topic in topics:
            profile["topics"][topic] += 1

        quality = classify_resolution(interaction["resolution"])
        profile["resolution_quality"][quality] += 1

        profile["interactions_by_date"].append(interaction["date"])

        if len(profile["examples"]) < 5:
            profile["examples"].append({
                "date": interaction["date"],
                "channel": interaction["channel_name"],
                "helpee": interaction["helpee"],
                "context": interaction["context"][:150] + "..." if len(interaction["context"]) > 150 else interaction["context"],
                "resolution": interaction["resolution"][:150] + "..." if len(interaction["resolution"]) > 150 else interaction["resolution"]
            })

    # Convert to final format
    final_profiles = {}
    for username, data in profiles.items():
        unique_helpees = len(data["unique_helpees"])

        total_resolved = data["resolution_quality"]["successful"] + data["resolution_quality"]["partial"]
        quality_rate = total_resolved / data["total_helps"] if data["total_helps"] > 0 else 0

        final_profiles[username] = {
            "total_helps": data["total_helps"],
            "weighted_helps": round(data["weighted_helps"], 2),
            "unique_helpees": unique_helpees,
            "channels": dict(data["channels"]),
            "topics": dict(data["topics"]),
            "resolution_quality": {
                "successful": data["resolution_quality"]["successful"],
                "partial": data["resolution_quality"]["partial"],
                "unanswered": data["resolution_quality"]["unanswered"],
                "quality_rate": round(quality_rate, 3)
            },
            "examples": data["examples"]
        }

    return final_profiles


def generate_network_graph(interactions: list[dict], profiles: dict) -> dict:
    """Generate network graph visualization data."""
    G = nx.DiGraph()

    edges_data = defaultdict(lambda: {
        "weight": 0,
        "weighted_sum": 0.0,
        "channels": set(),
        "last_interaction": None
    })

    for interaction in interactions:
        source = interaction["helper"]
        target = interaction["helpee"]

        if source == target:
            continue

        if source not in G:
            G.add_node(source)
        if target not in G:
            G.add_node(target)

        edge_key = (source, target)
        edges_data[edge_key]["weight"] += 1
        edges_data[edge_key]["weighted_sum"] += interaction["weights"]["combined"]
        edges_data[edge_key]["channels"].add(interaction["channel_name"])
        edges_data[edge_key]["last_interaction"] = interaction["date"]

        if G.has_edge(source, target):
            G[source][target]['weight'] += 1
        else:
            G.add_edge(source, target, weight=1)

    # Calculate centrality
    try:
        pagerank = nx.pagerank(G, weight='weight')
    except:
        pagerank = {node: 0 for node in G.nodes()}

    # Build nodes list
    nodes = []
    for node in G.nodes():
        in_degree = G.in_degree(node)
        out_degree = G.out_degree(node)

        if out_degree > 0 and in_degree == 0:
            node_type = "helper-only"
        elif in_degree > 0 and out_degree == 0:
            node_type = "helpee-only"
        else:
            node_type = "both"

        profile_data = profiles.get(node, {})

        nodes.append({
            "id": node,
            "type": node_type,
            "total_helps": profile_data.get("total_helps", 0),
            "weighted_helps": profile_data.get("weighted_helps", 0),
            "centrality": round(pagerank.get(node, 0), 4),
            "in_degree": in_degree,
            "out_degree": out_degree
        })

    # Build edges list
    edges = []
    for (source, target), data in edges_data.items():
        edges.append({
            "source": source,
            "target": target,
            "weight": data["weight"],
            "weighted_sum": round(data["weighted_sum"], 2),
            "channels": list(data["channels"]),
            "last_interaction": data["last_interaction"]
        })

    # Statistics
    helpers = [n for n in nodes if n["out_degree"] > 0]
    helpees = [n for n in nodes if n["in_degree"] > 0]

    top_helper = max(helpers, key=lambda x: x["total_helps"]) if helpers else None
    top_helpee = max(helpees, key=lambda x: x["in_degree"]) if helpees else None
    most_central = max(nodes, key=lambda x: x["centrality"]) if nodes else None

    statistics = {
        "total_nodes": len(nodes),
        "total_helpers": len(helpers),
        "total_helpees": len(helpees),
        "total_edges": len(edges),
        "most_active_helper": top_helper["id"] if top_helper else None,
        "most_helped_user": top_helpee["id"] if top_helpee else None,
        "most_central": most_central["id"] if most_central else None,
        "avg_helps_per_helper": round(sum(h["total_helps"] for h in helpers) / len(helpers), 2) if helpers else 0,
        "network_density": round(nx.density(G), 4) if G.number_of_nodes() > 0 else 0
    }

    return {
        "nodes": nodes,
        "edges": edges,
        "statistics": statistics
    }


def load_north_star() -> str:
    """Load the current north star context."""
    if NORTH_STAR_FILE.exists():
        return NORTH_STAR_FILE.read_text()
    return ""


def load_help_analysis_prompt() -> str:
    """Load the help analysis prompt template."""
    if HELP_ANALYSIS_PROMPT_FILE.exists():
        return HELP_ANALYSIS_PROMPT_FILE.read_text()
    logging.warning(f"Help analysis prompt file not found: {HELP_ANALYSIS_PROMPT_FILE}")
    return ""


def generate_llm_analysis(profiles: dict, network_stats: dict, month_name: str, north_star: str) -> Optional[dict]:
    """Generate multi-perspective analysis using LLM with council member personas."""
    top_profiles = dict(sorted(profiles.items(), key=lambda x: x[1]["weighted_helps"], reverse=True)[:20])

    simplified_profiles = {
        username: {k: v for k, v in data.items() if k != "examples"}
        for username, data in top_profiles.items()
    }

    # Load prompt template
    prompt_template = load_help_analysis_prompt()
    if not prompt_template:
        logging.error("Help analysis prompt template not found")
        return None

    # Interpolate variables into prompt using Template (safe for JSON in template)
    template = Template(prompt_template)
    prompt = template.substitute(
        north_star=north_star,
        month_name=month_name,
        profiles_json=json.dumps(simplified_profiles, indent=2)[:15000],
        network_stats_json=json.dumps(network_stats, indent=2)
    )

    if not API_KEY:
        logging.error("OPENROUTER_API_KEY not set")
        return None

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/elizaOS/knowledge",
        "X-Title": "Monthly Help Report Analysis"
    }

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }

    try:
        logging.info("Calling LLM for multi-perspective analysis...")
        response = requests.post(OPENROUTER_API_ENDPOINT, headers=headers, json=payload, timeout=300)
        response.raise_for_status()

        content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")

        # Clean up response
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        result = json.loads(content.strip())

        if not isinstance(result, dict):
            logging.error("Invalid LLM response - expected dict")
            return None

        logging.info(f"LLM analysis keys: {list(result.keys())}")
        return result

    except Exception as e:
        logging.error(f"LLM API call failed: {e}")
        return None


def generate_markdown_report(report_data: dict) -> str:
    """Generate human-readable markdown report."""
    lines = []

    lines.append(f"# Help Analysis Report: {report_data['month']}")
    lines.append(f"\n**Report Period**: {report_data['date_range']['start']} to {report_data['date_range']['end']}")
    lines.append(f"**Generated**: {report_data['_metadata']['generated_at']}")
    lines.append("")

    summary = report_data['summary']
    lines.append("## Summary")
    lines.append(f"- **Total help interactions**: {summary['total_helps']} (weighted: {summary['total_weighted_helps']})")
    lines.append(f"- **Unique helpers**: {summary['unique_helpers']}")
    lines.append(f"- **Unique helpees**: {summary['unique_helpees']}")
    lines.append(f"- **Channels analyzed**: {', '.join(summary['channels_analyzed'])}")
    lines.append("")

    lines.append("### Channel Distribution")
    for channel_data in summary['top_channels'][:5]:
        lines.append(f"- **{channel_data['channel']}**: {channel_data['helps']} interactions")
    lines.append("")

    # Problem Patterns
    if "problem_patterns" in report_data:
        lines.append("## Problem Patterns")
        patterns = report_data["problem_patterns"]
        if isinstance(patterns, list):
            for pattern in patterns:
                cat = pattern.get("category", "Unknown")
                count = pattern.get("count", "?")
                lines.append(f"\n### {cat} ({count} occurrences)")
                if pattern.get("examples"):
                    lines.append("Examples: " + ", ".join(pattern["examples"][:3]))
                if pattern.get("upstream_signal"):
                    lines.append(f"\n*Signal*: {pattern['upstream_signal']}")
        lines.append("")

    # Documentation Gaps
    if "documentation_gaps" in report_data:
        lines.append("## Documentation Gaps")
        for gap in report_data["documentation_gaps"]:
            topic = gap.get("topic", "Unknown")
            lines.append(f"\n### {topic}")
            if gap.get("signal"):
                lines.append(gap["signal"])
            if gap.get("suggested_action"):
                lines.append(f"\n*Action*: {gap['suggested_action']}")
        lines.append("")

    # Expertise Map
    if "expertise_map" in report_data:
        lines.append("## Expertise Map")
        for area, helpers in report_data["expertise_map"].items():
            if helpers:
                lines.append(f"- **{area}**: {', '.join(helpers[:5])}")
        lines.append("")

    # AI Learning Notes
    if "ai_learning_notes" in report_data:
        lines.append("## AI Learning Notes")
        notes = report_data["ai_learning_notes"]
        if isinstance(notes, dict):
            for key, value in notes.items():
                if key == "channel_culture" and isinstance(value, dict):
                    lines.append(f"- **{key}**:")
                    for channel, culture in value.items():
                        lines.append(f"  - *{channel}*: {culture}")
                else:
                    lines.append(f"- **{key}**: {value}")
        lines.append("")

    # Helper Highlights
    if "helper_highlights" in report_data and report_data["helper_highlights"]:
        lines.append("## Helper Highlights")
        for highlight in report_data["helper_highlights"]:
            helper = highlight.get("helper", "Unknown")
            quality = highlight.get("quality", "")
            example = highlight.get("example", "")
            lines.append(f"\n### {helper}")
            lines.append(f"**{quality}**")
            if example:
                lines.append(f"\n_{example}_")
        lines.append("")

    # Council Commentary
    if "council_commentary" in report_data:
        lines.append("## Council Commentary")
        lines.append("")
        for member, comment in report_data["council_commentary"].items():
            lines.append(f"### {member}")
            lines.append(comment)
            lines.append("")

    return "\n".join(lines)


def cmd_analyze(args):
    """Analyze command handler."""
    target_year, target_month, month_name = get_target_month(args.year, args.month)
    logging.info(f"Generating help report for {month_name}")

    # Load interaction data
    input_file = HELPERS_DATA_DIR / f"{target_year}-{target_month:02d}-interactions.json"
    if not input_file.exists():
        logging.error(f"Interaction data not found: {input_file}")
        logging.error("Run 'helpers.py extract' first")
        sys.exit(1)

    with open(input_file, 'r') as f:
        interaction_data = json.load(f)

    interactions = interaction_data["interactions"]
    logging.info(f"Loaded {len(interactions)} interactions")

    if args.dry_run:
        print(f"\nDry run for {month_name}:")
        print(f"  Input: {input_file}")
        print(f"  Interactions: {len(interactions)}")
        print(f"  Would generate profiles, network graph, and LLM analysis")
        return

    # Generate profiles
    logging.info("Generating contributor profiles...")
    profiles = generate_contributor_profiles(interactions)
    logging.info(f"Generated {len(profiles)} contributor profiles")

    # Generate network
    logging.info("Generating network graph...")
    network_data = generate_network_graph(interactions, profiles)
    logging.info(f"Network: {network_data['statistics']['total_nodes']} nodes, {network_data['statistics']['total_edges']} edges")

    # Load North Star
    north_star = load_north_star()

    # LLM analysis
    llm_analysis = None
    if not args.skip_llm:
        llm_analysis = generate_llm_analysis(profiles, network_data["statistics"], month_name, north_star)
        if not llm_analysis:
            logging.warning("LLM analysis failed, continuing without it")

    # Build report
    report_data = {
        "report_id": f"HELP-{target_year}-{target_month:02d}",
        "month": f"{target_year}-{target_month:02d}",
        "date_range": interaction_data["date_range"],
        "summary": {
            "total_helps": len(interactions),
            "total_weighted_helps": round(sum(i["weights"]["combined"] for i in interactions), 2),
            "unique_helpers": len(profiles),
            "unique_helpees": len(set(i["helpee"] for i in interactions if not i["is_generic_helpee"])),
            "channels_analyzed": interaction_data["_metadata"]["channels_tracked"],
            "top_channels": [
                {"channel": ch, "helps": count}
                for ch, count in sorted(
                    interaction_data["_metadata"]["channel_distribution"].items(),
                    key=lambda x: -x[1]
                )
            ]
        },
        "contributor_profiles": profiles,
        "_metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
            "model": MODEL if llm_analysis else None,
            "interactions_analyzed": len(interactions),
            "input_file": str(input_file.relative_to(WORKSPACE_ROOT))
        }
    }

    if llm_analysis:
        # Add all LLM analysis sections to report
        for key in ["problem_patterns", "expertise_map", "resolution_patterns",
                   "documentation_gaps", "ai_learning_notes", "helper_highlights",
                   "council_commentary"]:
            if key in llm_analysis:
                report_data[key] = llm_analysis[key]

    # Write outputs
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORTS_DIR / f"{target_year}-{target_month:02d}-report.json"
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=True)
    logging.info(f"Report saved to {report_file}")

    HELPERS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    network_file = HELPERS_DATA_DIR / f"{target_year}-{target_month:02d}-network.json"
    with open(network_file, 'w') as f:
        json.dump({"month": report_data["month"], **network_data}, f, indent=2, ensure_ascii=True)
    logging.info(f"Network data saved to {network_file}")

    MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)
    markdown_file = MARKDOWN_DIR / f"{target_year}-{target_month:02d}.md"
    markdown_content = generate_markdown_report(report_data)
    with open(markdown_file, 'w') as f:
        f.write(markdown_content)
    logging.info(f"Markdown report saved to {markdown_file}")

    # Update latest symlink
    latest_link = REPORTS_DIR / "latest.json"
    if latest_link.exists() or latest_link.is_symlink():
        latest_link.unlink()
    latest_link.symlink_to(report_file.name)
    logging.info(f"Updated latest.json symlink")

    # Print summary
    print(f"\n{'='*60}")
    print(f"Monthly Help Analysis: {month_name}")
    print(f"{'='*60}")
    print(f"\nInteractions analyzed: {len(interactions)}")
    print(f"Contributors: {len(profiles)}")
    print(f"Network nodes: {network_data['statistics']['total_nodes']}")
    print(f"Network edges: {network_data['statistics']['total_edges']}")

    # Show top helpers by weighted_helps
    top_helpers = sorted(profiles.items(), key=lambda x: x[1]["weighted_helps"], reverse=True)[:5]
    print(f"\nTop 5 by weighted helps:")
    for i, (username, data) in enumerate(top_helpers, 1):
        print(f"  {i}. {username} ({data['weighted_helps']} weighted helps)")

    if llm_analysis:
        print(f"\nLLM analysis sections: {', '.join(llm_analysis.keys())}")

    print(f"\nOutputs:")
    print(f"  Report: {report_file}")
    print(f"  Network: {network_file}")
    print(f"  Markdown: {markdown_file}")


# ============================================================================
# Backfill Command - Process Historical Months
# ============================================================================

def detect_available_months() -> list[tuple[int, int]]:
    """Detect all months with Discord JSON data."""
    if not DISCORD_JSON_DIR.exists():
        logging.error(f"Discord JSON directory not found: {DISCORD_JSON_DIR}")
        return []

    dates = set()
    for json_file in DISCORD_JSON_DIR.glob("????-??-??.json"):
        try:
            date_str = json_file.stem
            date = datetime.strptime(date_str, "%Y-%m-%d")
            dates.add((date.year, date.month))
        except ValueError:
            continue

    return sorted(dates)


def month_already_processed(year: int, month: int) -> bool:
    """Check if a month has already been processed."""
    interactions_file = HELPERS_DATA_DIR / f"{year}-{month:02d}-interactions.json"
    report_file = REPORTS_DIR / f"{year}-{month:02d}-report.json"
    return interactions_file.exists() and report_file.exists()


def process_month_via_subprocess(year: int, month: int) -> bool:
    """Process a single month by calling extract and analyze subcommands."""
    month_str = f"{year}-{month:02d}"
    month_name = datetime(year, month, 1).strftime("%B %Y")

    logging.info(f"[{month_str}] Processing {month_name}")

    # Step 1: Extract
    logging.info(f"[{month_str}] Step 1/2: Extracting interactions...")
    try:
        result = subprocess.run(
            [sys.executable, __file__, "extract", "-y", str(year), "-m", str(month)],
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            logging.error(f"[{month_str}] Extraction failed: {result.stderr}")
            return False

        logging.info(f"[{month_str}] Extraction completed")

    except subprocess.TimeoutExpired:
        logging.error(f"[{month_str}] Extraction timed out")
        return False
    except Exception as e:
        logging.error(f"[{month_str}] Extraction error: {e}")
        return False

    # Step 2: Analyze
    logging.info(f"[{month_str}] Step 2/2: Generating report...")
    try:
        result = subprocess.run(
            [sys.executable, __file__, "analyze", "-y", str(year), "-m", str(month)],
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            timeout=600,
            env={**os.environ}
        )

        if result.returncode != 0:
            logging.error(f"[{month_str}] Analysis failed: {result.stderr}")
            return False

        logging.info(f"[{month_str}] Report generated successfully")
        return True

    except subprocess.TimeoutExpired:
        logging.error(f"[{month_str}] Analysis timed out")
        return False
    except Exception as e:
        logging.error(f"[{month_str}] Analysis error: {e}")
        return False


def cmd_backfill(args):
    """Backfill command handler."""
    logging.info("Detecting available months...")
    available_months = detect_available_months()

    if not available_months:
        logging.error("No months with Discord data found")
        sys.exit(1)

    logging.info(f"Found {len(available_months)} months with data: {available_months[0]} to {available_months[-1]}")

    # Apply filters
    months_to_process = available_months

    if args.start:
        start_date = datetime.strptime(args.start, "%Y-%m")
        months_to_process = [(y, m) for y, m in months_to_process if (y, m) >= (start_date.year, start_date.month)]

    if args.end:
        end_date = datetime.strptime(args.end, "%Y-%m")
        months_to_process = [(y, m) for y, m in months_to_process if (y, m) <= (end_date.year, end_date.month)]

    # Exclude current month
    today = datetime.now()
    current_month = (today.year, today.month)
    months_to_process = [(y, m) for y, m in months_to_process if (y, m) != current_month]

    if args.limit:
        months_to_process = months_to_process[:args.limit]

    logging.info(f"Will process {len(months_to_process)} months")

    if not months_to_process:
        logging.info("No months to process")
        return

    # Process each month
    successful = 0
    failed = 0
    skipped = 0

    for year, month in months_to_process:
        if not args.force and month_already_processed(year, month):
            skipped += 1
            logging.info(f"[{year}-{month:02d}] Already processed, skipping")
            continue

        success = process_month_via_subprocess(year, month)
        if success:
            successful += 1
        else:
            failed += 1

    # Print summary
    print(f"\n{'='*60}")
    print(f"Backfill Summary")
    print(f"{'='*60}")
    print(f"Total months: {len(months_to_process)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")

    if failed > 0:
        logging.warning(f"{failed} months failed to process")
        sys.exit(1)


# ============================================================================
# Main CLI Entry Point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Help-Reports ETL Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest='command', required=True, help='Command to run')

    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract help interactions from Discord JSON files')
    extract_parser.add_argument("-y", "--year", type=int, help="Year to process (default: previous month's year)")
    extract_parser.add_argument("-m", "--month", type=int, help="Month to process (1-12, default: previous month)")
    extract_parser.add_argument("-o", "--output", type=Path, help="Output file path")
    extract_parser.add_argument("--dry-run", action="store_true", help="Show what would be processed without writing")
    extract_parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose debug logging")
    extract_parser.set_defaults(func=cmd_extract)

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Generate contributor reports with LLM analysis')
    analyze_parser.add_argument("-y", "--year", type=int, help="Year to analyze (default: previous month's year)")
    analyze_parser.add_argument("-m", "--month", type=int, help="Month to analyze (1-12, default: previous month)")
    analyze_parser.add_argument("--skip-llm", action="store_true", help="Skip LLM analysis (faster, for testing)")
    analyze_parser.add_argument("--dry-run", action="store_true", help="Show what would be analyzed without generating")
    analyze_parser.set_defaults(func=cmd_analyze)

    # Backfill command
    backfill_parser = subparsers.add_parser('backfill', help='Process all historical months through the pipeline')
    backfill_parser.add_argument("--force", action="store_true", help="Reprocess already processed months")
    backfill_parser.add_argument("--start", type=str, help="Start from this month (YYYY-MM)")
    backfill_parser.add_argument("--end", type=str, help="End at this month (YYYY-MM)")
    backfill_parser.add_argument("--limit", type=int, help="Limit number of months to process")
    backfill_parser.set_defaults(func=cmd_backfill)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
