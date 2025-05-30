#!/usr/bin/env python3
"""Optimized Discord Facts Briefing Bot - Under 200 lines with smart features"""
import json, sys, os, argparse, discord, requests, asyncio
from discord import Embed
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

@dataclass
class Config:
    colors = {"github": 0x95a5a6, "discord": 0x5865F2, "feedback": 0x9b59b6, "default": 0xFF8A00}
    openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
    model = "google/gemini-2.5-flash-preview"
    hackmd_url = "https://hackmd.io/@elizaos/book"
    poster_url = "https://elizaos.github.io/knowledge/posters/"
    total_budget, min_section = 1600, 200

config = Config()

class Logger:
    @staticmethod
    def info(msg): print(f"\033[94m{msg}\033[0m")
    @staticmethod
    def success(msg): print(f"\033[92m{msg}\033[0m") 
    @staticmethod
    def warn(msg): print(f"\033[93m{msg}\033[0m")
    @staticmethod
    def error(msg): print(f"\033[91m{msg}\033[0m")

class TextProcessor:
    @staticmethod
    def smart_truncate(text: str, max_len: int) -> str:
        if len(text) <= max_len: return text
        for sep in ['\n• ', '\n- ', '. ', '.\n', '\n', ': ']:
            idx = text[:max_len].rfind(sep)
            if idx > 0 and idx > max_len - 200: return text[:idx + len(sep)].rstrip() + "..."
        words = text[:max_len].split()
        return ' '.join(words[:-1]) + "..." if len(words) > 1 else text[:max_len-3] + "..."
    
    @staticmethod
    def should_use_bullets(key: str, content_len: int, item_count: int) -> bool:
        return item_count > 3 or (key in ["discord", "github"] and content_len > 800) or content_len > 1200
    
    @staticmethod
    def format_feedback_with_sentiment(feedback_item: dict) -> str:
        """Format user feedback with sentiment markers (no code block wrapper)"""
        feedback_text = feedback_item.get('feedback_summary', '')
        sentiment = feedback_item.get('sentiment', 'neutral').lower()
        
        # Summarize the feedback concisely (first ~80 chars)
        summary = feedback_text[:80] + "..." if len(feedback_text) > 80 else feedback_text
        
        # Return just the marker and text - no individual code block wrapper
        marker = "+" if sentiment == "positive" else "-" if sentiment == "negative" else "*"
        return f"{marker} {summary}"
    
    @staticmethod
    def get_enhanced_prompt(section_key: str, target: int, use_bullets: bool = False) -> str:
        """Generate simple, consistent prompts without complex engagement detection"""
        bullet_instruction = "Start each main point with a bullet (•). " if use_bullets else ""
        return (f"Summarize for Discord embed. {bullet_instruction}"
               f"Target {target} characters (aim for {int(target * 0.9)}-{target}). "
               f"Merge similar topics and remove redundancy. BE CONCISE."
               f"ONLY summarize the content - DO NOT repeat back instructions")
    
    @staticmethod
    def calculate_budget(sections_data: List[tuple]) -> Dict[str, int]:
        lengths = {}
        for key, _, items, text_fn, prefix_fn in sections_data:
            if not items: continue
            content = "\n".join(f"{(prefix_fn(item) or '') + ': ' if prefix_fn and prefix_fn(item) else ''}{text_fn(item)}" for item in items)
            lengths[key] = len(content)
        
        total_raw = sum(lengths.values())
        if total_raw == 0: return {}
        
        # Priority weighting: GitHub and Discord get more budget
        priority_weights = {"github": 1.5, "discord": 1.3, "feedback": 1.0}
        
        budgets = {}
        total_weighted = sum(lengths[key] * priority_weights.get(key, 1.0) for key in lengths)
        
        for key, raw_len in lengths.items():
            weight = priority_weights.get(key, 1.0)
            weighted_share = (raw_len * weight) / total_weighted
            budget = int(weighted_share * config.total_budget)
            budgets[key] = max(config.min_section, min(1000, budget))
        return budgets
    
    @staticmethod
    async def summarize(text: str, api_key: str, target: int, section_key: str = "", use_bullets: bool = False) -> str:
        if not api_key or len(text) <= target: return text
        
        # Use enhanced prompt that adapts to content
        prompt = TextProcessor.get_enhanced_prompt(section_key, target, use_bullets)
        # Add the text separately to the prompt
        full_prompt = f"{prompt}:\n\n{text}"
        
        try:
            response = requests.post(config.openrouter_url, 
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": config.model, "messages": [{"role": "user", "content": full_prompt}],
                    "max_tokens": max(100, int(target / 3.0))}, timeout=60)
            result = response.json()["choices"][0]["message"]["content"].strip()
            # Use smart truncation instead of hard slice to avoid mid-word cuts
            return TextProcessor.smart_truncate(result, target) if len(result) > target else result
        except Exception as e:
            Logger.warn(f"LLM failed: {e}")
            return TextProcessor.smart_truncate(text, target)

class EmbedFactory:
    @staticmethod
    def create_main(data: dict) -> Embed:
        # Use overall summary for key observations - simple and objective, no truncation
        overall_summary = data.get('overall_summary', '')
        briefing_date = data.get('briefing_date', 'YYYY-MM-DD') # Get the briefing date
        
        # Construct the new GitHub link for the aggregated JSON
        github_link_base = "https://github.com/elizaOS/knowledge/blob/main/the-council/aggregated/"
        aggregated_json_filename = f"{briefing_date}.json"
        full_github_link = f"{github_link_base}{aggregated_json_filename}"
        link_text = f"Aggregated Sources - {briefing_date}"
        
        embed = Embed(title=f"📊 Eliza Daily – {briefing_date}", 
                     description=f"{overall_summary}\n\n📚 [{link_text}]({full_github_link})", # Updated link and text
                     color=config.colors["default"], timestamp=datetime.utcnow())
        embed.set_author(name="Eliza Daily", url=config.hackmd_url) # Author link can remain or change if needed
        embed.set_thumbnail(url="https://m3-org.github.io/avatars/eliza/thumb-bust_eliza.png")
        return embed
    
    @staticmethod
    async def create_section(key: str, title: str, items: list, text_fn, prefix_fn=None, 
                           budget: int = 800, api_key: str = None) -> Optional[Embed]:
        if not items: return None
        
        content = "\n".join(f"{(prefix_fn(item) or '') + ': ' if prefix_fn and prefix_fn(item) else ''}{text_fn(item)}" for item in items)
        raw_len = len(content)
        
        if api_key and raw_len > budget:
            use_bullets = TextProcessor.should_use_bullets(key, raw_len, len(items))
            Logger.info(f"Section {key}: {raw_len}→{budget} chars" + (" (bullets)" if use_bullets else ""))
            content = await TextProcessor.summarize(content, api_key, budget, key, use_bullets)
        elif raw_len > budget:
            content = TextProcessor.smart_truncate(content, budget)
            
        return Embed(title=title, description=content, color=config.colors.get(key, config.colors["default"]))
    
    @staticmethod
    def create_poster(url: str, date: str) -> Embed:
        embed = Embed(title="📊 Visual Summary", color=0x1abc9c)
        embed.set_image(url=url)
        embed.set_footer(text=f"AI generated • {date}")
        return embed

class BriefingProcessor:
    def __init__(self, api_key: Optional[str] = None): self.api_key = api_key
    
    async def create_embeds(self, file_path: str, poster_file: str) -> Tuple[List[Embed], Optional[str]]:
        try:
            with open(file_path) as f: data = json.load(f)
        except Exception as e:
            return [], f"File error: {e}"
        
        if not all(k in data for k in ['categories', 'briefing_date']):
            return [], "Invalid facts briefing format"
        
        embeds = [EmbedFactory.create_main(data)]
        cats = data['categories']
        
        # Handle user feedback separately to preserve diff formatting
        feedback_items = cats.get('user_feedback', [])
        if feedback_items:
            feedback_lines = []
            for item in feedback_items:
                formatted = TextProcessor.format_feedback_with_sentiment(item)
                feedback_lines.append(formatted)
            
            feedback_content = "\n".join(feedback_lines)
            if feedback_content:
                feedback_embed = Embed(title="📝 User Feedback", description=f"```diff\n{feedback_content}\n```", color=config.colors.get("feedback", config.colors["default"]))
                embeds.append(feedback_embed)
        
        # Regular sections that go through LLM processing
        sections_data = [
            ("github", "⚙️ GitHub", cats.get('github_updates', {}).get('new_issues_prs', []),
             lambda x: f"[{x.get('title', 'Untitled')}]({x.get('url', '#')}) by @{x.get('author', 'unknown')} - {x.get('significance', 'No description')}",
             None),
            ("discord", "💬 Discord", cats.get('discord_updates', []), 
             lambda x: f"[{x.get('channel', 'unknown')}] {x.get('summary', '')} (Participants: {', '.join(x.get('key_participants', []))})",
             None),
        ]
        
        # Filter out sections with no data
        sections_data = [(k, t, items, fn, pfn) for k, t, items, fn, pfn in sections_data if items]
        
        if not sections_data:
            Logger.warn("No priority sections found with data")
            return embeds, None
        
        budgets = TextProcessor.calculate_budget(sections_data)
        Logger.info(f"Priority sections budget allocation: {budgets}")
        
        for key, title, items, text_fn, prefix_fn in sections_data:
            if items and key in budgets:
                embed = await EmbedFactory.create_section(key, title, items, text_fn, prefix_fn, budgets[key], self.api_key)
                if embed: embeds.append(embed)
        
        # Removed separate PR/Issues sections to avoid redundancy
        # GitHub overall_focus already contains the important activity summary
        
        # Only add poster if a filename is provided
        if poster_file:
            embeds.append(EmbedFactory.create_poster(f"{config.poster_url}{poster_file}", data['briefing_date']))
        return embeds, None

async def send_to_discord(file_path: str, channels: str, api_key: str, poster: Optional[str]):
    processor = BriefingProcessor(api_key)
    embeds, error = await processor.create_embeds(file_path, poster)
    
    if error: return Logger.error(f"Processing failed: {error}")
    
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token: return Logger.error("DISCORD_BOT_TOKEN not set")
    
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        Logger.success(f"Logged in as {client.user}")
        success_count = 0
        
        for channel_id in channels.split(','):
            try:
                channel = await client.fetch_channel(int(channel_id.strip()))
                await channel.send(embeds=embeds)
                Logger.success(f"Posted to {channel.name}")
                success_count += 1
            except Exception as e:
                Logger.error(f"Failed to post to {channel_id}: {e}")
        
        Logger.info(f"Successfully posted to {success_count} channel(s)")
        # Close the client after all operations are done
        await client.close()
    
    try:
        await client.start(token)
    except Exception as e:
        Logger.error(f"Discord error: {e}")
    finally:
        # Ensure client is closed and connections are cleaned up
        if not client.is_closed():
            await client.close()
        # Give a moment for cleanup
        await asyncio.sleep(0.1)

async def export_json(file_path: str, output: str, api_key: str, poster: Optional[str]):
    processor = BriefingProcessor(api_key)
    embeds, error = await processor.create_embeds(file_path, poster)
    
    if error: return Logger.error(f"Processing failed: {error}")
    
    payload = {"embeds": [embed.to_dict() for embed in embeds]}
    with open(output, 'w') as f: json.dump(payload, f, indent=2)
    Logger.success(f"Exported to {output}")

def main():
    parser = argparse.ArgumentParser(description="Discord Facts Briefing Bot - Priority Sections Only")
    parser.add_argument("json_file", help="Facts briefing JSON file")
    parser.add_argument("-d", "--discord", action="store_true", help="Send to Discord")
    parser.add_argument("-c", "--channels", help="Discord channel IDs (comma-separated)")
    parser.add_argument("-o", "--out", help="Export to JSON file")
    parser.add_argument("-s", "--summarize", action="store_true", help="Enable LLM summarization")
    parser.add_argument(
        "-p", "--poster", 
        nargs='?', 
        const="hackmd-facts-briefing.png", 
        default=None, 
        help="Poster filename. If -p is used alone, defaults to hackmd-facts-briefing.png. If no -p, no poster."
    )
    
    args = parser.parse_args()
    api_key = os.getenv("OPENROUTER_API_KEY") if args.summarize else None
    
    if args.discord:
        if not args.channels: Logger.error("--channels required with --discord"); sys.exit(1)
        asyncio.run(send_to_discord(args.json_file, args.channels, api_key, args.poster))
    elif args.out:
        asyncio.run(export_json(args.json_file, args.out, api_key, args.poster))
    else:
        Logger.info(f"Use -d for Discord or -o for JSON export")

if __name__ == "__main__": main()
