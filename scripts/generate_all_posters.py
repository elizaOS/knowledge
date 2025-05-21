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
    
    # Regex for YYYY-MM-DD stems
    date_pattern = re.compile(r"^\\d{4}-\\d{2}-\\d{2}$")
    
    dated_files = []
    daily_file = None
    index_file = None
    readme_file = None
    other_md_files = []

    for f in markdown_files:
        stem = f.stem
        name = f.name
        logging.debug(f"   Checking file: '{name}' with stem: '{stem}'")

        if date_pattern.match(stem):
            logging.debug(f"     Matched date pattern: {f}")
            dated_files.append(f)
        elif name == "daily.md":
            daily_file = f
        elif name == "index.md":
            index_file = f
        elif name == "README.md":
            readme_file = f
        else:
            other_md_files.append(f)

    if dated_files:
        dated_files.sort(key=lambda p: p.stem, reverse=True)
        latest_selected = dated_files[0]
        logging.info(f"   Prioritizing dated files. Selected: {latest_selected}")
        return latest_selected
    
    if daily_file:
        logging.info(f"   No dated files. Using preferred: {daily_file}")
        return daily_file
    
    if index_file:
        logging.info(f"   No dated or daily.md. Using preferred: {index_file}")
        return index_file
        
    if readme_file:
        logging.info(f"   No dated, daily.md, or index.md. Using preferred: {readme_file}")
        return readme_file

    if other_md_files:
        logging.info(f"   No dated or specific preferred files found. Using most recently modified from other .md files: {other_md_files}")
        return max(other_md_files, key=lambda p: p.stat().st_mtime)
        
    if markdown_files: 
        logging.warning(f"   No files matched specific criteria. Fallback to most recent in original list: {markdown_files}")
        return max(markdown_files, key=lambda p: p.stat().st_mtime)

    logging.warning("   No markdown files found or list was empty.")
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
            
            specific_poster_filename = f"{clean_out_base_name}-content-{latest_md_file.stem}.png"
            output_poster_path = POSTER_OUTPUT_DIR / specific_poster_filename

            permalink_poster_filename = f"{clean_out_base_name}.png"
            permalink_poster_path = POSTER_OUTPUT_DIR / permalink_poster_filename
            
            logging.info(f"Generating poster: {output_poster_path}")
            
            output_base_for_script = POSTER_OUTPUT_DIR / Path(output_poster_path).stem
            actual_poster_script_path = SCRIPT_DIR / "posters.sh"
            cmd = [str(actual_poster_script_path), str(latest_md_file), str(output_base_for_script)]

            try:
                process = subprocess.run(cmd, check=False, capture_output=True, text=True) # Changed check to False
                if process.returncode == 0:
                    logging.info(f"Successfully generated poster: {output_poster_path}")
                    generated_posters_count += 1
                    if output_poster_path.exists():
                        shutil.copy(output_poster_path, permalink_poster_path)
                        logging.info(f"Created permalink: {permalink_poster_path}")
                    else:
                        # This case implies posters.sh exited 0 but didn't create the file, which is odd.
                        logging.error(f"Poster {output_poster_path} was reported as generated by posters.sh (exit 0) but not found. Cannot make permalink.")
                else:
                    # posters.sh exited with an error
                    logging.error(f"Error generating poster for {latest_md_file} (posters.sh exited {process.returncode}):")
                    logging.error(f"Command: {' '.join(cmd)}")
                    if process.stdout:
                        logging.error(f"Stdout: {process.stdout}")
                    if process.stderr:
                        logging.error(f"Stderr: {process.stderr}")
                        
            except Exception as e: # Catch other exceptions like file not found for posters.sh itself
                logging.error(f"Exception while trying to run posters.sh for {latest_md_file}:")
                logging.error(f"Command: {' '.join(cmd)}")
                logging.error(str(e))
        else:
            logging.info(f"No suitable markdown file found in {src_dir} after filtering. Skipping poster generation.")
    
    if generated_posters_count == 0:
        logging.info("No posters were generated in this run.")
        if os.getenv('GITHUB_ACTIONS') == 'true':
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write("posters_generated=false\n")
    else:
        logging.info(f"Total posters successfully created (specific versions): {generated_posters_count}")
        if os.getenv('GITHUB_ACTIONS') == 'true':
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write("posters_generated=true\n")

if __name__ == "__main__":
    main() 