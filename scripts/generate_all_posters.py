#!/usr/bin/env python3
import os
import re
from pathlib import Path
import shutil
import subprocess
import logging

# Setup logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO').upper(), format='%(asctime)s - %(levelname)s - %(message)s')

# --- Helper function to find the latest markdown file (adapted from update-hackmd.py) ---
def get_latest_md_file(markdown_files: list[Path]) -> Path | None:
    if not markdown_files:
        return None
    date_pattern = re.compile(r"^(\\d{4}-\\d{2}-\\d{2})$")
    dated_files = []
    preferred_files_present = {}
    other_md_files = []

    for f in markdown_files:
        logging.debug(f"   Checking file stem for date pattern: '{f.stem}' (Full name: '{f.name}')")
        match = date_pattern.match(f.stem)
        if match:
            dated_files.append(f)
        else:
            if f.name in ["daily.md", "index.md", "README.md"]:
                preferred_files_present[f.name] = f
            else:
                other_md_files.append(f)
    
    if dated_files:
        dated_files.sort(key=lambda p: p.stem, reverse=True)
        latest_dated = dated_files[0]
        logging.info(f"   Found dated files. Using latest by stem: {latest_dated}")
        return latest_dated
    
    for preferred_name in ["daily.md", "index.md", "README.md"]:
        if preferred_name in preferred_files_present:
            found_preferred = preferred_files_present[preferred_name]
            logging.info(f"   No YYYY-MM-DD files found. Using preferred file: {found_preferred}")
            return found_preferred
    
    if other_md_files:
        logging.info(f"   No YYYY-MM-DD or preferred files found. Using most recently modified of remaining files: {other_md_files}")
        return max(other_md_files, key=lambda p: p.stat().st_mtime)
    
    if markdown_files: # Should only be hit if markdown_files had items but none matched above criteria
        logging.warning(f"   No suitable .md files found by prioritization. Fallback to overall most recent if any .md file exists.")
        return max(markdown_files, key=lambda p: p.stat().st_mtime)
    return None

def main():
    # --- Configuration for poster generation ---
    POSTER_OUTPUT_DIR = Path("posters")
    POSTER_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SCRIPT_DIR = Path(__file__).parent.resolve()

    source_map = {
        "ai-news/elizaos/md/": "ainews-elizaos",
        "ai-news/elizaos/dev/md/": "ainews-elizaos-dev",
        "ai-news/elizaos/discord/md/": "ainews-elizaos-discord",
        "github/summaries/day/": "github-summaries-day",
        "github/summaries/week/": "github-summaries-week",
        "github/summaries/month/": "github-summaries-month",
        "daily-silk/": "daily-silk",
        "hackmd/council/": "hackmd-council-briefing",
        "hackmd/facts/": "hackmd-facts-briefing",
        "hackmd/comms/discord-announcement/": "hackmd-comms-discord-announcement",
        "hackmd/comms/elizaos-tweets/": "hackmd-comms-elizaos-tweets",
        "hackmd/comms/user-feedback/": "hackmd-comms-user-feedback",
        "hackmd/comms/weekly-newsletter/": "hackmd-comms-weekly-newsletter",
        "hackmd/dev/developer-update/": "hackmd-dev-developer-update",
        "hackmd/dev/issue-triage/": "hackmd-dev-issue-triage",
        "hackmd/strategy/intel/": "hackmd-strategy-intel",
        "hackmd/strategy/team-development/": "hackmd-strategy-team-development",
    }

    generated_posters_count = 0

    for src_dir_str, out_base_name in source_map.items():
        # Resolve source directory relative to the main repo root (parent of SCRIPT_DIR)
        src_dir = SCRIPT_DIR.parent / src_dir_str
        logging.info(f"Processing directory: {src_dir}")
        if not src_dir.is_dir():
            logging.warning(f"Source directory {src_dir} not found. Skipping.")
            continue

        markdown_files = list(src_dir.glob("*.md"))
        if not markdown_files:
            logging.info(f"No markdown files found in {src_dir}. Skipping.")
            continue

        latest_md_file = get_latest_md_file(markdown_files)

        if latest_md_file:
            logging.info(f"Latest markdown file for {src_dir_str}: {latest_md_file}")
            clean_out_base_name = out_base_name.replace("/", "-")
            
            # Poster based on the content of the latest markdown file
            specific_poster_filename = f"{clean_out_base_name}-content-{latest_md_file.stem}.png"
            output_poster_path = POSTER_OUTPUT_DIR / specific_poster_filename

            # Permalink poster (generic for the source type)
            permalink_poster_filename = f"{clean_out_base_name}.png"
            permalink_poster_path = POSTER_OUTPUT_DIR / permalink_poster_filename
            
            logging.info(f"Generating poster: {output_poster_path}")
            
            # posters.sh expects the output path *without* the .png extension
            output_base_for_script = POSTER_OUTPUT_DIR / Path(output_poster_path).stem

            cmd = [str(SCRIPT_DIR / "posters.sh"), str(latest_md_file), str(output_base_for_script)]
            
            try:
                # In GitHub Actions, an absolute path to posters.sh might be more reliable
                # For local testing, SCRIPT_DIR / "posters.sh" is fine.
                # The workflow sets chmod +x scripts/posters.sh, so ./scripts/posters.sh should work.
                # The python script is in scripts/ so relative path would be ./posters.sh
                cmd = ["./posters.sh", str(latest_md_file), str(output_base_for_script)] 
                # Assuming posters.sh is in the same directory as this script, or adjust path if not.
                # If generate_all_posters.py is in scripts/, and posters.sh is also in scripts/ then: 
                # cmd = [str(SCRIPT_DIR / "posters.sh"), str(latest_md_file), str(output_base_for_script)] is correct.
                # If posters.sh is at root, then: 
                # cmd = [str(SCRIPT_DIR.parent / "posters.sh"), str(latest_md_file), str(output_base_for_script)]
                # Workflow calls scripts/posters.sh so that implies scripts/ is current dir for it.
                # When python scripts/generate_all_posters.py is run from root, SCRIPT_DIR / "posters.sh" is correct.
                actual_poster_script_path = SCRIPT_DIR / "posters.sh"
                cmd = [str(actual_poster_script_path), str(latest_md_file), str(output_base_for_script)]

                subprocess.run(cmd, check=True, capture_output=True, text=True)
                logging.info(f"Successfully generated poster: {output_poster_path}")
                generated_posters_count += 1
                
                if output_poster_path.exists():
                    shutil.copy(output_poster_path, permalink_poster_path)
                    logging.info(f"Created permalink: {permalink_poster_path}")
                else:
                    logging.error(f"Poster {output_poster_path} was not created, cannot make permalink.")
                        
            except subprocess.CalledProcessError as e:
                logging.error(f"Error generating poster for {latest_md_file}:")
                logging.error(f"Command: {' '.join(e.cmd)}") # Use e.cmd for exact command
                logging.error(f"Stdout: {e.stdout}")
                logging.error(f"Stderr: {e.stderr}")
        else:
            logging.info(f"No suitable markdown file found in {src_dir} after filtering. Skipping poster generation.")
    
    if generated_posters_count == 0:
        logging.info("No posters were generated in this run.")
        # For GitHub Actions output
        if os.getenv('GITHUB_ACTIONS') == 'true':
            print(f"::set-output name=posters_generated::false")
    else:
        logging.info(f"Total posters generated/updated (including permalinks): {generated_posters_count}")
        if os.getenv('GITHUB_ACTIONS') == 'true':
            print(f"::set-output name=posters_generated::true")

if __name__ == "__main__":
    main() 