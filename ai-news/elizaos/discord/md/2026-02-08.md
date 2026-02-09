# elizaOS Discord - 2026-02-08

## Overall Discussion Highlights

### Database Performance & Infrastructure

A critical performance bottleneck was identified in the Eliza framework's database architecture. The logs table in PostgreSQL is being hit excessively, causing significant slowdowns in Eliza response times. Stan confirmed that a major optimization plan is already in development to address these scalability challenges, indicating the team has prioritized this infrastructure work.

### Milaidy Integration & Plugin Compatibility

The coders channel focused heavily on milaidy integration challenges. Several plugin compatibility issues emerged:

- Plugin integration bugs were acknowledged by the development team
- **MAX_EMBEDDING_TOKENS** constant is missing from latest plugin versions, requiring either rollback to older versions or PRs to add the constant across all plugin repositories
- Wallet fixes have been resolved locally but not yet deployed

### Character Configuration Issues

Multiple users struggled with character customization in the agent system:

- Agents defaulting to "eliza" personality instead of custom characters
- Model selection issues where claude-haiku-3.5 was used despite different configurations
- Character creation currently limited to onboarding setup only
- Bill Ding announced implementation of a character editor to address these limitations

### Twitter Plugin Limitations

The Twitter integration has functional gaps - quote repost feature doesn't work properly, only posting quoted text with a link instead of native quote tweets. The agent successfully connects and posts to Twitter but lacks proper character customization capabilities.

### Architectural Proposals

MochinoLabs proposed a significant architectural change: integrating PM2 as an external process manager for websocket management. The proposal includes a new directory structure using symlinks for better git-managed workflows, with separate config directories for OpenClaw gateway, PM2 processes, and organized data/market directories.

### Community Sentiment & Token Concerns

The discussion channel revealed significant community frustration with the ELIZAOS token project:

- Token price reported at $0.0013 with continuous daily drops exceeding 5%
- Upcoming delistings from three Korean exchanges scheduled for 3:00 PM KST
- Community concerns about lack of communication, missing product deliverables, and team transparency
- Questions about staking availability (confirmed unavailable), token use-cases, and status of five promised products
- Allegations of key developers leaving and poor community management practices

### Positive Developments

- Escrow payment implementation for agent rentals announced
- Upcoming launches mentioned
- Planned bullish video from "crypto gains" investor
- High traffic to ai.com causing website crashes (indicating strong interest)
- Community member ElBru planning to use milaidy setup as a homeschool project for his 10-year-old son

### Historical Context

DorianD shared a personal anecdote about currency devaluation during their great grandfather's migration from the Russian empire to Poland, illustrating the impact of hyperinflation on wealth preservation.

## Key Questions & Answers

**Q: Is there any places to stake $ELIZAOS?**  
A: No, at the moment there is no staking available. (answered by Arceon)

**Q: Why does the logs table cause Eliza to slow down?**  
A: The logs table gets hit excessively which slows down postgres and then makes Eliza responses slower. (answered by sayonara)

**Q: Is there a plan to fix the database performance issues?**  
A: Yes, we have a major optimization plan to implement, and that's part of it. (answered by Stan ⚡)

**Q: Where should I put the character files? It keeps defaulting to eliza**  
A: There isn't a way other than the one you make in the onboarding. (answered by Bill Ding)

**Q: Does Twitter plugin not allow quote reposts?**  
A: No idea, you're welcome to make an issue or attempt to fix yourself. (answered by Bill Ding)

### Unanswered Questions

- Would milaidy support the examples from elizaos? Or do we need to run both Eliza and milaidy for full functionality?
- Did anyone put milaidy on a VPS? or running it locally only?
- Should I submit PRs to all plugin repos to add MAX_EMBEDDING_TOKENS to the latest or what direction should we go?
- What is cluster mode? (in context of PM2 suggestion)
- Will team launch any token use-case or product which may use ElizaOS token?
- What about 5 products this team was about to deliver in few weeks - months gone?
- Do you even have a marketing team?
- Why should anyone buy elizaos?

## Community Help & Collaboration

**Bill Ding → azsxdc**  
Helped with agent defaulting to eliza personality issue by explaining that character editor is being wired in today, and currently only the onboarding method is available for character creation.

**Bill Ding → azsxdc**  
Addressed Twitter quote repost functionality issue by suggesting creating an issue or submitting a PR to fix it.

**s → Wes**  
Acknowledged plugin integration issues and MAX_EMBEDDING_TOKENS problems, mentioned having wallet fixes locally to resolve. Encouraged Wes to proceed with his proposed solution ("let him cook").

**Stan ⚡ → sayonara**  
Confirmed major optimization plan is being implemented to address database performance issues with logs table affecting Eliza response times.

**Arceon → mbat**  
Clarified that staking is not currently available for $ELIZAOS tokens.

### Community Engagement

ElBru expressed interest in using the milaidy setup as a homeschool project for his 10-year-old son, aligning with the project's accessibility goals and demonstrating community enthusiasm for educational applications.

## Action Items

### Technical

- **Implement major optimization plan for logs table** to reduce PostgreSQL load and improve Eliza response times (mentioned by Stan ⚡)
- **Optimize database queries hitting the logs table** to prevent excessive load (mentioned by sayonara)
- **Resolve plugin integration issues** into milaidy (mentioned by s)
- **Resolve wallet fixes** that are currently local (mentioned by s)
- **Decide whether to use older plugin versions or submit PRs** to add MAX_EMBEDDING_TOKENS to all plugin repos (mentioned by Wes)
- **Wire in character editor functionality** (mentioned by Bill Ding)
- **Fix Twitter quote repost functionality** to support native quote tweets instead of text+link (mentioned by azsxdc)
- **Fix model selection issue** where claude-haiku-3.5 is used instead of configured model (mentioned by azsxdc)
- **Fix character file loading** - agent defaults to eliza instead of custom characters (mentioned by azsxdc)
- **Include PM2 as external process manager** for websocket management (mentioned by MochinoLabs)
- **Implement proposed directory structure** with symlinks for git-managed workflow (config/openclaw, config/pm2, data/market structure) (mentioned by MochinoLabs)
- **Address ai.com website crashes** due to high traffic (mentioned by The Void)

### Feature

- **Implement staking functionality** for $ELIZAOS tokens (mentioned by mbat)

### Documentation

- **Provide updates on token use-cases and utility** (mentioned by averma)
- **Deliver status update on 5 promised products** (mentioned by averma)
- **Communicate clear value proposition** for why to buy elizaos (mentioned by gby)

---

**Summary:** February 8, 2026 discussions centered on critical technical infrastructure challenges (database performance, plugin compatibility, character configuration) alongside significant community concerns about token economics and project transparency. The development team acknowledged key issues and confirmed optimization plans are underway, while community frustration highlighted the need for improved communication and product delivery.