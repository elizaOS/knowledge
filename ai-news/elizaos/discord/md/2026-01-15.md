# elizaOS Discord - 2026-01-15

## Overall Discussion Highlights

### Token Migration & Exchange Issues

The ai16z to elizaos token migration dominated community discussions, with **February 4th confirmed as the official deadline** by moderator Kenk. Multiple users encountered technical difficulties during the migration process:

- **Trust Wallet users** experienced "serialized message is not a function" errors
- **Phantom wallet users** reported non-functional migration buttons, resolved through clearing browser cache and site data
- **Bithumb exchange** completed their token swap, resolving concerns about wallet movements and potential price suppression

The migration eligibility was clarified by Arceon: only users who purchased ai16z before the snapshot are eligible to migrate. Conflicting information between the migration bot and official announcements created confusion that required moderator intervention.

### Market Sentiment & Project Positioning

Community members expressed significant concern over price performance, with mentions of -99.53% drops from peak values. DorianD noted the project's position outside the top 200 preventing auto-invest flows. Broccolex identified a lack of conscious effort to link the token with the project as contributing to price decline.

### Polymarket Trading Integration

Shaw released an **Eliza 2.0.0 example plugin for Polymarket trading**, describing the evolution from "sloppy" initial implementation to "pretty good" using Claude code. Key technical insights included:

- Polymarket has an **official API** and automated trading is legitimate and above board
- Alternative implementation available at github.com/Okay-Bet/plugin-polymarket
- Recommended architecture: custom code with SDK, private nodes, inline stream mempool for constant flow, and parallel CLOB API usage
- For multi-user scenarios: **BullMQ** suggested for worker management

### Jeju Network Technical Vision

DorianD provided substantive analysis of the planned Jeju decentralized compute network, acknowledging it as a "gargantuan undertaking" with uncertain timelines. The core technical challenge identified:

**Latency constraints** make parallelized inference across multi-node ad-hoc networks impractical for real-time LLM applications where users expect immediate responses.

**Viable use cases proposed:**
1. **Long-running agent tasks** with overnight execution windows where users check results asynchronously
2. **Autonomous agents** performing independent economic activities without human time-sensitivity constraints

These scenarios could effectively leverage decentralized networks for compute cycles and hardware resources.

### Socket.IO Integration & Plugin Development

Chucknorris encountered challenges accessing Socket.IO server from custom plugins to broadcast real-time events. The goal was pushing WebSocket data (tweets) to the frontend via `socketIO.emit()`. Issues included:

- `getGlobalAgentServer()` not being exported
- `MessageBusService.serverInstance` being private

Shaw provided guidance pointing to the socketio implementation in the develop branch and plugin-knowledge frontend examples. Chucknorris resolved the issue independently within 5 minutes by navigating through dependencies directly.

Supreem developed a **together.ai inference plugin** and sought contribution guidance, receiving documentation links to docs.elizaos.ai/plugins/development and docs.elizaos.ai/guides/contribute-to-core.

### Platform Issues & Bugs

**Discord Client Bug**: DigitalDiva reported a TypeError in the latest ElizaOS version where `this.runtime.elizaOS.sendMessage` is undefined, breaking Discord message handling.

**Windows/WSL Compatibility**: Casino struggled with Spartan setup on Windows without Docker, experiencing plugin path resolution errors. Chucknorris recommended WSL over PowerShell, though issues persisted in both environments.

### Core Development Updates

**PR #6113 Review**: Odilitime requested review for a PR pending since November, re-engineered to accommodate recent streaming work with focus on correctness over speed. Stan committed to reviewing and merging.

**Hiscores API**: Jin announced the addition of an API to the hiscores feature, documented at elizaos.github.io/api. Concerns were raised about the "hiscores" naming (inspired by RuneScape) potentially creating perception of the project being a grindfest. Alternative suggestions included "rpg stats," "player card," or "character sheet."

## Key Questions & Answers

**Q: Which info is true about migration deadline - Feb 4 or no deadline?**  
A: Feb 4th is the deadline for the migration (answered by Kenk)

**Q: Migration buttons don't work in Phantom wallet, any ideas?**  
A: Try disconnecting wallet, clear site data via Inspect > Application > Storage > Clear site data, then reload (answered by .)

**Q: How to access Socket.IO server from a custom plugin to broadcast events to the frontend?**  
A: Check the socketio implementation at github.com/elizaOS/eliza/blob/develop/packages/server/src/socketio/index.ts and plugin routes example at github.com/elizaos-plugins/plugin-knowledge/tree/1.x/src/frontend (answered by shaw)

**Q: What's the status with Polymarket's ToS on automated trading?**  
A: They have an official API and it's all above board - automated agents are fair game and benefit them by adding orders to the book (answered by shaw)

**Q: How to contribute a plugin to the community?**  
A: docs.elizaos.ai/guides/contribute-to-core (answered by Chucknorris | ONYX P9 NODE RENT)

**Q: Any update from Bithumb on the elizaos token movement?**  
A: The issue has been resolved, they completed their swap yesterday (answered by jasyn_bjorn)

**Q: What alternatives exist for the "hiscores" name?**  
A: Suggested alternatives include "rpg stats," "player card," or "character sheet" to make it more fun and gamesy (answered by Odilitime)

**Q: What is the status of PR #6113?**  
A: Stan committed to review and merge it, though delayed to the next morning due to time constraints (answered by Stan ⚡)

## Community Help & Collaboration

**Migration Support**
- **Hexx 🌐** helped **ppckl** with ticket creation for ai16z change, suggesting connection to Migration link on official website
- **Kenk** clarified migration deadline confusion for **chomppp**, confirming Feb 4th as official date
- **.** (moderator) provided step-by-step troubleshooting to **Defi | Doctore** for non-functional Phantom wallet buttons
- **Arceon** clarified migration eligibility for the general community

**Technical Development**
- **shaw** guided **Chucknorris** on Socket.IO access patterns and provided implementation examples
- **shaw** confirmed Polymarket API legitimacy for **Lxa**, addressing ToS concerns
- **Chucknorris** provided comprehensive Polymarket architecture recommendations to **ElizaBAO**
- **Chucknorris** supplied plugin development documentation to **Supreem**
- **Chucknorris** recommended WSL and manual plugin installation to **Casino** for Windows issues
- **sayonara** recommended alternative Polymarket plugin to **Lxa**
- **shaw** shared Polymarket plugin code with **ElizaBAO**

**Core Development**
- **Odilitime** suggested alternative naming conventions to **jin** for hiscores feature
- **Stan ⚡** committed to reviewing **Odilitime's** long-pending PR

**Exchange Issues**
- **jasyn_bjorn** confirmed resolution of Bithumb token swap for **sayitaintso25**

## Action Items

### Technical

- **Fix Discord client TypeError** where this.runtime.elizaOS.sendMessage is undefined in latest ElizaOS version (Mentioned by: DigitalDiva)
- **Resolve serialization error** "serialized message is not a function" in Trust Wallet during migration (Mentioned by: Sas)
- **Fix non-functional migration buttons** in Phantom wallet interface (Mentioned by: Defi | Doctore)
- **Resolve Spartan plugin path resolution issues** on Windows/WSL environments (Mentioned by: Casino)
- **Implement full gRPC** with track tx/pnl based on real-time tweet feed WSS with token and trend detection (Mentioned by: Chucknorris | ONYX P9 NODE RENT)
- **Review and merge PR #6113** which addresses correctness issues and was re-engineered for streaming work (Mentioned by: Odilitime)
- **Reconsider naming for hiscores API** to avoid negative perception (Mentioned by: jin)
- **Implement Jeju network** for decentralized compute with focus on non-time-sensitive agent workloads (Mentioned by: DorianD)
- **Improve Socket.IO server access pattern documentation** for custom plugins (Mentioned by: Chucknorris | ONYX P9 NODE RENT)

### Documentation

- **Clarify official migration deadline information** to resolve conflicting messages between bot and announcements (Mentioned by: chomppp)
- **Clarify Eliza 1.7 to 2.0 plugin compatibility** and migration path (Mentioned by: Supreem)
- **API documentation published** at elizaos.github.io/api for hiscores feature (Mentioned by: jin)

### Feature

- **Publish together.ai inference plugin** to community (Mentioned by: Supreem)
- **Convert pre-made Poly/Kalshi bot** into Eliza plugin and action (Mentioned by: Chucknorris | ONYX P9 NODE RENT)
- **Develop use cases for long-running agent tasks** that execute overnight without real-time latency requirements (Mentioned by: DorianD)
- **Create infrastructure for autonomous agents** to utilize decentralized compute cycles and hardware for independent economic activities (Mentioned by: DorianD)