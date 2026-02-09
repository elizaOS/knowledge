#!/usr/bin/env python3
"""
Generate API manifest for the knowledge repo static API.

Scans all data source directories and produces:
  - api/manifest.json  (full registry with metadata, dates, health)
  - api/latest.json    (lightweight quick-access latest dates)

Output is served via GitHub Pages at:
  https://elizaos.github.io/knowledge/api/manifest.json

Usage:
  python scripts/etl/generate-manifest.py
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent
API_DIR = WORKSPACE_ROOT / "api"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# --------------- Data Source Definitions ---------------

DATA_SOURCES = {
    "facts": {
        "directory": "the-council/facts",
        "glob": "2*.json",
        "path_template": "the-council/facts/{date}.json",
        "signal_value": "VERY HIGH",
        "description": "LLM-extracted daily insights with categorization and sentiment",
        "update_frequency": "daily",
        "use_case": "Primary dashboard briefing, key facts display",
    },
    "council_briefing": {
        "directory": "the-council/council_briefing",
        "glob": "2*.json",
        "path_template": "the-council/council_briefing/{date}.json",
        "signal_value": "HIGH",
        "description": "Strategic deliberation briefings with multi-choice questions",
        "update_frequency": "daily",
        "use_case": "Strategic insights, council questions",
    },
    "aggregated": {
        "directory": "the-council/aggregated",
        "glob": "2*.json",
        "path_template": "the-council/aggregated/{date}.json",
        "signal_value": "LOW",
        "description": "Raw combined data from all sources (large files)",
        "update_frequency": "daily",
        "use_case": "Debugging, raw data access (not for dashboards)",
    },
    "github_week": {
        "directory": "github/stats/week",
        "glob": "stats_2*.json",
        "path_template": "github/stats/week/stats_{date}.json",
        "signal_value": "VERY HIGH",
        "description": "Weekly GitHub statistics (most stable for dashboards)",
        "update_frequency": "weekly",
        "use_case": "Primary KPI cards, contributor leaderboards",
    },
    "github_day": {
        "directory": "github/stats/day",
        "glob": "stats_2*.json",
        "path_template": "github/stats/day/stats_{date}.json",
        "signal_value": "MEDIUM",
        "description": "Daily GitHub statistics (may have gaps on weekends)",
        "update_frequency": "daily",
        "use_case": "Activity trend charts, recent activity feeds",
    },
    "github_month": {
        "directory": "github/stats/month",
        "glob": "stats_2*.json",
        "path_template": "github/stats/month/stats_{date}.json",
        "signal_value": "MEDIUM",
        "description": "Monthly GitHub statistics (aggregated rollups)",
        "update_frequency": "monthly",
        "use_case": "Historical trends, month selector",
    },
    "ai_news_json": {
        "directory": "ai-news/elizaos/json",
        "glob": "2*.json",
        "path_template": "ai-news/elizaos/json/{date}.json",
        "signal_value": "HIGH",
        "description": "Multi-source AI news aggregation",
        "update_frequency": "daily",
        "use_case": "News feed widget, media gallery",
    },
    "ai_news_md": {
        "directory": "ai-news/elizaos/md",
        "glob": "2*.md",
        "path_template": "ai-news/elizaos/md/{date}.md",
        "signal_value": "MEDIUM",
        "description": "Markdown-formatted AI news summaries",
        "update_frequency": "daily",
        "use_case": "Human-readable news display",
    },
    "daily_silk": {
        "directory": "daily-silk",
        "glob": "2*.md",
        "path_template": "daily-silk/{date}.md",
        "signal_value": "MEDIUM",
        "description": "Discord AI news collection",
        "update_frequency": "daily",
        "use_case": "Community pulse, Discord highlights",
    },
    "hackmd_facts": {
        "directory": "hackmd/facts",
        "glob": "2*.md",
        "path_template": "hackmd/facts/{date}.md",
        "signal_value": "MEDIUM",
        "description": "HackMD-formatted daily facts",
        "update_frequency": "daily",
        "use_case": "External publishing, backups",
    },
    "help_reports": {
        "directory": "the-council/help-reports",
        "glob": "2*.json",
        "path_template": "the-council/help-reports/{date}.json",
        "signal_value": "HIGH",
        "description": "Monthly community help interaction analysis",
        "update_frequency": "monthly",
        "use_case": "Community health metrics, helper leaderboards",
    },
    "highlights": {
        "directory": "the-council/highlights",
        "glob": "2*.json",
        "path_template": "the-council/highlights/{date}.json",
        "signal_value": "HIGH",
        "description": "Editorial highlights curated from ai-news",
        "update_frequency": "daily",
        "use_case": "Top stories, editorial curation",
    },
    "retros": {
        "directory": "the-council/retros",
        "glob": "*.json",
        "path_template": "the-council/retros/{date}.json",
        "signal_value": "VERY HIGH",
        "description": "Monthly retrospectives and quarterly/annual summaries",
        "update_frequency": "monthly",
        "use_case": "Strategic insights, persistent challenges",
    },
}


def scan_directory(source_key: str, source_def: dict) -> dict:
    """Scan a data source directory and return file metadata."""
    directory = WORKSPACE_ROOT / source_def["directory"]

    if not directory.exists():
        return {"file_count": 0, "size_mb": 0, "latest": None, "dates": []}

    files = sorted(directory.glob(source_def["glob"]))
    total_size = sum(f.stat().st_size for f in files)

    # Extract date strings from filenames
    dates = []
    for f in files:
        if f.is_symlink():
            continue
        stem = f.stem
        # Strip prefix like "stats_" for github sources
        if stem.startswith("stats_"):
            stem = stem[6:]
        dates.append(stem)

    dates.sort(reverse=True)

    return {
        "file_count": len(files),
        "size_mb": round(total_size / (1024 * 1024), 2),
        "latest": dates[0] if dates else None,
        "dates": dates,
    }


def extract_months(dates: list[str]) -> list[str]:
    """Extract unique YYYY-MM months from date strings."""
    months = set()
    for d in dates:
        # Handle YYYY-MM-DD
        if len(d) >= 7 and d[4] == "-":
            months.add(d[:7])
    return sorted(months, reverse=True)


def extract_retro_months(dates: list[str]) -> dict:
    """Classify retro dates into monthly/quarterly/annual."""
    monthly = []
    quarterly = []

    for d in dates:
        if "-retro" in d:
            # 2025-12-retro -> 2025-12
            monthly.append(d.replace("-retro", ""))
        elif "-Q" in d and "-summary" in d:
            # 2025-Q4-summary -> 2025-Q4
            quarterly.append(d.replace("-summary", ""))

    return {
        "retros_monthly": sorted(monthly, reverse=True),
        "retros_quarterly": sorted(quarterly, reverse=True),
    }


def generate_manifest() -> dict:
    """Generate the full API manifest."""
    now = datetime.now(timezone.utc).isoformat()

    manifest = {
        "version": "1.1.0",
        "generated_at": now,
        "latest": {},
        "data_sources": {},
        "data_health": {"last_successful_run": now},
        "available_dates": {},
        "available_months": {},
    }

    for key, source_def in DATA_SOURCES.items():
        logging.info(f"Scanning {key}: {source_def['directory']}")
        scan = scan_directory(key, source_def)

        # Build data_sources entry
        manifest["data_sources"][key] = {
            "path_template": source_def["path_template"],
            "signal_value": source_def["signal_value"],
            "description": source_def["description"],
            "update_frequency": source_def["update_frequency"],
            "use_case": source_def["use_case"],
            "file_count": scan["file_count"],
            "size_mb": scan["size_mb"],
        }

        # Latest dates
        manifest["latest"][key] = scan["latest"]

        # Health counts
        manifest["data_health"][f"{key}_count"] = scan["file_count"]

        # Available dates (only for key sources to keep size reasonable)
        if key in ("facts", "council_briefing", "github_week", "highlights"):
            manifest["available_dates"][key] = scan["dates"]

    # Available months - aggregate from scanned data
    # GitHub months
    github_month_scan = scan_directory("github_month", DATA_SOURCES["github_month"])
    manifest["available_months"]["github_month"] = github_month_scan["dates"]

    # Help reports months
    help_scan = scan_directory("help_reports", DATA_SOURCES["help_reports"])
    manifest["available_months"]["help_reports"] = extract_months(help_scan["dates"])

    # Retro classification
    retro_scan = scan_directory("retros", DATA_SOURCES["retros"])
    retro_months = extract_retro_months(retro_scan["dates"])
    manifest["available_months"]["retros_monthly"] = retro_months["retros_monthly"]
    manifest["available_months"]["retros_quarterly"] = retro_months["retros_quarterly"]

    # GitHub overall months (from daily data)
    github_day_scan = scan_directory("github_day", DATA_SOURCES["github_day"])
    manifest["available_months"]["github"] = extract_months(github_day_scan["dates"])

    return manifest


def generate_latest(manifest: dict) -> dict:
    """Generate lightweight latest.json from manifest."""
    return {
        "version": manifest["version"],
        "generated_at": manifest["generated_at"],
        "latest": manifest["latest"],
    }


def main():
    API_DIR.mkdir(parents=True, exist_ok=True)

    logging.info("Generating API manifest...")
    manifest = generate_manifest()

    manifest_path = API_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    logging.info(f"Wrote {manifest_path} ({manifest_path.stat().st_size} bytes)")

    latest = generate_latest(manifest)
    latest_path = API_DIR / "latest.json"
    latest_path.write_text(json.dumps(latest, indent=2) + "\n")
    logging.info(f"Wrote {latest_path} ({latest_path.stat().st_size} bytes)")

    # Summary
    source_count = len(manifest["data_sources"])
    total_files = sum(s["file_count"] for s in manifest["data_sources"].values())
    total_size = sum(s["size_mb"] for s in manifest["data_sources"].values())
    logging.info(f"Done: {source_count} sources, {total_files} files, {total_size:.1f} MB total")


if __name__ == "__main__":
    main()
