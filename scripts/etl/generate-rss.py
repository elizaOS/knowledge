#!/usr/bin/env python3
"""
Generates RSS feeds from daily facts, council briefings, and retrospectives.
Output: rss/feed.xml (facts), rss/council.xml (council + retros)
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

# Configuration
SCRIPT_DIR = Path(__file__).resolve().parent  # scripts/etl/
SCRIPTS_ROOT = SCRIPT_DIR.parent  # scripts/
WORKSPACE_ROOT = SCRIPTS_ROOT.parent  # repository root
FACTS_DIR = WORKSPACE_ROOT / "the-council" / "facts"
COUNCIL_DIR = WORKSPACE_ROOT / "the-council" / "council_briefing"
RETROS_DIR = WORKSPACE_ROOT / "the-council" / "retros"
OUTPUT_DIR = WORKSPACE_ROOT / "rss"
SITE_URL = "https://elizaos.github.io/knowledge"

# External feeds (cross-linked in footers)
GITHUB_FEED_URL = "https://elizaos.github.io/rss.xml"

# Character hosting (avatars deferred - see GitHub issue)
# SHAW_AVATAR = "https://m3-org.github.io/avatars/shaw/thumb-bust_shaw.png"
# ELIZA_AVATAR = "https://m3-org.github.io/avatars/eliza/thumb-bust_eliza.png"

# Social links
TWITTER_URL = "https://x.com/elizaos"

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


def create_rss_channel(title: str, description: str, feed_url: str, image_url: str = None) -> tuple[Element, Element]:
    """Create RSS root and channel elements."""
    rss = Element("rss", version="2.0")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")

    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = title
    SubElement(channel, "link").text = SITE_URL
    SubElement(channel, "description").text = description
    SubElement(channel, "language").text = "en-us"
    SubElement(channel, "lastBuildDate").text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

    # Self link
    atom_link = SubElement(channel, "{http://www.w3.org/2005/Atom}link")
    atom_link.set("href", feed_url)
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")

    # Twitter/X social link
    twitter_link = SubElement(channel, "{http://www.w3.org/2005/Atom}link")
    twitter_link.set("href", TWITTER_URL)
    twitter_link.set("rel", "related")
    twitter_link.set("title", "@elizaos on X")

    # GitHub activity feed (external)
    github_link = SubElement(channel, "{http://www.w3.org/2005/Atom}link")
    github_link.set("href", GITHUB_FEED_URL)
    github_link.set("rel", "related")
    github_link.set("title", "GitHub Activity Feed")

    # Channel image (character avatar)
    if image_url:
        image = SubElement(channel, "image")
        SubElement(image, "url").text = image_url
        SubElement(image, "title").text = title
        SubElement(image, "link").text = SITE_URL

    return rss, channel


def prettify_xml(element: Element) -> str:
    """Convert Element to pretty-printed XML string."""
    xml_str = tostring(element, encoding="unicode")
    return minidom.parseString(xml_str).toprettyxml(indent="  ")


def add_stylesheet_reference(xml_str: str, stylesheet: str = "style.xsl") -> str:
    """Insert XSLT stylesheet reference after XML declaration."""
    return xml_str.replace(
        '<?xml version="1.0" ?>',
        f'<?xml version="1.0" ?>\n<?xml-stylesheet type="text/xsl" href="{stylesheet}"?>'
    )


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

        # Add image enclosure if available
        poster_url = None
        images = facts.get("images")
        if isinstance(images, dict):
            poster_url = images.get("overall")
        elif isinstance(images, str):
            poster_url = images
        elif isinstance(images, list) and images:
            poster_url = images[0]

        if poster_url:
            enclosure = SubElement(item, "enclosure")
            enclosure.set("url", poster_url)
            enclosure.set("type", "image/png")
            enclosure.set("length", "0")

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


def create_council_feed(briefings: list[dict], retros: list[dict] = None) -> str:
    """Generate RSS XML from council briefings and retrospectives."""
    feed_url = f"{SITE_URL}/rss/council.xml"
    briefing_base_url = f"{SITE_URL}/the-council/council_briefing"
    retros_base_url = f"{SITE_URL}/the-council/retros"

    rss, channel = create_rss_channel(
        title="elizaOS Council Briefings",
        description="Strategic briefings, retrospectives, and deliberation items for elizaOS leadership",
        feed_url=feed_url
    )

    # Collect all items with sort dates
    all_items = []

    # Add briefings
    for briefing in briefings:
        date_str = briefing.get("date") or briefing.get("_filename", "unknown")
        all_items.append({
            "type": "briefing",
            "data": briefing,
            "sort_date": date_str,
            "base_url": briefing_base_url
        })

    # Add retros
    if retros:
        for retro in retros:
            all_items.append({
                "type": "retro",
                "data": retro,
                "sort_date": retro.get("_sort_date", ""),
                "base_url": retros_base_url
            })

    # Sort all items by date (newest first)
    all_items.sort(key=lambda x: x["sort_date"], reverse=True)

    # Generate RSS items
    for entry in all_items:
        data = entry["data"]
        item = SubElement(channel, "item")

        if entry["type"] == "briefing":
            date_str = data.get("date") or data.get("_filename", "unknown")
            SubElement(item, "title").text = f"Council Briefing: {date_str}"
            SubElement(item, "link").text = f"{entry['base_url']}/{data['_filename']}.json"
            SubElement(item, "guid").text = f"{entry['base_url']}/{data['_filename']}.json"
            SubElement(item, "description").text = format_council_description(data)
            try:
                pub_date = datetime.strptime(date_str, "%Y-%m-%d")
                SubElement(item, "pubDate").text = pub_date.strftime("%a, %d %b %Y 14:00:00 +0000")
            except ValueError:
                pass
        else:  # retro
            SubElement(item, "title").text = format_retro_title(data)
            SubElement(item, "link").text = f"{entry['base_url']}/{data['_filename']}.json"
            SubElement(item, "guid").text = f"{entry['base_url']}/{data['_filename']}.json"
            SubElement(item, "description").text = format_retro_description(data)
            try:
                sort_date = data.get("_sort_date", "")
                pub_date = datetime.strptime(sort_date, "%Y-%m-%d")
                SubElement(item, "pubDate").text = pub_date.strftime("%a, %d %b %Y 16:00:00 +0000")
            except ValueError:
                pass
            # Add category for retros
            category = SubElement(item, "category")
            category.text = data.get("_retro_type", "retrospective")

    return prettify_xml(rss)


# --- Retrospectives (included in Council Feed) ---

def load_retros(limit: int = 10) -> list[dict]:
    """Load retrospective files (monthly retros, quarterly/annual summaries)."""
    retro_files = sorted(RETROS_DIR.glob("*.json"), reverse=True)[:limit]

    items = []
    for f in retro_files:
        # Skip symlinks like latest.json
        if f.is_symlink():
            continue
        try:
            data = json.loads(f.read_text())
            data["_filename"] = f.stem
            data["_retro_type"] = classify_retro(f.stem)
            data["_sort_date"] = extract_retro_date(f.stem)
            items.append(data)
        except Exception as e:
            logging.warning(f"Failed to load retro {f}: {e}")

    return items


def classify_retro(filename: str) -> str:
    """Classify retro type from filename."""
    if "annual" in filename:
        return "annual"
    elif "-Q" in filename:
        return "quarterly"
    elif "-retro" in filename:
        return "monthly"
    return "retro"


def extract_retro_date(filename: str) -> str:
    """Extract a sortable date string from retro filename."""
    # Annual: 2025-annual-summary -> 2025-12-31
    if "annual" in filename:
        match = re.match(r"(\d{4})-annual", filename)
        if match:
            return f"{match.group(1)}-12-31"
    # Quarterly: 2025-Q4-summary -> 2025-12-01
    elif "-Q" in filename:
        match = re.match(r"(\d{4})-Q(\d)", filename)
        if match:
            year, quarter = match.groups()
            month = {"1": "03", "2": "06", "3": "09", "4": "12"}[quarter]
            return f"{year}-{month}-01"
    # Monthly: 2025-12-retro -> 2025-12-01
    elif "-retro" in filename:
        match = re.match(r"(\d{4})-(\d{2})-retro", filename)
        if match:
            return f"{match.group(1)}-{match.group(2)}-01"
    return filename


def format_retro_title(retro: dict) -> str:
    """Format retro title with distinctive prefix."""
    retro_type = retro.get("_retro_type", "retro")

    if retro_type == "annual":
        period = retro.get("period", retro.get("_filename", ""))
        return f"Annual Summary: {period}"
    elif retro_type == "quarterly":
        period = retro.get("period", retro.get("_filename", ""))
        return f"Quarterly Summary: {period}"
    else:  # monthly
        name = retro.get("name", "")
        if name:
            return name  # Already formatted like "Monthly Retro: December 2025"
        return f"Monthly Retro: {retro.get('month_reviewed', retro.get('_filename', ''))}"


def format_retro_description(retro: dict) -> str:
    """Format retrospective into readable HTML description."""
    lines = []
    retro_type = retro.get("_retro_type", "retro")

    # Premise/executive summary
    premise = retro.get("premise") or retro.get("executive_summary", "")
    if premise:
        label = "Executive Summary" if retro_type in ("quarterly", "annual") else "Premise"
        lines.append(f"<p><strong>{label}:</strong> {premise[:500]}{'...' if len(premise) > 500 else ''}</p>")

    # Summary (for monthly)
    summary = retro.get("summary", "")
    if summary and retro_type == "monthly":
        lines.append(f"<p>{summary[:300]}{'...' if len(summary) > 300 else ''}</p>")

    # Key developments/achievements
    key_items = retro.get("key_developments") or retro.get("key_achievements", [])
    if key_items:
        label = "Key Achievements" if retro_type in ("quarterly", "annual") else "Key Developments"
        lines.append(f"<p><strong>{label}:</strong></p><ul>")
        for item in key_items[:5]:
            area = item.get("area") or item.get("theme", "")
            item_summary = item.get("summary", "")[:150]
            lines.append(f"<li><strong>{area}:</strong> {item_summary}...</li>")
        lines.append("</ul>")

    return "\n".join(lines) if lines else "<p>No details available.</p>"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate facts feed
    logging.info("Generating facts RSS feed...")
    facts_items = load_json_files(FACTS_DIR, limit=20)
    if facts_items:
        logging.info(f"Loaded {len(facts_items)} facts files")
        facts_feed = add_stylesheet_reference(create_facts_feed(facts_items))
        (OUTPUT_DIR / "feed.xml").write_text(facts_feed)
        logging.info(f"Facts feed written to {OUTPUT_DIR / 'feed.xml'}")
    else:
        logging.warning("No facts files found")

    # Generate council feed (with retros)
    logging.info("Generating council RSS feed...")
    council_items = load_json_files(COUNCIL_DIR, limit=20)
    retro_items = load_retros(limit=10)
    logging.info(f"Loaded {len(council_items)} council briefings, {len(retro_items)} retrospectives")

    if council_items or retro_items:
        council_feed = add_stylesheet_reference(create_council_feed(council_items, retro_items))
        (OUTPUT_DIR / "council.xml").write_text(council_feed)
        logging.info(f"Council feed written to {OUTPUT_DIR / 'council.xml'}")
    else:
        logging.warning("No council briefing or retro files found")


if __name__ == "__main__":
    main()
