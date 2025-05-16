# Scripts

This directory contains various scripts for automating tasks related to content aggregation, generation, and publishing for the elizaOS knowledge system.

## `aggregate_sources.py`

**Purpose**: Aggregates content from diverse data sources into a unified daily JSON file.

**Details**:
This Python script is the primary engine for collecting daily context. It navigates predefined paths within the workspace (e.g., `ai-news/` subfolders for elizaos, discord, and dev content in both Markdown and JSON formats, `github/summaries/` for daily, weekly, and monthly GitHub activity summaries, and `github/stats/month/` for monthly statistics). It also processes `github/user_summaries.ndjson` to extract recent user activity.
The script intelligently reads text and JSON files, handling potential errors gracefully. For date-specific content, it can fetch files for a given date or the latest available.
The final output is a structured JSON file named `the-council/YYYY-MM-DD.json`, where `YYYY-MM-DD` is the target date. This file serves as the foundational input for other context generation and summarization scripts.

**Usage**:
```bash
./scripts/aggregate_sources.py [YYYY-MM-DD]
```
- If `[YYYY-MM-DD]` is provided, it generates the context for that specific date.
- If no date is provided, it defaults to the current date.

**Dependencies**: Python 3.

**Status**: Deprecated. Use `aggregate_sources.py` instead.

---

## `prompts/` Directory

**Purpose**: This directory houses all the prompt template files used by various scripts for interacting with Language Models (LLMs).

**Structure**:
- Prompt files are typically plain text (`.txt`) files.
- Subdirectories within `prompts/` (e.g., `prompts/comms/`, `prompts/dev/`, `prompts/strategy/`) are used by scripts like `create-hackmd.py` and `update-hackmd.py` to categorize the generated content and corresponding HackMD notes. The name of the subdirectory often becomes a category tag.
- Individual prompt files are named to reflect their specific purpose (e.g., `elizaos_prompt.txt`, `user_feedback_prompt.txt`). These names are also used by `create-hackmd.py` when generating titles or identifying notes.

**Usage**:
- Scripts such as `tweet-summarizer.sh`, `summarize.sh`, `process_prompts.sh`, `generate_council_context.py`, and `update-hackmd.py` utilize these files to provide specific instructions, context, and formatting guidance to the LLM for tasks like content generation, summarization, or reformatting.
- Some prompt files may contain placeholders (e.g., `{CONTENT}`, `{UPDATE_TYPE}`) that the calling script replaces with dynamic data before sending the complete prompt to the LLM.

---

## `generate_council_context.py`

**Purpose**: Generates a high-level "council context" summary from the daily aggregated data.

**Details**:
This Python script takes the `the-council/YYYY-MM-DD.json` file (produced by `aggregate_sources.py`) as its main input. It uses a predefined prompt (or one implicitly embedded) to process this aggregated data through an AI model via the OpenRouter API (specifically `anthropic/claude-3.7-sonnet` by default).
The goal is to distill the extensive daily information into a more concise, high-level summary suitable for strategic review or "council" consumption.
The output is another JSON file, typically named `the-council/council_context_YYYY-MM-DD.json`.

**Environment Variables**:
- `OPENROUTER_API_KEY`: Required for API access.
- `HMD_API_ACCESS_TOKEN` or `HACKMD_API_TOKEN`: Required if the script interacts with HackMD (though current primary function seems to be local JSON to JSON processing).

**Dependencies**: Python 3, `requests` library.

---

## `tweet-summarizer.sh`

A script to generate tweets from GitHub activity logs in the elizaOS brand voice.

**Overview**

This script takes GitHub activity logs (daily or weekly updates) and generates tweets that follow the elizaOS brand guidelines. It can also generate tweets in the auto.fun sub-brand style for a more chaotic, terminal-native voice.

**Requirements**

- Bash shell
- `curl` and `jq` command-line tools
- OpenRouter API key

**Installation**

1. Make the script executable:
   ```bash
   chmod +x tweet-summarizer.sh
   ```

2. Set your OpenRouter API key as an environment variable (optional):
   ```bash
   export OPENROUTER_API_KEY="your-api-key-here"
   ```

**Usage**

```bash
./tweet-summarizer.sh -i <input_file> [-m <model>] [-o <output_file>] [-k <api_key>] [-b <brand>] [-p <prompt_file>]
```

**Options**

- `-i`: Input file to summarize (required): markdown file from `github/day` or `github/week`
- `-m`: OpenRouter model to use (default: `anthropic/claude-3.7-sonnet`)
- `-o`: Output file for the tweet (default: `tweets/input_filename_brand_tweet.txt`)
- `-k`: OpenRouter API key (optional, can also use `OPENROUTER_API_KEY` env var)
- `-b`: Brand style to use: 'elizaos' (default) or 'autofun'
- `-p`: Custom prompt file to use (optional, overrides `-b` option)
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