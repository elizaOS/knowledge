# ElizaOS Briefing Bots

This directory contains two specialized bots for handling different types of ElizaOS briefings:

## 🤖 Scripts Overview

### 1. `webhook-refactored.py` - Facts Briefing Bot
**Purpose**: Handles daily facts briefings with LLM summarization and webhook posting
- **Input**: Facts briefing JSON files (containing `categories` and `briefing_date`)
- **Output**: Discord webhook posts with rich embeds and visual summaries
- **Best for**: Automated daily summaries, simple content distribution

### 2. `council-bot-enhanced.py` - Interactive Council Bot  
**Purpose**: Interactive Discord bot for strategic council briefings with voting and engagement
- **Input**: Council briefing JSON files (containing `key_strategic_points` and `daily_focus_theme`)
- **Output**: Interactive Discord messages with buttons for detailed exploration and voting
- **Best for**: Strategic discussions, community engagement, decision-making

## 🚀 Quick Start

### Facts Briefing (webhook-refactored.py)

```bash
# Simple webhook post
python scripts/webhook-refactored.py the-council/facts/2025-05-18.json -d -c "CHANNEL_ID" -s

# Multiple channels
python scripts/webhook-refactored.py the-council/facts/2025-05-18.json -d -c "ID1,ID2,ID3" -s

# JSON export for curl
python scripts/webhook-refactored.py the-council/facts/2025-05-18.json -o payload.json -s
```

### Interactive Council Bot (council-bot-enhanced.py)

```bash
# Auto-post to channels on startup
DISCORD_BOT_TOKEN=your_token BRIEFING_FILE=the-council/council_briefing/daily.json TARGET_CHANNEL_IDS="ID1,ID2" python scripts/council-bot-enhanced.py

# Manual posting via commands
python scripts/council-bot-enhanced.py --briefing-file the-council/council_briefing/daily.json

# Then use Discord commands:
# !council-brief                    - Post to current channel
# !council-multi CHANNEL_ID1 ID2   - Post to multiple channels
```

## 📊 Features Comparison

| Feature | Facts Bot | Council Bot |
|---------|-----------|-------------|
| **LLM Summarization** | ✅ Advanced budget system | ✅ Context-aware summaries |
| **Multiple Channels** | ✅ Sequential posting | ✅ Auto-post + commands |
| **JSON Export** | ✅ For curl usage | ❌ Interactive only |
| **Button Interactions** | ❌ Static embeds | ✅ Info, Vote, Results |
| **Voting System** | ❌ | ✅ With percentages |
| **Detailed Expansion** | ❌ | ✅ Ephemeral detailed views |
| **Persistent State** | ❌ | ✅ 24-hour voting sessions |

## 🎯 When to Use Which Bot

### Use Facts Bot (`webhook-refactored.py`) when:
- ✅ You have **facts briefing data** with categories (Twitter, GitHub, Discord, etc.)
- ✅ You want **automated, scheduled posting** 
- ✅ You need **webhook compatibility** for external systems
- ✅ You want **JSON export** for curl or other tools
- ✅ Content is **informational** and doesn't require interaction

### Use Council Bot (`council-bot-enhanced.py`) when:
- ✅ You have **council briefing data** with strategic points
- ✅ You want **community engagement** and discussion
- ✅ You need **voting** on strategic priorities
- ✅ You want **detailed exploration** of topics via buttons
- ✅ Content requires **decision-making** or **feedback**

## 🔧 Environment Variables

### Both Bots
```bash
DISCORD_BOT_TOKEN=your_discord_bot_token
OPENROUTER_API_KEY=your_openrouter_key  # Optional, for LLM summarization
```

### Facts Bot Additional
```bash
# None required - uses command line arguments
```

### Council Bot Additional  
```bash
BRIEFING_FILE=path/to/council_briefing.json    # Auto-load briefing file
TARGET_CHANNEL_IDS="123,456,789"               # Auto-post channels
```

## 📋 Data Format Requirements

### Facts Briefing JSON Structure
```json
{
  "briefing_date": "2025-05-18",
  "overall_summary": "...",
  "categories": {
    "twitter_news_highlights": [{"claim": "..."}],
    "github_updates": {"overall_focus": [{"claim": "..."}]},
    "discord_updates": [{"channel": "...", "summary": "..."}],
    "strategic_insights": [{"theme": "...", "insight": "..."}],
    "market_analysis": [{"observation": "..."}]
  }
}
```

### Council Briefing JSON Structure
```json
{
  "date": "2025-05-22", 
  "daily_focus_theme": "...",
  "monthly_goal": "Current focus: ...",
  "key_strategic_points": [
    {
      "theme": "Strategic Topic",
      "summary": "Detailed analysis...",
      "related_operational_context": ["Evidence 1", "Evidence 2"],
      "potential_council_questions": ["Question 1?", "Question 2?"]
    }
  ]
}
```

## 🎨 Visual Examples

### Facts Bot Output
- **Main Embed**: Overall summary with HackMD link
- **Section Embeds**: Twitter, GitHub, Discord, Strategy, Market
- **Poster Embed**: Visual summary image
- **Smart Bullets**: Automatic bullet points for appropriate sections
- **Budget System**: Intelligent content allocation

### Council Bot Output
- **Header Embed**: Theme and monthly goal
- **Point Embeds**: Strategic points with discussion questions  
- **Interactive Buttons**: 
  - `Info 1-4`: Detailed analysis (ephemeral)
  - `Vote 1️⃣-4️⃣`: Cast votes for priorities
  - `View Results`: Voting statistics (ephemeral)

## 🔄 Migration from Original

### From `webhook-combined.py`
The facts functionality has been **preserved and enhanced** in `webhook-refactored.py`:
- ✅ Same proven budget system
- ✅ Same LLM summarization  
- ✅ Same multi-channel support
- ✅ Cleaner, more maintainable code
- ❌ Council briefing support removed (use council bot instead)

### From `council-bot.js`  
The JavaScript council bot is **superseded** by `council-bot-enhanced.py`:
- ✅ All existing functionality preserved
- ✅ Advanced LLM summarization added
- ✅ Better error handling and logging
- ✅ More robust vote management
- ✅ Enhanced visual presentation

## 🚧 Troubleshooting

### Common Issues

**"Unknown briefing format" error**
- Make sure you're using the right bot for your data format
- Facts bot expects `categories` + `briefing_date`
- Council bot expects `key_strategic_points` + `daily_focus_theme`

**Discord connection errors**
- Verify `DISCORD_BOT_TOKEN` is set correctly
- Ensure bot has permissions in target channels
- Check channel IDs are valid

**LLM summarization not working**
- Set `OPENROUTER_API_KEY` environment variable
- Use `-s` flag for facts bot
- Check API key balance/permissions

**Buttons not working (Council Bot)**
- Ensure bot uses `discord.py` 2.0+ with interactions
- Bot needs `Send Messages` and `Use Slash Commands` permissions
- Views timeout after 24 hours (repost for fresh interactions)

## 📈 Performance & Line Count

| Script | Lines | Purpose | Complexity |
|--------|-------|---------|------------|
| `webhook-combined.py` | 823 | Combined facts + council | High |
| `webhook-refactored.py` | 845 | Facts only | Medium |
| `council-bot-enhanced.py` | 431 | Council only | Medium |

**Total reduction**: Single 823-line file → Two focused files (1276 lines total)
- **Benefit**: Clearer separation of concerns, easier maintenance
- **Trade-off**: Slightly more total lines due to separate configurations

## 🔮 Future Enhancements

### Facts Bot
- [ ] Database integration for vote storage  
- [ ] Slack/Teams webhook support
- [ ] Custom embed templates
- [ ] Analytics and metrics

### Council Bot
- [ ] Database-backed vote persistence
- [ ] Scheduled briefing posts
- [ ] User role-based voting weights
- [ ] Discussion thread creation
- [ ] Vote deadline timers

---

**Note**: This separation allows each bot to evolve independently while maintaining their core strengths. Facts bot excels at content distribution, while Council bot excels at community engagement. 