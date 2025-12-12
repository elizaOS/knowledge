#!/usr/bin/env python3
"""
Script to summarize council episodes from the-council/episodes/ directory.
Generates concise summaries optimized for Discord embedding (~1000 chars).
"""

import os
import sys
import json
import requests
import argparse
from pathlib import Path
from datetime import datetime
import logging

# --- Configuration ---
MODEL = "openai/gpt-5.2"
API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_API_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# Directories
SCRIPT_DIR = Path(__file__).parent.resolve()
INTEGRATIONS_DIR = SCRIPT_DIR.parent  # integrations/
SCRIPTS_ROOT = INTEGRATIONS_DIR.parent  # scripts/
WORKSPACE_ROOT = SCRIPTS_ROOT.parent  # repository root
EPISODES_DIR = WORKSPACE_ROOT / "the-council" / "episodes"
OUTPUT_DIR = WORKSPACE_ROOT / "hackmd" / "council-episodes"

# Logging configuration
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def extract_episode_content(episode_data: dict) -> str:
    """Extract text content from episode JSON data."""
    if not isinstance(episode_data, dict):
        return ""
    
    content_parts = []
    
    # Extract title
    title = episode_data.get("title", "")
    if title:
        content_parts.append(f"Title: {title}")
    
    # Extract description/summary
    description = episode_data.get("description", "") or episode_data.get("summary", "")
    if description:
        content_parts.append(f"Description: {description}")
    
    # Extract transcript or content
    transcript = episode_data.get("transcript", "") or episode_data.get("content", "")
    if transcript:
        content_parts.append(f"Content: {transcript}")
    
    # Extract other text fields recursively
    def extract_text_recursive(obj, path=""):
        texts = []
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key not in ["title", "description", "summary", "transcript", "content"]:  # Skip already processed
                    texts.extend(extract_text_recursive(value, f"{path}.{key}" if path else key))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                texts.extend(extract_text_recursive(item, f"{path}[{i}]" if path else f"[{i}]"))
        elif isinstance(obj, str) and obj.strip():
            texts.append(obj.strip())
        return texts
    
    other_texts = extract_text_recursive(episode_data)
    if other_texts:
        content_parts.extend(other_texts)
    
    return "\n\n".join(content_parts)

def construct_episode_summary_prompt(episodes_content: str, date_str: str) -> str:
    """Construct prompt for episode summary generation."""
    prompt = f"""
You are an AI assistant tasked with creating a concise daily summary of council episodes for Discord sharing.

**Instructions:**
- Create a summary of the provided council episodes for {date_str}
- Keep the summary under 1000 characters total (aim for ~800-900 chars)
- Focus on the most important themes, decisions, and insights
- Use bullet points or concise paragraphs
- Include key episode titles if relevant
- Make it engaging and informative for a Discord audience
- Do not include markdown formatting that won't work in Discord (no headers #, but bullets • are fine)

**Council Episodes Content:**
{episodes_content}

**Output only the summary content, nothing else:**
"""
    return prompt

def main():
    parser = argparse.ArgumentParser(
        description="Summarize council episodes for daily briefing"
    )
    parser.add_argument(
        "-d", "--date",
        help="Date to process (YYYY-MM-DD). If not specified, uses today's date."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file path. If not specified, uses hackmd/council-episodes/YYYY-MM-DD.md"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate API key
    if not API_KEY:
        logging.error("Error: OpenRouter API key is required (set OPENROUTER_API_KEY env var).")
        sys.exit(1)
    
    # Determine date
    if args.date:
        try:
            datetime.strptime(args.date, "%Y-%m-%d")
            date_str = args.date
        except ValueError:
            logging.error(f"Error: Invalid date format '{args.date}'. Use YYYY-MM-DD.")
            sys.exit(1)
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    logging.info(f"Processing council episodes for date: {date_str}")
    
    # Check episodes directory
    if not EPISODES_DIR.is_dir():
        logging.error(f"Error: Episodes directory not found at '{EPISODES_DIR}'")
        sys.exit(1)
    
    # Find and process episode files
    episode_files = list(EPISODES_DIR.glob("*.json"))
    if not episode_files:
        logging.warning(f"No episode JSON files found in '{EPISODES_DIR}'")
        
        # Create empty summary
        empty_summary = f"No council episodes found for {date_str}."
        
        # Determine output path
        if args.output:
            output_path = args.output
        else:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            output_path = OUTPUT_DIR / f"{date_str}.md"
        
        # Save empty summary
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(empty_summary)
            logging.info(f"Saved empty summary to: {output_path}")
            print(empty_summary)  # Output for potential use in workflows
        except Exception as e:
            logging.error(f"Error writing output file: {e}")
            sys.exit(1)
        
        sys.exit(0)
    
    logging.info(f"Found {len(episode_files)} episode files")
    
    # Process episode files
    all_episodes_content = []
    
    for episode_file in episode_files:
        logging.debug(f"Processing episode file: {episode_file}")
        
        try:
            with open(episode_file, 'r', encoding='utf-8') as f:
                episode_data = json.load(f)
        except json.JSONDecodeError as e:
            logging.warning(f"Warning: Could not parse JSON from '{episode_file}': {e}")
            continue
        except Exception as e:
            logging.warning(f"Warning: Could not read '{episode_file}': {e}")
            continue
        
        episode_content = extract_episode_content(episode_data)
        if episode_content:
            all_episodes_content.append(f"--- Episode: {episode_file.stem} ---\n{episode_content}")
    
    if not all_episodes_content:
        logging.warning("No content extracted from episode files")
        empty_summary = f"Council episodes found but no content could be extracted for {date_str}."
        
        # Determine output path
        if args.output:
            output_path = args.output
        else:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            output_path = OUTPUT_DIR / f"{date_str}.md"
        
        # Save empty summary
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(empty_summary)
            logging.info(f"Saved empty summary to: {output_path}")
            print(empty_summary)  # Output for potential use in workflows
        except Exception as e:
            logging.error(f"Error writing output file: {e}")
            sys.exit(1)
        
        sys.exit(0)
    
    combined_content = "\n\n".join(all_episodes_content)
    logging.info(f"Extracted content from {len(all_episodes_content)} episodes")
    
    # Generate summary using LLM
    prompt = construct_episode_summary_prompt(combined_content, date_str)
    
    logging.info(f"Calling LLM ({MODEL}) for episode summary...")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/elizaOS/knowledge",
        "X-Title": "Council Episodes Summary Generator"
    }
    
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(OPENROUTER_API_ENDPOINT, headers=headers, json=payload, timeout=180)
        response.raise_for_status()
        response_data = response.json()
        summary = response_data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        
        if not summary:
            raise ValueError("LLM response did not contain expected content.")
        
        logging.info("Episode summary generated successfully")
        
        # Validate summary length
        if len(summary) > 2000:
            logging.warning(f"Summary length ({len(summary)} chars) exceeds 2000 character limit")
        elif len(summary) > 1000:
            logging.info(f"Summary length ({len(summary)} chars) is within 2000 limit but over 1000")
        else:
            logging.info(f"Summary length ({len(summary)} chars) is within optimal range")
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling OpenRouter API: {e}")
        summary = f"Error generating episode summary for {date_str}: API request failed"
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        logging.error(f"Error processing LLM response: {e}")
        summary = f"Error generating episode summary for {date_str}: Invalid LLM response"
    except Exception as e:
        logging.error(f"Unexpected error during summary generation: {e}")
        summary = f"Error generating episode summary for {date_str}: Unexpected error"
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT_DIR / f"{date_str}.md"
    
    # Save summary
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        logging.info(f"Saved episode summary to: {output_path}")
        print(summary)  # Output for potential use in workflows
    except Exception as e:
        logging.error(f"Error writing output file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()