# elizaOS Discord - 2026-01-26

## Overall Discussion Highlights

### Platform Integration & Partnerships
The partners channel explored a potential integration opportunity with the Seeker phone platform, which features a decentralized app (Dapp) store similar to Apple's App Store or Google Play Store. The proposal involves deploying Eliza as a Claude-style AI assistant on the platform, with the observation that current apps on the Seeker Dapp store are of poor quality, presenting an opportunity for Eliza to become a standout application.

### Technical Development & Bug Reports
**Plugin Action Handler Issues:** A significant technical discussion emerged around plugin action handler callbacks in Eliza framework version 1.7.2. The reported issue involved callbacks only sending the first response instead of multiple callbacks as documented, with callbacks being sent as action completion responses rather than immediate feedback. The investigation confirmed that multiple callbacks are indeed supported by the framework, with troubleshooting focusing on task planner configuration (onestep vs multistep).

**Team Updates:** Sam announced his return to work after medical leave for surgery, reporting 80% recovery and readiness to resume cloud-related projects. Shaw also rejoined the Discord server.

### Community Concerns & Token Discussion
The discussion channel saw significant community concern about ElizaOS token price performance, with multiple users expressing worry about continuous all-time lows. Key concerns included:
- Token validity and long-term viability
- Perceived lack of team communication during market downturns
- Token migration procedures (from Ledger and from ai16z to ElizaOS)

Community members provided reassurance by emphasizing ElizaOS's position as a leading AI agent project, contextualizing the price action within broader market volatility affecting all crypto assets, and sharing long-term investment strategies (4-year cycle approach).

## Key Questions & Answers

**Q: What is the seeker app?**  
A: Seeker phone has a Dapp store kind of like Apple/Google Play App Store (answered by 𝔭𝔩𝔞𝔱𝔞 𝔑𝔬 𝔉𝔞𝔭 𝔞𝔯𝔠)

**Q: Should it be possible to run multiple plugin action handler callbacks?**  
A: Yes, you can callback multiple times and some actions do so (answered by Odilitime)

**Q: Are you using onestep or multistep task planner?**  
A: Default settings (answered by Victor Creed)

**Q: Is the Elizaos token still valid? Is the community interested in it, or is it being left to die?**  
A: The token is valid; the market downturn is affecting all crypto, not just ElizaOS specifically. The team is building the future of AI agents and ElizaOS is among leading projects in this space (answered by Matthib123, Rainman)

**Q: How do I open a ticket?**  
A: Use channel #1425417640071139358 (answered by The Void)

## Community Help & Collaboration

**Plugin Callback Troubleshooting**  
Helper: Odilitime | Helpee: Victor Creed  
Odilitime assisted Victor Creed with investigating why plugin action handler callbacks were only sending the first callback instead of multiple callbacks as documented. Confirmed that multiple callbacks are supported and began systematic troubleshooting by asking about task planner configuration.

**Platform Information**  
Helper: 𝔭𝔩𝔞𝔱𝔞 𝔑𝔬 𝔉𝔞𝔭 𝔞𝔯𝔠 | Helpee: DorianD  
Provided clarification about the Seeker app, explaining it's a phone platform with a Dapp store similar to Apple/Google Play Store.

**Token Price Concerns**  
Helper: Matthib123 & Rainman | Helpee: paolin  
Multiple community members provided perspective on token price concerns, explaining that ElizaOS is a high-risk/high-potential asset, the whole market is in downtrend, and shared long-term holding strategies. Emphasized ElizaOS's position as a leading AI agent project.

**Migration Support**  
Helper: The Void | Helpee: realist  
Directed users needing token migration assistance (from Ledger and from ai16z to ElizaOS) to the appropriate ticket channel for formal support.

## Action Items

### Technical
- **Investigate plugin action handler callback behavior** - Investigate why plugin action handler callbacks only send first callback in clean 1.7.2 project with default settings (Mentioned by: Victor Creed)
- **Resume cloud project work** - Resume work on cloud projects following Sam's return from medical leave (Mentioned by: sam)

### Documentation
- **Verify callback documentation accuracy** - Verify documentation accuracy regarding callback behavior (immediate feedback vs action completion response) (Mentioned by: Victor Creed)
- **Clarify token migration process** - Clarify token migration process from Ledger and from ai16z to ElizaOS (Mentioned by: Jeburek12, realist)
- **Improve team communication** - Provide clearer communication about team activity and project status during market downturns (Mentioned by: paolin)

### Feature
- **Seeker platform integration** - Integrate Eliza on Seeker app as Claude bot style AI assistant to attract attention (Mentioned by: 𝔭𝔩𝔞𝔱𝔞 𝔑𝔬 𝔉𝔞𝔭 𝔞𝔯𝔠)