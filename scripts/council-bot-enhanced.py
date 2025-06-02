#!/usr/bin/env python3
"""
Enhanced Interactive Council Bot for ElizaOS - V2 Schema
Handles new JSON structure with topics, questions, and multiple-choice answers.
"""
import json
import sys
import os
import argparse
import discord
from discord import Embed, ButtonStyle
from discord.ui import Button, View, Select
from discord.ext import commands
from datetime import datetime
import requests
import asyncio # Keep asyncio for bot.run() and potential future async operations
import csv # Ensure csv is imported
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any

# --- V2 Configuration ---
@dataclass
class CouncilBotConfigV2: # Renamed to avoid conflict if old script is in same env
    colors: List[int] = field(default_factory=lambda: [
        0x2026ad, 0xe67e22, 0x9b59b6, 0x2ecc71, 0x1abc9c, 0xf1c40f 
    ]) 
    number_emojis: List[str] = field(default_factory=lambda: ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟'])
    openrouter_endpoint: str = "https://openrouter.ai/api/v1/chat/completions"
    default_summary_model: str = "google/gemini-2.5-flash-preview"
    max_embed_length: int = 2000 # For individual embed descriptions
    hackmd_book_url: str = "https://hackmd.io/@elizaos/book"
    avatar_url: str = "https://m3-org.github.io/avatars/eliza/thumb-bust_eliza.png"

class LogColors:
    HEADER = '\033[95m'
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    DIM = '\033[2m'
    INFO = '\033[94m'

config = CouncilBotConfigV2()

# --- V2 Vote Storage ---
class VoteStorageV2:
    def __init__(self):
        self.votes: Dict[str, Dict[str, str]] = {}  # {user_id: {question_id: answer_key}}
        self.vote_counts: Dict[str, Dict[str, int]] = {}  # {question_id: {answer_key: count}}
        
    def reset_votes(self):
        self.votes.clear()
        self.vote_counts.clear()
        
    def cast_vote(self, user_id: str, question_id: str, answer_key: str) -> Tuple[bool, str, Optional[str]]:
        user_votes = self.votes.get(user_id, {})
        previous_answer_for_question = user_votes.get(question_id)

        if previous_answer_for_question == answer_key:
            return False, "already_voted_this_answer", previous_answer_for_question
            
        if question_id not in self.vote_counts:
            self.vote_counts[question_id] = {}

        if previous_answer_for_question is not None:
            if self.vote_counts[question_id].get(previous_answer_for_question, 0) > 0:
                self.vote_counts[question_id][previous_answer_for_question] -= 1
            self.vote_counts[question_id][answer_key] = self.vote_counts[question_id].get(answer_key, 0) + 1
            user_votes[question_id] = answer_key
            self.votes[user_id] = user_votes
            return True, "vote_changed_for_question", previous_answer_for_question
        else:
            self.vote_counts[question_id][answer_key] = self.vote_counts[question_id].get(answer_key, 0) + 1
            user_votes[question_id] = answer_key
            self.votes[user_id] = user_votes
            return True, "vote_cast_for_question", None
            
    def get_vote_counts_for_question(self, question_id: str) -> Dict[str, int]:
        return self.vote_counts.get(question_id, {}).copy()
        
    def get_all_vote_counts(self) -> Dict[str, Dict[str, int]]:
        return self.vote_counts.copy()

    def get_total_votes_for_question(self, question_id: str) -> int:
        return sum(self.vote_counts.get(question_id, {}).values())

global_vote_storage_v2 = VoteStorageV2() # Changed instance name

# --- Helper Functions ---
def safe_truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    truncated = text[:max_len]
    for separator in ['\n\n', '. ', '.\n', '\n']:
        idx = truncated.rfind(separator)
        if idx > 0 and idx > max_len - 150:
            return truncated[:idx + len(separator)].rstrip() + "..."
    last_space = truncated.rfind(' ')
    if last_space > max_len - 50:
        return truncated[:last_space].rstrip() + "..."
    return truncated.rstrip() + "..."

async def summarize_text_openrouter(text: str, api_key: str, model: str, target_length: int, context_hint: str = "council briefing content") -> str:
    if not api_key or len(text) <= target_length:
        return text
    prompt = f"""Summarize this {context_hint} for Discord. Keep key insights and make it engaging.
Target length: ~{target_length} characters. Be comprehensive but concise.

CONTENT:
{text}

SUMMARY:"""
    headers = {
        "Authorization": f"Bearer {api_key}", "Content-Type": "application/json",
        "HTTP-Referer": config.hackmd_book_url, "X-Title": "Council Bot V2 Summarizer"
    }
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max(100, int(target_length / 3.0))}
    try:
        response = requests.post(config.openrouter_endpoint, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        summary = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return summary[:target_length] if summary and len(summary) > target_length else (summary if summary else safe_truncate(text, target_length))
    except Exception as e:
        print(f"{LogColors.WARNING}Summarization failed: {e}{LogColors.ENDC}")
        return safe_truncate(text, target_length)

# --- V2 UI Components (REACTION-BASED FLOW - These Select/Button classes are now OBSOLETE) --- #
# class AnswerButton(Button): ... (entire class commented out)
# class AnswerVoteView(View): ... (entire class commented out)
# class QuestionSelect(discord.ui.Select): ... (entire class commented out)
# class QuestionSelectView(View): ... (entire class commented out)
# class TopicSelect(discord.ui.Select): ... (entire class commented out)
# class OverallResultsButtonV2(Button): ... (entire class commented out)
# class CouncilInteractionViewV2(View): ... (entire class commented out)

# --- V1 Interaction Classes (Commented Out) --- # 
# ... (old V1 classes remain commented out) ...

# --- CouncilBot Class (V2 - Survey/Reaction Flow) ---
class CouncilBotV2(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True # Enable for potential future text commands if needed
        intents.reactions = True # Crucial: Enable reactions intent for on_raw_reaction_add
        super().__init__(command_prefix='!councilv2-', intents=intents) # New prefix
        self.active_surveys: Dict[Tuple[int, int], Dict[str, Any]] = {} # (channel_id, user_id) -> Survey State
        self.last_briefing_data_loaded = None
        
    async def on_ready(self):
        print(f'{LogColors.SUCCESS}Council Bot V2 logged in as {self.user}{LogColors.ENDC}')
        target_channels_str = os.getenv('TARGET_CHANNEL_IDS', '')
        briefing_file = os.getenv('BRIEFING_FILE')
        if target_channels_str and briefing_file:
            target_channels = [ch_id.strip() for ch_id in target_channels_str.split(',') if ch_id.strip()]
            if target_channels:
                await self.auto_post_briefing(target_channels, briefing_file)
    
    async def auto_post_briefing(self, channel_ids: List[str], briefing_file: str):
        for channel_id in channel_ids:
            try:
                channel = await self.fetch_channel(int(channel_id))
                await self.post_briefing_to_channel(channel, briefing_file)
                print(f'{LogColors.SUCCESS}Posted V2 Briefing to channel {channel_id}{LogColors.ENDC}')
            except Exception as e:
                print(f'{LogColors.FAIL}Error posting V2 briefing to channel {channel_id}: {e}{LogColors.ENDC}')
    
    async def post_briefing_to_channel(self, channel, briefing_file: str):
        """Posts a static message in the channel inviting users to start the survey in DMs."""
        try:
            # global_vote_storage_v2.reset_votes() # Reset votes globally when a new briefing is posted
            # Decided to let votes accumulate across postings unless explicitly reset elsewhere / by schedule
            
            with open(briefing_file, 'r', encoding='utf-8') as f:
                briefing_data = json.load(f)
            self.last_briefing_data_loaded = briefing_data # Store for !myvotes command

            if not briefing_data.get('key_points'):
                await channel.send("Briefing data loaded, but no key points found for a survey.")
                return

            embed = Embed(title="📝 Jedai Council Daily Survey Available!", 
                          description=(
                              "A new council survey is ready for your input.\n"
                              "Click the button below to start the survey."
                          ),
                          color=config.colors[0])
            embed.set_author(name="JEDAI COUNCIL", url=config.hackmd_book_url)
            embed.set_thumbnail(url=config.avatar_url)
            embed.set_footer(text=f"Briefing Date: {briefing_data.get('date', 'N/A')}")

            view = InitialSurveyView(briefing_data, self) # Pass briefing_data and bot instance
            await channel.send(embed=embed, view=view)
            print(f'{LogColors.SUCCESS}Posted V2 Survey invitation to {channel.name}{LogColors.ENDC}')
            
        except FileNotFoundError:
            print(f'{LogColors.FAIL}Error: Briefing file {briefing_file} not found.{LogColors.ENDC}')
            await channel.send(f"Error: Briefing file `{briefing_file}` not found.")
        except json.JSONDecodeError:
            print(f'{LogColors.FAIL}Error: Briefing file {briefing_file} is not valid JSON.{LogColors.ENDC}')
            await channel.send(f"Error: Briefing file `{briefing_file}` is not valid JSON.")
        except Exception as e:
            print(f'{LogColors.FAIL}Error posting V2 survey: {e}{LogColors.ENDC}')
            await channel.send(f"An unexpected error occurred while loading the V2 survey: {str(e)}")

    async def _prepare_question_content(self, topic_data: dict, question_data: dict, survey_key: Tuple[int, int], is_initial_question: bool = False) -> Tuple[List[Embed], 'EphemeralSurveyQuestionView']:
        if survey_key not in self.active_surveys:
            print(f"{LogColors.WARNING}Survey key {survey_key} not found in _prepare_question_content.{LogColors.ENDC}")
            error_embed = Embed(title="Error", description="Could not retrieve survey session. Please try restarting the survey.", color=discord.Color.red())
            return ([error_embed], None)

        survey_state = self.active_surveys[survey_key] # Get survey_state
        briefing_data = survey_state['briefing_data']
        briefing_date = briefing_data.get('date', 'N/A')
        topic_title = topic_data.get('topic', 'Current Topic')
        question_id = question_data.get('question_id', 'unknown_q')
        question_text_full = question_data.get('text', 'No question text available.')
        answers = question_data.get('multiple_choice_answers', {})

        # Calculate total questions and current question number
        total_questions = 0
        for kp in briefing_data.get('key_points', []):
            total_questions += len(kp.get('deliberation_items', []))
        
        current_question_number = 0
        for i in range(survey_state['current_topic_index']):
            current_question_number += len(briefing_data['key_points'][i].get('deliberation_items', []))
        current_question_number += survey_state['current_question_index'] + 1


        orange_color = config.colors[1 % len(config.colors)]

        description_parts = [f"**❓ Question: {question_text_full}**", "\n**🗳️ Answer Options:**\n"]
        sorted_answer_keys = sorted(answers.keys(), key=lambda x: int(x.split('_')[1]) if '_' in x and x.split('_')[1].isdigit() else float('inf'))
        
        for i, ans_key in enumerate(sorted_answer_keys):
            if i < len(config.number_emojis): # Use number_emojis for iteration limit, but label buttons with numbers
                ans_obj = answers[ans_key]
                ans_text = ans_obj.get('text', 'N/A')
                # Use numeric label for embed, buttons will use simple numbers
                description_parts.append(f"{config.number_emojis[i]} {ans_text}")
            else:
                break
        description_parts.append("\nClick a button below to cast your vote.")
        question_embed_description = "\n".join(description_parts)

        question_embed_title = f"Topic: {safe_truncate(topic_title,100)}"
        if is_initial_question:
            question_embed_title = f"📝 Council Survey - Topic: {safe_truncate(topic_title,100)}"
        
        question_embed = Embed(
            title=question_embed_title,
            description=question_embed_description,
            color=orange_color
        )
        if is_initial_question:
            question_embed.set_author(name="JEDAI COUNCIL DAILY SURVEY", url=config.hackmd_book_url)
            question_embed.set_thumbnail(url=config.avatar_url)
        
        # Update footer with progress
        question_embed.set_footer(text=f"Question {current_question_number}/{total_questions} | Briefing Date: {briefing_date}")
        
        # Pass current_question_number for button labeling if needed, or handle in EphemeralSurveyQuestionView
        view = EphemeralSurveyQuestionView(self, survey_key, briefing_data, question_data)
        return ([question_embed], view)

    async def progress_ephemeral_survey(self, interaction: discord.Interaction, survey_key: Tuple[int, int]):
        if survey_key not in self.active_surveys:
            await interaction.edit_original_response(content="Survey session ended or encountered an issue. Please try starting again.", embeds=[], view=None)
            return

        survey_state = self.active_surveys[survey_key]
        briefing_data = survey_state['briefing_data']
        # Store user object from interaction, as it's needed for saving if survey completes here
        current_user = interaction.user 

        current_topic_idx = survey_state['current_topic_index']
        current_question_idx = survey_state['current_question_index'] + 1

        key_points = briefing_data.get('key_points', [])
        if current_topic_idx >= len(key_points):
            await interaction.edit_original_response(content="🎉 Survey Complete! Thank you for your participation. Your responses have been recorded.", embeds=[], view=None)
            user_final_votes = global_vote_storage_v2.votes.get(str(current_user.id), {})
            await self._save_user_responses_to_csv(current_user, user_final_votes, briefing_data)
            await self._send_user_vote_summary_dm(current_user, None) 
            if survey_key in self.active_surveys: del self.active_surveys[survey_key]
            return

        current_topic_data = key_points[current_topic_idx]
        deliberation_items = current_topic_data.get('deliberation_items', [])
        if current_question_idx >= len(deliberation_items):
            current_topic_idx += 1
            current_question_idx = 0 
            survey_state['current_topic_index'] = current_topic_idx
            if current_topic_idx >= len(key_points):
                await interaction.edit_original_response(content="🎉 Survey Complete! Thank you for your participation. Your responses have been recorded.", embeds=[], view=None)
                user_final_votes = global_vote_storage_v2.votes.get(str(current_user.id), {})
                await self._save_user_responses_to_csv(current_user, user_final_votes, briefing_data)
                await self._send_user_vote_summary_dm(current_user, None)
                if survey_key in self.active_surveys: del self.active_surveys[survey_key]
                return
            else:
                current_topic_data = key_points[current_topic_idx]
                deliberation_items = current_topic_data.get('deliberation_items', [])
                if not deliberation_items:
                    survey_state['current_question_index'] = -1 
                    await self.progress_ephemeral_survey(interaction, survey_key) # Recursive call, interaction object is passed
                    return 

        survey_state['current_question_index'] = current_question_idx
        question_to_post_data = deliberation_items[current_question_idx]
        
        embeds, view = await self._prepare_question_content(current_topic_data, question_to_post_data, survey_key, is_initial_question=False)
        if view is None and embeds and "Error" in embeds[0].title:
             await interaction.edit_original_response(embeds=embeds, view=None)
        else:
            await interaction.edit_original_response(embeds=embeds, view=view)

    # async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
    #     # ... (entire method commented out as it's replaced by button callbacks) ...
    #     pass

    async def _send_user_vote_summary_dm(self, user_to_dm: discord.User, source_channel_for_fallback: Optional[discord.TextChannel] = None):
        """Helper to compile and DM a user's vote summary for the last briefing."""
        user_id_str = str(user_to_dm.id)
        user_votes_for_briefing = global_vote_storage_v2.votes.get(user_id_str, {})

        if not user_votes_for_briefing:
            try:
                await user_to_dm.send("You haven't cast any votes in the current council survey session.")
                if source_channel_for_fallback: # e.g., called from a command
                    # Find the original message if possible to react, or just skip reaction if too complex from a helper
                    pass # Or try to get ctx from higher up if this was for a command context
            except discord.Forbidden:
                if source_channel_for_fallback:
                    await source_channel_for_fallback.send(f"{user_to_dm.mention} I couldn't DM you. You haven't cast any votes.", ephemeral=True, delete_after=30)
            return False # Indicate DM might have failed or no votes

        if not self.last_briefing_data_loaded:
            try:
                await user_to_dm.send("Sorry, I don't have the details of the last briefing to provide full context for your votes.")
            except discord.Forbidden:
                if source_channel_for_fallback:
                    await source_channel_for_fallback.send(f"{user_to_dm.mention} I couldn't DM you. No briefing data loaded to give context to votes.", ephemeral=True, delete_after=30)
            return False

        briefing_data = self.last_briefing_data_loaded
        dm_parts = [f"📋 **Your Votes for Council Survey (Date: {briefing_data.get('date', 'N/A')})**"]

        for kp_idx, kp in enumerate(briefing_data.get('key_points', [])):
            topic_title = kp.get('topic', f'Topic {kp_idx + 1}')
            has_votes_in_topic = False
            current_topic_lines = []
            for q_idx, di in enumerate(kp.get('deliberation_items', [])):
                question_id = di.get('question_id')
                question_text_full = di.get('text', 'Unknown Question')
                if question_id in user_votes_for_briefing:
                    if not has_votes_in_topic:
                        current_topic_lines.append(f"\n**Topic: {topic_title}**")
                        has_votes_in_topic = True
                    voted_answer_key = user_votes_for_briefing[question_id]
                    answer_obj = di.get('multiple_choice_answers', {}).get(voted_answer_key)
                    answer_text_full = answer_obj.get('text', voted_answer_key) if answer_obj else voted_answer_key
                    implication_text = answer_obj.get('implication') if answer_obj else None

                    voted_emoji = "➡️"
                    sorted_answer_keys = sorted(di.get('multiple_choice_answers', {}).keys(), 
                                                key=lambda x: int(x.split('_')[1]) if '_' in x and x.split('_')[1].isdigit() else float('inf'))
                    for i, ans_key_iter in enumerate(sorted_answer_keys):
                        if ans_key_iter == voted_answer_key and i < len(config.number_emojis):
                            voted_emoji = config.number_emojis[i]
                            break
                    
                    current_topic_lines.append(f"Q: {question_text_full}")
                    current_topic_lines.append(f"A: {answer_text_full}")
            if has_votes_in_topic:
                dm_parts.extend(current_topic_lines)
        
        if len(dm_parts) == 1:
            try: 
                await user_to_dm.send("It seems you haven't voted on any questions from the latest briefing for which I have details.")
            except discord.Forbidden:
                if source_channel_for_fallback:
                    await source_channel_for_fallback.send(f"{user_to_dm.mention} I couldn't DM you. No votes found for this briefing.", ephemeral=True, delete_after=30)
            return False
        else:
            full_dm_text = "\n".join(dm_parts)
            message_chunk = ""
            dm_send_successful = True
            for line in full_dm_text.split('\n'):
                if len(message_chunk) + len(line) + 1 > 1990:
                    try: await user_to_dm.send(message_chunk)
                    except discord.Forbidden: dm_send_successful = False; break
                    except Exception as e: print(f"{LogColors.ERROR}Helper DM chunk error: {e}{LogColors.ENDC}"); dm_send_successful = False; break
                    message_chunk = line
                else: message_chunk += line + "\n"
            if dm_send_successful and message_chunk:
                try: await user_to_dm.send(message_chunk)
                except discord.Forbidden: dm_send_successful = False
                except Exception as e: print(f"{LogColors.ERROR}Helper final DM chunk error: {e}{LogColors.ENDC}"); dm_send_successful = False
            
            if not dm_send_successful and source_channel_for_fallback:
                ephemeral_summary_header = f"📋 {user_to_dm.mention}, I couldn't DM your vote summary. Here it is (ephemerally):\n"
                ephemeral_full_text = "\n".join(dm_parts) 
                if len(ephemeral_full_text) > 1950: ephemeral_full_text = ephemeral_full_text[:1950] + "... (summary truncated)"
                try: 
                    await source_channel_for_fallback.send(f"{ephemeral_summary_header}{ephemeral_full_text}", ephemeral=True, delete_after=60)
                except Exception as e: print(f"{LogColors.ERROR}Helper ephemeral fallback error: {e}{LogColors.ENDC}")
            return dm_send_successful

    @commands.command(name='myvotes')
    async def my_votes_command_v2(self, ctx):
        """DMs the calling user a summary of their votes for the current/last briefing.
           If DM fails, sends an ephemeral message in the channel with the summary.
        """
        dm_success = await self._send_user_vote_summary_dm(ctx.author, ctx.channel)
        try:
            if dm_success:
                await ctx.message.add_reaction("✅") # DM was successful or no votes to send
            else:
                # Ephemeral message already handled by helper if DM failed and channel was provided
                # Adding a different reaction if DM failed but ephemeral might have also failed or wasn't possible
                await ctx.message.add_reaction("⚠️") # General issue / DM failed and ephemeral might not have shown
        except Exception as e:
            print(f"{LogColors.WARNING}Could not add reaction to myvotes command: {e}{LogColors.ENDC}")

    @commands.command(name='brief')
    async def post_briefing_command_v2(self, ctx, briefing_file: str = None):
        if not briefing_file:
            # Point to a V2 default if applicable, or require explicit path for now
            briefing_file = os.getenv('BRIEFING_FILE_V2', 'the-council/council_briefing/daily.json') 
        await self.post_briefing_to_channel(ctx.channel, briefing_file)
        
    @commands.command(name='multi')
    async def post_briefing_multi_v2(self, ctx, *channel_ids):
        briefing_file = os.getenv('BRIEFING_FILE_V2', 'the-council/council_briefing/daily.json')
        if not channel_ids:
            await ctx.send("Please provide one or more channel IDs.")
            return
        for channel_id in channel_ids:
            try:
                channel = await self.fetch_channel(int(channel_id))
                await self.post_briefing_to_channel(channel, briefing_file)
                await ctx.send(f"Posted V2 briefing to <#{channel_id}>")
            except Exception as e:
                await ctx.send(f"Error posting V2 briefing to channel {channel_id}: {e}")

    async def _format_user_vote_summary_embeds(self, user: discord.User, briefing_data: dict) -> List[discord.Embed]:
        user_id_str = str(user.id)
        user_votes_for_briefing = global_vote_storage_v2.votes.get(user_id_str, {})
        summary_embeds = []

        if not user_votes_for_briefing:
            summary_embed = Embed(title="📋 Your Survey Vote Summary", 
                                  description="You did not cast any votes in this survey session.", 
                                  color=config.colors[0])
            summary_embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
            summary_embeds.append(summary_embed)
            return summary_embeds

        title_embed = Embed(title=f"📋 {user.display_name}\'s Vote Summary", 
                              description=f"Survey Date: {briefing_data.get('date', 'N/A')}", 
                              color=config.colors[0])
        title_embed.set_author(name="Jedai Council Daily Survey", icon_url=self.user.display_avatar.url) 
        title_embed.set_thumbnail(url=user.display_avatar.url) 
        summary_embeds.append(title_embed)

        for kp_idx, kp in enumerate(briefing_data.get('key_points', [])):
            topic_title = kp.get('topic', f'Topic {kp_idx + 1}')
            topic_summary_lines = [] # This will hold lines for the description of the topic_embed

            for q_idx, di in enumerate(kp.get('deliberation_items', [])):
                question_id = di.get('question_id')
                question_text_full = di.get('text', 'Unknown Question')
                
                if question_id in user_votes_for_briefing:
                    voted_answer_key = user_votes_for_briefing[question_id]
                    answer_obj = di.get('multiple_choice_answers', {}).get(voted_answer_key)
                    answer_text_full = answer_obj.get('text', voted_answer_key) if answer_obj else voted_answer_key
                    implication_text = answer_obj.get('implication') if answer_obj else None # Get implication for the chosen answer

                    voted_emoji = "➡️" # Default emoji if not found
                    sorted_answer_keys = sorted(di.get('multiple_choice_answers', {}).keys(), 
                                                key=lambda x: int(x.split('_')[1]) if '_' in x and x.split('_')[1].isdigit() else float('inf'))
                    for i, ans_key_iter in enumerate(sorted_answer_keys):
                        if ans_key_iter == voted_answer_key and i < len(config.number_emojis):
                            voted_emoji = config.number_emojis[i]
                            break
                    
                    # Add question, chosen answer, and its implication to the lines for this topic's embed description
                    topic_summary_lines.append(f"**❓ {question_id}: {question_text_full}**")
                    topic_summary_lines.append(f"{voted_emoji} Your choice ({voted_answer_key}): **{answer_text_full}**")
                    if implication_text and voted_answer_key != 'answer_4': # Don't show for 'Other'
                        topic_summary_lines.append(f"> *Implication: {safe_truncate(implication_text, 500)}*" ) # Using blockquote and italics
                    topic_summary_lines.append("") # Add a blank line for separation before the next question in this topic
            
            if topic_summary_lines: # If user voted on any question in this topic, create an embed for it
                topic_embed = Embed(title=f"📌 Topic: {topic_title}", 
                                    description="\n".join(topic_summary_lines).strip(), # Ensure no leading/trailing newlines in description
                                    color=config.colors[(kp_idx + 1) % len(config.colors)])
                summary_embeds.append(topic_embed)
        
        if len(summary_embeds) == 1: # Only title_embed was added, means no votes matched questions
            no_votes_embed = Embed(title="No Recorded Votes Found for this Briefing's Questions", 
                                 description="Could not match your recorded votes to the questions in this specific briefing structure, or you haven't voted on these questions.", 
                                 color=config.colors[0])
            return [title_embed, no_votes_embed] # Return title + explanation
            
        return summary_embeds

    async def update_survey_message_with_question(self, channel_id: int, topic_data: dict, question_data: dict, is_initial_post: bool = False):
        # channel_id is dm_channel_id for DMs, or interaction.channel_id for initial ephemeral
        survey_key = None
        if hasattr(self, 'active_surveys'): # If using the ephemeral-in-channel model key
            # This key construction needs to be consistent with how it's set.
            # If this function is called from StartSurveyButton's callback via interaction,
            # interaction.channel_id and interaction.user.id are available.
            # For now, let's assume channel_id is the first part of the key if it's a tuple from active_surveys
             # This part needs to align with how survey_key is structured and how this function is called
            # For a DM based flow, channel_id would be the dm_channel.id, which IS the key.
            # For an ephemeral-in-guild-channel flow, the key is (guild_channel_id, user_id)
            # Let's assume channel_id IS the correct key for active_surveys for now.
            survey_state = self.active_surveys.get(channel_id)
        else: # Fallback for older call patterns, though this should be harmonized
            survey_state = self.active_surveys.get(channel_id)


        if not survey_state:
            print(f"{LogColors.WARNING}No active survey for key {channel_id} in update_survey_message_with_question{LogColors.ENDC}")
            # If an interaction object was passed, we could try to send an ephemeral error
            # For now, just return if state is unexpectedly missing.
            return

        briefing_data = survey_state['briefing_data']
        briefing_date = briefing_data.get('date', 'N/A')
        user_id_for_survey = survey_state.get('user_id') # Ensure user_id is in survey_state
        user_obj_for_survey = None
        if user_id_for_survey:
            user_obj_for_survey = await self.fetch_user(user_id_for_survey)

        topic_title = topic_data.get('topic', 'Current Topic')
        question_id = question_data.get('question_id', f'unknown_q_{survey_state.get("current_topic_index",0)}_{survey_state.get("current_question_index",0)}')
        question_text_full = question_data.get('text', 'No question text available.')
        answers = question_data.get('multiple_choice_answers', {})
        
        orange_color = config.colors[1 % len(config.colors)]

        embed_title = f"Topic: {safe_truncate(topic_title,100)}"
        # For DMs/Ephemeral, the first message IS the survey start, so always include full title elements
        if is_initial_post :
            embed_title = f"📝 Jedai Council Daily Survey - Topic: {safe_truncate(topic_title,100)}"
        
        description_lines = [
            f"**❓ Question {question_id}: {question_text_full}**",
            "\n**🗳️ Answer Options (Vote by reacting below):**\n" 
        ]

        sorted_answer_keys = sorted(answers.keys(), key=lambda x: int(x.split('_')[1]) if '_' in x and x.split('_')[1].isdigit() else float('inf'))
        current_valid_reactions_map = {}
        for i, ans_key in enumerate(sorted_answer_keys):
            if i < len(config.number_emojis):
                ans_obj = answers[ans_key]
                ans_text = ans_obj.get('text', 'N/A')
                # Implication is NOT displayed here in the question message
                emoji_to_use = config.number_emojis[i]
                current_valid_reactions_map[emoji_to_use] = ans_key
                
                answer_line = f"{emoji_to_use} {ans_text}" 
                description_lines.append(answer_line)
                # Add a blank line between answers, if not the last one
                if i < len(sorted_answer_keys) - 1 and i < len(config.number_emojis) -1:
                    description_lines.append("") 
            else: break

        main_embed = Embed(
            title=embed_title, 
            description="\n".join(description_lines), 
            color=orange_color 
        )

        # Author/thumbnail for DMs should reflect the survey & bot/user context
        if user_obj_for_survey:
            main_embed.set_author(name=f"Survey for {user_obj_for_survey.display_name}", icon_url=self.user.display_avatar.url)
            if is_initial_post : # Show user avatar as thumb on first question in DM
                 main_embed.set_thumbnail(url=user_obj_for_survey.display_avatar.url)
        else: # Fallback if user object couldn't be fetched
            main_embed.set_author(name="Jedai Council Daily Survey", icon_url=self.user.display_avatar.url)

        main_embed.set_footer(text=f"AI Generated Council Survey | {briefing_date} | QID: {question_id}")
        
        embeds_to_send = [main_embed] 

        target_channel = await self.fetch_channel(channel_id) # channel_id is the DM channel ID
        if not target_channel:
            print(f"{LogColors.FAIL}Could not fetch DM channel for ID {channel_id}{LogColors.ENDC}")
            return
            
        message_to_update_or_send = None
        # The SurveyQuestionView holds the "More Context" button.
        # current_question_data is crucial for the MoreContextButton to show relevant specific context.
        current_view = SurveyQuestionView(briefing_data=briefing_data, current_question_data=question_data)

        if is_initial_post or not survey_state.get('current_message_id'):
            message_to_update_or_send = await target_channel.send(embeds=embeds_to_send, view=current_view) 
            survey_state['current_message_id'] = message_to_update_or_send.id
        else:
            try:
                message_to_update_or_send = await target_channel.fetch_message(survey_state['current_message_id'])
                await message_to_update_or_send.edit(embeds=embeds_to_send, view=current_view)
                await message_to_update_or_send.clear_reactions()
            except discord.NotFound:
                print(f"{LogColors.WARNING}Survey message {survey_state['current_message_id']} not found in DM. Posting new.{LogColors.ENDC}")
                message_to_update_or_send = await target_channel.send(embeds=embeds_to_send, view=current_view)
                survey_state['current_message_id'] = message_to_update_or_send.id
            except discord.Forbidden:
                print(f"{LogColors.FAIL}No permission to edit/clear in DM {channel_id}. Posting new.{LogColors.ENDC}")
                message_to_update_or_send = await target_channel.send(embeds=embeds_to_send, view=current_view)
                survey_state['current_message_id'] = message_to_update_or_send.id
            except Exception as e_edit:
                 print(f"{LogColors.ERROR}Error editing message in DM {channel_id}: {e_edit}{LogColors.ENDC}")
                 # Fallback to sending a new message if edit fails for other reasons
                 try:
                    message_to_update_or_send = await target_channel.send(embeds=embeds_to_send, view=current_view)
                    survey_state['current_message_id'] = message_to_update_or_send.id
                 except Exception as e_send_new:
                    print(f"{LogColors.ERROR}Failed to send new message in DM {channel_id} after edit error: {e_send_new}{LogColors.ENDC}")
                    return # Critical failure for this user's survey progression


        for emoji in current_valid_reactions_map.keys():
            try:
                await message_to_update_or_send.add_reaction(emoji)
            except Exception as e_react:
                print(f"{LogColors.WARNING}Failed to add reaction {emoji} in DM {channel_id}: {e_react}{LogColors.ENDC}")

        survey_state['current_question_id'] = question_id
        survey_state['valid_reactions_map'] = current_valid_reactions_map

    async def _get_all_question_ids(self, briefing_data: dict) -> List[str]:
        """Helper to extract all question_ids from the briefing data in order."""
        all_q_ids = []
        if briefing_data and 'key_points' in briefing_data:
            for topic in briefing_data['key_points']:
                for item in topic.get('deliberation_items', []):
                    if 'question_id' in item:
                        all_q_ids.append(item['question_id'])
        return all_q_ids

    async def _save_user_responses_to_csv(self, user: discord.User, user_votes: Dict[str, str], briefing_data: dict):
        """Saves the user's responses to a CSV file."""
        if not briefing_data:
            print(f"{LogColors.WARNING}No briefing data available, cannot save responses for {user.name}{LogColors.ENDC}")
            return

        survey_date = briefing_data.get('date', 'N/A')
        filepath = 'council_survey_responses.csv'
        
        all_question_ids = await self._get_all_question_ids(briefing_data)
        if not all_question_ids:
            print(f"{LogColors.WARNING}No question IDs found in briefing, cannot save responses for {user.name}{LogColors.ENDC}")
            return

        # Updated fieldnames to use discord_username and display_name
        fieldnames = ['discord_username', 'display_name', 'survey_date'] + all_question_ids

        response_row = {
            'discord_username': user.name,       # Global Discord username
            'display_name': user.display_name, # Server nickname or global display name
            'survey_date': survey_date,
        }

        for q_id in all_question_ids:
            answer_key = user_votes.get(q_id)
            if answer_key and isinstance(answer_key, str) and '_' in answer_key:
                try:
                    response_row[q_id] = answer_key.split('_')[1] # Extract number from "answer_X"
                except (IndexError, ValueError):
                    response_row[q_id] = answer_key # Fallback to full key if parsing fails
            else:
                response_row[q_id] = '' # Or 'N/A' if no vote

        file_exists = os.path.isfile(filepath)
        try:
            with open(filepath, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(response_row)
            print(f"{LogColors.SUCCESS}Saved responses for {user.name} to {filepath}{LogColors.ENDC}")
        except Exception as e:
            print(f"{LogColors.FAIL}Error saving responses for {user.name} to CSV: {e}{LogColors.ENDC}")

class MoreContextButton(discord.ui.Button):
    def __init__(self, briefing_data: dict, current_question_data: dict):
        super().__init__(style=ButtonStyle.success, label="ℹ️ Context", custom_id="show_more_context")
        self.briefing_data = briefing_data
        self.current_question_data = current_question_data

    async def callback(self, interaction: discord.Interaction):
        # No defer needed if sending a new message directly
        ephemeral_embeds = []

        # 1. Monthly Goal & Daily Focus
        monthly_goal = self.briefing_data.get('monthly_goal')
        daily_focus = self.briefing_data.get('daily_focus')
        if monthly_goal or daily_focus:
            goal_focus_desc_parts = []
            if monthly_goal: goal_focus_desc_parts.append(f"**Monthly Goal:** {monthly_goal}")
            if daily_focus: goal_focus_desc_parts.append(f"**Daily Focus:** {daily_focus}")
            gf_embed = Embed(title="Current Directives", description="\n".join(goal_focus_desc_parts), color=config.colors[1])
            ephemeral_embeds.append(gf_embed)
        
        # 2. Question-Specific Context
        question_context_list = self.current_question_data.get('context', [])
        question_text_for_title = self.current_question_data.get('text', 'Selected Question')
        if question_context_list:
            context_str = "\n".join([f"- {ctx}" for ctx in question_context_list])
            q_ctx_embed = Embed(title=f"📜 Question-Specific Context for: {safe_truncate(question_text_for_title,70)}", description=safe_truncate(context_str, 1000), color=config.colors[1])
            ephemeral_embeds.append(q_ctx_embed)

        if ephemeral_embeds:
            ephemeral_embeds[-1].set_footer(text="AI generated content")
            # Send as a new ephemeral message, don't edit original
            await interaction.response.send_message(embeds=ephemeral_embeds, ephemeral=True)
        else:
            await interaction.response.send_message("No additional context details (Directives or Question-Specific) are available.", ephemeral=True)

class ImplicationsButton(discord.ui.Button):
    def __init__(self, current_question_data: dict):
        super().__init__(style=ButtonStyle.secondary, label="🔍 Help", custom_id="show_implications")
        self.current_question_data = current_question_data

    async def callback(self, interaction: discord.Interaction):
        # No defer needed if sending a new message directly
        question_text = self.current_question_data.get('text', 'Selected Question')
        answers = self.current_question_data.get('multiple_choice_answers', {})
        
        embed_description_lines = [f"**{question_text}**\n"]
        
        sorted_answer_keys = sorted(answers.keys(), key=lambda x: int(x.split('_')[1]) if '_' in x and x.split('_')[1].isdigit() else float('inf'))

        for i, ans_key in enumerate(sorted_answer_keys):
            ans_obj = answers.get(ans_key, {})
            ans_text = ans_obj.get('text', 'N/A')
            implication = ans_obj.get('implication')
            emoji_label = config.number_emojis[i] if i < len(config.number_emojis) else str(i+1)

            embed_description_lines.append(f"**{emoji_label} {ans_text}**")
            if ans_key != 'answer_4' and implication: 
                embed_description_lines.append(f"> _{safe_truncate(implication, 300)}_\n")
            else:
                embed_description_lines.append("\n")

        if not embed_description_lines or len(embed_description_lines) <=1 : # Check if only the question text was added
            await interaction.response.send_message("No implication details available for this question.", ephemeral=True)
            return

        implications_embed = Embed(
            title="🔍 Answer Implications",
            description="\n".join(embed_description_lines),
            color=config.colors[2 % len(config.colors)] 
        )
        implications_embed.set_footer(text="Review the potential outcomes of each choice.")
        
        # Send as a new ephemeral message, don't edit original
        await interaction.response.send_message(embeds=[implications_embed], ephemeral=True)

class EphemeralAnswerButton(discord.ui.Button):
    def __init__(self, bot_instance: "CouncilBotV2", survey_key: Tuple[int, int], question_id: str, answer_key: str, answer_text: str, button_label: str):
        super().__init__(style=ButtonStyle.primary, 
                         label=button_label, 
                         custom_id=f"ephemeral_vote_{question_id}_{answer_key}")
        self.bot = bot_instance
        self.survey_key = survey_key # (channel_id, user_id)
        self.question_id = question_id
        self.answer_key = answer_key

    async def callback(self, interaction: discord.Interaction):
        # Defer the interaction first, keeping it ephemeral
        await interaction.response.defer(ephemeral=True)

        if self.survey_key not in self.bot.active_surveys:
            try:
                # Try to edit the original response to indicate expiry
                await interaction.edit_original_response(content="This survey session has expired or is no longer active.", embeds=[], view=None)
            except discord.NotFound:
                pass 
            except Exception as e:
                print(f"{LogColors.WARNING}Could not edit expired survey message: {e}{LogColors.ENDC}")
            return
        
        user_id_str = str(self.survey_key[1]) 
        global_vote_storage_v2.cast_vote(user_id_str, self.question_id, self.answer_key)
        
        # message_to_edit is no longer needed here
        
        await self.bot.progress_ephemeral_survey(interaction, self.survey_key) # Pass interaction

class EphemeralSurveyQuestionView(discord.ui.View):
    def __init__(self, bot_instance: "CouncilBotV2", survey_key: Tuple[int,int], briefing_data: dict, current_question_data: dict):
        super().__init__(timeout=1800)
        self.bot = bot_instance
        self.survey_key = survey_key
        self.briefing_data = briefing_data
        self.current_question_data = current_question_data

        answers = current_question_data.get('multiple_choice_answers', {})
        question_id = current_question_data.get('question_id', 'unknown_q')
        sorted_answer_keys = sorted(answers.keys(), key=lambda x: int(x.split('_')[1]) if '_' in x and x.split('_')[1].isdigit() else float('inf'))

        for i, ans_key in enumerate(sorted_answer_keys):
            if i < 10: 
                ans_obj = answers[ans_key]
                ans_text = ans_obj.get('text', 'N/A')
                button_numeric_label = str(i + 1)
                
                button = EphemeralAnswerButton(
                    bot_instance=self.bot,
                    survey_key=self.survey_key,
                    question_id=question_id,
                    answer_key=ans_key,
                    answer_text=ans_text, 
                    button_label=button_numeric_label 
                )
                self.add_item(button)
            else: break

        self.add_item(MoreContextButton(briefing_data, current_question_data))
        self.add_item(ImplicationsButton(current_question_data)) # Add the new button

class StartSurveyButton(discord.ui.Button):
    def __init__(self, briefing_data_to_pass: dict, bot_instance: "CouncilBotV2"):
        super().__init__(style=ButtonStyle.success, label="🗳️ Start Survey", custom_id="start_ephemeral_survey_v2")
        self.briefing_data = briefing_data_to_pass
        self.bot = bot_instance

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        channel_id = interaction.channel_id
        survey_key = (channel_id, user.id) # Use (channel_id, user_id) as key

        if not self.briefing_data.get('key_points') or not self.briefing_data['key_points'][0].get('deliberation_items'):
            await interaction.response.send_message("Sorry, the briefing data seems incomplete for the survey.", ephemeral=True)
            return

        # Initialize or re-initialize survey state for this user in this channel
        self.bot.active_surveys[survey_key] = {
            'briefing_data': self.briefing_data,
            'user_id': user.id,
            'current_topic_index': 0,
            'current_question_index': 0, 
            # 'current_message_id' is not needed for ephemeral progression
            # 'valid_reactions_map' will be replaced by button custom_ids
        }
        
        first_topic_data = self.briefing_data['key_points'][0]
        first_question_data = first_topic_data['deliberation_items'][0]
        
        embeds, view = await self.bot._prepare_question_content(first_topic_data, first_question_data, survey_key, is_initial_question=True)

        if view is None and embeds and "Error" in embeds[0].title: # Check if _prepare_question_content signaled an error
            await interaction.response.send_message(embeds=embeds, ephemeral=True)
        else:
            await interaction.response.send_message(embeds=embeds, view=view, ephemeral=True)

class InitialSurveyView(discord.ui.View):
    def __init__(self, briefing_data: dict, bot_instance: "CouncilBotV2"):
        super().__init__(timeout=None) 
        self.add_item(StartSurveyButton(briefing_data, bot_instance))

# --- Main Execution ---
def main():
    parser = argparse.ArgumentParser(description="Enhanced Interactive Council Bot (V2 Schema)")
    parser.add_argument("--briefing-file", help="Path to V2 council briefing JSON file (e.g., the-council/council_briefing/YYYY-MM-DD.json)")
    parser.add_argument("--channels", help="Comma-separated list of Discord channel IDs to auto-post to")
    args = parser.parse_args()
    
    if args.briefing_file:
        os.environ['BRIEFING_FILE'] = args.briefing_file # Bot uses BRIEFING_FILE internally
    if args.channels:
        os.environ['TARGET_CHANNEL_IDS'] = args.channels
    
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print(f"{LogColors.FAIL}Error: DISCORD_BOT_TOKEN environment variable not set{LogColors.ENDC}")
        sys.exit(1)
    
    bot = CouncilBotV2()
    try:
        bot.run(token)
    except KeyboardInterrupt:
        print(f"{LogColors.WARNING}Bot V2 interrupted by user{LogColors.ENDC}")
    except Exception as e:
        print(f"{LogColors.FAIL}Bot V2 error: {e}{LogColors.ENDC}")

if __name__ == "__main__":
    main() 
