#!/usr/bin/env python3

import os
import sys
import json
import requests
import argparse
from pathlib import Path
from datetime import datetime

# --- Configuration ---
MODEL = "openai/gpt-5.2"
API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_API_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# Determine the script's directory to find related files
SCRIPT_DIR = Path(__file__).parent.resolve()
SCRIPTS_ROOT = SCRIPT_DIR.parent  # scripts/
WORKSPACE_ROOT = SCRIPTS_ROOT.parent  # repository root
STRATEGIC_CONTEXT_FILE = SCRIPTS_ROOT / "prompts" / "config" / "north-star.txt"

# Default output directory for council JSON if not specified
DEFAULT_COUNCIL_OUTPUT_DIR = WORKSPACE_ROOT / "the-council" / "council_briefing"

# Monthly Goal (more dynamic, can still use Env Var or default)
MONTHLY_GOAL = os.environ.get(
    "COUNCIL_MONTHLY_GOAL",
    "December 2025: Execution excellence—complete token migration with high success rate, launch ElizaOS Cloud, stabilize flagship agents, and build developer trust through reliability and clear documentation."
)
# --- End Configuration ---

def format_json_to_markdown(council_data):
    """Formats the council context JSON (Final V2 schema) into a Markdown string."""
    if not isinstance(council_data, dict):
        return "Error: Invalid council data format."

    date_str = council_data.get("date", "Unknown Date")
    title = f"# Council Briefing: {date_str}"
    lines = [title]

    monthly_gl = council_data.get("monthly_goal")
    if monthly_gl:
        lines.append(f"\n## Monthly Goal\n\n{monthly_gl}")

    daily_fcs = council_data.get("daily_focus")
    if daily_fcs:
        lines.append(f"\n## Daily Focus\n\n- {daily_fcs}")

    key_pts = council_data.get("key_points", [])
    if key_pts:
        lines.append("\n## Key Points for Deliberation")
        for i, point in enumerate(key_pts):
            lines.append(f"\n### {i+1}. Topic: {point.get('topic', 'N/A')}")
            topic_summary = point.get("summary")
            if topic_summary:
                lines.append(f"\n**Summary of Topic:** {topic_summary}")
            
            deliberation_items = point.get("deliberation_items", [])
            if deliberation_items:
                lines.append("\n#### Deliberation Items (Questions):")
                for j, item in enumerate(deliberation_items):
                    lines.append(f"\n**Question {j+1}:** {item.get('text', 'N/A')}")
                    
                    item_context = item.get('context')
                    if item_context:
                        lines.append("\n  **Context:**")
                        for ctx_item in item_context:
                            lines.append(f"  - `{ctx_item}`")
                           
                    answers = item.get('multiple_choice_answers')
                    if answers and isinstance(answers, dict):
                        lines.append("\n  **Multiple Choice Answers:**")
                        sorted_answer_keys = sorted(answers.keys(), key=lambda x: int(x.split('_')[1]) if '_' in x and x.split('_')[1].isdigit() else float('inf'))
                        for ans_idx, ans_key in enumerate(sorted_answer_keys):
                            ans_obj = answers[ans_key]
                            lines.append(f"    {chr(97 + ans_idx)}) {ans_obj.get('text', 'N/A')}")
                            implication = ans_obj.get('implication')
                            if implication:
                                lines.append(f"        *Implication:* {implication}")
            if i < len(key_pts) - 1:
                lines.append("\n---\n")

    return "\n".join(lines)

def extract_all_text_values(data: any, current_path: str = "", excluded_paths: list = None) -> list[tuple[str, str]]:
    """Recursively flattens the input data and extracts all non-empty string values,
       along with their constructed dot-notation path.
       Skips paths if the current_path starts with any of the excluded_paths.
    """
    if excluded_paths is None:
        excluded_paths = []

    for excluded_path in excluded_paths:
        if current_path.startswith(excluded_path):
            return []

    items = []
    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{current_path}.{key}" if current_path else key
            items.extend(extract_all_text_values(value, new_path, excluded_paths))
    elif isinstance(data, list):
        for i, item_val in enumerate(data):
            items.extend(extract_all_text_values(item_val, current_path, excluded_paths))
    elif isinstance(data, str) and data.strip():
        items.append((current_path, data.strip()))
    return items

def construct_prompt(strategic_context, monthly_goal, date_str, aggregated_content):
    """Constructs the prompt for the LLM API call using the final V2 schema."""
    prompt = f"""
You are the AI Chief of Staff for the elizaOS Agent Council. Your duty is to analyze the latest operational data, evaluate it against our strategic objectives (Mission, Goals), and prepare a concise, structured briefing for the Council's review. Frame this as a high-level performance review and strategic planning input, suitable for a sci-fi council setting.

**Overall Meeting Context (Mission, Vision, Background - The Force Guiding Us):**
{strategic_context}

**Current Monthly Directive (Goal):**
{monthly_goal}

**Recent Operational Holo-Logs ({date_str}):**
---
{aggregated_content}
---

**Briefing Instructions (FINAL Schema):**
Based *primarily* on the operational Holo-Logs, but evaluated through the lens of the Meeting Context and Monthly Directive:
1.  Provide a `daily_focus`: A concise (1-sentence) assessment of the day's most critical strategic event, challenge, or breakthrough.
2.  Extract 2-3 `key_points` (major topics) for the Council's deliberation. These must represent significant strategic questions, performance highlights/lowlights, or emergent risks/opportunities.
3.  For each object in the `key_points` array:
    *   `topic`: A short, thematic title for the agenda item (e.g., "V2 Launch Readiness", "Token Utility Strategy").
    *   `summary`: A 1-2 sentence strategic summary of *this specific topic*.
    *   `deliberation_items`: An array of 2-3 specific questions related to this topic.
        *   For each object in the `deliberation_items` array:
            *   `question_id`: A short, sequential ID for this question (e.g., "q1", "q2").
            *   `text`: The focused strategic or philosophical question itself.
            *   `context`: (Optional Array of 1-2 brief strings) *Directly relevant* snippets from the Holo-Logs that ground *this specific question*. Include usernames/sources where available.
            *   `multiple_choice_answers`: A JSON object (not an array). The keys for this object must be strings like "answer_1", "answer_2", "answer_3". You must generate **exactly 3** such answers. The value for each key must be an object containing:
                *   `text`: (string) Plausible answer choice text.
                *   `implication`: (Optional string) A 1-sentence strategic implication of choosing this answer.

Please format your entire response as a single JSON object matching this structure (ensure all strings are valid JSON strings):
{{ // Outermost brace
  "date": "{date_str}",
  "meeting_context": "{strategic_context}", // Echo the provided strategic_context here as the meeting_context
  "monthly_goal": "{monthly_goal}", // Echo the provided Monthly Goal
  "daily_focus": "(string) Concise 1-sentence assessment of the day's focus.",
  "key_points": [
    {{
      "topic": "(string) Thematic title for the agenda item.",
      "summary": "(string) 1-2 sentence summary of this topic.",
      "deliberation_items": [
        {{
          "question_id": "(string) e.g., q1",
          "text": "(string) Focused strategic/philosophical question for Council.",
          "context": [
            "(string) Optional: Brief citation 1 relevant to THIS question."
          ],
          "multiple_choice_answers": {{
            "answer_1": {{
              "text": "(string) Plausible answer choice 1.",
              "implication": "(string) Optional: 1-sentence strategic implication."
            }},
            "answer_2": {{
              "text": "(string) Plausible answer choice 2.",
              "implication": "(string) Optional: 1-sentence strategic implication."
            }},
            "answer_3": {{
              "text": "(string) Plausible answer choice 3.",
              "implication": "(string) Optional: 1-sentence strategic implication."
            }}
            // Exactly 3 answers (answer_1, answer_2, answer_3) to be AI-generated.
          }}
        }}
        // ... 2-3 deliberation_items (questions) per topic
      ]
    }}
    // ... 2-3 key_points (topics) total
  ]
}} // Outermost brace

Ensure the output is **only** the JSON object, with no introductory text or explanations.
"""
    prompt = prompt.replace("{{ // Outermost brace", "{").replace("}} // Outermost brace", "}")
    prompt = prompt.replace("{{", "{").replace("}}", "}") # General fallback for any missed
    return prompt

def main():
    parser = argparse.ArgumentParser(
        description="Generates structured AI Agent Council context (V2 Schema) from aggregated daily data."
    )
    parser.add_argument(
        "input_lean_json_file",
        type=Path,
        help="Path to the lean context JSON file (output of aggregate-sources.py)"
    )
    parser.add_argument(
        "output_council_json_file",
        nargs='?',
        type=Path,
        default=None,
        help="Optional: Path to write the final council context JSON file. Defaults to 'the-council/council_briefing/[input_filename].json'"
    )
    args = parser.parse_args()

    input_path = args.input_lean_json_file
    output_path = args.output_council_json_file

    if output_path is None:
        DEFAULT_COUNCIL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = DEFAULT_COUNCIL_OUTPUT_DIR / (input_path.stem + ".json")
        print(f"Output file not specified. Defaulting to: {output_path}")

    # --- Add Markdown output path ---
    output_markdown_dir = WORKSPACE_ROOT / "hackmd" / "council"
    output_markdown_dir.mkdir(parents=True, exist_ok=True)
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

    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Processing lean context file: {input_path} for V2 output.")

    try:
        strategic_context = STRATEGIC_CONTEXT_FILE.read_text()
    except Exception as e:
        print(f"Error reading strategic context file: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(input_path, 'r') as f:
            lean_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding input JSON file '{input_path}': {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file '{input_path}': {e}", file=sys.stderr)
        sys.exit(1)

    extracted_text_tuples = extract_all_text_values(lean_data) 
    content_list = [text_val for path, text_val in extracted_text_tuples]
    aggregated_content = "\n\n---\n\n".join(content_list)

    try:
        date_str = datetime.strptime(input_path.stem, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        print(f"Warning: Could not parse date from filename '{input_path.stem}'. Using placeholder.")
        date_str = "unknown-date"

    if not aggregated_content:
        print("Warning: No content found in the input JSON file. Creating empty V2 output.", file=sys.stderr)
        empty_output_json = {
            "date": date_str,
            "strategic_context_summary": "N/A - No operational data processed.",
            "monthly_goal": MONTHLY_GOAL,
            "daily_focus_theme": "No operational data processed.",
            "key_strategic_points": []
        }
        empty_output_md = f"# Council Briefing (V2): {date_str}\n\nNo operational data processed."
        try:
            with open(output_path, 'w') as f:
                json.dump(empty_output_json, f, indent=2)
            with open(output_markdown_path, 'w') as f:
                f.write(empty_output_md)
            print(f"Saved empty V2 council context JSON to: {output_path}")
            print(f"Saved empty V2 council context Markdown to: {output_markdown_path}")
            sys.exit(0)
        except Exception as e:
            print(f"Error writing empty V2 output files: {e}", file=sys.stderr)
            sys.exit(1)

    prompt = construct_prompt(strategic_context, MONTHLY_GOAL, date_str, aggregated_content)

    print(f"Sending V2 request to {MODEL} via OpenRouter...")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/elizaOS/knowledge", 
        "X-Title": "AI Council Context Generator V2"
    }
    payload = {
        "model": MODEL,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "user", "content": prompt}]
    }

    council_context_json = None
    council_context_md = None
    error_output_json = None
    error_output_md = None

    # Metadata for observability
    council_metadata = {
        "model": MODEL,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
    generation_start_time = datetime.utcnow()

    try:
        response = requests.post(OPENROUTER_API_ENDPOINT, headers=headers, json=payload, timeout=180)
        response.raise_for_status()
        response_data = response.json()

        # Capture token usage
        usage = response_data.get("usage", {})
        if usage:
            council_metadata["prompt_tokens"] = usage.get("prompt_tokens")
            council_metadata["completion_tokens"] = usage.get("completion_tokens")
            council_metadata["total_tokens"] = usage.get("total_tokens")
            print(f"LLM Usage - Prompt: {usage.get('prompt_tokens')}, Completion: {usage.get('completion_tokens')}, Total: {usage.get('total_tokens')}")

        council_context_str = response_data.get("choices", [{}])[0].get("message", {}).get("content")

        if not council_context_str:
            raise ValueError("LLM response did not contain expected content structure.")

        council_context_json = json.loads(council_context_str)

        # FINAL Schema Validation
        if not isinstance(council_context_json, dict) or \
           "date" not in council_context_json or \
           "meeting_context" not in council_context_json or \
           "monthly_goal" not in council_context_json or \
           "daily_focus" not in council_context_json or \
           "key_points" not in council_context_json or \
           not isinstance(council_context_json["key_points"], list):
            raise ValueError("LLM response JSON is missing top-level V2 keys or key_points is not a list.")

        for point in council_context_json["key_points"]:
            if not isinstance(point, dict) or \
               "topic" not in point or \
               "summary" not in point or \
               "deliberation_items" not in point or \
               not isinstance(point["deliberation_items"], list):
                raise ValueError("A key_point is missing keys (topic, summary, deliberation_items) or deliberation_items is not a list.")
            
            for item_val_loop in point["deliberation_items"]:
                if not isinstance(item_val_loop, dict) or \
                   "question_id" not in item_val_loop or \
                   "text" not in item_val_loop or \
                   "multiple_choice_answers" not in item_val_loop or \
                   not isinstance(item_val_loop["multiple_choice_answers"], dict): # Check if it's a dictionary
                    if "context" in item_val_loop and not isinstance(item_val_loop["context"], list):
                        raise ValueError("A deliberation_item has an invalid context (must be a list if present).")
                    raise ValueError("A deliberation_item is missing keys (question_id, text, multiple_choice_answers) or multiple_choice_answers is not a dict.")
                
                for answer_key, answer_obj in item_val_loop["multiple_choice_answers"].items():
                    if not isinstance(answer_obj, dict) or \
                       "text" not in answer_obj: # 'implication' is optional
                        raise ValueError(f"A multiple_choice_answer ('{answer_key}') is missing 'text'.")
                    if "implication" in answer_obj and not isinstance(answer_obj["implication"], str):
                         raise ValueError(f"A multiple_choice_answer ('{answer_key}') has an invalid 'implication' (must be a string if present).")

        # Programmatically add the "Other" option to multiple_choice_answers
        for point in council_context_json["key_points"]:
            for item_val_loop in point["deliberation_items"]:
                if "multiple_choice_answers" in item_val_loop and isinstance(item_val_loop["multiple_choice_answers"], dict):
                    item_val_loop["multiple_choice_answers"]["answer_4"] = {
                        "text": "Other / More discussion needed / None of the above.",
                        "implication": None # Explicitly set no implication for "Other"
                    }

        council_context_md = format_json_to_markdown(council_context_json)
        print("V2 Council context generated successfully by LLM and 'Other' (answer_4) option added.")

        # Add success metadata with deliberation stats
        council_metadata["status"] = "success"
        council_metadata["processing_seconds"] = round((datetime.utcnow() - generation_start_time).total_seconds(), 2)
        council_metadata["key_points_count"] = len(council_context_json.get("key_points", []))
        total_questions = sum(
            len(point.get("deliberation_items", []))
            for point in council_context_json.get("key_points", [])
        )
        council_metadata["total_deliberation_questions"] = total_questions
        council_context_json["_metadata"] = council_metadata

    except requests.exceptions.RequestException as e:
        print(f"Error calling OpenRouter API for V2: {e}", file=sys.stderr)
        council_metadata["status"] = "error"
        council_metadata["error"] = f"API Request Failed: {e}"
        council_metadata["processing_seconds"] = round((datetime.utcnow() - generation_start_time).total_seconds(), 2)
        error_output_json = {"date": date_str, "monthly_goal": MONTHLY_GOAL, "daily_focus_theme": f"Error V2: API Request Failed ({e})", "key_strategic_points": [], "_metadata": council_metadata}
        error_output_md = f"# Council Briefing (V2): {date_str}\n\nError: API Request Failed ({e})"
    except (json.JSONDecodeError, ValueError, KeyError, IndexError) as e:
        print(f"Error processing LLM response for V2: {e}", file=sys.stderr)
        if 'response' in locals() and response is not None:
             print(f"LLM Response Data (V2): {response.text[:500]}...", file=sys.stderr)
        council_metadata["status"] = "error"
        council_metadata["error"] = f"Invalid LLM Response: {e}"
        council_metadata["processing_seconds"] = round((datetime.utcnow() - generation_start_time).total_seconds(), 2)
        error_output_json = {"date": date_str, "monthly_goal": MONTHLY_GOAL, "daily_focus_theme": f"Error V2: Invalid LLM Response ({e})", "key_strategic_points": [], "_metadata": council_metadata}
        error_output_md = f"# Council Briefing (V2): {date_str}\n\nError: Invalid LLM Response ({e})"
    except Exception as e:
         print(f"An unexpected error occurred during V2 generation: {e}", file=sys.stderr)
         council_metadata["status"] = "error"
         council_metadata["error"] = f"Unexpected error: {e}"
         council_metadata["processing_seconds"] = round((datetime.utcnow() - generation_start_time).total_seconds(), 2)
         error_output_json = {"date": date_str, "monthly_goal": MONTHLY_GOAL, "daily_focus_theme": f"Error V2: Unexpected error ({e})", "key_strategic_points": [], "_metadata": council_metadata}
         error_output_md = f"# Council Briefing (V2): {date_str}\n\nError: Unexpected error ({e})"
    finally:
        final_json_to_save = council_context_json if council_context_json else error_output_json
        final_md_to_save = council_context_md if council_context_md else error_output_md
        
        if final_json_to_save is None:
            print("Critical error: No JSON data (success or error) to save.", file=sys.stderr)
            sys.exit(1)
        if final_md_to_save is None:
            print("Critical error: No Markdown data (success or error) to save.", file=sys.stderr)
            if final_json_to_save:
                 try:
                    with open(output_path, 'w') as f_json:
                        json.dump(final_json_to_save, f_json, indent=2)
                    print(f"Saved V2 council context JSON (despite MD error) to: {output_path}")
                 except Exception as e_json_write:
                    print(f"Error writing final V2 JSON output file during MD error: {e_json_write}", file=sys.stderr)
            sys.exit(1)

        try:
            with open(output_path, 'w') as f:
                json.dump(final_json_to_save, f, indent=2)
            print(f"Saved V2 council context JSON to: {output_path}")

            with open(output_markdown_path, 'w') as f:
                f.write(final_md_to_save)
            print(f"Saved V2 council context Markdown to: {output_markdown_path}")

            if not council_context_json:
                 print("Exiting with error code due to V2 context generation failure.")
                 sys.exit(1)

        except Exception as e:
            print(f"Error writing final V2 output files: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
