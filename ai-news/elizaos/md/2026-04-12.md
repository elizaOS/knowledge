## ElizaOS Community and Repository Update - April 12, 2026

## Eliza Labs Shutdown Announcement

- Shaw (shawmakesmagic) announced Eliza Labs is shutting down due to deteriorating market conditions, treasury trending toward zero, and failure to reach revenue targets
- Shaw committed to continuing Eliza as an open source community project and offered to assist displaced team members
- Odilitime expressed willingness to contribute in a personal capacity to keep the project moving forward

## Community and Token Discussions

- Community members raised concerns about the disconnect between ElizaOS development and token value
- Odilitime acknowledged failures in project communications and indicated plans to discuss restructuring Discord and social media presence with Shaw
- A community member proposed allowing a trusted community member to manage social media administration for more consistent updates
- The token delisting from Bitget CEX was attributed to low trading volume, as market makers require sufficient activity to justify listings
- The migration window from ai16z to elizaOS tokens has closed

## Technical Updates

- A developer reported recurring Ollama local model integration errors, including invalid JSON responses and XML parsing failures
- Odilitime recommended Gemma, gptoss, and Qwen as working local model options and noted ongoing work to improve local model support
- Bao created elizaOK-branded merchandise built using elizacloud

## Repository Cleanup

- Completed a major repository-wide cleanup, closing stale issues 8 or more months old
- Retired V3 planning goals and removed deprecated milestones across all repositories
- Standardized policy directing third-party plugin contributors to independently host integrations under the elizaOS-plugins organization

## Core Framework Improvements

- Integrated task-completion assessment into the reflection evaluator pipeline to improve runtime accuracy
- Removed duplicate action result formatting from the RECENT_MESSAGES provider to reduce unnecessary token usage in LLM context management
- Resolved a TypeScript build error (TS2769) in the Anthropic plugin for compatibility with the latest core alpha updates
- Bumped the cryptography Python package to version 46.0.6 to address security requirements

## Active Development Areas

- Multi-agent coordination patterns under discussion, covering persistent peer relationships and on-chain credential verification
- Payment infrastructure design for AI agents in progress, including identity verification and trust-based spend limits
- Work ongoing to address custom plugin callback interference in the Discord plugin, separating provider state composition from action callback processing
- New registry entry for the hashlock plugin under review