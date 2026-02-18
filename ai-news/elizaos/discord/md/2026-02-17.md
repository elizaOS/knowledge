# elizaOS Discord - 2026-02-17

## Overall Discussion Highlights

### ElizaOS News Platform Development

Jin made significant progress on the elizaos.news platform, experimenting with various design approaches before settling on a "spread" design that offers better visual appeal and readability. The platform features 100% automated video generation using PlayCanvas (not AI rendering), with automated subtitles and agent narration. A notable upcoming feature is 1-1 interview functionality where users interact with a chatbot, and conversations are transformed into generated interview shows that combine human and AI elements.

### Spartan Setup & Plugin Architecture Challenges

Einav Livne encountered significant installation issues with Spartan, experiencing hanging during `bun install` due to missing plugins (@elizaos/plugin-evm, plugin-farcaster, plugin-jupiter, plugin-knowledge, plugin-mysql, plugin-solana) that required manual cloning. Odilitime acknowledged that Spartan setup remains challenging and hasn't been polished yet due to ongoing plugin upgrades. While Docker files exist, they are currently non-functional. The good news is that plugin installation order doesn't matter, providing some flexibility during setup.

### Milady.ai Project Status & Distribution Issues

The milady-ai/milady project encountered a distribution problem where `npx milady` installed an unrelated, unmaintained Alibaba tool instead of the intended project. Odilitime confirmed the project is in pre-release status and recommended using binaries from GitHub releases instead. Issue #324 was opened to address the npm package confusion.

### MoltBridge Integration Exploration

Vlt9 discussed potential integration between MoltBridge and the Agentic Web system. Their current Beta phase implementation uses header-based API keys for developer integration and stress-testing of scoring logic. They acknowledged the need to transition to cryptographic identity (request signing) for a truly decentralized agent-to-agent (A2A) economy. The discussion centered on mapping security signals into a trust graph and exploring identity standards for oracle accessibility within MoltBridge-native agents.

### Team Changes & Token Economics

Important organizational updates were shared: CJ was replaced by Hanzla, who had been contributing to Shaw's projects. Sayo transitioned from team member to partner status but continues to work daily with the project. Regarding recruitment, the team is not actively hiring but developers can get noticed by contributing to Shaw's periodic project callouts (every 1-2 months). On the token front, the team confirmed that $elizaos is the main token and that buybacks are conducted using revenue, with Odilitime committing to clarify timing and public disclosure processes with the Ops team.

### AI Model Updates

Odilitime announced the release of Sonnet 4.6 (likely referring to Claude Sonnet 4.6), though no implementation details were discussed.

### Security & Infrastructure

A brief security concern arose when Odilitime discovered an "API Explorer Key" in their cloud account without their knowledge. However, this was quickly self-resolved after confirming that the API Explorer automatically creates this key as part of its normal operation.

## Key Questions & Answers

**Q: Is $milady.ai the token?**  
A: Yes, confirmed by MDMnvest who added the contract address to the appropriate channel.

**Q: Why does bun install hang after cloning plugins manually?**  
A: Einav fixed the bug themselves; Odilitime confirmed Spartan is difficult to set up and hasn't been polished yet.

**Q: Is there an order to clone and install plugins to prevent breaking?**  
A: Order doesn't matter (Odilitime).

**Q: What's the use of $elizaos coins now?**  
A: It's the main token, team does buybacks with revenue (Odilitime).

**Q: When will the team buy back and will it be made public?**  
A: Odilitime will ask Ops team during sync later this week.

**Q: Have several people left the team and are new people joining?**  
A: After CJ left, replaced with Hanzla; Sayo is now a partner working daily with the team (Odilitime).

**Q: Are you guys recruiting?**  
A: Not hiring currently; best way is to work on Shaw's projects when he calls for devs every 1-2 months (Odilitime).

**Q: Can the milady-ai/milady project be tested?**  
A: Yes, but it's not on npm yet, use binaries from GitHub releases (Odilitime).

**Q: Is milady officially released yet?**  
A: It's pre-release (Odilitime).

**Q: Is the video AI generated or manually edited?**  
A: 100% automated, using PlayCanvas not AI rendering (jin).

**Q: Are you open to a quick DM or a technical chat to discuss a potential integration?**  
A: Unanswered (asked by Vlt9 regarding MoltBridge integration).

## Community Help & Collaboration

**MDMnvest → jin**  
Provided design feedback for the news site, confirming the "spread" design was more visually appealing with better readability.

**Odilitime → Einav Livne**  
Addressed multiple concerns about Spartan setup, confirming that plugin installation order doesn't matter and acknowledging the setup difficulties. Also provided clear guidance on how to join the team through contributing to Shaw's projects.

**Odilitime → work**  
Explained the $elizaos token buyback mechanism and committed to getting timeline information from the Ops team. Also clarified recent team changes.

**Odilitime → davidhq**  
Resolved the milady-ai/milady testing issue by directing to GitHub release binaries instead of npm, and opened issue #324 to address the package confusion.

**jin → ElizaBAO**  
Explained the 100% automated PlayCanvas video generation system and described the upcoming interview feature functionality.

## Action Items

### Technical

- **Fix npx milady command installing wrong package** (GitHub issue #324) - Mentioned by Odilitime
- **Complete plugin upgrades that are blocking Spartan polish work** - Mentioned by Odilitime
- **Fix Docker files for Spartan that currently don't work** - Mentioned by Odilitime
- **Explore integration between MoltBridge's graph-based trust system and Agentic Web security signals** - Mentioned by Vlt9
- **Transition from header-based API keys to cryptographic identity (request signing) for decentralized A2A economy** - Mentioned by Vlt9
- **Map security signals into trust graph for MoltBridge integration** - Mentioned by Vlt9

### Documentation

- **Create better instructions for Spartan setup including required vs optional plugins list** - Mentioned by Odilitime
- **Define identity standards for oracle accessibility to MoltBridge-native agents** - Mentioned by Vlt9
- **Clarify timing and public disclosure process for $elizaos token buybacks** - Mentioned by work

### Feature

- **Implement 1-1 interview functionality with chatbot for elizaos.news** - Mentioned by jin
- **Concept and storyboard the look for new interview feature** - Mentioned by jin