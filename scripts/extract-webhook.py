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
SECTION_SUMMARIZATION_TARGET_LENGTH = 400 # Target for LLM summary of a section

# New constants for dynamic summarization trigger logic
MIN_CHARS_FOR_LLM_CONSIDERATION = 300       # Min raw chars in a section to even consider using LLM for it.
LLM_WORTHWHILE_REDUCTION_THRESHOLD = 150    # Only use LLM if it can reduce by at least this many chars OR if current length is already very long.
TARGET_DISPLAY_LENGTH_WITHOUT_LLM = 450     # Preferred max display length for a section if NOT summarized by LLM.
                                            # (Actual per-embed desc limit `max_embed_len` is a hard final truncate)

def summarize_text_openrouter(text_to_summarize: str, api_key: str, model: str, target_max_length: int) -> str:
    if not api_key:
        print(f"{LogColors.WARNING}Warning: OPENROUTER_API_KEY not provided. Skipping summarization.{LogColors.ENDC}")
        return text_to_summarize
    if not text_to_summarize.strip():
        print(f"{LogColors.WARNING}Warning: Empty text provided for summarization. Skipping.{LogColors.ENDC}")
        return ""
    if len(text_to_summarize) <= target_max_length:
        # print(f"Text length ({len(text_to_summarize)}) is already within target ({target_max_length}). Skipping summarization by LLM.")
        return text_to_summarize
    
    prompt_template = (
        f"Please summarize the following text concisely to fit within approximately {target_max_length} characters. "
        f"The summary is for a Discord embed. Maintain clarity and key information. Output only the summary.\n\n"
        f"TEXT TO SUMMARIZE:\n\"\"\"\n{text_to_summarize}\n\"\"\"\n\nCONCISE SUMMARY:"
    )
    # Calculate max_tokens for the completion. Approx 3.5 chars per token.
    # Ensure a minimum reasonable number of tokens if target_max_length is very small.
    completion_max_tokens = max(50, int(target_max_length / 3.5)) 

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
                return summary[:target_max_length -4] + "..."
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
    # poster_link_text = poster_filename_arg.replace('.png', '').replace('-', ' ').title() # No longer needed for main embed desc
    hackmd_link_text = "View the full report in the HackMD Book"
    
    # Embed 1: Main Overview & Links
    overall_summary_text = briefing_data.get('overall_summary', "No overall summary available.")
    main_embed_description = ""

    if summarize_flag and openrouter_api_key:
        objective_summary_prompt = (
            f"Rewrite the following summary objectively, focusing on key metrics and factual observations from the ElizaOS project, suitable for a daily briefing. "
            f"Avoid subjective phrases like 'significant activity' or 'bustling'. Aim for conciseness, around {SECTION_SUMMARIZATION_TARGET_LENGTH // 2} characters.\n\n"
            f"ORIGINAL SUMMARY:\n\"\"\"\n{overall_summary_text}\n\"\"\"\n\nOBJECTIVE REWRITE:"
        )
        rewritten_summary = summarize_text_openrouter(objective_summary_prompt, openrouter_api_key, summary_model, SECTION_SUMMARIZATION_TARGET_LENGTH // 2)
        main_embed_description = rewritten_summary if rewritten_summary.strip() else "Key observations: " + overall_summary_text
    else:
        main_embed_description = "Key observations: " + overall_summary_text

    # Add links to the main embed description
    # main_embed_description += f"\n\n🖼️ [View the {poster_link_text} poster]({main_poster_url})" # Removed as poster is its own embed
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

    embeds_to_send = [main_embed]
    categories_data = briefing_data.get('categories', {})

    # Helper to create section embeds
    def create_section_embed(section_key: str, title_prefix: str, items_data: list, item_text_extractor, item_prefix_extractor=None):
        if not items_data:
            print(f"{LogColors.DIM}Section '{title_prefix}': No items provided.{LogColors.ENDC}")
            return None

        raw_item_texts = []
        for item in items_data:
            text = item_text_extractor(item)
            prefix = item_prefix_extractor(item) if item_prefix_extractor else None
            raw_item_texts.append(f"{prefix}: {text}" if prefix else text)
        
        if not raw_item_texts:
            return None

        compiled_items_text = "\n".join(raw_item_texts)
        display_text = compiled_items_text
        log_prefix = f"{LogColors.SECTION}Section '{title_prefix}':{LogColors.ENDC}"

        print(f"{log_prefix} Initial compiled text length: {LogColors.DIM}{len(compiled_items_text)} chars.{LogColors.ENDC}")

        should_try_llm = False
        if summarize_flag and openrouter_api_key and len(compiled_items_text) > MIN_CHARS_FOR_LLM_CONSIDERATION:
            # Condition 1: Is the text very long anyway (well beyond our target display length for non-LLM content)?
            if len(compiled_items_text) > TARGET_DISPLAY_LENGTH_WITHOUT_LLM + LLM_WORTHWHILE_REDUCTION_THRESHOLD: 
                should_try_llm = True
                print(f"{log_prefix} Text is very long ({len(compiled_items_text)}), flagging for LLM summarization.")
            # Condition 2: Would LLM (aiming for SECTION_SUMMARIZATION_TARGET_LENGTH) provide a significant reduction?
            elif (len(compiled_items_text) - SECTION_SUMMARIZATION_TARGET_LENGTH) > LLM_WORTHWHILE_REDUCTION_THRESHOLD:
                should_try_llm = True
                print(f"{log_prefix} LLM could provide significant reduction from {len(compiled_items_text)} to ~{SECTION_SUMMARIZATION_TARGET_LENGTH}, flagging for LLM summarization.")

        if should_try_llm:
            print(f"{log_prefix} Attempting LLM summarization to ~{LogColors.DIM}{SECTION_SUMMARIZATION_TARGET_LENGTH}{LogColors.ENDC} chars.")
            section_summary = summarize_text_openrouter(compiled_items_text, openrouter_api_key, summary_model, SECTION_SUMMARIZATION_TARGET_LENGTH)
            if section_summary.strip() and len(section_summary) < len(display_text): # Use summary if it's shorter and not empty
                display_text = section_summary
                print(f"{log_prefix} {LogColors.SUCCESS}Used LLM summary. New length: {len(display_text)} chars.{LogColors.ENDC}")
            elif not section_summary.strip():
                print(f"{log_prefix} {LogColors.WARNING}LLM summary was empty. Will use original compiled text (potentially truncated).{LogColors.ENDC}")
                # Fall through to non-LLM path truncation if needed
            else:
                print(f"{log_prefix} {LogColors.DIM}LLM summary (len {len(section_summary)}) was not shorter than original (len {len(display_text)}) or was empty. Will use original (potentially truncated).{LogColors.ENDC}")
                # Fall through to non-LLM path truncation if needed
            
            # After LLM attempt (used or not), check if current display_text (original or LLM summary) exceeds TARGET_DISPLAY_LENGTH_WITHOUT_LLM
            # This applies if LLM summary was still too long, or if LLM wasn't used effectively.
            if len(display_text) > TARGET_DISPLAY_LENGTH_WITHOUT_LLM:
                print(f"{log_prefix} {LogColors.WARNING}Text (length {len(display_text)}) still exceeds preferred display length ({TARGET_DISPLAY_LENGTH_WITHOUT_LLM}) after LLM attempt. Truncating.{LogColors.ENDC}")
                display_text = display_text[:TARGET_DISPLAY_LENGTH_WITHOUT_LLM - 4] + "..."

        else: # Not trying LLM (or conditions not met)
            print(f"{log_prefix} {LogColors.DIM}Not attempting LLM summarization (text length {len(compiled_items_text)}, min_consider {MIN_CHARS_FOR_LLM_CONSIDERATION}).{LogColors.ENDC}")
            if len(display_text) > TARGET_DISPLAY_LENGTH_WITHOUT_LLM: 
                print(f"{log_prefix} {LogColors.WARNING}Original text (length {len(display_text)}) exceeds preferred display length ({TARGET_DISPLAY_LENGTH_WITHOUT_LLM}). Truncating.{LogColors.ENDC}")
                display_text = display_text[:TARGET_DISPLAY_LENGTH_WITHOUT_LLM - 4] + "..."
        
        # Final hard truncation to absolute per-embed description limit
        if len(display_text) > max_embed_len: 
            print(f"{log_prefix} {LogColors.WARNING}Display text (length {len(display_text)}) exceeds absolute embed limit ({max_embed_len}). Hard Truncating.{LogColors.ENDC}")
            display_text = display_text[:max_embed_len - 4] + "..."
            print(f"{log_prefix} {LogColors.DIM}Final display text length after hard truncation: {len(display_text)} chars.{LogColors.ENDC}")
        elif not display_text.strip(): 
            print(f"{log_prefix} {LogColors.WARNING}Display text is empty after processing. Skipping embed.{LogColors.ENDC}")
            return None

        section_embed = Embed(
            title=title_prefix,
            description=display_text.strip(),
            color=SECTION_COLORS.get(section_key, SECTION_COLORS["default"])
        )
        return section_embed

    # Twitter Section
    twitter_items = categories_data.get('twitter_news_highlights', [])
    twitter_embed = create_section_embed("twitter", "🐦 Twitter Buzz", twitter_items, 
                                         lambda item: item.get('claim', 'N/A'))
    if twitter_embed: embeds_to_send.append(twitter_embed)

    # GitHub Section
    github_items = categories_data.get('github_updates', {}).get('overall_focus', [])
    github_embed = create_section_embed("github", "⚙️ GitHub Beat", github_items, 
                                        lambda item: item.get('claim', 'N/A'))
    if github_embed: embeds_to_send.append(github_embed)

    # Discord Section
    discord_items = categories_data.get('discord_updates', [])
    discord_embed = create_section_embed("discord", "💬 Discord Updates", discord_items, 
                                         item_text_extractor=lambda item: f"{item.get('summary', 'N/A')} (Participants: {', '.join(item.get('key_participants', [])) if item.get('key_participants') else 'N/A'})",
                                         item_prefix_extractor=lambda item: item.get('channel', ''))
    if discord_embed: embeds_to_send.append(discord_embed)

    # Strategy Section
    strategy_items = categories_data.get('strategic_insights', [])
    strategy_embed = create_section_embed("strategy", "🚀 Strategic Insights", strategy_items, 
                                          item_text_extractor=lambda item: item.get('insight', 'N/A'),
                                          item_prefix_extractor=lambda item: item.get('theme', 'Insight'))
    if strategy_embed: embeds_to_send.append(strategy_embed)

    # Market Analysis Section
    market_items = categories_data.get('market_analysis', [])
    market_embed = create_section_embed("market", "📈 (WIP) Market Analysis", market_items, 
                                        lambda item: item.get('observation', 'N/A'))
    if market_embed: embeds_to_send.append(market_embed)

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

        # For local output, we primarily use max_text_summary_length for the entire body.
        # The summarization flag also applies here for section-level summaries if enabled.
        final_text_output = format_body_from_briefing_data(
            briefing_data_main, 
            args.max_text_summary_length, # Use max_text_summary_length as the budget for the whole body
            args.summarize, # User's intent to summarize sections
            openrouter_api_key, 
            args.summary_model
        )
            
        # format_body_from_briefing_data should already try to respect its overall max length.
        # A final truncation for plain text output if it somehow still exceeded.
        if len(final_text_output) > args.max_text_summary_length:
             print(f"{LogColors.WARNING}Warning: Final plain text output too long ({len(final_text_output)} chars). Truncating.{LogColors.ENDC}")
             final_text_output = final_text_output[:args.max_text_summary_length - 4] + "..."
            
        print(final_text_output)