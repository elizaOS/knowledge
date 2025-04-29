# elizaOS Tweet Summarizer

A script to generate tweets from GitHub activity logs in the elizaOS brand voice.

## Overview

This script takes GitHub activity logs (daily or weekly updates) and generates tweets that follow the elizaOS brand guidelines. It can also generate tweets in the auto.fun sub-brand style for a more chaotic, terminal-native voice.

## Requirements

- Bash shell
- `curl` and `jq` command-line tools
- OpenRouter API key

## Installation

1. Make the script executable:
   ```bash
   chmod +x tweet-summarizer.sh
   ```

2. Set your OpenRouter API key as an environment variable (optional):
   ```bash
   export OPENROUTER_API_KEY="your-api-key-here"
   ```

## Usage

```bash
./tweet-summarizer.sh -i <input_file> [-m <model>] [-o <output_file>] [-k <api_key>] [-b <brand>] [-p <prompt_file>]
```

### Options

- `-i`: Input file to summarize (required): markdown file from github/day or github/week
- `-m`: OpenRouter model to use (default: anthropic/claude-3.7-sonnet)
- `-o`: Output file for the tweet (default: tweets/input_filename_brand_tweet.txt)
- `-k`: OpenRouter API key (optional, can also use OPENROUTER_API_KEY env var)
- `-b`: Brand style to use: 'elizaos' (default) or 'autofun'
- `-p`: Custom prompt file to use (optional, overrides -b option)
- `-h`: Display help message

### Examples

Generate a tweet in the elizaOS brand style:
```bash
./tweet-summarizer.sh -i github/day/2025-04-06.md
```

Generate a tweet in the auto.fun brand style:
```bash
./tweet-summarizer.sh -i github/week/2025-04-06.md -b autofun
```

Specify a custom output file:
```bash
./tweet-summarizer.sh -i github/day/2025-04-06.md -o my_tweet.txt
```

Use a different model:
```bash
./tweet-summarizer.sh -i github/day/2025-04-06.md -m anthropic/claude-3-opus
```

Use a custom prompt file:
```bash
./tweet-summarizer.sh -i github/day/2025-04-06.md -p my_custom_prompt.txt
```

## Prompt Files

The script uses external prompt files for easier maintenance and extensibility. The default prompt files are located in the `prompts` directory:

- `prompts/elizaos_prompt.txt`: Prompt for the elizaOS brand style
- `prompts/autofun_prompt.txt`: Prompt for the auto.fun brand style

You can create your own prompt files and use them with the `-p` option. The prompt files use the following placeholders:

- `{UPDATE_TYPE}`: Replaced with "daily" or "weekly"
- `{CONTENT}`: Replaced with the content of the input file

## Brand Guidelines

### elizaOS Brand

The elizaOS brand tweets follow these guidelines:
- Calm, stable, declarative tone
- Minimal and intentional (no filler)
- Domain-specific terms used correctly
- Slightly uncanny when appropriate (poetic, synthetic)
- Speaks to contributors, not consumers
- No marketing speak, consumer-centric tone, or excessive hype
- No emojis or @ mentions
- Lowercase for brand soft tone
- Technically fluent and emotionally intelligent

### auto.fun Sub-Brand

The auto.fun sub-brand tweets follow these guidelines:
- Fast-talking, smart-degen, meme-aware tone
- Technically accurate but with a crypto-twitter vibe
- Lowercase for everything
- Concise and impactful
- No emojis or @ mentions
- Technically fluent with a hint of chaos

## Integration with GitHub Actions

You can integrate this script with the existing GitHub Actions workflow to automatically generate tweets for each daily and weekly update. The workflow is configured to run daily at 5 AM UTC (after the sync workflow) and will generate tweets for both the latest daily update and the latest weekly update (on Mondays).

The generated tweets are saved to the `tweets` directory and committed to the repository. 