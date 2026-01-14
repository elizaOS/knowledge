## ElizaOS Development Updates - January 8-9, 2026

### Technical Development and Infrastructure

- Shaw announced Eliza 2.0 plans with TypeScript, Rust, and Python versions featuring FFI plugin interop between languages
- The new version will have no API, server, CLI, or projects - just a Claude-friendly documented runtime with same abstractions across three languages and examples for common use cases
- Jin built context graphs from decision traces, leveraging ElizaOS's strong data foundation for AI agents as collaborators
- Daily, weekly, and monthly insights generated from agentic workflows were integrated into last mile applications
- Work progressed on converting ElizaOS plugins into skills for interoperability with other agent tools, testing with Discord and blockchain plugins

### Plugin Ecosystem Expansion

- Added @kamiyo/eliza plugin and @zane-archer/plugin-aimo-router plugin to the registry
- Implemented major improvements to plugin-sql module including Neon serverless database support and enhanced Row-Level Security (RLS)
- Fixed pgcrypto extension installation with PGLite
- Implemented OAuth2 PKCE authentication in plugin-twitter repository for enhanced security and backward compatibility
- Strengthened plugin-sql testing by integrating withEntityContext() into RLS tests and adding ENABLE_DATA_ISOLATION=true to CI

### Development Workflow Enhancements

- Fixed critical bug enabling comprehensive hot reload functionality for backend development
- Optimized build task inputs in turbo.json
- Developers implemented MiniMax M2 for coding with interleaved thinking for long-running tasks
- Shared VPS setup running Claude Code with Kimi K2 and access via Happy on iOS

### Jeju Platform

- Explained Jeju platform as a Layer 2 blockchain that is decentralized and focused on powering AI applications
- Platform connects everything ElizaOS is building
- Named after a Korean island used for testing new technology before rolling it out to the rest of Korea

### ElizaCloud

- ElizaCloud agents performed well
- App creator feature is functional
- Added billing page to allow credit top-ups
- Confirmed both PGlite and PostgreSQL work for deployment via containers

### Community Events and Partnerships

- Scheduled space event with Solana Foundation, PayAI, and Quantu for Tuesday January 13th at 7pm UTC to discuss 8004 protocol and Eliza Cloud utilization
- Kamiyo AI project launched using ElizaOS plugin for autonomous agent payments with escrow-protected x402 payments and on-chain dispute resolution
- BountyBoard project using Eliza highlighted as a decentralized platform for Web3 community activities

### Leaderboard and Meritverse Development

- Planned MMORPG-style character system for leaderboard API
- Created implementation for full Orders and Evolution class tree with progression paths
- Enabled users to choose evolution paths at tier thresholds
- Added tracking for class evolution history for profile lore display
- Implemented unique visual identities for each Order
- Enabled class respec with history preservation
- Made character class thresholds configurable
- Extended grouped organization/repository format to day, week, and month summaries
- Referenced work on Meritverse concept combining MMORPG lessons for a unified, rewarding, and meritocratic online ecosystem

### Token Migration

- Team members clarified that exchanges supporting migration would handle the swap automatically

### V2.0.0 Release

- Commenced work on V2.0.0 release