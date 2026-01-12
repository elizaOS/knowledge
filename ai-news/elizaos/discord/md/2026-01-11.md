# elizaOS Discord - 2026-01-11

## Overall Discussion Highlights

### Leaderboard & AI Council Enhancements

**Jin** announced a major new beta feature for the ElizaOS leaderboard: lifetime summarization for contributor profiles. This feature provides comprehensive historical context about contributors, accessible through the API at https://elizaos.github.io/profile/madjin. The AI council can now access full contributor histories when evaluating updates and progress, significantly improving the review process.

Plans were also announced to resume the "jedai council" with several improvements:
- Enhanced site functionality
- New Discord channel for post-meeting agent interactions
- Human-in-the-loop feedback capabilities

### Agent Architecture & Visual Generation

The **core-devs** channel showcased impressive visual generation capabilities, with **jin** demonstrating a 3D model or avatar generation system featuring a "low poly mode." The technical quality exceeded expectations for certain user profiles.

An important architectural clarification emerged when **sayonara** explained their agent design approach to **Stan**, noting they use separate human simulator/evaluator components rather than a subagent architecture pattern.

**Jin** articulated a specific technical requirement for a local-first Claude Code implementation that works across multiple platforms (Discord, Telegram, web, CLI) rather than having Eliza manage Claude Code directly. A reference implementation was shared at github.com/clawdbot/clawdbot.

### Migration & Deployment Issues

Multiple users reported technical problems with the AI16z to ElizaOS token migration interface. **Mattish** encountered issues where the max button wasn't functioning and manual input of token amounts was prevented. This issue remains unresolved.

**MDMnvest** reported cloud deployment problems with their agent, while **MRT0B13** experienced issues with an agent refusing to follow prompts specified in configuration files, suggesting potential prompt engineering or configuration parsing problems.

### Community Safety & Communication

**MDMnvest** actively warned users against scam links, directing **mattish** to only trust links from official announcement or links channels. The team coordinated responses to external inquiries about elizaCloud, with **ElizaBAO** noting that a Solana figure (Toly) followed someone asking questions about the platform.

### Social & Philosophical Discussions

The **💬-discussion** channel included conversations about crypto adoption timelines, with **DorianD** suggesting crypto adoption would take 50+ years across generations. **Shaw** and **Error P015-A** discussed the strategy of separating political content from project accounts to avoid alienating potential investors, though acknowledging crypto's historically political nature.

## Key Questions & Answers

**Q: Evaluator? / Sub agent?** (asked by Stan ⚡)  
**A:** Not subagent - separate human simulator / evaluator (answered by sayonara)

**Q: How do I get a response after opening a Ticket in official ElizaOs support? In the opened ticket or through the DM?** (asked by mattish)  
**A:** Team will respond. Just be patient (answered by MDMnvest)

### Unanswered Questions

- I'm trying to migrate my AI16z to ElizaOS but the max button doesn't work and I'm not able to put the number of AI16Z for swap. Is there any fix or help for this? (mattish)
- Having issues deploying agent in cloud. Anyone experiencing similar issues? (MDMnvest)
- What model you use for the generation? (Agent Joshua ₱ | TEE)
- Can this be done in Eliza cloud now? Or local installation? How do? (DearDaniel)
- What price level is the foundation targeting for 2026? (Uchi)

## Community Help & Collaboration

**MDMnvest → mattish**  
Prevented a potential scam by directing the user to never click links unless in official announcement or links channels, providing proper channel references after mattish almost fell for scammers.

**sayonara → Stan ⚡**  
Clarified agent architecture design patterns, explaining the system uses separate human simulator/evaluator components rather than subagent architecture.

**$cott → Unknown**  
Diagnosed an agent loop issue, identifying the problem as a loop-related malfunction.

**cjft → ElizaBAO**  
Coordinated response to external post about elizaCloud functionality.

## Action Items

### Technical

- **Investigate and resolve cloud deployment issues for agents** (mentioned by MDMnvest)
- **Fix agent prompt following issue where agent refuses to follow prompts in configuration file** (mentioned by MRT0B13)
- **Fix max button functionality in AI16z to ElizaOS migration interface** (mentioned by mattish)
- **Review clawdbot implementation at github.com/clawdbot/clawdbot as potential reference** (mentioned by jin)
- **Complete site improvements for leaderboard/council system** (mentioned by jin)

### Feature

- **Create local-first Claude Code implementation usable across Discord, Telegram, web, and CLI platforms** (mentioned by jin)
- **Resume jedai council with improvements and enhanced intelligence** (mentioned by jin)
- **Create Discord channel for post-meeting agent interactions to enable human-in-the-loop feedback** (mentioned by jin)
- **Consider separate social media accounts for political content vs project updates** (mentioned by Error P015-A)

### Documentation

- **Clarify official support ticket response process and communication channels** (mentioned by mattish)
- **Document Eliza cloud vs local installation setup procedures** (mentioned by DearDaniel)
- **Respond to external questions about elizaCloud functionality** (mentioned by ElizaBAO)