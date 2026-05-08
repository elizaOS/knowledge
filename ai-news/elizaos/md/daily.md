## ElizaOS Community Discussion and Development Progress - May 3, 2026

## Community Discussion

### Token Price Debate

- Community members expressed frustration over ELIZAOS token price decline, citing communication concerns and unfulfilled promises including a Babylon airdrop
- Shaw responded directly, stating token holders are not traditional investors and that the project prioritizes building revenue-generating products over token price management
- Shaw confirmed buybacks require revenue first, and announced Eliza V3 is launching soon
- Odilitime shared a visual roadmap image and coordinated with Shaw to post it in the announcements channel, with plans to update the GitHub text version
- Community member satsbased noted recent improvements in communications and confirmed the Milady app is nearly ready alongside other products in development

### Project Updates from Shaw

- Team is prepared for another major push with a new app in good shape
- Several partners lined up to whitelabel and support the project for their own agents
- Cloud infrastructure configured to be profitable
- A model is being trained intended for users at quality comparable to Sonnet 4.5, with harness-tuned DeepSeek planned after cloud onboarding
- Shadow is launching waifu.fun launchpad with four.meme and flap contracts, powered by the new Eliza

### Trading Repositories Shared

- Shaw shared plugin-auto-trader, plugin-social-alpha, and the Spartan project
- The social alpha plugin analyzes trenches channels to evaluate profitability of shilled tokens, with potential for a social copy trader

### Coders Channel

- Odilitime shared a Twitter poll for a book he is writing on converting vibe-coded projects into durable real projects, currently at 150 pages
- A backtick-wrapped URL workaround was identified for server spam filters blocking certain links

## Development Progress

### Runtime and Infrastructure

- Resolved process-level segfaults on headless Linux via D-Bus detection fallback for the keyring library
- Fixed Telegram bot launch errors and message loss caused by polling race conditions and non-writable error messages in Bun
- Removed legacy components and updated CI workflows to improve repository maintainability

### Authentication and Client Architecture

- Merged duplicate MiladyClient definitions into a canonical ElizaClient to standardize client architecture
- Fixed SIWE domain resolution and updated Codex CLI token recognition to improve authentication reliability

### Automation and User Experience

- Enhanced n8n workflow capabilities with structured clarification rules and ID-based directives
- Restored the NL-first hero centerpiece in the Automations Overview
- Added ConnectorTargetCatalog to surface Discord context

### Pull Requests and Issue Closures

- Pull requests in progress include Clarification UI, trigger deletion fix, SIWE typing fix, Clean Architecture migration, multiple ExergyNet plugin additions, and dependency updates
- Several issues closed across the main eliza repository and the plugin-n8n-workflow repository