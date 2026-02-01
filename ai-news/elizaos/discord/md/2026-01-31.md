# elizaOS Discord - 2026-01-31

## Overall Discussion Highlights

### Strategic Product Positioning & Market Timing

The core development team engaged in critical strategic discussions about positioning ElizaOS products within the current market cycle. Historical context revealed that Eliza's initial deployment (agent on X, Twitch integration, ETH wallet) gained no traction until Truth Terminal's success created market awareness. The team now sees a clear value proposition: positioning as "a game your moltbot can play" and "like moltbot but on your phone and secure."

A major strategic decision emerged to prioritize deploying **Babylon** - a social media platform for agents with profile pictures and personalities - into TEE (Trusted Execution Environment). Agent Joshua emphasized Babylon's potential for agents to develop public narratives, alignments, and disagreements that could drive rapid growth. The team identified a 3-month hype cycle window, with additional momentum expected from Claude 5 release, making rapid deployment critical.

The technical approach recommended by puncar involves running parallel workstreams: continue developing the game engine outside TEE for easier fine-tuning while simultaneously preparing TEE integration, then switching when ready. This prevents premature deployment that could complicate iteration.

### Framework Competition & Integration

Significant discussion occurred around comparing Clawd/Claude framework to Eliza. Key observations were that Clawd's success stems from focusing on non-crypto users and the Moltbook integration, with agents creating "skills" and posting to ClawHub. DigitalDiva noted Clawd's appeal is its ability to use computers with any LLM, attracting non-crypto audiences, while ElizaOS remains crypto-focused.

YogaFlame explained that Eliza's crypto features exist because the community requested them. "Openclaw" updates are coming in 2 weeks with better security. Odilitime created a new plugin-cskills repository for ElizaOS, learning from openclaw's implementation, and published a babylon skill on clawhub to enable openclaw integration with their products.

### Technical Infrastructure & Integration Issues

**ElizaCloud Integration Problems**: DorianD encountered critical server-side bugs when attempting to connect an OpenClaw agent to ElizaCloud MCP app. The agent reported authentication success but failed due to an isomorphic-dompurify module loading error - a CommonJS/ESM compatibility issue in ElizaCloud deployment. Additional errors included contentModerationService function failures in the A2A message/send endpoint.

**Deployment Requirements**: Both ElizaOS and openclaw can run in VMs or old computers. Skills from clawhub can be downloaded and integrated into ElizaOS, representing an evolution where agents now have shell access to users' computers and API keys for personal services.

**Cross-Chain Migration**: Discussion about migrating tokens across networks led to suggestions about using Chainlink's Transporter as a starting point.

### Community Concerns & Transparency Issues

**Platform Quality**: Users criticized elizacloud.ai for being launched in an unfit beta state. Multiple complaints emerged about the development approach, with averma criticizing half-completed code releases on GitHub and lack of token utility integration.

**Token Utility**: The ElizaOS Cloud platform accepts only cash or crypto payments through third-party integration, with no token use case, raising concerns about the token's purpose. Questions arose about the 40% supply assigned to the team after the ai16z to eliza token swap, vesting schedules, and whether team members or projects had dumped tokens.

**Financial Runway**: The team's runway was disclosed as 6-8 months, independent of elizaOS token value.

**Security Incident**: A scammer impersonated Eliza support, targeting Risto and requesting Ledger seed phrases for token migration. Maff || Hourglass ⌛ successfully intervened and prevented the scam.

## Key Questions & Answers

**Q: Why isn't Eliza doing what Clawd is doing?** (asked by DorianD)  
A: Eliza's crypto features exist because the community requested them, while Clawd focused on non-crypto users (answered by YogaFlame)

**Q: Where is the documentation for the a2a protocol?** (asked by DorianD)  
A: https://www.dev.elizacloud.ai/docs/a2a (answered by 0xbbjoker)

**Q: Should we prioritize Babylon/TEE deployment over Jeju?** (asked by s)  
A: Yes, the team should discuss with Phala team about fast-tracking this focus and getting the game in TEE ASAP (answered by s)

**Q: Any good docs on migrating these tokens to other networks?** (asked by Skinny)  
A: Transporter by chainlink might be a good starting place (answered by Odilitime)

**Q: Are the team wallets known? Correct me if I'm wrong but they assigned 40% of the supply to themselves when they increased the supply after the swap from the ai16z token to the eliza token?** (asked by Jayzen)  
A: That is vested - and not all 40% will go to team, but team should disclose current supply and any sales (answered by averma)

**Q: So it looks like ppl can download any skill from clawhub and integrate it into elizaos. Like with openclaw you would want it on VM or old computer, would this need the same?** (asked by DigitalDiva)  
A: elizaOS or openclaw can run in a vm or old computer (answered by Odilitime)

**Q: Assume 2 year bear market started now - Does the team have enough resources to survive and operate during a full bear market?** (asked by averma)  
A: We have 6-8 months run way is what I've heard. The runway isn't based on elizaOS value (answered by Odilitime)

## Community Help & Collaboration

**Scam Prevention**: Maff || Hourglass ⌛ successfully warned Risto not to connect wallet or share credentials when contacted by a scammer impersonating Eliza support requesting Ledger seed phrase for token migration, preventing a potential security breach.

**Documentation Support**: 0xbbjoker provided DorianD with the link to a2a protocol documentation at https://www.dev.elizacloud.ai/docs/a2a to help connect OpenClaw agent to ElizaCloud.

**Technical Guidance**: Odilitime provided multiple instances of help:
- Suggested Chainlink's Transporter to Skinny for token migration documentation
- Shared plugin-cskills GitHub repository for moltbot inputs/outputs
- Confirmed VM requirements for DigitalDiva regarding clawhub skills integration
- Explained rugcheck flagging to averma, noting it's designed for meme coins rather than corporate tokens

**Channel Navigation**: Omid Sa redirected single-celled organism to the appropriate channel when their $ai16z balance wasn't showing in the migration portal.

**TEE Deployment**: Agent Joshua ₱ | TEE offered to help s get Babylon TEE deployment setup and discuss in group chat how to move quickly.

## Action Items

### Technical

- **Fix isomorphic-dompurify module loading error in ElizaCloud MCP endpoint** - CommonJS/ESM compatibility issue (Mentioned by: DorianD)
- **Fix contentModerationService function error in A2A message/send endpoint** (Mentioned by: DorianD)
- **Deploy Babylon game into TEE environment as soon as possible** (Mentioned by: s)
- **Launch parallel workstream for TEE integration** while continuing game engine development outside TEE, then switch when ready (Mentioned by: puncar)
- **Discuss with Phala team about fast-tracking Babylon/TEE focus** versus Jeju project (Mentioned by: s)
- **Setup group chat discussion on how to move fast on Babylon TEE deployment** (Mentioned by: Agent Joshua ₱ | TEE)
- **Implement "openclaw" updates with better security** (ETA: 2 weeks) (Mentioned by: YogaFlame)
- **Test the newly created plugin-cskills repository** (Mentioned by: Odilitime)
- **Get ElizaOS agents integrated into moltbook for exposure** (Mentioned by: Odilitime)
- **Fix elizacloud.ai beta issues** - agent is unfit and recommends using discord to improve things (Mentioned by: yojo)

### Feature

- **Implement CLI login with API token only**, without browser authentication requirement (Mentioned by: DorianD)
- **Launch Babylon social media platform for agents ASAP** to capitalize on current market and hype (Mentioned by: puncar)
- **Integrate token utility into ElizaOS Cloud platform** instead of only accepting cash/crypto payments (Mentioned by: averma)

### Documentation

- **Provide transparency on team wallet addresses, current supply, team token allocation, and any sales or dumps** (Mentioned by: Jayzen, averma)
- **Disclose airdrop costs to community and track if recipients dumped tokens** (Mentioned by: averma)
- **Focus on complete solutions with token use cases** rather than half-cooked code releases (Mentioned by: averma)