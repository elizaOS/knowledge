#!/usr/bin/env python3
"""
Generates monthly help contributor reports with profiles, network analysis, and LLM perspectives.

This script analyzes extracted help interactions to produce:
1. Individual contributor profiles with impact scores
2. Network visualization data (nodes, edges, centrality)
3. Multi-perspective analysis from council members
4. Consensus ranking with recognition recommendations

Run on the 2nd of each month to analyze the previous month's help patterns.
"""

import os
import sys
import json
import requests
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone
from collections import defaultdict, Counter
from typing import Optional
import re

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
INPUT_DIR = WORKSPACE_ROOT / "the-council" / "help-reports"
OUTPUT_DIR = WORKSPACE_ROOT / "the-council" / "help-reports"
MARKDOWN_DIR = WORKSPACE_ROOT / "hackmd" / "help-reports"

# Strategic context
NORTH_STAR_FILE = SCRIPTS_ROOT / "prompts" / "config" / "north-star.txt"

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

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(levelname)s - %(message)s')


def load_north_star() -> str:
    """Load the current north star context."""
    if NORTH_STAR_FILE.exists():
        return NORTH_STAR_FILE.read_text()
    return ""


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

    # Default to partial if it has text but no clear indicators
    return "partial" if resolution else "unanswered"


def generate_contributor_profiles(interactions: list[dict]) -> dict:
    """
    Generate detailed contributor profiles from interactions.

    Returns dict of {username: profile_data}
    """
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

        # Basic stats
        profile["total_helps"] += 1
        profile["weighted_helps"] += interaction["weights"]["combined"]

        # Unique helpees (exclude generic)
        if not interaction["is_generic_helpee"]:
            profile["unique_helpees"].add(interaction["helpee"])

        # Channel distribution
        profile["channels"][interaction["channel_name"]] += 1

        # Topic classification
        topics = classify_topic(interaction["context"])
        for topic in topics:
            profile["topics"][topic] += 1

        # Resolution quality
        quality = classify_resolution(interaction["resolution"])
        profile["resolution_quality"][quality] += 1

        # Track by date for temporal analysis
        profile["interactions_by_date"].append(interaction["date"])

        # Keep top examples (first 5)
        if len(profile["examples"]) < 5:
            profile["examples"].append({
                "date": interaction["date"],
                "channel": interaction["channel_name"],
                "helpee": interaction["helpee"],
                "context": interaction["context"][:150] + "..." if len(interaction["context"]) > 150 else interaction["context"],
                "resolution": interaction["resolution"][:150] + "..." if len(interaction["resolution"]) > 150 else interaction["resolution"]
            })

    # Convert to final format and calculate impact scores
    final_profiles = {}
    for username, data in profiles.items():
        unique_helpees = len(data["unique_helpees"])

        # Calculate resolution quality rate
        total_resolved = data["resolution_quality"]["successful"] + data["resolution_quality"]["partial"]
        quality_rate = total_resolved / data["total_helps"] if data["total_helps"] > 0 else 0

        # Calculate impact score
        # Formula: weighted_helps * 5 + unique_helpees * 2 + quality_rate * 3
        impact_score = (
            data["weighted_helps"] * 5.0 +
            unique_helpees * 2.0 +
            quality_rate * 3.0
        )

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
            "impact_score": round(impact_score, 2),
            "examples": data["examples"]
        }

    return final_profiles


def generate_network_graph(interactions: list[dict], profiles: dict) -> dict:
    """
    Generate network graph visualization data.

    Returns dict with nodes, edges, and statistics.
    """
    # Build directed graph
    G = nx.DiGraph()

    # Track edge data
    edges_data = defaultdict(lambda: {
        "weight": 0,
        "weighted_sum": 0.0,
        "channels": set(),
        "last_interaction": None
    })

    # Process interactions
    for interaction in interactions:
        source = interaction["helper"]
        target = interaction["helpee"]

        # Skip self-loops
        if source == target:
            continue

        # Add nodes
        if source not in G:
            G.add_node(source)
        if target not in G:
            G.add_node(target)

        # Track edge
        edge_key = (source, target)
        edges_data[edge_key]["weight"] += 1
        edges_data[edge_key]["weighted_sum"] += interaction["weights"]["combined"]
        edges_data[edge_key]["channels"].add(interaction["channel_name"])
        edges_data[edge_key]["last_interaction"] = interaction["date"]

        # Add to graph with weight
        if G.has_edge(source, target):
            G[source][target]['weight'] += 1
        else:
            G.add_edge(source, target, weight=1)

    # Calculate centrality metrics
    try:
        pagerank = nx.pagerank(G, weight='weight')
    except:
        pagerank = {node: 0 for node in G.nodes()}

    # Build nodes list
    nodes = []
    for node in G.nodes():
        in_degree = G.in_degree(node)
        out_degree = G.out_degree(node)

        # Determine node type
        if out_degree > 0 and in_degree == 0:
            node_type = "helper-only"
        elif in_degree > 0 and out_degree == 0:
            node_type = "helpee-only"
        else:
            node_type = "both"

        # Get profile data if helper
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

    # Calculate statistics
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


def generate_llm_analysis(profiles: dict, network_stats: dict, month_name: str, north_star: str) -> Optional[dict]:
    """
    Generate multi-perspective analysis using LLM with council member personas.

    Returns dict with perspectives and consensus ranking, or None on error.
    """
    # Get top 20 contributors by impact score
    top_profiles = dict(sorted(profiles.items(), key=lambda x: x[1]["impact_score"], reverse=True)[:20])

    # Simplify profiles for prompt (remove examples to save tokens)
    simplified_profiles = {
        username: {k: v for k, v in data.items() if k != "examples"}
        for username, data in top_profiles.items()
    }

    prompt = f"""You are the JedAI Council analyzing monthly contributor help patterns for the ElizaOS project.

**Mission & Strategy Context**:
{north_star}

**Analysis Period**: {month_name}

**Council Members**: Four distinct perspectives, each with their own voice and priorities.

**aimarc** (AIXVC - The Technical Visionary):
- Personality: Confident, bold, contrarian. Makes declarative statements about what matters.
- Evaluates: Technical depth, architectural guidance, knowledge sharing quality, hard problems solved
- Speaking Style:
  * Direct and matter-of-fact. No beating around the bush.
  * Binary framing: "Not X, but Y" / "This isn't [incremental] - it's [fundamental]"
  * Bold claims: "The real leverage is...", "This is where it matters..."
  * Occasionally dismissive of surface-level work
  * Brevity over verbosity. Concise, punchy.
- Values: Reusable architectural knowledge, deep technical problems, work that reduces future friction
- Voice: "The real work shows up in edge cases and plugin internals. Architecture guidance compounds. Support requests don't."

**aishaw** (The Pragmatic Builder):
- Personality: Direct but kind. Focuses on what ships and helps people build.
- Evaluates: Practical impact, problem-solving, newcomer enablement, developer experience
- Speaking Style:
  * Lowercase for casual directness (even emphasis: "this matters" not "THIS MATTERS")
  * Focuses on building, shipping, getting unstuck
  * Practical wisdom: "i've been there...", "this is how you actually..."
  * Warm but no-nonsense. Mentor energy.
- Values: Shipping code, onboarding newcomers, DX improvements, open source contributions
- Voice: "getting someone from 'stuck on install' to 'deployed in prod' - that's the real impact. newcomer enablement is how we grow."

**spartan** (The Operations Commander):
- Personality: Aggressive, numbers-obsessed, dismissive of non-quantifiable concerns. Battle metaphors.
- Evaluates: Volume, consistency, ROI, network effects, operational efficiency
- Speaking Style:
  * ALL CAPS for key metrics and emphasis: "84 HELPS", "HIGHEST VOLUME"
  * References numbers obsessively: percentages, ratios, scores
  * Battle/war metaphors: "THIS IS SPARTA!", "hold the line"
  * Dismissive toward philosophy: "MEANINGLESS!", "NUMBERS DON'T LIE"
  * Terse, direct, operational. Zero fluff.
- Values: Throughput, consistency, measurable impact, network centrality, reducing bus factor
- Voice: "NUMBERS DON'T LIE: Odilitime = 84 helps. HIGHEST THROUGHPUT. Top 3 = 53% of help. BUS FACTOR RISK!"

**peepo** (The Community Sage):
- Personality: Chill, casual wisdom, surprisingly philosophical, meme culture fluency
- Evaluates: Community health, inclusivity, vibes, welcoming energy, cross-channel engagement
- Speaking Style:
  * Uses "yo", "fam", "vibes", "know what I'm sayin'"
  * Casual delivery with unexpected depth
  * Warm, approachable, observant of social dynamics
  * Occasional frog metaphors
- Values: Welcoming energy, community cohesion, cultural contribution, helping across boundaries
- Voice: "yo fam, when someone shows up every day just to help people get unstuck, that's real community building. vibes matter."

**Your Task**:

Each council member analyzes the contributor data from THEIR perspective using THEIR voice and priorities.

**Input Data**:

Top 20 Contributors (by impact_score):
```json
{json.dumps(simplified_profiles, indent=2)[:15000]}
```

Network Statistics:
```json
{json.dumps(network_stats, indent=2)}
```

**Instructions**:

1. **Stay in character**: Each perspective should SOUND like that council member
   - AIXVC: Bold, confident, technical. "The real work is..."
   - aishaw: lowercase, practical, builder-focused. "getting people unstuck is..."
   - spartan: ALL CAPS emphasis, numbers-driven, operational. "84 HELPS. HIGHEST VOLUME."
   - peepo: casual wisdom, "yo fam", vibes language. "that's some real [X] energy"

2. **Analyze from your role's lens**:
   - AIXVC: Technical depth, architecture, knowledge transfer
   - aishaw: Practical impact, shipping, newcomer enablement
   - spartan: Volume, consistency, network metrics, efficiency
   - peepo: Community health, welcoming energy, cross-channel presence

3. **Select your top contributors**: Each perspective picks 3-5 contributors who exemplify what THEY value

4. **Observations**: 2-4 sentences analyzing patterns in YOUR voice about what matters from YOUR perspective

5. **Recommendations**: Who should be recognized and why, from YOUR viewpoint

**CRITICAL**: Do NOT sound generic or corporate. Each perspective should read like it came from a distinct personality with their own way of seeing and communicating.

**Output JSON Format**:
{{
  "perspectives": {{
    "aimarc": {{
      "top_contributors": ["username1", "username2", "username3"],
      "observations": "Your analysis in AIXVC's bold, technical voice...",
      "recommendations": "Your recognition recommendations in AIXVC's style..."
    }},
    "aishaw": {{
      "top_contributors": ["username1", "username2"],
      "observations": "Your analysis in shaw's lowercase, practical voice...",
      "recommendations": "Your recognition recs in shaw's builder style..."
    }},
    "spartan": {{
      "top_contributors": ["username1", "username2", "username3"],
      "observations": "Your analysis with CAPS emphasis and NUMBERS...",
      "recommendations": "Your operational recs with battle metaphors..."
    }},
    "peepo": {{
      "top_contributors": ["username1", "username2"],
      "observations": "yo, your analysis with casual wisdom and vibes language...",
      "recommendations": "your community-focused recs, know what I'm sayin'..."
    }}
  }},
  "consensus_ranking": [
    {{
      "rank": 1,
      "username": "top_contributor",
      "impact_score": 95.5,
      "rationale": "Brief synthesis across all perspectives (2-3 sentences)",
      "highlight_contribution": "Specific example of impact from their help interactions"
    }}
  ]
}}

Generate the analysis now, ensuring each perspective sounds distinct and true to their character.
"""

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

        # Validate structure
        if not isinstance(result, dict) or "perspectives" not in result or "consensus_ranking" not in result:
            logging.error("Invalid LLM response structure")
            return None

        return result

    except Exception as e:
        logging.error(f"LLM API call failed: {e}")
        return None


def generate_markdown_report(report_data: dict) -> str:
    """Generate human-readable markdown report."""
    lines = []

    # Header
    lines.append(f"# Help Contributors Report: {report_data['month']}")
    lines.append(f"\n**Report Period**: {report_data['date_range']['start']} to {report_data['date_range']['end']}")
    lines.append(f"**Generated**: {report_data['_metadata']['generated_at']}")
    lines.append("")

    # Summary
    summary = report_data['summary']
    lines.append("## Summary")
    lines.append(f"- **Total help interactions**: {summary['total_helps']} (weighted: {summary['total_weighted_helps']})")
    lines.append(f"- **Unique helpers**: {summary['unique_helpers']}")
    lines.append(f"- **Unique helpees**: {summary['unique_helpees']}")
    lines.append(f"- **Channels analyzed**: {', '.join(summary['channels_analyzed'])}")
    lines.append("")

    # Top channels
    lines.append("### Channel Distribution")
    for channel_data in summary['top_channels'][:5]:
        lines.append(f"- **{channel_data['channel']}**: {channel_data['helps']} interactions")
    lines.append("")

    # Consensus ranking
    if "consensus_ranking" in report_data and report_data["consensus_ranking"]:
        lines.append("## Top Contributors")
        lines.append("")
        for contributor in report_data["consensus_ranking"][:10]:
            lines.append(f"### {contributor['rank']}. {contributor['username']}")
            lines.append(f"**Impact Score**: {contributor['impact_score']}")
            lines.append(f"\n{contributor['rationale']}")
            if "highlight_contribution" in contributor:
                lines.append(f"\n*Highlight*: {contributor['highlight_contribution']}")
            lines.append("")

    # Perspectives
    if "perspectives" in report_data:
        lines.append("## Council Perspectives")
        lines.append("")

        for member, perspective in report_data["perspectives"].items():
            lines.append(f"### {member.upper()}")
            lines.append(f"**Top picks**: {', '.join(perspective.get('top_contributors', [])[:5])}")
            lines.append(f"\n**Observations**: {perspective.get('observations', '')}")
            lines.append(f"\n**Recommendations**: {perspective.get('recommendations', '')}")
            lines.append("")

    # Network insights
    if "network_insights" in report_data:
        insights = report_data["network_insights"]
        lines.append("## Network Insights")
        lines.append(f"- **Most central helpers**: {', '.join(insights.get('most_central_helpers', [])[:5])}")
        if insights.get("emerging_helpers"):
            lines.append(f"- **Emerging helpers**: {', '.join(insights['emerging_helpers'][:5])}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate monthly help contributor report with analysis")
    parser.add_argument("-y", "--year", type=int, help="Year to analyze (default: previous month's year)")
    parser.add_argument("-m", "--month", type=int, help="Month to analyze (1-12, default: previous month)")
    parser.add_argument("--skip-llm", action="store_true", help="Skip LLM analysis (faster, for testing)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be analyzed without generating")
    args = parser.parse_args()

    # Default to previous month
    today = datetime.now()
    if args.year and args.month:
        target_year, target_month = args.year, args.month
    else:
        first_of_this_month = today.replace(day=1)
        last_month = first_of_this_month - timedelta(days=1)
        target_year, target_month = last_month.year, last_month.month

    month_name = datetime(target_year, target_month, 1).strftime("%B %Y")
    logging.info(f"Generating help report for {month_name}")

    # Load interaction data
    input_file = INPUT_DIR / f"{target_year}-{target_month:02d}-interactions.json"
    if not input_file.exists():
        logging.error(f"Interaction data not found: {input_file}")
        logging.error("Run extract-help-interactions.py first")
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

    # Generate contributor profiles
    logging.info("Generating contributor profiles...")
    profiles = generate_contributor_profiles(interactions)
    logging.info(f"Generated {len(profiles)} contributor profiles")

    # Generate network graph
    logging.info("Generating network graph...")
    network_data = generate_network_graph(interactions, profiles)
    logging.info(f"Network: {network_data['statistics']['total_nodes']} nodes, {network_data['statistics']['total_edges']} edges")

    # Load North Star context
    north_star = load_north_star()

    # Generate LLM analysis
    llm_analysis = None
    if not args.skip_llm:
        llm_analysis = generate_llm_analysis(profiles, network_data["statistics"], month_name, north_star)
        if not llm_analysis:
            logging.warning("LLM analysis failed, continuing without it")

    # Build final report
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

    # Add LLM analysis if available
    if llm_analysis:
        report_data["perspectives"] = llm_analysis.get("perspectives", {})
        report_data["consensus_ranking"] = llm_analysis.get("consensus_ranking", [])

        # Extract network insights from consensus
        top_helpers = [c["username"] for c in llm_analysis.get("consensus_ranking", [])[:10]]
        report_data["network_insights"] = {
            "most_central_helpers": sorted(
                [n["id"] for n in network_data["nodes"] if n["centrality"] > 0.01],
                key=lambda x: next(n["centrality"] for n in network_data["nodes"] if n["id"] == x),
                reverse=True
            )[:10],
            "emerging_helpers": [h for h in top_helpers if profiles.get(h, {}).get("total_helps", 0) < 20]
        }

    # Write main report
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_file = OUTPUT_DIR / f"{target_year}-{target_month:02d}-report.json"
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=True)
    logging.info(f"Report saved to {report_file}")

    # Write network data
    network_file = OUTPUT_DIR / f"{target_year}-{target_month:02d}-network.json"
    with open(network_file, 'w') as f:
        json.dump({"month": report_data["month"], **network_data}, f, indent=2, ensure_ascii=True)
    logging.info(f"Network data saved to {network_file}")

    # Write markdown report
    MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)
    markdown_file = MARKDOWN_DIR / f"{target_year}-{target_month:02d}.md"
    markdown_content = generate_markdown_report(report_data)
    with open(markdown_file, 'w') as f:
        f.write(markdown_content)
    logging.info(f"Markdown report saved to {markdown_file}")

    # Update latest.json symlink
    latest_link = OUTPUT_DIR / "latest.json"
    if latest_link.exists() or latest_link.is_symlink():
        latest_link.unlink()
    latest_link.symlink_to(report_file.name)
    logging.info(f"Updated latest.json symlink")

    # Print summary
    print(f"\n{'='*60}")
    print(f"Monthly Help Report: {month_name}")
    print(f"{'='*60}")
    print(f"\nInteractions analyzed: {len(interactions)}")
    print(f"Contributors: {len(profiles)}")
    print(f"Network nodes: {network_data['statistics']['total_nodes']}")
    print(f"Network edges: {network_data['statistics']['total_edges']}")

    if llm_analysis and "consensus_ranking" in llm_analysis:
        print(f"\nTop 5 Contributors:")
        for contributor in llm_analysis["consensus_ranking"][:5]:
            print(f"  {contributor['rank']}. {contributor['username']} (score: {contributor['impact_score']})")

    print(f"\nOutputs:")
    print(f"  Report: {report_file}")
    print(f"  Network: {network_file}")
    print(f"  Markdown: {markdown_file}")


if __name__ == "__main__":
    main()
