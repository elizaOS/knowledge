#!/usr/bin/env python3
import json
import sys
import os
import argparse
import discord
from discord import Embed
from datetime import datetime
import requests # Added for OpenRouter API calls
import asyncio 

# ANSI escape codes for console colors
class LogColors:
    HEADER = '\033[95m'    # Bright Magenta
    SECTION = '\033[94m'   # Bright Blue
    LLM_CALL = '\033[93m'  # Bright Yellow
    SUCCESS = '\033[92m'   # Bright Green
    WARNING = '\033[93m'   # Bright Yellow (same as LLM_CALL for simplicity or use \033[91m for red)
    FAIL = '\033[91m'      # Bright Red
    ENDC = '\033[0m'       # Reset to default
    DIM = '\033[2m'        # Dim text

# General Colors (used for fallback or main embed)
GENERAL_COLORS = [0x2026ad, 0xe67e22, 0x9b59b6, 0x2ecc71, 0x1abc9c, 0xf1c40f] # Blue, Orange, Purple, Green, Teal, Yellow

# Section Specific Colors
SECTION_COLORS = {
    "twitter": 0x1DA1F2,    # Twitter Blue
    "github": 0x95a5a6,     # Light Grey
    "discord": 0x5865F2,    # Discord Purple/Blurple
    "strategy": 0xe67e22,   # Orange
    "market": 0x2ecc71,     # Green
    "default": GENERAL_COLORS[0] # Default Blue for main/other
}

# Discord webhook colors (matching webhook.js)
COLORS = [0x2026ad, 0xe67e22, 0x9b59b6, 0x2ecc71, 0x1abc9c, 0xf1c40f] # Blue, Orange, Purple, Green, Teal, Yellow

# OpenRouter Configuration
OPENROUTER_API_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_SUMMARY_MODEL = "google/gemini-2.5-flash-preview"
DEFAULT_MAX_TEXT_SUMMARY_LENGTH = 1800 # For plain text output
DEFAULT_MAX_EMBED_SUMMARY_LENGTH = 2000 # Max length for Discord embed description (Discord limit is 4096, but 2000 is a good target)
CHARACTER_LIMIT_PER_FIELD = 1000 # Approx limit for fields if we were to use them

# Base URL for posters on GitHub Pages
POSTER_BASE_URL = "https://elizaos.github.io/knowledge/posters/"

HACKMD_BOOK_URL = "https://hackmd.io/@elizaos/book" # Centralized HackMD book URL
DEFAULT_POSTER_FILENAME = "hackmd-facts-briefing.png" # Default poster

# Define a budget for how much text we want from each summarized section (approx)
# This helps ensure multiple sections can fit.
SECTION_SUMMARIZATION_TARGET_LENGTH = 550 # Target for LLM summary (if LLM is called), was 450

# Constants for dynamic summarization trigger logic
MIN_CHARS_FOR_LLM_CONSIDERATION = 250       # Min raw chars in a section to even consider using LLM for it.
# LLM_WORTHWHILE_REDUCTION_THRESHOLD = 150    # REMOVED
# TARGET_DISPLAY_LENGTH_WITHOUT_LLM = 450     # REMOVED

TOTAL_BUDGET_FOR_ALL_SECTIONS = 1600 # Target total characters for all section descriptions combined
MAX_CHARS_PER_SECTION_ESTIMATE = 600 # A soft cap for any single section's dynamic target budget
                                     # to prevent one very large section from hogging all budget initially.

def should_use_bullets_for_section(section_key: str, raw_length: int, items_count: int) -> bool:
    """
    Determine if a section should use bullet points based on:
    - Section type (some sections benefit more from bullets)
    - Content length (longer content benefits from bullets)
    - Number of items (multiple items benefit from bullets)
    """
    # Always use bullets for sections with multiple distinct items
    if items_count > 3:
        return True
    
    # Use bullets for longer content in specific sections
    if section_key in ["discord", "twitter", "github"] and raw_length > 800:
        return True
    
    # Use bullets for very long content regardless of section
    if raw_length > 1200:
        return True
    
    return False

def safe_truncate(text: str, max_len: int) -> str:
    """
    Truncate text at logical breakpoints (sentences, bullets) rather than mid-sentence.
    """
    if len(text) <= max_len:
        return text
    
    truncated = text[:max_len]
    
    # Try to cut at last logical breakpoint before max_len
    # Order matters: prefer cutting at bullets/newlines, then sentences
    for separator in ['\n• ', '\n- ', '. ', '.\n', '\n']:
        idx = truncated.rfind(separator)
        if idx > 0 and idx > max_len - 150:  # Don't cut too much content
            return truncated[:idx + len(separator)].rstrip() + "..."
    
    # Fallback: cut at last word boundary
    last_space = truncated.rfind(' ')
    if last_space > max_len - 50:
        return truncated[:last_space].rstrip() + "..."
    
    # Ultimate fallback: hard truncate
    return truncated.rstrip() + "..."

def summarize_text_openrouter(text_to_summarize: str, api_key: str, model: str, target_max_length: int, use_bullets: bool = False) -> str:
    if not api_key:
        print(f"{LogColors.WARNING}Warning: OPENROUTER_API_KEY not provided. Skipping summarization.{LogColors.ENDC}")
        return text_to_summarize
    if not text_to_summarize.strip():
        print(f"{LogColors.WARNING}Warning: Empty text provided for summarization. Skipping.{LogColors.ENDC}")
        return ""
    if len(text_to_summarize) <= target_max_length:
        # print(f"Text length ({len(text_to_summarize)}) is already within target ({target_max_length}). Skipping summarization by LLM.")
        return text_to_summarize
    
    if use_bullets:
        prompt_template = (
            f"Summarize the following text using bullet points for a Discord embed. "
            f"Fit within {target_max_length} characters (aim for {int(target_max_length * 0.85)} to {target_max_length}). "
            f"Start each main point with a bullet (•). Be clear and preserve key details. "
            f"Use the available space effectively. Output only the summary.\n\n"
            f"TEXT TO SUMMARIZE:\n\"\"\"\n{text_to_summarize}\n\"\"\"\n\nSUMMARY:"
        )
    else:
        prompt_template = (
            f"Please summarize the following text to approximately {target_max_length} characters. "
            f"Aim for {int(target_max_length * 0.85)} to {target_max_length} characters. "
            f"The summary is for a Discord embed. Maintain clarity and key information. "
            f"Do not be overly concise - use the available space to preserve important details. "
            f"Output only the summary.\n\n"
            f"TEXT TO SUMMARIZE:\n\"\"\"\n{text_to_summarize}\n\"\"\"\n\nSUMMARY:"
        )
    # Calculate max_tokens for the completion. Approx 3.0 chars per token.
    # Ensure a minimum reasonable number of tokens if target_max_length is very small.
    completion_max_tokens = max(100, int(target_max_length / 3.0)) 

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/elizaOS/knowledge", 
        "X-Title": "Webhook Summarizer" 
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt_template}],
        "max_tokens": completion_max_tokens 
    }
    print(f"{LogColors.LLM_CALL}Calling LLM: Input {len(text_to_summarize)} chars, Target ~{target_max_length} chars, max_tokens={completion_max_tokens} for {model}...{LogColors.ENDC}")
    try:
        response = requests.post(OPENROUTER_API_ENDPOINT, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        llm_response_data = response.json()
        summary = llm_response_data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        # Defensively replace literal '\n' from LLM output with actual newlines
        summary = summary.replace('\\n', '\n')

        if summary:
            print(f"{LogColors.SUCCESS}LLM Summary successful. Original length: {len(text_to_summarize)}, Summary length: {len(summary)}{LogColors.ENDC}")
            if len(summary) > target_max_length:
                print(f"{LogColors.WARNING}Warning: LLM summary ({len(summary)}) exceeded target ({target_max_length}). Truncating in script.{LogColors.ENDC}")
                return safe_truncate(summary, target_max_length)
            return summary
        else:
            print(f"{LogColors.WARNING}Warning: Summarization returned empty content. Using original text (truncated if needed).{LogColors.ENDC}")
            return text_to_summarize[:target_max_length-4] + "..." if len(text_to_summarize) > target_max_length else text_to_summarize
    except requests.exceptions.RequestException as e_req:
        print(f"{LogColors.FAIL}Warning: OpenRouter API request failed: {e_req}. Using original text (truncated if needed).{LogColors.ENDC}")
        return text_to_summarize[:target_max_length-4] + "..." if len(text_to_summarize) > target_max_length else text_to_summarize
    except Exception as e_gen:
        print(f"{LogColors.FAIL}Warning: Error processing OpenRouter response: {e_gen}. Using original text (truncated if needed).{LogColors.ENDC}")
        return text_to_summarize[:target_max_length-4] + "..." if len(text_to_summarize) > target_max_length else text_to_summarize

async def send_discord_webhook(channel, json_file, summarize_flag, summary_model, openrouter_api_key, max_embed_len, poster_filename_arg):
    try:
        with open(json_file, 'r') as f:
            briefing_data = json.load(f)
    except Exception as e:
        print(f"{LogColors.FAIL}Error reading or parsing JSON file {json_file}: {e}{LogColors.ENDC}")
        await channel.send(f"Error: Could not load briefing data from {os.path.basename(json_file)}.")
        return

    fact_poster_date = briefing_data.get('briefing_date')
    if not fact_poster_date:
        print(f"{LogColors.FAIL}Error: briefing_date not found in facts JSON.{LogColors.ENDC}")
        await channel.send('Error: briefing_date missing from fact briefing data.')
        return
    
    main_poster_url = f"{POSTER_BASE_URL}{poster_filename_arg}"
    hackmd_link_text = "View the full report in the HackMD Book"
    
    # Embed 1: Main Overview & Links
    overall_summary_text = briefing_data.get('overall_summary', "No overall summary available.")
    main_embed_description = ""

    if summarize_flag and openrouter_api_key:
        objective_summary_prompt = (
            f"Rewrite the following summary objectively, focusing on key metrics and factual observations from the ElizaOS project, suitable for a daily briefing. "
            f"Avoid subjective phrases. Aim for conciseness, around {SECTION_SUMMARIZATION_TARGET_LENGTH // 2} characters.\n\n"
            f"ORIGINAL SUMMARY:\n\"\"\"\n{overall_summary_text}\n\"\"\"\n\nOBJECTIVE REWRITE:"
        )
        rewritten_summary = summarize_text_openrouter(objective_summary_prompt, openrouter_api_key, summary_model, SECTION_SUMMARIZATION_TARGET_LENGTH // 2)
        main_embed_description = rewritten_summary if rewritten_summary.strip() else "Key observations: " + overall_summary_text
    else:
        main_embed_description = "Key observations: " + overall_summary_text

    # Add links to the main embed description
    main_embed_description += f"\n\n📚 [{hackmd_link_text}]({HACKMD_BOOK_URL})"

    if len(main_embed_description) > max_embed_len:
        print(f"{LogColors.WARNING}Warning: Main embed description ({len(main_embed_description)}) too long. Truncating.{LogColors.ENDC}")
        # Prioritize keeping links if possible
        links_len = len(f"\n\n📚 [{hackmd_link_text}]({HACKMD_BOOK_URL})")
        main_embed_description = main_embed_description[:max_embed_len - links_len - 4] + "..." + main_embed_description[-(links_len):]
        if len(main_embed_description) > max_embed_len: # If still too long, hard truncate
             main_embed_description = main_embed_description[:max_embed_len-4] + "..."

    main_embed = Embed(
        title=f"📊 Eliza Daily – {fact_poster_date}", # Changed title here too
        description=main_embed_description.strip(),
        color=SECTION_COLORS.get("default", GENERAL_COLORS[0]),
        timestamp=datetime.utcnow()
    )
    main_embed.set_author(name="Eliza Daily", url=HACKMD_BOOK_URL)
    main_embed.set_thumbnail(url="https://m3-org.github.io/avatars/eliza/thumb-bust_eliza.png")

    embeds_to_send = [main_embed] # Initialize with the main embed

    # --- Helper to create section embeds (must be defined before use) --- 
    def create_section_embed(section_key: str, title_prefix: str, items_data: list, 
                             item_text_extractor, item_prefix_extractor=None,
                             current_section_dynamic_budget: int = MAX_CHARS_PER_SECTION_ESTIMATE, # New dynamic budget param
                             summarize_flag: bool = False, openrouter_api_key: str | None = None, 
                             summary_model: str = DEFAULT_SUMMARY_MODEL, max_embed_len: int = DEFAULT_MAX_EMBED_SUMMARY_LENGTH) -> tuple[Embed | None, int]:
        
        actual_chars_used = 0
        if not items_data:
            print(f"{LogColors.DIM}Section '{title_prefix}': No items provided.{LogColors.ENDC}")
            return None, actual_chars_used

        raw_item_texts = []
        for item in items_data:
            text = item_text_extractor(item)
            prefix = item_prefix_extractor(item) if item_prefix_extractor else None
            raw_item_texts.append(f"{prefix}: {text}" if prefix else text)
        
        if not raw_item_texts:
            print(f"{LogColors.DIM}Section '{title_prefix}': No raw item texts generated.{LogColors.ENDC}")
            return None, actual_chars_used

        compiled_items_text = "\n".join(raw_item_texts)
        display_text = compiled_items_text
        len_compiled = len(compiled_items_text)
        log_prefix = f"{LogColors.SECTION}Section '{title_prefix}':{LogColors.ENDC}"

        print(f"{log_prefix} Initial compiled length: {LogColors.DIM}{len_compiled}{LogColors.ENDC} chars. Dynamic budget for this section: {LogColors.DIM}{current_section_dynamic_budget}{LogColors.ENDC} chars.")

        should_try_llm = False
        if summarize_flag and openrouter_api_key and len_compiled > MIN_CHARS_FOR_LLM_CONSIDERATION:
            # Try LLM if compiled text is over its dynamically allocated budget for this section
            if len_compiled > current_section_dynamic_budget:
                should_try_llm = True
                print(f"{log_prefix} Text length ({len_compiled}) > dynamic budget ({current_section_dynamic_budget}). Flagging for LLM.")
        
        if should_try_llm:
            # LLM target is now the section's dynamic budget, ensuring it's not excessively small.
            # SECTION_SUMMARIZATION_TARGET_LENGTH is not directly used here for LLM target anymore.
            llm_actual_target = max(MIN_CHARS_FOR_LLM_CONSIDERATION, current_section_dynamic_budget) 
            # We also need to respect a practical upper limit for what we ask the LLM in one go, even if dynamic budget is huge.
            # MAX_CHARS_PER_SECTION_ESTIMATE could serve this purpose, or a new constant.
            # Let's use SECTION_SUMMARIZATION_TARGET_LENGTH as that practical upper bound for an LLM request for now.
            # llm_actual_target = min(llm_actual_target, SECTION_SUMMARIZATION_TARGET_LENGTH) 
            # Instead, use 90% of the dynamic budget to encourage fuller summaries
            llm_actual_target = min(llm_actual_target, int(current_section_dynamic_budget * 0.9))
            # But still cap at a reasonable maximum to prevent excessive API costs
            if llm_actual_target > 800:
                llm_actual_target = 800

            # Determine if this section should use bullet points
            use_bullets = should_use_bullets_for_section(section_key, len_compiled, len(items_data))
            bullet_indicator = " (bullets)" if use_bullets else ""
            
            print(f"{log_prefix} Attempting LLM summarization to ~{LogColors.DIM}{llm_actual_target}{LogColors.ENDC} chars{bullet_indicator}.")
            section_summary = summarize_text_openrouter(compiled_items_text, openrouter_api_key, summary_model, llm_actual_target, use_bullets)
            if section_summary.strip() and len(section_summary) < len_compiled: 
                display_text = section_summary
                print(f"{log_prefix} {LogColors.SUCCESS}Used LLM summary. New length: {len(display_text)} chars.{LogColors.ENDC}")
            else:
                reason = "empty" if not section_summary.strip() else "not shorter/effective"
                print(f"{log_prefix} {LogColors.WARNING}LLM summary was {reason}. Using original (potentially truncated).{LogColors.ENDC}")
        else: 
            print(f"{log_prefix} {LogColors.DIM}Not attempting LLM (compiled len: {len_compiled}, min_consider: {MIN_CHARS_FOR_LLM_CONSIDERATION}, or within dynamic budget).{LogColors.ENDC}")
        
        # Truncate display_text to its dynamically calculated budget if it's longer
        if len(display_text) > current_section_dynamic_budget:
            print(f"{log_prefix} {LogColors.WARNING}Current display text (length {len(display_text)}) exceeds dynamic budget ({current_section_dynamic_budget}). Truncating.{LogColors.ENDC}")
            display_text = safe_truncate(display_text, current_section_dynamic_budget)
        
        # Final hard truncation to absolute per-embed description limit
        if len(display_text) > max_embed_len: 
            print(f"{log_prefix} {LogColors.WARNING}Display text (length {len(display_text)}) exceeds absolute embed limit ({max_embed_len}). Hard Truncating.{LogColors.ENDC}")
            display_text = safe_truncate(display_text, max_embed_len)
        
        final_text_for_embed = display_text.strip()
        actual_chars_used = len(final_text_for_embed)

        if not final_text_for_embed: 
            print(f"{log_prefix} {LogColors.WARNING}Display text is empty after processing. Skipping embed.{LogColors.ENDC}")
            return None, 0 # Return 0 chars used

        section_embed = Embed(
            title=title_prefix,
            description=final_text_for_embed,
            color=SECTION_COLORS.get(section_key, SECTION_COLORS["default"])
        )
        return section_embed, actual_chars_used

    # --- Section Processing with Iterative Rollover Budget & Decoupled Order --- 
    categories_data = briefing_data.get('categories', {})
    # Define sections in their DESIRED OUTPUT ORDER
    section_definitions_ordered = [
        {"key": "twitter", "title": "🐦 Twitter Buzz", "items": categories_data.get('twitter_news_highlights', []), "text_extractor": lambda item: item.get('claim', 'N/A'), "prefix_extractor": None, "embed_placeholder": None, "original_order_index": 0},
        {"key": "github", "title": "⚙️ GitHub Beat", "items": categories_data.get('github_updates', {}).get('overall_focus', []), "text_extractor": lambda item: item.get('claim', 'N/A'), "prefix_extractor": None, "embed_placeholder": None, "original_order_index": 1},
        {"key": "discord", "title": "💬 Discord Updates", "items": categories_data.get('discord_updates', []), "text_extractor": lambda item: f"{item.get('summary', 'N/A')} (Participants: {', '.join(item.get('key_participants', [])) if item.get('key_participants') else 'N/A'})", "prefix_extractor": lambda item: item.get('channel', ''), "embed_placeholder": None, "original_order_index": 2},
        {"key": "strategy", "title": "🚀 Strategic Insights", "items": categories_data.get('strategic_insights', []), "text_extractor": lambda item: item.get('insight', 'N/A'), "prefix_extractor": lambda item: item.get('theme', 'Insight'), "embed_placeholder": None, "original_order_index": 3},
        {"key": "market", "title": "📈 (WIP) Market Analysis", "items": categories_data.get('market_analysis', []), "text_extractor": lambda item: item.get('observation', 'N/A'), "prefix_extractor": None, "embed_placeholder": None, "original_order_index": 4}
    ]

    # Calculate initial raw lengths and populate for processing, keeping original definition
    sections_to_calculate_len = []
    total_initial_raw_chars = 0
    for i, sec_def in enumerate(section_definitions_ordered):
        current_raw_len = 0
        if sec_def["items"]:
            raw_item_texts = []
            for item in sec_def["items"]:
                text = sec_def["text_extractor"](item)
                prefix = sec_def["prefix_extractor"](item) if sec_def["prefix_extractor"] else None
                raw_item_texts.append(f"{prefix}: {text}" if prefix else text)
            compiled_text_for_len_calc = "\n".join(raw_item_texts)
            current_raw_len = len(compiled_text_for_len_calc)
        
        sections_to_calculate_len.append({**sec_def, 'raw_length': current_raw_len, 'original_index_for_ordering': i}) # Use actual index for later re-sorting if needed
        total_initial_raw_chars += current_raw_len
    
    # Sort sections by their raw_length for PROCESSING ORDER
    # sections_for_processing_sorted = sorted(sections_to_calculate_len, key=lambda x: x['raw_length'])
    # Keep a mutable list that we will sort for processing, but results will be stored based on original_order_index
    processing_order_list = sorted(sections_to_calculate_len, key=lambda x: x['raw_length'])
    
    # This list will store results in the original definition order
    results_in_original_order = [None] * len(section_definitions_ordered)

    print(f"{LogColors.DIM}Iterative Budget: Total initial raw chars for sections: {total_initial_raw_chars}. Overall budget: {TOTAL_BUDGET_FOR_ALL_SECTIONS}{LogColors.ENDC}")
    print(f"{LogColors.DIM}Processing order (shortest to longest raw content): {[s['title'] for s in processing_order_list]}{LogColors.ENDC}")

    remaining_budget_for_sections = TOTAL_BUDGET_FOR_ALL_SECTIONS
    sum_of_remaining_raw_lengths = total_initial_raw_chars

    # Process sections according to sorted order (shortest first)
    for section_detail in processing_order_list:
        original_idx = section_detail['original_order_index'] # Get the original index for storing result

        if not section_detail["items"] or section_detail['raw_length'] == 0 or remaining_budget_for_sections <= MIN_CHARS_FOR_LLM_CONSIDERATION // 2: # Ensure some minimal budget left
            print(f"{LogColors.DIM}Skipping section '{section_detail['title']}' (no items, zero raw length, or insufficient budget remaining).{LogColors.ENDC}")
            if sum_of_remaining_raw_lengths > 0: # Avoid division by zero if only one section was left and skipped
                sum_of_remaining_raw_lengths -= section_detail['raw_length']
            results_in_original_order[original_idx] = None # Store None for this skipped section
            continue

        current_section_target_budget = 0
        if sum_of_remaining_raw_lengths > 0:
            proportion = section_detail['raw_length'] / sum_of_remaining_raw_lengths
            ideal_proportional_budget = int(proportion * remaining_budget_for_sections)
            current_section_target_budget = max(MIN_CHARS_FOR_LLM_CONSIDERATION // 2, ideal_proportional_budget)
            current_section_target_budget = min(current_section_target_budget, MAX_CHARS_PER_SECTION_ESTIMATE) 
        else: 
             current_section_target_budget = min(remaining_budget_for_sections, MAX_CHARS_PER_SECTION_ESTIMATE)
        
        current_section_target_budget = max(0, current_section_target_budget)

        section_embed, chars_actually_used = create_section_embed(
            section_detail["key"],
            section_detail["title"],
            section_detail["items"], 
            section_detail["text_extractor"],
            section_detail["prefix_extractor"],
            current_section_dynamic_budget=current_section_target_budget,
            summarize_flag=summarize_flag, 
            openrouter_api_key=openrouter_api_key, 
            summary_model=summary_model, 
            max_embed_len=max_embed_len
        )
        
        results_in_original_order[original_idx] = section_embed # Store the created embed (or None)
        
        if section_embed: # Only adjust budget if an embed was actually created and used chars
            remaining_budget_for_sections -= chars_actually_used
            print(f"{LogColors.DIM}Budget update: Section '{section_detail['title']}' used {chars_actually_used}. Remaining budget for sections: {remaining_budget_for_sections}{LogColors.ENDC}")
        
        sum_of_remaining_raw_lengths -= section_detail['raw_length']
        if remaining_budget_for_sections < -MAX_CHARS_PER_SECTION_ESTIMATE: 
            print(f"{LogColors.FAIL}Critical: Section budget massively overdrawn. Stopping further section processing.{LogColors.ENDC}")
            break 
    
    # Add processed embeds to embeds_to_send IN THEIR ORIGINAL ORDER
    for embed_result in results_in_original_order:
        if embed_result:
            embeds_to_send.append(embed_result)

    # Embed for the Poster Image
    if main_poster_url:
        poster_embed = Embed(
            title="📊 Visual Summary Poster",
            color=GENERAL_COLORS[4] # Using a Teal color from GENERAL_COLORS for distinction
        )
        poster_embed.set_image(url=main_poster_url)
        poster_embed.set_footer(text=f"Note: AI generated summary • {fact_poster_date}")
        embeds_to_send.append(poster_embed)

    # Sending the embeds
    # Discord allows up to 10 embeds per message. We have 1 main + up to 5 sections + 1 poster = up to 7 embeds.

    try:
        await channel.send(embeds=embeds_to_send) # Send list of embeds
        print(f'{LogColors.SUCCESS}{len(embeds_to_send)} embed(s) posted successfully!{LogColors.ENDC}')
        
        # Poster URL is now sent as an embed, so no need to send separately.
        # if main_poster_url: 
        #     await channel.send(main_poster_url)
        #     print('Main poster image URL sent successfully as a separate message for unfurling.')

    except discord.errors.HTTPException as e:
        if e.status == 400 and e.text and 'embeds.0.description' in str(e.text).lower():
             print(f"{LogColors.FAIL}Failed to send Discord message due to description length: {len(main_embed_description)}. Error: {e.text}{LogColors.ENDC}")
        else:
            print(f"{LogColors.FAIL}Failed to send fact briefing message: {e} (Code: {e.code}, Status: {e.status}, Text: {e.text if hasattr(e, 'text') else 'N/A'}){LogColors.ENDC}")
    except Exception as e:
        print(f"{LogColors.FAIL}An unexpected error occurred while sending fact briefing message: {e}{LogColors.ENDC}")

async def run_discord_bot(json_file, channel_id, summarize_flag, summary_model, openrouter_api_key, max_embed_len, poster_filename_arg):
    intents = discord.Intents.default() 
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f"{LogColors.SUCCESS}Logged in as {client.user}{LogColors.ENDC}")
        try:
            channel = await client.fetch_channel(channel_id)
            if channel:
                await send_discord_webhook(channel, json_file, summarize_flag, summary_model, openrouter_api_key, max_embed_len, poster_filename_arg)
            else:
                print(f"{LogColors.FAIL}Error: Could not find channel with ID {channel_id}{LogColors.ENDC}")
        except discord.errors.Forbidden:
            print(f"{LogColors.FAIL}Error: Bot does not have permissions to fetch or send to channel {channel_id}{LogColors.ENDC}")
        except discord.errors.HTTPException as e: 
            print(f"{LogColors.FAIL}Error during Discord operation: {e.status} {e.text if hasattr(e, 'text') else e}{LogColors.ENDC}")
        except Exception as e:
            print(f"{LogColors.FAIL}An unexpected error occurred in on_ready: {e}{LogColors.ENDC}")
        finally:
            print(f"{LogColors.DIM}Attempting to close bot client after on_ready tasks...{LogColors.ENDC}")
            await asyncio.sleep(0.5) 
            await client.close()
            print(f"{LogColors.DIM}Bot client close signal sent.{LogColors.ENDC}") 
    
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print(f"{LogColors.FAIL}Error: DISCORD_BOT_TOKEN environment variable not set{LogColors.ENDC}")
        return 
    
    try:
        await client.start(token) 
    except discord.errors.LoginFailure:
        print(f"{LogColors.FAIL}Error: Failed to log in with the provided DISCORD_BOT_TOKEN. Check the token.{LogColors.ENDC}")
    except discord.errors.HTTPException as e:
        print(f"{LogColors.FAIL}An HTTP error occurred while starting or connecting the bot: {e.status} {e.text if hasattr(e, 'text') else ''}{LogColors.ENDC}") 
    except KeyboardInterrupt:
        print(f"{LogColors.WARNING}Bot operation interrupted by user (KeyboardInterrupt). Closing client...{LogColors.ENDC}")
        if client and not client.is_closed(): 
            await client.close()
    except Exception as e:
        print(f"{LogColors.FAIL}An unexpected error occurred with the Discord client management: {e}{LogColors.ENDC}")
    finally:
        if client and not client.is_closed(): 
             print(f"{LogColors.DIM}Ensuring client is closed in outer finally block.{LogColors.ENDC}")
             await client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Format and optionally send fact briefing to Discord, with summarization.")
    parser.add_argument("json_file", help="Path to the JSON fact briefing file")
    parser.add_argument("--discord", "-d", action="store_true", help="Send to Discord webhook")
    parser.add_argument("--channel", "-c", help="Discord channel ID (required if --discord is used)")
    parser.add_argument("--summarize", "-s", action="store_true", help="Enable summarization of long content via OpenRouter.")
    parser.add_argument("--summary-model", type=str, default=DEFAULT_SUMMARY_MODEL, help=f"OpenRouter model for summarization (default: {DEFAULT_SUMMARY_MODEL})")
    parser.add_argument("--max-text-summary-length", type=int, default=DEFAULT_MAX_TEXT_SUMMARY_LENGTH, help=f"Target max length for summarized plain text output (default: {DEFAULT_MAX_TEXT_SUMMARY_LENGTH} chars).")
    parser.add_argument("--max-embed-summary-length", type=int, default=DEFAULT_MAX_EMBED_SUMMARY_LENGTH, help=f"Overall max length for Discord embed description, including footers (default: {DEFAULT_MAX_EMBED_SUMMARY_LENGTH} chars).")
    parser.add_argument("--poster-filename", type=str, default=DEFAULT_POSTER_FILENAME, help=f"Filename of the main poster to display (e.g., {DEFAULT_POSTER_FILENAME}). Must be in the {POSTER_BASE_URL} directory.")
    
    args = parser.parse_args()
    
    openrouter_api_key = None
    if args.summarize: # User wants summarization
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_api_key:
            print(f"{LogColors.WARNING}Warning: --summarize flag is set, but OPENROUTER_API_KEY environment variable is not found. Summarization will be SKIPPED for sections.{LogColors.ENDC}")
            # Keep args.summarize as True if user intended it, format_body will handle no-key
    
    if args.discord:
        if not args.channel:
            print(f"{LogColors.FAIL}Error: --channel is required when using --discord{LogColors.ENDC}")
            sys.exit(1)
        
        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            loop.run_until_complete(run_discord_bot(
                args.json_file, 
                args.channel, 
                args.summarize, # Pass the user's intent to summarize
                args.summary_model, 
                openrouter_api_key, # Pass the key, might be None
                args.max_embed_summary_length,
                args.poster_filename 
            ))
        except KeyboardInterrupt:
            print(f"{LogColors.WARNING}Script interrupted by user (main block).{LogColors.ENDC}")
        except Exception as e:
            print(f"{LogColors.FAIL}An error occurred running the bot (main block): {e}{LogColors.ENDC}")
        finally:
            print(f"{LogColors.DIM}Script finished (main block).{LogColors.ENDC}")

    else: 
        try:
            with open(args.json_file, 'r') as f:
                briefing_data_main = json.load(f)
        except Exception as e:
            print(f"{LogColors.FAIL}Error reading {args.json_file} for local output: {e}{LogColors.ENDC}")
            sys.exit(1)

        # Simple text output for local testing
        print(f"📊 Eliza Daily – {briefing_data_main.get('briefing_date', 'Unknown Date')}")
        print("=" * 50)
        print(f"Overall Summary: {briefing_data_main.get('overall_summary', 'No summary available.')}")
        
        categories = briefing_data_main.get('categories', {})
        for section_name, section_data in categories.items():
            print(f"\n{section_name.replace('_', ' ').title()}:")
            if isinstance(section_data, list):
                for i, item in enumerate(section_data[:3]):  # Show first 3 items
                    print(f"  {i+1}. {str(item)[:100]}...")
            elif isinstance(section_data, dict):
                for key, value in section_data.items():
                    print(f"  {key}: {str(value)[:100]}...")
        
        print(f"\nThis script is primarily designed for Discord output. Use -d flag for full functionality.")