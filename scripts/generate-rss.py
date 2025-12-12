#!/usr/bin/env python3
"""
Generates RSS feeds from daily facts and council briefings.
Output: rss/feed.xml (facts), rss/council.xml (council briefings)
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

# Configuration
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
FACTS_DIR = WORKSPACE_ROOT / "the-council" / "facts"
COUNCIL_DIR = WORKSPACE_ROOT / "the-council" / "council_briefing"
OUTPUT_DIR = WORKSPACE_ROOT / "rss"
SITE_URL = "https://elizaos.github.io/knowledge"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_json_files(directory: Path, limit: int = 20) -> list[dict]:
    """Load recent JSON files from a directory."""
    json_files = sorted(directory.glob("2*.json"), reverse=True)[:limit]

    items = []
    for f in json_files:
        try:
            data = json.loads(f.read_text())
            data["_filename"] = f.stem  # e.g., "2025-12-12"
            items.append(data)
        except Exception as e:
            logging.warning(f"Failed to load {f}: {e}")

    return items


def create_rss_channel(title: str, description: str, feed_url: str) -> tuple[Element, Element]:
    """Create RSS root and channel elements."""
    rss = Element("rss", version="2.0")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")

    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = title
    SubElement(channel, "link").text = SITE_URL
    SubElement(channel, "description").text = description
    SubElement(channel, "language").text = "en-us"
    SubElement(channel, "lastBuildDate").text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

    atom_link = SubElement(channel, "{http://www.w3.org/2005/Atom}link")
    atom_link.set("href", feed_url)
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")

    return rss, channel


def prettify_xml(element: Element) -> str:
    """Convert Element to pretty-printed XML string."""
    xml_str = tostring(element, encoding="unicode")
    return minidom.parseString(xml_str).toprettyxml(indent="  ")


# --- Facts Feed ---

def format_facts_description(facts: dict) -> str:
    """Format facts into readable HTML description."""
    lines = []

    summary = facts.get("overall_summary", "")
    if summary:
        lines.append(f"<p><strong>Summary:</strong> {summary}</p>")

    categories = facts.get("categories", {})

    github = categories.get("github_updates", {})
    prs = github.get("new_issues_prs", [])
    if prs:
        lines.append("<p><strong>GitHub Activity:</strong></p><ul>")
        for pr in prs[:5]:
            title = pr.get("title", "Unknown")
            status = pr.get("status", "")
            lines.append(f"<li>{title} ({status})</li>")
        lines.append("</ul>")

    discord = categories.get("discord_updates", [])
    if discord:
        lines.append("<p><strong>Community Highlights:</strong></p><ul>")
        for update in discord[:3]:
            channel = update.get("channel", "")
            disc_summary = update.get("summary", "")[:200]
            lines.append(f"<li><em>{channel}:</em> {disc_summary}...</li>")
        lines.append("</ul>")

    return "\n".join(lines) if lines else "<p>No details available.</p>"


def create_facts_feed(items: list[dict]) -> str:
    """Generate RSS XML from facts items."""
    feed_url = f"{SITE_URL}/rss/feed.xml"
    base_url = f"{SITE_URL}/the-council/facts"

    rss, channel = create_rss_channel(
        title="elizaOS Daily Intelligence",
        description="Daily facts and insights from the elizaOS ecosystem",
        feed_url=feed_url
    )

    for facts in items:
        date_str = facts.get("briefing_date") or facts.get("_filename", "unknown")

        item = SubElement(channel, "item")
        SubElement(item, "title").text = f"elizaOS Intelligence: {date_str}"
        SubElement(item, "link").text = f"{base_url}/{facts['_filename']}.json"
        SubElement(item, "guid").text = f"{base_url}/{facts['_filename']}.json"
        SubElement(item, "description").text = format_facts_description(facts)

        try:
            pub_date = datetime.strptime(date_str, "%Y-%m-%d")
            SubElement(item, "pubDate").text = pub_date.strftime("%a, %d %b %Y 12:00:00 +0000")
        except ValueError:
            pass

    return prettify_xml(rss)


# --- Council Feed ---

def format_council_description(briefing: dict) -> str:
    """Format council briefing into readable HTML description."""
    lines = []

    daily_focus = briefing.get("daily_focus", "")
    if daily_focus:
        lines.append(f"<p><strong>Daily Focus:</strong> {daily_focus}</p>")

    monthly_goal = briefing.get("monthly_goal", "")
    if monthly_goal:
        lines.append(f"<p><em>Monthly Goal:</em> {monthly_goal}</p>")

    key_points = briefing.get("key_points", [])
    if key_points:
        lines.append("<p><strong>Key Topics:</strong></p><ul>")
        for point in key_points[:5]:
            topic = point.get("topic", "Unknown")
            summary = point.get("summary", "")[:200]
            lines.append(f"<li><strong>{topic}:</strong> {summary}...</li>")
        lines.append("</ul>")

    return "\n".join(lines) if lines else "<p>No details available.</p>"


def create_council_feed(items: list[dict]) -> str:
    """Generate RSS XML from council briefing items."""
    feed_url = f"{SITE_URL}/rss/council.xml"
    base_url = f"{SITE_URL}/the-council/council_briefing"

    rss, channel = create_rss_channel(
        title="elizaOS Council Briefings",
        description="Strategic briefings and deliberation items for elizaOS leadership",
        feed_url=feed_url
    )

    for briefing in items:
        date_str = briefing.get("date") or briefing.get("_filename", "unknown")

        item = SubElement(channel, "item")
        SubElement(item, "title").text = f"Council Briefing: {date_str}"
        SubElement(item, "link").text = f"{base_url}/{briefing['_filename']}.json"
        SubElement(item, "guid").text = f"{base_url}/{briefing['_filename']}.json"
        SubElement(item, "description").text = format_council_description(briefing)

        try:
            pub_date = datetime.strptime(date_str, "%Y-%m-%d")
            SubElement(item, "pubDate").text = pub_date.strftime("%a, %d %b %Y 14:00:00 +0000")
        except ValueError:
            pass

    return prettify_xml(rss)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate facts feed
    logging.info("Generating facts RSS feed...")
    facts_items = load_json_files(FACTS_DIR, limit=20)
    if facts_items:
        logging.info(f"Loaded {len(facts_items)} facts files")
        facts_feed = create_facts_feed(facts_items)
        (OUTPUT_DIR / "feed.xml").write_text(facts_feed)
        logging.info(f"Facts feed written to {OUTPUT_DIR / 'feed.xml'}")
    else:
        logging.warning("No facts files found")

    # Generate council feed
    logging.info("Generating council RSS feed...")
    council_items = load_json_files(COUNCIL_DIR, limit=20)
    if council_items:
        logging.info(f"Loaded {len(council_items)} council briefing files")
        council_feed = create_council_feed(council_items)
        (OUTPUT_DIR / "council.xml").write_text(council_feed)
        logging.info(f"Council feed written to {OUTPUT_DIR / 'council.xml'}")
    else:
        logging.warning("No council briefing files found")


if __name__ == "__main__":
    main()
