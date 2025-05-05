#!/usr/bin/env python3

import os
import sys
import json
import requests
import argparse
from pathlib import Path
from datetime import datetime

# --- Configuration ---
MODEL = "anthropic/claude-3.7-sonnet"
API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_API_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# Determine the script's directory to find related files
SCRIPT_DIR = Path(__file__).parent.resolve()
STRATEGIC_CONTEXT_FILE = SCRIPT_DIR / "prompts/north-star.txt"

# Monthly Goal (more dynamic, can still use Env Var or default)
MONTHLY_GOAL = os.environ.get(
    "COUNCIL_MONTHLY_GOAL",
    "Current focus: Stabilize and attract new users to auto.fun by showcasing 24/7 agent activity (streaming, trading, shitposting), ship production ready elizaOS v2."
)
# --- End Configuration ---

def format_json_to_markdown(council_data):
    """Formats the council context JSON into a Markdown string."""
    if not isinstance(council_data, dict):
        return "Error: Invalid council data format."

    date_str = council_data.get("date", "Unknown Date")
    title = f"# Council Briefing: {date_str}"
    lines = [title]

    theme = council_data.get("daily_focus_theme")
    if theme:
        lines.append(f"\n## Daily Focus Theme\n\n- {theme}")

    points = council_data.get("key_strategic_points", [])
    if points:
        lines.append("\n## Key Strategic Points for Deliberation")
        for i, point in enumerate(points):
            lines.append(f"\n### {i+1}. {point.get('theme', 'N/A')}")
            lines.append(f"\n**Summary:** {point.get('summary', 'N/A')}")
            context = point.get('related_operational_context')
            if context:
                lines.append("\n**Related Context:**")
                for ctx in context:
                    lines.append(f"- `{ctx}`") # Format context as code
            questions = point.get('potential_council_questions')
            if questions:
                lines.append("\n**Potential Questions:**")
                for q in questions:
                    lines.append(f"- {q}")

    # Include Strategic Context and Monthly Goal for reference
    strat_context = council_data.get("strategic_context_summary")
    if strat_context:
        lines.append(f"\n---\n**Reference: Strategic Context:** {strat_context}")
    monthly_goal = council_data.get("monthly_goal")
    if monthly_goal:
         lines.append(f"\n**Reference: Monthly Goal:** {monthly_goal}")

    return "\n".join(lines)

def extract_content_from_json(data):
    """Recursively extracts 'content' field values from nested JSON."""
    contents = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key == 'content' and isinstance(value, str) and value:
                contents.append(value)
            else:
                contents.extend(extract_content_from_json(value))
    elif isinstance(data, list):
        for item in data:
            contents.extend(extract_content_from_json(item))
    return contents

def construct_prompt(strategic_context, monthly_goal, date_str, aggregated_content):
    """Constructs the prompt for the LLM API call."""
    prompt = f"""
You are the AI Chief of Staff for the elizaOS Agent Council. Your duty is to analyze the latest operational data, evaluate it against our strategic objectives (Mission, Goals), and prepare a concise, structured briefing for the Council's review. Frame this as a high-level performance review and strategic planning input, suitable for a sci-fi council setting (think Star Wars Jedi Council meets strategic boardroom).

**Strategic Context (Mission, Vision, Background - The Force Guiding Us):**
{strategic_context}

**Current Monthly Directive (Goal):**
{monthly_goal}

**Recent Operational Holo-Logs ({date_str}):**
---
{aggregated_content}
---

**Briefing Instructions:**
Based *primarily* on the operational Holo-Logs, but evaluated through the lens of the Strategic Context and Monthly Directive:
1.  Identify the **single, most prominent Daily Focus Theme**. This should be a concise (1 sentence) assessment of the day's most critical strategic event, challenge, or breakthrough related to our mission.
2.  Extract **3-4 Key Strategic Points** for the Council's deliberation. These must represent significant strategic questions, performance highlights/lowlights, emergent risks/opportunities, or philosophical tensions impacting our goals. Avoid mundane operational details; focus on what requires the Council's wisdom.
3.  For each Strategic Point, provide:
    *   `theme`: A short, thematic title for the agenda item (e.g., "Auto.fun Stability vs. Feature Velocity", "Agent Adoption: Hardware Barriers", "Cross-Brand Synergy Assessment").
    *   `summary`: A 1-2 sentence strategic assessment explaining the core issue, achievement, or tension and its relevance to our goals.
    *   `related_operational_context`: (Optional, use sparingly) 1-2 *very brief* citations from the Holo-Logs (e.g., "Discord: User 'starlord' highlighted RAM limits", "GitHub: PR #4390 'scopable knowledge' merged by 'lalalune'") that ground the point. Include usernames where available and relevant.
    *   `potential_council_questions`: 1-2 focused strategic or philosophical questions this point raises for the Council. Frame these to provoke deliberation on direction, priorities, or values (e.g., "Does prioritizing auto.fun stability conflict with our mandate for rapid V2 deployment?", "How can we ensure decentralized agent development isn't gated by hardware accessibility?").

Please format your entire response as a single JSON object matching this structure:
{{
  "date": "{date_str}",
  "strategic_context_summary": "Briefly echo the core North Star/Mission here for reference.", // Example: "Briefing for the Council dedicated to the DAO's mission of achieving AGI via open-source agents and auto.fun."
  "monthly_goal": "{monthly_goal}", // Echo the provided Monthly Goal
  "daily_focus_theme": "(string) Concise 1-sentence strategic assessment of the day's focus.",
  "key_strategic_points": [
    {{
      "theme": "(string) Thematic title for Council agenda item",
      "summary": "(string) 1-2 sentence strategic assessment.",
      "related_operational_context": [
        "(string) Optional: Brief citation with username/source",
        "(string) Optional: Brief citation with username/source"
      ],
      "potential_council_questions": [
        "(string) Focused strategic/philosophical question 1 for Council",
        "(string) Focused strategic/philosophical question 2 for Council"
      ]
    }}
    // ... 3-4 points total
  ]
}}

Ensure the output is **only** the JSON object, with no introductory text or explanations.
"""
    # Need to escape the curly braces intended for the JSON structure example
    prompt = prompt.replace("{{", "{").replace("}}", "}")
    return prompt


def main():
    parser = argparse.ArgumentParser(
        description="Generates structured AI Agent Council context from aggregated daily data."
    )
    parser.add_argument(
        "input_lean_json_file",
        type=Path,
        help="Path to the lean context JSON file (output of generate_context_map.sh)"
    )
    parser.add_argument(
        "output_council_json_file",
        type=Path,
        help="Path to write the final council context JSON file"
    )
    args = parser.parse_args()

    input_path = args.input_lean_json_file
    output_path = args.output_council_json_file
    # --- Add Markdown output path ---
    output_markdown_dir = SCRIPT_DIR.parent / "hackmd" / "council"
    output_markdown_dir.mkdir(parents=True, exist_ok=True)
    # Determine markdown filename from input JSON filename stem (YYYY-MM-DD)
    markdown_filename = input_path.stem + ".md"
    output_markdown_path = output_markdown_dir / markdown_filename

    # --- Validations ---
    if not API_KEY:
        print("Error: OpenRouter API key is required (set OPENROUTER_API_KEY env var).", file=sys.stderr)
        sys.exit(1)

    if not STRATEGIC_CONTEXT_FILE.is_file():
        print(f"Error: Strategic context file not found at '{STRATEGIC_CONTEXT_FILE}'", file=sys.stderr)
        sys.exit(1)

    if not input_path.is_file():
        print(f"Error: Input JSON file not found at '{input_path}'", file=sys.stderr)
        sys.exit(1)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # --- Processing ---
    print(f"Processing lean context file: {input_path}")

    # Read strategic context
    try:
        strategic_context = STRATEGIC_CONTEXT_FILE.read_text()
    except Exception as e:
        print(f"Error reading strategic context file: {e}", file=sys.stderr)
        sys.exit(1)

    # Read and parse input lean JSON
    try:
        with open(input_path, 'r') as f:
            lean_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding input JSON file '{input_path}': {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file '{input_path}': {e}", file=sys.stderr)
        sys.exit(1)

    # Extract content
    content_list = extract_content_from_json(lean_data)
    aggregated_content = "\n\n---\n\n".join(content_list)

    # Extract date from filename
    try:
        # Attempt to parse date from filename
        date_str = datetime.strptime(input_path.stem, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        print(f"Warning: Could not parse date from filename '{input_path.stem}'. Using placeholder.")
        date_str = "unknown-date" # Fallback if parsing fails


    # Handle case with no content found
    if not aggregated_content:
        print("Warning: No content found in the input JSON file. Creating empty output.", file=sys.stderr)
        empty_output_json = {
            "date": date_str,
            # "strategic_context": strategic_context, # Keep original JSON minimal
            "monthly_goal": MONTHLY_GOAL,
            "daily_focus_theme": "No operational data processed.",
            "key_strategic_points": []
        }
        empty_output_md = f"# Council Briefing: {date_str}\n\nNo operational data processed."
        try:
            with open(output_path, 'w') as f:
                json.dump(empty_output_json, f, indent=2)
            # --- Write empty Markdown ---
            with open(output_markdown_path, 'w') as f:
                f.write(empty_output_md)
            print(f"Saved empty council context JSON to: {output_path}")
            print(f"Saved empty council context Markdown to: {output_markdown_path}")
            sys.exit(0)
        except Exception as e:
            print(f"Error writing empty output files: {e}", file=sys.stderr)
            sys.exit(1)


    # Construct the prompt
    prompt = construct_prompt(strategic_context, MONTHLY_GOAL, date_str, aggregated_content)

    # Call the LLM API
    print(f"Sending request to {MODEL} via OpenRouter...")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/elizaOS/knowledge", # Replace with your actual referer if desired
        "X-Title": "AI Council Context Generator" # Replace with your actual title if desired
    }
    payload = {
        "model": MODEL,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(OPENROUTER_API_ENDPOINT, headers=headers, json=payload, timeout=180) # Increased timeout
        response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)
        response_data = response.json()

        council_context_str = response_data.get("choices", [{}])[0].get("message", {}).get("content")

        if not council_context_str:
            raise ValueError("LLM response did not contain expected content structure.")

        # Parse the JSON content from the LLM response
        council_context_json = json.loads(council_context_str)

        # Basic validation
        if not isinstance(council_context_json, dict) or \
           "daily_focus_theme" not in council_context_json or \
           "key_strategic_points" not in council_context_json or \
           "date" not in council_context_json:
             raise ValueError("LLM response JSON is missing required keys.")

        # --- Format to Markdown ---
        council_context_md = format_json_to_markdown(council_context_json)

    except requests.exceptions.RequestException as e:
        print(f"Error calling OpenRouter API: {e}", file=sys.stderr)
        # Optionally save error structure
        error_output_json = {
            "date": date_str, "monthly_goal": MONTHLY_GOAL,
            "daily_focus_theme": f"Error generating context: API Request Failed ({e})",
            "key_strategic_points": []
        }
        error_output_md = f"# Council Briefing: {date_str}\n\nError generating context: API Request Failed ({e})"
        try:
            with open(output_path, 'w') as f: json.dump(error_output_json, f, indent=2)
            # --- Write error Markdown ---
            with open(output_markdown_path, 'w') as f: f.write(error_output_md)
            print(f"Saved error context JSON to: {output_path}")
            print(f"Saved error context Markdown to: {output_markdown_path}")
        except Exception as write_e:
             print(f"Error writing error output files: {write_e}", file=sys.stderr)

        sys.exit(1)
    except (json.JSONDecodeError, ValueError, KeyError, IndexError) as e:
        print(f"Error processing LLM response: {e}", file=sys.stderr)
        print(f"LLM Response Data: {response.text[:500]}...", file=sys.stderr) # Print first 500 chars of response
        # Optionally save error structure
        error_output_json = {
            "date": date_str, "monthly_goal": MONTHLY_GOAL,
            "daily_focus_theme": f"Error generating context: Invalid LLM Response ({e})",
            "key_strategic_points": []
        }
        error_output_md = f"# Council Briefing: {date_str}\n\nError generating context: Invalid LLM Response ({e})"
        try:
            with open(output_path, 'w') as f: json.dump(error_output_json, f, indent=2)
             # --- Write error Markdown ---
            with open(output_markdown_path, 'w') as f: f.write(error_output_md)
            print(f"Saved error context JSON to: {output_path}")
            print(f"Saved error context Markdown to: {output_markdown_path}")
        except Exception as write_e:
             print(f"Error writing error output files: {write_e}", file=sys.stderr)

        sys.exit(1)
    except Exception as e:
         print(f"An unexpected error occurred: {e}", file=sys.stderr)
         sys.exit(1)


    # Save the final JSON and Markdown
    try:
        # Save JSON
        with open(output_path, 'w') as f:
            json.dump(council_context_json, f, indent=2) # Pretty print with indent=2
        print(f"Saved council context JSON to: {output_path}")

        # Save Markdown
        with open(output_markdown_path, 'w') as f:
            f.write(council_context_md)
        print(f"Saved council context Markdown to: {output_markdown_path}")

        print("Council context generated successfully.")

    except Exception as e:
        print(f"Error writing final output files: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 