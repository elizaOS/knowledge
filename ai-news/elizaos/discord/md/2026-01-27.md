# elizaOS Discord - 2026-01-27

## Overall Discussion Highlights

### Strategic Direction & Product Development

The ElizaOS team is executing a multi-product strategy with several initiatives in parallel development: Babylon, Hyperscape, Cloud, OTC desk, and Eliza Anime. The core philosophy involves iterating on multiple products until one achieves viral success, then rewarding long-term ElizaOS holders through airdrops (with HYPE and BABY cited as examples). The Babylon airdrop for ElizaOS holders is confirmed in principle, though specific details remain unfinalized, with consideration being given to rewarding long-term holders specifically.

### Major Technical Pivot: AI Agent Platform with Workflow Automation

The core development team is pivoting from hardware-focused development to building an AI agent platform called "Eliza" that performs automated tasks. The most significant technical decision involves integrating n8n workflow automation with Eliza v2.0.0 (published to npm as @elizaos/core@next) to enable dynamic workflow creation through natural language.

**Architecture Decision:** The team is adopting n8n plugin architecture as the primary approach for workflow automation instead of building native plugins for each service. A three-layer architecture has been proposed:
- **Layer 3:** AI Workflow Generator
- **Layer 2:** Workflow Engine with TaskService/cron
- **Layer 1:** OAuth Gateway for multi-tenant credentials

**Implementation Strategy:** The team identified that 95% of users want AI-powered workflow builders rather than extensive auto-coding capabilities. The focus is on connecting services like Gmail, Calendar, Notion, and Linear with conditional logic. The approach involves creating pre-built common workflows, then using Claude Opus to generate new ones based on closest matches, marking them as experimental and debugging with users before adding to the library.

**Eliza v2.0.0 Features:** The new version includes computer use and browser use capabilities based on working open source implementations. The team is leveraging n8n-intelligence (open source) to enable agents to create workflows conversationally.

### Knowledge Plugin Issues & Cost Optimization

Two critical technical issues emerged around the Knowledge plugin:

**Configuration Errors:** Users encountered validation errors with EMBEDDING_PROVIDER receiving 'openrouter' when only 'openai' | 'google' are valid enum values. The root cause was identified as incorrectly setting openrouter as the embedding provider instead of openai.

**Cost Optimization:** A significant cost issue was discovered where the Knowledge plugin with OpenAI was generating extremely high costs ($0.03-0.04 per query, tens of thousands of tokens) for simple requests on small markdown documents. The issue was traced to contextual embeddings being enabled (CTX_KNOWLEDGE_ENABLED=true). A minimal configuration solution using OPENROUTER_EMBEDDING_MODEL with openai/text-embedding-3-small was demonstrated, successfully embedding a 3.1MB PDF with 517 chunks at reasonable cost.

### Development Priorities & Timeline

**Immediate Priority:** End-of-week deadline for top-of-funnel: landing page → poke integration → agent conversation. The agent personality needs to be "funny, spunky, and spicy" but not mean.

**Parallel Development Tracks:**
- Sam: SMS/iMessage plugins and cloud platform integration
- Stan: Mail/calendar plugins and n8n plugin development with OAuth support
- Odilitime: plugin-pim (Personal Information Manager) using entity/component architecture and memories

The team is exploring n8n capabilities first before continuing plugin development to understand limitations and determine optimal tool selection.

### Model Preferences & Technical Discussions

Strong preference was expressed for Opus 4.5 model among developers. Discussions also covered mapping human decision patterns into agent logic, particularly for trading and high-pressure decisions, with insights that agents excel at processing large amounts of context from multiple sources to provide insights.

### Community Concerns

Community members raised questions about token price performance, airdrop eligibility (including whether trading on Solana DEXs counts and if tokens need to be moved off Kraken), and ETH chain token liquidity issues. Concerns were also expressed about restoring ElizaOS's memetic value through community effort.

## Key Questions & Answers

**Q: Will Babylon be 100% airdrop for ElizaOS holders?**  
A: That's the idea but details aren't finalized yet, may include other requirements, want to reward long term holders *(answered by Odilitime)*

**Q: How do I fix the "Invalid enum value" error for EMBEDDING_PROVIDER when it receives 'openrouter'?**  
A: Change your embedding provider from openrouter to openai *(answered by DigitalDiva)*

**Q: Why is the knowledge plugin extremely expensive with OpenAI - tens of thousands tokens per simple request ($0.03-0.04 per query)?**  
A: You're using contextual embeddings (CTX_KNOWLEDGE_ENABLED=true) which increases costs significantly; use minimum config without contextual embeddings *(answered by 0xbbjoker)*

**Q: Is Eliza v2.0.0 available for testing?**  
A: Yes, published to "next" - install with npm install @elizaos/core@next *(answered by s)*

**Q: Should we build native plugins or use n8n?**  
A: After OAuth, n8n plugin would be slickest - can validate workflows by credentials needed and create stuff for users on the fly *(answered by s)*

**Q: How do we test dynamically generated workflows?**  
A: Pre-create common workflows, use Opus to generate new ones based on closest matches, mark as experimental, debug with users, review/fix on backend, add fixed versions to library *(answered by s)*

**Q: What's the main user need - autocoding or workflows?**  
A: 95% want AI workflow builder, only few nerds want autocoding - people want to connect email/notion/calendar/linear with if statements *(answered by s)*

**Q: Should we stop Twilio/BLOOIO work and focus on n8n?**  
A: n8n is for workflows, still need cloud runtime for iMessage/WhatsApp chat clients - should prioritize n8n first to understand limits before continuing plugins *(answered by Stan ⚡ and Odilitime)*

**Q: Is n8n-intelligence open sourced?**  
A: Yes *(answered by s)*

**Q: Can we pass plugin credentials to n8n?**  
A: Yes, credentials from plugins like plugin-gmail can be passed to n8n for workflow access *(answered by Stan ⚡)*

**Q: Should I move my ElizaOS off of Kraken to get airdrops?**  
A: No airdrop details have been announced, stay tuned for official announcement *(answered by Hexx 🌐)*

**Q: Why can't DegenAI track PumpFun tokens and smart wallets with the best ROI?**  
A: Spartan has been focused on autonomous trading which is a big problem to solve; Otaku can likely do what you're talking about *(answered by Kenk)*

**Q: How do people think about mapping human decision patterns into agent logic, especially for trading or high pressure decisions?**  
A: Agents are very good at taking in large amounts of context from multiple sources and providing insight, mapping human logic afterwards is interesting *(answered by Kenk)*

## Community Help & Collaboration

**DigitalDiva → YogaFlame:** Identified that openrouter should not be used as embedding provider and advised changing to openai to resolve "Invalid enum value" error for EMBEDDING_PROVIDER.

**0xbbjoker → Tyrone:** Provided comprehensive solution for extremely high Knowledge plugin costs by explaining that CTX_KNOWLEDGE_ENABLED=true causes higher costs and sharing minimal configuration example with 3.1MB PDF costing much less.

**Odilitime → Tyrone:** Directed to 0xbbjoker as the plugin-knowledge expert and offered to test latest version for cost optimization.

**s → sam:** Confirmed Eliza v2.0.0 is working and provided npm install command for @elizaos/core@next for testing new features.

**s → Stan ⚡ and sam:** Proposed n8n plugin approach with prefab workflows and dynamic generation strategy to resolve architecture decision for service integrations.

**Stan ⚡ → ziflie:** Explained goal to create dynamic workflows with n8n-plugin that can create actions/providers based on user wants and reuse existing plugins.

**s → ziflie:** Directed to focus on top of funnel first - lander → poke → agent conversation, then add features incrementally.

**s → Stan ⚡:** Shared n8n-intelligence and n8n-workflow-builder GitHub repositories as solutions for finding workflow builder tools.

**Borko → Team:** Created n8n cloud account and sent invites to Shaw, Stan and Sam for proper access.

**Odilitime → Team:** Clarified that plugin credentials (like gmail) should be passable to n8n for workflow access.

**Odilitime → crypto:** Confirmed intention to airdrop Babylon to ElizaOS holders but details not finalized, considering rewarding long-term holders.

**Kenk → web3buidl:** Explained agents excel at processing large context from multiple sources for insights when mapping human decision patterns into agent logic.

**Kenk → MATTIOBOY 🇦🇺:** Clarified Spartan focuses on autonomous trading, suggested Otaku has PumpFun token tracking capabilities.

**Hexx 🌐 → Wes:** Clarified no airdrop details announced yet, advised waiting for official announcement regarding moving ElizaOS off Kraken.

**Maff || Hourglass ⌛ → CRYPTONIAN:** Attempted to help with ETH chain token swapping issues by asking which chain to swap to.

**Kenk → DigitalDiva:** Encouraged asking questions publicly in the channel rather than DMing about integrating ElizaOS AI agents.

## Action Items

### Technical

- Test Eliza v2.0.0 with computer use and browser use capabilities *(sam)*
- Develop SMS and iMessage plugin and integrate with cloud platform for clawdbot/poke app *(sam)*
- Build mail/calendar plugins *(Stan ⚡)*
- Implement n8n plugin with OAuth support for dynamic workflow creation *(Stan ⚡)*
- Create validation/testing system for workflows based on required credentials *(s)*
- Build pre-fabricated n8n workflows for common actions (check email, send email, etc.) *(s)*
- Implement workflow review and fix system on backend to help users and add to library *(s)*
- Complete landing page → poke integration → agent conversation funnel by end of week *(s)*
- Integrate n8n-intelligence into Eliza agent for conversational workflow creation *(s)*
- Set up n8n hosted cloud instance with proper scaling (workers) *(Stan ⚡)*
- Implement three-layer architecture: AI Workflow Generator, Workflow Engine with TaskService/cron, OAuth Gateway *(Stan ⚡)*
- Continue development of plugin-pim with entity/component architecture *(Odilitime)*
- Implement credential passing from plugins to n8n workflows *(Odilitime)*
- Test n8n capabilities and limitations before continuing plugin development *(Odilitime)*
- Fix Knowledge plugin example configuration documentation to reflect correct EMBEDDING_PROVIDER enum values *(YogaFlame)*
- Test latest version of plugin-knowledge for cost optimization *(Odilitime)*
- Address ETH chain token liquidity issues and exchange support *(CRYPTONIAN)*

### Feature

- Continue development on multiple products (Babylon, Hyperscape, Cloud, OTC desk, Eliza Anime) until one achieves viral success *(Seppmos)*
- Implement airdrop strategy to reward long-term ElizaOS holders when products succeed *(Seppmos)*
- Enable natural language plugin/skill addition through chat interface *(Agent Joshua ₱ | TEE)*
- Make Eliza personality funny, spunky, and spicy (not mean like poke bouncer) *(s)*
- Build interface for any chat app to integrate with Eliza *(Agent Joshua ₱ | TEE)*
- Implement PumpFun token tracking and smart wallet ROI monitoring capabilities *(MATTIOBOY 🇦🇺)*
- Restore ElizaOS memetic value through community initiatives *(satsbased)*

### Documentation

- Update Knowledge plugin documentation to clarify cost implications of contextual embeddings (CTX_KNOWLEDGE_ENABLED=true) *(Tyrone)*
- Document reference to ctx-embeddings.ts for understanding contextual embeddings behavior *(0xbbjoker)*
- Create starter plan for n8n workflow implementation and share with team *(Stan ⚡)*
- Finalize and announce official Babylon airdrop details including eligibility requirements and long-term holder rewards *(Odilitime)*
- Provide official announcement on airdrop details for community *(Hexx 🌐)*
- Clarify regular update schedule and communication channels for team developments *(Rainman)*

### Investigation

- Investigate OpenAI-compatible chat completions endpoint integration for ElizaOS AI agents supporting OpenAI JSON API, OpenRouter, and Kobold API *(DigitalDiva)*