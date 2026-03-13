# elizaOS Discord - 2026-03-12

## Overall Discussion Highlights

### Product Development & Roadmap

**Milady App Launch Timeline**: The team announced that the Milady app is targeting release in approximately 2 weeks from March 12th. This represents a significant milestone for the ecosystem's expansion beyond the core framework.

**Token Economics & Business Model**: A comprehensive discussion clarified the elizaOS tokenomics strategy. The business model centers on cloud services, with profits from Milady cloud operations directed toward buybacks of elizaOS tokens (not Milady tokens). This buyback mechanism represents the primary value accrual for token holders. The team holds 10% of tokens vested over multiple years, with minimal selling pressure reported. Odilitime confirmed he hasn't sold any tokens in the previous 2 months.

### Technical Architecture & Infrastructure

**Runtime Refactor Proposal**: Odilitime published a significant runtime refactor proposal on HackMD with a Sunday deadline for feedback. The proposal addresses fundamental architectural concerns in the Eliza framework, particularly around plugin initialization and infrastructure component registration.

**Plugin Initialization Race Condition**: A critical design flaw was identified where plugin-sql registers its database adapter as a side-effect during init(), which runs in parallel with other plugins. This creates a race condition where plugin-personality may execute before the adapter is available. The current workaround in milaidy manually pre-registers plugin-sql before calling initialize(), but this is acknowledged as addressing a symptom rather than the root cause. The proposed solution involves making the adapter a required constructor argument instead of relying on plugin side-effects.

**Repository Structure Concerns**: Questions were raised about the eliza-cloud-v2 repository structure, specifically why the entire repo exists in the v2.0.0 branch instead of using git submodules for better composability and single-source-of-truth architecture.

### Agent Registry & Orchestration

**Autonomous Agent Discovery System**: lightningprox presented an open agent registry with autonomous orchestration capabilities at aiprox.dev. The system achieved a notable milestone when an external agent autonomously discovered the registry and attempted self-registration without prompting. Key features include:

- Self-registration capabilities for agents
- Usage-based rating system
- Multi-payment rail support (Lightning/Solana/x402)
- Auto-approver pipeline scoring new registrations 1-10 to filter low-quality agents
- 14 live agents operational at time of discussion

The registry operates via public REST API with endpoints for registration (/api/agents/register) and querying (/api/agents). Registration requires capability slug, payment rail, price per call, and endpoint. Integration with agentskills.io was implemented through a skill.md file for discovery by openclaw and Hermes-agent.

### Security & User Support

**Token Migration Scam Alert**: A scam attempt was identified involving a fake support bot directing users to a colabdesk site requesting seed phrases. This occurred in the context of the $AI16Z to $elizaOS token migration, which permanently closed on February 4, 2026, after a 3-month window. Odilitime is maintaining a list of affected users for potential future reopening attempts.

### Community Growth

A new community member, genife, introduced themselves as an AI & Full-Stack Engineer with expertise in production-ready AI systems, including LLM orchestration, RAG pipelines, multi-agent systems, and various AI frameworks (DSPy, LangChain, AutoGen, CrewAI).

## Key Questions & Answers

**Q: Any token use case or still nothing for token holders?**  
A: No direct token use case currently. The business model focuses on cloud services with profits going toward buybacks of elizaOS tokens. *(answered by Odilitime)*

**Q: When will the Milady app be released?**  
A: Aiming for roughly 2 weeks from March 12th. *(answered by Odilitime)*

**Q: Will the MILADY token have any function?**  
A: Not directly; the strategy is pushing the cloud and profits from cloud will go into buybacks of elizaOS tokens. *(answered by Odilitime)*

**Q: How does the discovery mechanism work for the agent registry?**  
A: Discovery uses a public REST registry where agents POST to /api/agents/register with capability slug, payment rail, price per call, and endpoint. Orchestrators query /api/agents with parameters for capability, rating sort, and payment rail to find matches. *(answered by lightningprox)*

**Q: How does the auto-approver pipeline work?**  
A: The auto-approver pipeline scores new registrations 1-10 to filter low quality agents. Bad agents get rated down naturally through usage and stop getting hired. *(answered by lightningprox)*

**Q: Why was token migration from $AI16Z to $elizaOS permanently closed on Feb 4, 2026?**  
A: There was a 3-month window with a clearly stated time period when it started. The window has closed. *(answered by Odilitime)*

**Q: Is the Support Ticket bot directing to colabdesk site legitimate?**  
A: Scam - the site requesting seed phrases is not legitimate. *(answered by Odilitime)*

**Q: Why does milaidy manually register plugin-sql before calling initialize()?**  
A: Because plugin-sql registers the adapter as a side-effect of init(), which runs in parallel with other plugins, creating a race condition. *(answered by s)*

**Q: How can agents integrate with agentskills.io for discovery?**  
A: Create a skill.md file at your domain root for discovery by openclaw and Hermes-agent. *(answered by Odilitime)*

## Community Help & Collaboration

**Agent Registry Discovery Enhancement**  
Helper: Odilitime | Helpee: lightningprox  
Odilitime suggested creating aiprox.dev/skill.md for agentskills.io integration to enable openclaw and Hermes-agent discovery. lightningprox successfully implemented this integration.

**Token Migration Scam Prevention**  
Helper: Odilitime | Helpee: Jay  
When Jay was directed to a scam site requesting seed phrases through a fake support bot, Odilitime confirmed it was a scam and advised not to provide seed phrase. He also offered to add Jay to a list for potential future migration reopening and provided Shaw's handle for follow-up.

**Tokenomics Clarification**  
Helper: Odilitime | Helpee: 梦行人  
Addressed confusion about which token (Milady vs elizaOS) would benefit from buybacks, clarifying that elizaOS tokens will receive buybacks from Milady cloud profits.

**Runtime Architecture Understanding**  
Helper: s | Helpee: Odilitime  
Explained that the plugin-sql initialization issue is a design problem where infrastructure is registered as plugin side-effect, and plugin-sql should always load properly instead of relying on manual pre-registration.

## Action Items

### Feature Development

- **Release Milady app in approximately 2 weeks** *(Mentioned by: Odilitime)*

### Technical Implementation

- **Implement runtime refactor proposal by Sunday deadline** *(Mentioned by: Odilitime)*
- **Fix plugin-sql to always load properly instead of relying on manual pre-registration** *(Mentioned by: s)*
- **Make database adapter a required constructor argument instead of plugin side-effect registration** *(Mentioned by: Odilitime)*
- **Split runtime setup logic out of runtime module** *(Mentioned by: Odilitime)*
- **Ensure API changes don't increase complexity and minimize impact during refactor** *(Mentioned by: s)*
- **Implement cloud service infrastructure for Milady with profit-driven elizaOS buyback mechanism** *(Mentioned by: Odilitime)*
- **Investigate reopening token migration window from $AI16Z to $elizaOS** *(Mentioned by: Odilitime)*

### Documentation

- **Merge GitHub PR #243 for elizaos.github.io adding cloud-related content** *(Mentioned by: Stan ⚡)*
- **Create skill.md file at aiprox.dev for agentskills.io discovery integration** *(Mentioned by: Odilitime)*
- **Update runtime refactor proposal to accurately describe milaidy's defensive pre-registration as architectural concern rather than bug fix** *(Mentioned by: Odilitime)*