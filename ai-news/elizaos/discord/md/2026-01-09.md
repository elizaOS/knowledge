# elizaOS Discord - 2026-01-09

## Overall Discussion Highlights

### Platform Development & Infrastructure

**Eliza Cloud Evolution**: The Eliza Cloud platform showed signs of active development with new billing pages enabling credit top-ups. ElizaBAO initially reported operational failures with the app creator feature, but cjft confirmed it's functional though still in early stages. The platform continues to evolve as a core infrastructure component for the ElizaOS ecosystem.

**Eliza 2.0 Radical Redesign**: Shaw proposed a significant architectural overhaul for Eliza 2.0, featuring multi-language support (TypeScript, Rust, Python) with FFI plugin interoperability. The vision eliminates traditional API, server, CLI, and project structures in favor of an extremely Claude-friendly documented runtime with unified abstractions across all three languages. Shaw confirmed having already ported the implementation with a branch available for review.

**Cloud Infrastructure**: Stan announced delays in cloud cleanup work due to medical issues, indicating ongoing optimization efforts for the platform's backend infrastructure.

### Skills & Plugin Interoperability

**Cross-Platform Skills Initiative**: Jin initiated a major collaboration effort to convert ElizaOS plugins into skills for testing interoperability across different agent tools, focusing on Discord and blockchain integrations. This aims to establish cross-platform compatibility standards.

**Skills Architecture**: R0am outlined a technical approach where skills are organized as folders containing .md instruction files and deterministic scripts in any language. The key technical challenge identified was enabling Claude to use skills implicitly rather than explicitly, which R0am claims to have solved using hooks.

**Workflow Complexity**: Agent Joshua highlighted the complexity of chaining skills together, providing a concrete example workflow: specialized skill → PDF manipulation → filesystem storage → display. The community acknowledged this as a difficult problem requiring further exploration.

### AI & Mental Health Integration

**Dopamine Monitoring Proposal**: DorianD proposed integrating the "Dopa One" AI algorithm by Behavidence into a future ElizaOS Phone app. This technology monitors brain dopamine levels through mobile phone and wearable device interactions to detect mental health fluctuations (ADHD, Depression, Anxiety). DorianD noted that 5 years of LLM progress and improved smartwatch technology could make this more feasible than when the company went dormant during COVID.

**AI Image Analysis**: DorianD also suggested implementing AI agents for image analysis use cases, with Jin providing the deepface library from GitHub as a technical starting point.

### Technical Experiments

**MiniMax M2 Integration**: R0am explored using MiniMax M2's Anthropic-compatible endpoint with Claude Code, sharing an "interleaved thinking" approach for long-running tasks. They successfully deployed a VPS running Claude Code with Kimi K2, accessible via Happy on iOS.

### Community Events & Announcements

**Solana Foundation Twitter Space**: Kenk announced an upcoming Twitter Space scheduled for Tuesday, January 13th at 7pm UTC featuring Solana Foundation, PayAI, and Quantu. The event will deep-dive into protocol 8004 and its integration with Eliza Cloud. Jin added credibility by noting that Dan Boneh, a renowned Stanford cryptographer, mentioned 8004.

**Leaderboard Updates**: Jin teased upcoming enhancements to the elizaos leaderboard as part 2 of the meritverse initiative.

**JEJU Platform Context**: DorianD explained that Jeju is a Korean island traditionally used for testing new technology before nationwide rollout, providing context for platform naming.

## Key Questions & Answers

**Q: Why is the platform named JEJU?**  
A: Jeju is a Korean island where they usually use for running new stuff before they roll out the tech in the rest of Korea (answered by DorianD)

**Q: Is the elizacloud app creator functioning?**  
A: Yes, it's working but it's an early feature (answered by cjft)

**Q: What's the structure for skills implementation?**  
A: Folder with .md instructions and tools in scripts (any language) to make them deterministic (answered by R0am)

**Q: What's the real challenge with skills?**  
A: Getting Claude to use skills without explicit instruction, solved using hooks (answered by R0am)

**Q: How to build effective workflows for chaining skills?**  
A: Acknowledged as difficult; example workflow shared: specialized skill → PDF manipulation → filesystem storage → display (partially answered by Agent Joshua)

### Unanswered Questions

- How do I set Discord Timer/Interval Settings for my elizaos agents in discord? (asked by DigitalDiva)
- Do you need Twitter API to use Eliza to run a Twitter agent? (asked by Psyxh)
- Can I top up credit into the cloud now with the billing pages? (asked by ElizaBAO)

## Community Help & Collaboration

**Skills Development Collaboration**: Jin's call for collaboration on converting ElizaOS plugins to skills received immediate response from R0am, who volunteered and shared their technical approach using folders with .md instructions and deterministic scripts. Stan also confirmed doing similar work.

**Platform Naming Clarification**: DorianD helped Skullcross understand the JEJU platform naming origin, explaining Jeju's role as a Korean technology testing ground and providing pronunciation guidance.

**Cloud Platform Support**: cjft assisted ElizaBAO with elizacloud app creator issues, confirming functionality and suggesting retry while acknowledging the early-stage nature of the feature.

**AI Implementation Guidance**: Jin provided DorianD with a technical starting point for AI image analysis implementation by sharing the deepface library GitHub repository.

**Workflow Complexity Discussion**: Agent Joshua shared insights with jin and R0am about skill workflow complexity, providing concrete examples from their skill factory implementation. R0am reciprocated by providing a Reddit reference about successfully linking subagents.

## Action Items

### Technical

- Experiment converting elizaos plugins (Discord + blockchain) into skills for interoperability testing (mentioned by jin)
- Implement skills as folders with .md instructions and deterministic scripts (mentioned by R0am)
- Develop hooks solution to enable Claude to use skills implicitly (mentioned by R0am)
- Complete cloud cleanups and optimizations (mentioned by Stan)
- Review and merge shaw's Eliza port branch (mentioned by shaw)
- Solve effective workflow patterns for chaining skills back and forth (mentioned by Agent Joshua)
- Investigate and resolve elizacloud app creator operation failures for stability (mentioned by ElizaBAO)

### Feature

- Integrate Dopa One AI algorithm (mental health monitoring via mobile interaction patterns) into future ElizaOS Phone app to monitor users' dopamine levels and mental well-being (mentioned by DorianD)
- Build Eliza 2.0 with TS, Rust, Python support and FFI plugin interop, eliminating API/server/CLI/projects (mentioned by shaw)
- Implement AI agent for image analysis use cases using deepface or similar libraries (mentioned by DorianD)

### Documentation

- Answer question about Discord Timer/Interval Settings configuration for ElizaOS agents (mentioned by DigitalDiva)
- Document Twitter API requirements for running Twitter agents with Eliza (mentioned by Psyxh)
- Create extremely Claude-friendly documentation for Eliza 2.0 runtime with examples for common use cases (mentioned by shaw)
- Publish blog post about elizaos leaderboard updates (part 2 of meritverse) (mentioned by jin)