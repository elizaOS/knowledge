# elizaOS Discord - 2026-04-14

## Summary

### Organizational Transition

Shaw announced the shutdown of Eliza Labs on April 12, 2026, citing market conditions, depleted treasury, and inability to reach revenue. However, odilitime clarified this represents a shift from paid development to community-driven open source work rather than a complete shutdown. The core framework development continues with Shaw and odilitime leading efforts. The transition separates development discussion (Cozy devs) from economic/community discussion (main Discord). Internal frustrations were revealed about previous team productivity issues and focus on UI over core agent functionality.

### Framework Development Progress

ElizaOS v3 is nearing completion. The Spartan agent is being developed for marketing automation with local model support for cost reduction. Plans include agentic business demos and potential revival of agentic DAO stack given improved AI models. Odilitime mentioned repurposing Spartan technology built for previous projects.

### Plugin Development

A pull request for the elizaos-plugins/plugin-anthropic repository added two key features: a 'claude -p' command solution and missing reasoning type support. The PR introduced TEXT_REASONING_SMALL_MODEL_TYPE with fallback to the main model. Additional functionality including streaming support for the 'claude -p' command was prepared in a follow-up PR.

### Payment Infrastructure

Discussion focused on x402 agent payment infrastructure on Solana. huhuhu0621_67650 is building a trust scoring service for agent wallets and evaluating between USDC-SPL on Solana versus Base USDC for settlements. Stan0473 recommended supporting multiple chains to reduce friction.

### Security Concerns

Scammers were impersonating odilitime and sending fake airdrop messages to community members. The scam attempts were identified and required cleanup from the Discord server.

### CI/CD Pipeline Issues

The CI/CD pipeline encountered multiple build errors during package publishing: workspace dependency '@elizaos/core' not found error attributed to alpha path changes, and 'jsonrepair' resolution failure during browser build. Work was ongoing to fix package.json to resolve these issues.

## FAQ

**Q: Is Eliza Labs completely shutting down?**
A: No, this represents a shift from paid development to community-driven open source work rather than a complete shutdown. Core framework development continues with Shaw and odilitime leading efforts.

**Q: What is the status of ElizaOS v3?**
A: ElizaOS v3 is nearing completion according to odilitime.

**Q: What is the Spartan agent?**
A: Spartan agent is being developed for marketing automation with local model support for cost reduction. The technology is being repurposed from previous projects.

**Q: Which blockchain should be used for agent payment settlements?**
A: Stan0473 recommended supporting multiple chains to reduce friction, though the discussion focused on USDC-SPL on Solana versus Base USDC.

**Q: What new features were added to the Anthropic plugin?**
A: The plugin received a 'claude -p' command solution, missing reasoning type support (TEXT_REASONING_SMALL_MODEL_TYPE), and streaming support for the 'claude -p' command.

**Q: What caused the CI/CD pipeline failures?**
A: Two main issues: workspace dependency '@elizaos/core' not found error due to alpha path changes, and 'jsonrepair' resolution failure during browser build.

## Help Interactions

**Helper:** odilitime
**Helpee:** semipai
**Resolution:** odilitime identified a reported airdrop mention as a scam attempt and requested information about where the message appeared for removal.

**Helper:** odilitime
**Helpee:** stan0473
**Resolution:** odilitime reviewed PR #17 for the Anthropic plugin, raised concerns about potential Anthropic account bans (which were addressed), identified two code issues via PR comments, and merged the PR after fixes were applied.

**Helper:** Stan0473
**Helpee:** huhuhu0621_67650
**Resolution:** Stan0473 recommended supporting multiple chains to reduce friction when deciding between USDC-SPL on Solana versus Base USDC for agent payment settlements.

## Action Items

### Technical

- Fix package.json to resolve '@elizaos/core' workspace dependency not found error (mentioned by odilitime)
- Resolve 'jsonrepair' resolution failure during browser build (mentioned by odilitime)
- Remove scam messages impersonating odilitime from Discord server (mentioned by odilitime)
- Implement trust scoring service for agent wallets (mentioned by huhuhu0621_67650)
- Evaluate multi-chain support for payment settlements (mentioned by Stan0473)

### Features

- Complete ElizaOS v3 development (mentioned by odilitime)
- Develop Spartan agent for marketing automation with local model support (mentioned by odilitime)
- Create agentic business demos (mentioned by odilitime)
- Add streaming support for 'claude -p' command in Anthropic plugin (mentioned by stan0473)
- Implement TEXT_REASONING_SMALL_MODEL_TYPE with fallback to main model (mentioned by stan0473)
- Consider revival of agentic DAO stack (mentioned by odilitime)