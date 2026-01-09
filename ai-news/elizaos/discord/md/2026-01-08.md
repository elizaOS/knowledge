# elizaOS Discord - 2026-01-08

## Overall Discussion Highlights

### Token Migration & Exchange Listings

The community faced significant concerns regarding the ai16z to elizaOS token migration process. Multiple users reported eligibility verification issues, particularly with LP tokens showing "max amount reached" errors. A major development emerged with the confirmed delisting of ai16z/elizaOS from Korean exchanges (Bithumb, Coinone, Korbit) scheduled for February 2026. DAXA cited lack of transparency in rebranding/token swap procedures as the primary reason. Questions arose about whether exchanges would automatically migrate tokens for pre-November holders, receiving conflicting responses from community helpers.

### Token Utility & Ecosystem Strategy

A critical discussion emerged around elizaOS token utility within the ecosystem. Community member stoikol raised pointed questions about why the token isn't being used for payments or gas fees, questioning the fundamental need for a token without clear utility. No definitive answers were provided by team members regarding the token's utility roadmap, highlighting a documentation gap that needs addressing.

### Technical Development & Infrastructure

**Jeju Layer2 & Bazaar Protocol**: Development activity was observed on the Kamiyo protocol via GitHub commits. The Bazaar protocol was clarified as a decentralized marketplace application running on Jeju, described as "the appstore for agents." This represents a key infrastructure component connecting Eliza's ecosystem.

**Data Foundation & Context Graphs**: Jin emphasized the platform's strong data foundation for building context graphs, noting that Foundation Capital's article on context graphs aligns with Eliza's capabilities. The agentic workflows generate high-quality daily, weekly, and monthly insights, though integration into last-mile applications (agents, webhooks, apps) remains a gap.

**Deployment Configurations**: Technical questions arose about ElizaCloud container deployments, specifically database choices between Pglite and PostgreSQL (both confirmed as viable options).

### AI Agent Development & Data Collection

An innovative discussion emerged around data collection strategies for AI training. DorianD proposed several forward-thinking concepts:

- **Eliza Phone App**: Users could share data in exchange for reputation points for LLM training
- **Agent-Paid Data Collection**: Agents could pay IOUs for user-generated data (e.g., "fishingcoin" for fly-fishing footage)
- **Motion Capture Data**: Inertial motion capture suits for various professions (McDonald's workers, hairdressers, battlefield applications) where workers earn royalties when AI/androids use their captured movement data
- **Babylon Game Experiment**: Mentioned as an ongoing data collection initiative

### Market Dynamics

Agent Joshua provided market analysis noting that inference markets are not highly profitable based on observations from models offered on their platform and OpenRouter over the past year, providing strategic context for development priorities.

## Key Questions & Answers

**Q: For deploying in Elizacloud via containers should I use Pglite or PostgresSQL?**  
A: Either will work (answered by cjft)

**Q: Can I migrate my old ai16z tokens purchased before November 2025? I'm getting 0 eligible tokens.**  
A: User was directed to migration support channels; issue unresolved in main discussion (answered by Hexx 🌐)

**Q: If I have been holding ai16z on Bithumb since before November, will the exchange automatically migrate it to elizaOS?**  
A: Conflicting answers - FoRever_BIG said yes, jessy initially said no but later agreed to check (answered by FoRever_BIG, jessy)

**Q: What is the Bazaar protocol shown in the GitHub commit?**  
A: Bazaar is the decentralized marketplace application running on Jeju, the appstore for agents (answered by sb)

## Unanswered Critical Questions

- When is elizaOS token going to get some usecase as utility within the ecosystem, why is it not being used for payments? (asked by stoikol)
- Can I use Eliza for X without paying for X API ($200/month)? (asked by Discostu)
- Does the Bithumb/Coinone delisting mean elizaOS will be listed after ai16z delisting in February? (asked by KARA)
- Are these guys (KamiyoAI) using the elizaos plugin? (asked by elizafan222)

## Community Help & Collaboration

**Migration Support**  
Hexx 🌐 actively assisted multiple users with migration issues, directing XXI_Rapax to verify in entry channel and access migration support channels when they couldn't post in migration questions. Hexx also protected the community by identifying and reporting scammers (GUIDE BASE, guidebt) attempting to contact users about migration.

**Technical Guidance**  
- cjft helped Omid Sa resolve uncertainty about database choice for ElizaCloud container deployment, confirming either Pglite or PostgreSQL would work
- sb provided clarity to elizafan222 about the Bazaar protocol, explaining it as a decentralized marketplace on Jeju
- sb directed aicodeflow (AI/full-stack developer seeking collaboration) to the developer channel to contribute to the open source project

**LP Token Migration**  
FoRever_BIG assisted Dabel with LP token migration issues showing "max amount reached" errors, directing them to ticket and migration question channels for specialized support.

## Action Items

### Technical

- **Resolve migration eligibility issues for pre-November ai16z token holders** (Mentioned by: XXI_Rapax)
- **Integrate daily/weekly/monthly insights from agentic workflows into last mile applications (agents, webhooks, apps)** (Mentioned by: jin)
- **Investigate KamiyoAI project's use of ElizaOS plugin** (Mentioned by: elizafan222)

### Documentation

- **Clarify token utility roadmap and use cases within the elizaOS ecosystem** (Mentioned by: stoikol)
- **Provide clear guidance on LP token migration process and "max amount reached" errors** (Mentioned by: Dabel)
- **Clarify automatic migration process for exchange holders (Bithumb/Coinone)** (Mentioned by: KARA)
- **Fix docs website that is currently down at elizacloud.ai/docs** (Mentioned by: Amir)

### Feature Development

- **Develop Eliza Phone App that lets users give Eliza access to their data for LLM training and earning reputation points** (Mentioned by: DorianD)
- **Build context graph leveraging Eliza's strong data foundation** (Mentioned by: jin)
- **Create agents that pay people IOUs to collect their data for specific activities** (Mentioned by: DorianD)
- **Develop cheap solution for mocap suits to capture movement data for AI training** (Mentioned by: DorianD)
- **Implement inertial motion capture suits as uniforms for professions like McDonald's workers to capture training data** (Mentioned by: DorianD)
- **Develop alternative to expensive X API for Eliza X integration** (Mentioned by: Discostu)

---

*Summary compiled from discussions across #💬-discussion, #💬-coders, and #core-devs channels on January 8, 2026*