#!/usr/bin/env python3
"""
Enhanced Interactive Council Bot for ElizaOS
Combines the best of both worlds: interactive features + advanced LLM processing
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
import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any

# Configuration similar to webhook script but focused on council briefings
@dataclass
class CouncilBotConfig:
    """Configuration for the council bot"""
    # Discord Colors
    colors: List[int] = field(default_factory=lambda: [
        0x2026ad, 0xe67e22, 0x9b59b6, 0x2ecc71, 0x1abc9c, 0xf1c40f
    ])  # Blue, Orange, Purple, Green, Teal, Yellow
    
    number_emojis: List[str] = field(default_factory=lambda: ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣'])
    
    # OpenRouter Configuration for summarization
    openrouter_endpoint: str = "https://openrouter.ai/api/v1/chat/completions"
    default_summary_model: str = "google/gemini-2.5-flash-preview"
    max_embed_length: int = 2000
    
    # URLs
    hackmd_book_url: str = "https://hackmd.io/@elizaos/book"
    avatar_url: str = "https://m3-org.github.io/avatars/eliza/thumb-bust_eliza.png"

# ANSI escape codes for console colors (for logging)
class LogColors:
    HEADER = '\033[95m'
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    DIM = '\033[2m'

# Global config
config = CouncilBotConfig()

# Vote storage (in production, this would be a database)
class VoteStorage:
    def __init__(self):
        self.votes = {}  # {user_id: point_index}
        self.vote_counts = [0, 0, 0, 0, 0]  # Support up to 5 points
        
    def reset_votes(self):
        """Reset all votes for a new day"""
        self.votes.clear()
        self.vote_counts = [0] * len(self.vote_counts)
        
    def cast_vote(self, user_id: str, point_index: int) -> Tuple[bool, str, Optional[int]]:
        """
        Cast or change a vote
        Returns: (success, message, previous_vote_index)
        """
        previous_vote = self.votes.get(user_id)
        
        if previous_vote == point_index:
            return False, "already_voted", previous_vote
            
        if previous_vote is not None:
            # Change vote
            self.vote_counts[previous_vote] -= 1
            self.vote_counts[point_index] += 1
            self.votes[user_id] = point_index
            return True, "vote_changed", previous_vote
        else:
            # New vote
            self.vote_counts[point_index] += 1
            self.votes[user_id] = point_index
            return True, "vote_cast", None
            
    def get_vote_counts(self) -> List[int]:
        return self.vote_counts.copy()
        
    def get_total_votes(self) -> int:
        return sum(self.vote_counts)

# Global vote storage
vote_storage = VoteStorage()

def safe_truncate(text: str, max_len: int) -> str:
    """Truncate text at logical breakpoints"""
    if len(text) <= max_len:
        return text
    
    truncated = text[:max_len]
    
    # Try to cut at logical breakpoints
    for separator in ['\n\n', '. ', '.\n', '\n']:
        idx = truncated.rfind(separator)
        if idx > 0 and idx > max_len - 150:
            return truncated[:idx + len(separator)].rstrip() + "..."
    
    # Fallback: cut at last word boundary
    last_space = truncated.rfind(' ')
    if last_space > max_len - 50:
        return truncated[:last_space].rstrip() + "..."
    
    return truncated.rstrip() + "..."

async def summarize_text_openrouter(text: str, api_key: str, model: str, target_length: int) -> str:
    """Summarize text using OpenRouter API"""
    if not api_key or len(text) <= target_length:
        return text
        
    prompt = f"""Summarize this council briefing content for Discord. Keep key insights and make it engaging.
Target length: ~{target_length} characters. Be comprehensive but concise.

CONTENT:
{text}

SUMMARY:"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/elizaOS/knowledge",
        "X-Title": "Council Bot Summarizer"
    }
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max(100, int(target_length / 3.0))
    }
    
    try:
        response = requests.post(config.openrouter_endpoint, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        summary = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        
        if summary and len(summary) < len(text):
            return summary[:target_length] if len(summary) > target_length else summary
        else:
            return safe_truncate(text, target_length)
            
    except Exception as e:
        print(f"Summarization failed: {e}")
        return safe_truncate(text, target_length)

class CouncilInteractionView(View):
    """Interactive view for council briefing with buttons"""
    
    def __init__(self, briefing_data: dict, openrouter_api_key: Optional[str] = None):
        super().__init__(timeout=24*3600)  # 24 hour timeout
        self.briefing_data = briefing_data
        self.openrouter_api_key = openrouter_api_key
        
        # Add info buttons
        for i, point in enumerate(briefing_data['key_strategic_points']):
            self.add_item(InfoButton(i, point['theme'][:20] + "..." if len(point['theme']) > 20 else point['theme']))
        
        # Add vote buttons
        for i, point in enumerate(briefing_data['key_strategic_points']):
            self.add_item(VoteButton(i, f"Vote {config.number_emojis[i]}"))
            
        # Add results button
        self.add_item(ResultsButton())

class InfoButton(Button):
    """Button to show detailed information about a strategic point"""
    
    def __init__(self, point_index: int, label: str):
        super().__init__(
            style=ButtonStyle.secondary,
            label=f"Info {point_index + 1}",
            custom_id=f"info_{point_index}",
            row=0 if point_index < 2 else 1
        )
        self.point_index = point_index
        
    async def callback(self, interaction: discord.Interaction):
        view = self.view
        briefing_data = view.briefing_data
        point = briefing_data['key_strategic_points'][self.point_index]
        
        # Create detailed embeds
        summary_text = point['summary']
        if view.openrouter_api_key and len(summary_text) > config.max_embed_length:
            summary_text = await summarize_text_openrouter(
                summary_text, view.openrouter_api_key, config.default_summary_model, config.max_embed_length
            )
        
        main_embed = Embed(
            title=f"{config.number_emojis[self.point_index]} {point['theme']}",
            description=safe_truncate(summary_text, config.max_embed_length),
            color=config.colors[self.point_index % len(config.colors)]
        )
        main_embed.set_author(name="DETAILED ANALYSIS", url=config.hackmd_book_url)
        
        # Context embed
        context_text = "\n".join([f"• {ctx}" for ctx in point['related_operational_context']])
        context_embed = Embed(
            title="Supporting Evidence",
            description=safe_truncate(context_text, config.max_embed_length),
            color=config.colors[self.point_index % len(config.colors)]
        )
        
        # Questions embed
        questions_text = "\n".join([f"**{i+1}.** {q}" for i, q in enumerate(point['potential_council_questions'])])
        questions_embed = Embed(
            title="Discussion Questions",
            description=safe_truncate(questions_text, config.max_embed_length),
            color=config.colors[self.point_index % len(config.colors)]
        )
        questions_embed.set_footer(text=f"Vote for topics you find most important • {briefing_data['date']}")
        
        await interaction.response.send_message(
            embeds=[main_embed, context_embed, questions_embed],
            ephemeral=True
        )

class VoteButton(Button):
    """Button to vote for a strategic point"""
    
    def __init__(self, point_index: int, label: str):
        super().__init__(
            style=ButtonStyle.primary,
            label=label,
            custom_id=f"vote_{point_index}",
            row=2 if point_index < 2 else 3
        )
        self.point_index = point_index
        
    async def callback(self, interaction: discord.Interaction):
        view = self.view
        briefing_data = view.briefing_data
        user_id = str(interaction.user.id)
        
        success, result_type, previous_vote = vote_storage.cast_vote(user_id, self.point_index)
        
        point_name = briefing_data['key_strategic_points'][self.point_index]['theme']
        
        if result_type == "already_voted":
            message = f"You've already voted for **{point_name}**"
        elif result_type == "vote_changed":
            previous_name = briefing_data['key_strategic_points'][previous_vote]['theme']
            message = f"Vote changed from **{previous_name}** to **{point_name}**"
        else:  # vote_cast
            message = f"Vote recorded for **{point_name}**"
            
        await interaction.response.send_message(message, ephemeral=True)

class ResultsButton(Button):
    """Button to show voting results"""
    
    def __init__(self):
        super().__init__(
            style=ButtonStyle.success,
            label="View Results",
            custom_id="results",
            row=4
        )
        
    async def callback(self, interaction: discord.Interaction):
        view = self.view
        briefing_data = view.briefing_data
        vote_counts = vote_storage.get_vote_counts()
        total_votes = vote_storage.get_total_votes()
        
        results_embed = Embed(
            title=f"Voting Results – {briefing_data['date']}",
            color=config.colors[0]
        )
        results_embed.set_author(name="COUNCIL VOTES", url=config.hackmd_book_url)
        
        for i, point in enumerate(briefing_data['key_strategic_points']):
            count = vote_counts[i] if i < len(vote_counts) else 0
            percentage = (count / total_votes * 100) if total_votes > 0 else 0
            
            results_embed.add_field(
                name=f"{config.number_emojis[i]} {point['theme']}",
                value=f"**{count} vote{'s' if count != 1 else ''}** ({percentage:.1f}%)",
                inline=False
            )
            
        results_embed.set_footer(text=f"Total votes: {total_votes} • {briefing_data['date']}")
        
        await interaction.response.send_message(embed=results_embed, ephemeral=True)

class CouncilBot(commands.Bot):
    """Enhanced Council Bot"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!council-', intents=intents)
        
    async def on_ready(self):
        print(f'{LogColors.SUCCESS}Council Bot logged in as {self.user}{LogColors.ENDC}')
        
        # Auto-post if channels are specified
        target_channels = os.getenv('TARGET_CHANNEL_IDS', '').split(',')
        briefing_file = os.getenv('BRIEFING_FILE')
        
        if target_channels and briefing_file and target_channels != ['']:
            await self.auto_post_briefing(target_channels, briefing_file)
    
    async def auto_post_briefing(self, channel_ids: List[str], briefing_file: str):
        """Auto-post briefing to specified channels"""
        try:
            for channel_id in channel_ids:
                if channel_id.strip():
                    try:
                        channel = await self.fetch_channel(int(channel_id.strip()))
                        await self.post_briefing_to_channel(channel, briefing_file)
                        print(f'{LogColors.SUCCESS}Posted to channel {channel_id}{LogColors.ENDC}')
                    except Exception as e:
                        print(f'{LogColors.FAIL}Error posting to channel {channel_id}: {e}{LogColors.ENDC}')
        except Exception as e:
            print(f'{LogColors.FAIL}Error in auto-post: {e}{LogColors.ENDC}')
    
    async def post_briefing_to_channel(self, channel, briefing_file: str):
        """Post council briefing to a specific channel"""
        try:
            # Reset votes for new briefing
            vote_storage.reset_votes()
            
            with open(briefing_file, 'r') as f:
                briefing_data = json.load(f)
                
            openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
            
            # Create header embed
            monthly_goal = briefing_data['monthly_goal']
            if ':' in monthly_goal:
                monthly_goal = monthly_goal.split(':', 1)[1].strip()
                
            header_embed = Embed(
                title=f"🧠 Council Briefing – {briefing_data['date']}",
                description=f"{briefing_data['daily_focus_theme']}\n\n**Monthly Goal:** {monthly_goal}",
                color=config.colors[0],
                timestamp=datetime.utcnow()
            )
            header_embed.set_author(name="JEDAI COUNCIL DAILY", url=config.hackmd_book_url)
            header_embed.set_thumbnail(url=config.avatar_url)
            
            # Create point embeds with just questions for overview
            point_embeds = []
            for i, point in enumerate(briefing_data['key_strategic_points']):
                questions_text = " ".join(point['potential_council_questions'])
                
                point_embed = Embed(
                    title=f"{config.number_emojis[i]} {point['theme']}",
                    description=safe_truncate(questions_text, config.max_embed_length),
                    color=config.colors[i % len(config.colors)]
                )
                point_embeds.append(point_embed)
            
            # Add footer to last embed
            if point_embeds:
                point_embeds[-1].set_footer(
                    text=f"Click buttons below to explore topics and vote • {briefing_data['date']}"
                )
            
            # Create interactive view
            view = CouncilInteractionView(briefing_data, openrouter_api_key)
            
            # Send message with embeds and interactive components
            await channel.send(
                embeds=[header_embed] + point_embeds,
                view=view
            )
            
        except Exception as e:
            print(f'{LogColors.FAIL}Error posting briefing: {e}{LogColors.ENDC}')
            await channel.send(f"Error loading briefing: {e}")

    @commands.command(name='brief')
    async def post_briefing_command(self, ctx, briefing_file: str = None):
        """Command to post briefing to current channel"""
        if not briefing_file:
            briefing_file = os.getenv('BRIEFING_FILE', '../the-council/council_briefing/daily.json')
            
        await self.post_briefing_to_channel(ctx.channel, briefing_file)
        
    @commands.command(name='multi')
    async def post_briefing_multi(self, ctx, *channel_ids):
        """Command to post briefing to multiple channels"""
        briefing_file = os.getenv('BRIEFING_FILE', '../the-council/council_briefing/daily.json')
        
        for channel_id in channel_ids:
            try:
                channel = await self.fetch_channel(int(channel_id))
                await self.post_briefing_to_channel(channel, briefing_file)
                await ctx.send(f"Posted to <#{channel_id}>")
            except Exception as e:
                await ctx.send(f"Error posting to {channel_id}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Enhanced Interactive Council Bot")
    parser.add_argument("--briefing-file", help="Path to council briefing JSON file")
    parser.add_argument("--channels", help="Comma-separated list of Discord channel IDs to auto-post to")
    args = parser.parse_args()
    
    # Set environment variables if provided
    if args.briefing_file:
        os.environ['BRIEFING_FILE'] = args.briefing_file
    if args.channels:
        os.environ['TARGET_CHANNEL_IDS'] = args.channels
    
    # Check for required token
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print(f"{LogColors.FAIL}Error: DISCORD_BOT_TOKEN environment variable not set{LogColors.ENDC}")
        sys.exit(1)
    
    # Create and run bot
    bot = CouncilBot()
    try:
        bot.run(token)
    except KeyboardInterrupt:
        print(f"{LogColors.WARNING}Bot interrupted by user{LogColors.ENDC}")
    except Exception as e:
        print(f"{LogColors.FAIL}Bot error: {e}{LogColors.ENDC}")

if __name__ == "__main__":
    main() 