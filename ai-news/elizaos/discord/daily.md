# elizaOS Discord - 2026-01-14

## Overall Discussion Highlights

### Eliza 2.0 Architecture Overhaul

**Shaw** announced major architectural improvements for Eliza 2.0, representing a significant simplification of the framework:

- **Planning Plugin Integration**: The planning plugin has been merged directly into Eliza core, activated via `advancedPlanning: true` flag
- **Extended Memory**: Integrated with similar flag-based activation system
- **Bootstrap Capabilities**: Implemented `advancedCapabilities` with `basicCapabilities` (reply, etc.) defaulting to true
- **Reduced Boilerplate**: Eliminated plugin configuration requirements for basic agent functionality
- **Dynamic Loading**: Unused features never load, improving performance
- **Default Room/World Handling**: Set to 00000 UUID, allowing messages without explicit room/world specification

**0xbbjoker** raised optimization concerns about reducing LLM calls by making action params optional to eliminate the params extraction step, and noted database architecture issues requiring attention.

### Voice-Controlled AI Interface Innovation

**M I A M I** demonstrated NIKITA, a voice-controlled AI interface that eliminates traditional navigation:

- Uses **Deepgram** for speech-to-text recognition
- Dynamically morphs between three modes (social, trade, cinema) based on voice input
- Currently developing trading intents for voice-commanded swaps
- Building data pool for agentic trading decisions
- Available at sentientspace.io
- Plans for mobile app and text-to-speech voice generation

**DorianD** engaged in discussion about future AI interaction paradigms, predicting reduced reliance on traditional input methods in favor of voice and AR glasses like Meta Raybans.

### Polymarket Integration & Auto-Trading

**ElizaBAO** and **sedano.npc** discussed implementing auto-trading capabilities with Polymarket:

- Existing plugin-polymarket provides market data and CLOB information but lacks built-in trade execution logic
- **sedano.npc** identified a bug where the agent retrieves older markets instead of latest ones
- Discussion centered on extending the plugin with order management actions (placing/canceling orders)
- Strategy logic would need to be built on top of Polymarket API calls
- **Shaw's** upcoming tutorial stream will cover polymarket plugin/tutorial setup

### Technical Challenges & Solutions

**Twitter Authentication Issues**: **NintyNine** reported problems with agent-twitter-client on VPS, where despite successfully loading cookies, isLoggedIn() returns false and sendTweet() fails with error code 34. The issue may be related to running on data center IP addresses.

**Vector DB & RAG Implementation**: **sedano.npc** sought guidance on implementing vector database and RAG features for local Eliza setup. They discovered the plugin-knowledge solution (https://github.com/elizaos-plugins/plugin-knowledge), though **cjft** noted that a subscription is now required for this functionality.

### Token Economics & Community Concerns

**averma** questioned the token's use case beyond buyback plans, noting lack of utility for development or agent creation. **Majid** raised concerns about price-development misalignment.

**DorianD** explained that falling out of the top 100 cryptocurrencies by market cap blocks automated index investment flows, creating budget sustainability challenges. **DannyNOR NoFapArc** expressed the need to return to billion-dollar market cap status.

### Security & Migration Issues

**코인케인** reported suspicious migration messages from fake support accounts. **DorianD** confirmed these as fake and directed users to check labs-announcements channel for official migration info.

**kiddala** experienced non-functional transfer buttons in Phantom wallet during migration. **Broccolex** directed them to the appropriate channel for migration help.

### Alternative Frameworks

**MemeBroker** introduced the Open Souls framework as an alternative, highlighting its superior personality depth through "mental processes" and "cognitive steps" architecture, using internal dialogue, external dialogue, and memory relay systems, though it lacks Eliza's extensive tooling and integrations.

## Key Questions & Answers

**Q: Is the GitHub tips connect wallet safe?** (asked by ElizaBAO)  
**A:** Yes, tip.md is Roam's app and it's safe (answered by Odilitime)

**Q: What do you use for voice recognition?** (asked by DorianD)  
**A:** Deepgram for speech-to-text; currently only users do STT, NIKITA's output is text only (answered by M I A M I)

**Q: Is the "elizaOS live support" account official?** (asked by 코인케인)  
**A:** Sounds fake, all migration stuff is in labs-announcements channel (answered by DorianD)

**Q: What's the best way to setup a vector DB + RAG feature for Eliza local setup?** (asked by sedano.npc)  
**A:** Use the plugin-knowledge from https://github.com/elizaos-plugins/plugin-knowledge, though it now requires a subscription (answered by sedano.npc, cjft)

**Q: Can the elizacloud agent auto trade at polymarket?** (asked by ElizaBAO)  
**A:** Will be covered in Shaw's tutorial stream on YouTube showing polymarket plugin/tutorial setup (answered by sedano.npc)

**Q: Does the Polymarket plugin include any built-in trade execution logic?** (asked by ElizaBAO)  
**A:** No, it mainly provides market data and CLOB info; would need to build strategy logic on top of Polymarket API calls and extend plugin for order management (answered by sedano.npc)

**Q: Are you setting this up on cloud or within the cli + elizaOS framework?** (asked by Kenk)  
**A:** cli + framework (answered by sedano.npc)

## Community Help & Collaboration

**DorianD → 코인케인**: Confirmed suspicious migration message from "elizaOS live support" was fake and directed to check labs-announcements channel for official migration info

**Odilitime → ElizaBAO**: Confirmed tip.md wallet connection safety, explaining it's Roam's app

**Broccolex → kiddala**: Directed to appropriate channel for migration help with non-functional transfer buttons

**M I A M I → DorianD**: Explained voice recognition implementation using Deepgram for STT with text-only output

**Kenk → sedano.npc**: Helped clarify deployment environment for vector DB + RAG setup

**sedano.npc → ElizaBAO**: Directed to upcoming Shaw tutorial stream and shared plugin-polymarket repository link for auto-trading questions

**cjft → sedano.npc**: Informed that plugin-knowledge now requires a subscription

**shaw → General team**: Provided detailed explanation of new 2.0 flag-based system and dynamic loading implementation

## Action Items

### Technical

- **Debug agent-twitter-client authentication failure on VPS** (isLoggedIn returns false, error code 34) - investigate data center IP blocking (Mentioned by: NintyNine)
- **Fix polymarket plugin bug** where agent retrieves older markets instead of latest ones (Mentioned by: sedano.npc)
- **Build data pool for agentic trading/decision making** based on trader semantics and habits (Mentioned by: M I A M I)
- **Investigate migration transfer button functionality issues** in Phantom wallet (Mentioned by: kiddala)
- **Add action params as optional** to reduce LLM calls by eliminating params extraction step (Mentioned by: 0xbbjoker)
- **Address database architecture issues** in 2.0 (Mentioned by: 0xbbjoker)
- **Build SQLite plugin** if message server is removed (Mentioned by: 0xbbjoker)

### Feature

- **Voice-commanded swap/trading functionality** for NIKITA interface (Mentioned by: M I A M I)
- **Mobile app version** of sentientspace.io (Mentioned by: M I A M I)
- **Text-to-speech voice generation** for NIKITA output (Mentioned by: M I A M I)
- **Research assistant** that scans socials and news (Mentioned by: DorianD)
- **AI launchpad** based on PumpFun implementation (Mentioned by: Mfairy)
- **Extend plugin-polymarket** to add trade execution logic including placing and canceling orders (Mentioned by: ElizaBAO)
- **Build strategy logic layer** on top of Polymarket API calls for auto-trading (Mentioned by: ElizaBAO)
- **Investigate strategies** to return to billion-dollar market cap and top 100 ranking to restore automated index investment flows (Mentioned by: DannyNOR NoFapArc, DorianD)

### Documentation

- **Clarify token use case and utility** for development/agent creation (Mentioned by: averma)
- **Clarify whether message bus is still needed** in 2.0 architecture (Mentioned by: Stan ⚡)
- **Document extended memory functionality** in 2.0 (Mentioned by: Odilitime)
- **Clarify bootstrap plugin necessity** and BOOTSTRAP environment variables behavior (Mentioned by: Stan ⚡, Odilitime)
- **Document policy layers, risk limits, and on-chain verification** for AI agent auto-trading safety (Mentioned by: aicodeflow)
- **Provide update on NDA-related matter** status and progression (Mentioned by: hirong)