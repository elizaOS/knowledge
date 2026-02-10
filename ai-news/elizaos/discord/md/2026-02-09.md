# elizaOS Discord - 2026-02-09

## Overall Discussion Highlights

### Community Concerns & Token Economics

The most prominent theme across channels was significant community anxiety about token performance and project direction. Multiple users in **💬-discussion** expressed frustration over:

- **Token price decline** and perceived lack of utility for holders
- **Korean exchange delisting confusion**: Initial panic about ELIZAOS being delisted from Bithumb, Coinone, and Korbit was later clarified by **davidhq** and **paolin** - only the pre-rebrand AI16Z token was delisted, not the current ELIZAOS token
- **Team communication gaps**: Community members felt disconnected from development progress and questioned team commitment
- **Wallet monitoring**: Users tracked wallet address DScqtGwFoDTme2Rzdjpdb2w7CtuKc6Z8KF7hMhbx8ugQ (allegedly Shaw's) for potential token sales, though **ovo** and **davidhq** disputed selling claims and requested transaction proof
- **Developer departures**: Concerns raised about CJ and another unnamed developer leaving the project

**ovo** defended the team, noting Shaw covered unexpected costs to recover the X account and that the team burned 22M tokens. The discussion revealed a fundamental tension between open-source development work and token holder expectations for value appreciation.

### Technical Issues & Bug Reports

**💬-coders** surfaced several critical technical problems:

- **Agent Skills Provider Crash**: **azsxdc** reported a fresh milaidy VPS installation crash in the "agent_skill_instructions" provider where `skill.description.toLowerCase is not a function`. **Odilitime** confirmed this as a known bug requiring a fix
- **Normal vs. Critical Errors**: **Odilitime** clarified that server ID and ownership errors are normal and ignorable, while the pluginRegistryService 401 Unauthorized error represents work-in-progress functionality
- **Token Migration Deadline**: **ufw** discovered they missed the ai16z to ELIZA token migration deadline, asking if tokens were lost - this critical question went unanswered

### Product Development & Features

Several feature developments and requests emerged:

- **SillyTavern Integration**: **Vega** announced development of a plugin to use SillyTavern character cards for openclaw, promising release later
- **ElizaCloud.ai UX Optimization**: **yojo** provided detailed feedback suggesting prompt-only user features, visual generation optimization, plug-in marketplace, and crypto transfers without wallet connect
- **Wallet Management**: **kira** inquired about wallet management plugins for openclaw game skill integration with security considerations (unanswered)
- **Cardano Integration**: **Wes** questioned the need for Cardano wallet integration in ElizaOS (unanswered)
- **Hackathon Project**: **ElizaBAO** promoted their Colosseum Agent Hackathon project combining ElizaBAO + Claw with Polymarket signal scanning, x402/SOL paywall, and Moltbook autoposters

### Marketing & Visibility Efforts

**🥇-partners** focused on strategic positioning:

- **DorianD** emphasized the need for "organic" promotional content, sharing a LinkedIn post about OpenClaw/MoltBot AI as an example
- **Broccolex** shared a Twitter/X post from @joemccann to generate attention for Eliza
- **Krippトメア** acknowledged regime and world-order change use cases as representing a "different beast" in complexity

### Project Updates

- **jin** shared weekly roundup videos of ElizaOS updates in both **core-devs** and **💬-discussion**
- **Seppmos** shared a video covering Babylon and Hyperscape developments
- **s** confirmed existing WebSocket functionality via plugin/server

### Security Concerns

Multiple users encountered scam attempts, with **azsxdc** and **Odilitime** acknowledging the need for better autoban systems for scam support tickets. **Monsgroow.** confirmed to **ufw** that the support desk discord was a scam.

## Key Questions & Answers

**Q: Is $ELIZAOS going to be delisted from the 3 Korean exchanges?**  
**A:** Initial confusion was clarified by **davidhq** and **paolin** - only the pre-rebrand AI16Z token was delisted from Bithumb, Coinone, and Korbit, not the current ELIZAOS token. (Asked by avi_rajput563 | TABI 💢)

**Q: Are these errors normal on a fresh install on VPS for milaidy?**  
**A:** **Odilitime** confirmed that server ID and ownership errors are normal and ignorable, but the agent_skill_instructions crash is a bug needing fixing, and the pluginRegistryService 401 error is work-in-progress functionality. (Asked by azsxdc)

**Q: Where can I bridge eliza token from solana to bsc?**  
**A:** **EMERSON3S** confirmed there is currently NO official or safe bridge for Eliza from Solana to BSC. (Asked by clutch)

**Q: Is the support desk discord thing a scam?**  
**A:** **Monsgroow.** confirmed it is a scam. (Asked by ufw)

**Q: Is Shaw selling his elizaos tokens?**  
**A:** **gby** provided wallet address DScqtGwFoDTme2Rzdjpdb2w7CtuKc6Z8KF7hMhbx8ugQ claiming Shaw was selling; **ovo** and **davidhq** disputed this, requesting transaction IDs as proof. (Asked by gby)

## Community Help & Collaboration

**Odilitime → azsxdc**: Provided comprehensive troubleshooting for multiple errors on fresh milaidy VPS installation, distinguishing between critical bugs, normal errors, and work-in-progress features.

**EMERSON3S → clutch**: Prevented potential security risk by confirming no official bridge exists for ELIZA from Solana to BSC.

**Monsgroow. → ufw**: Protected user from scam by confirming support desk discord was fraudulent.

**davidhq & paolin → Community**: Clarified Korean exchange delisting confusion, preventing panic by explaining only AI16Z (pre-rebrand) was delisted, not ELIZAOS.

**ovo → Community**: Defended team actions by providing context about Shaw covering X account recovery costs and the 22M token burn.

**jin → Rainman**: Directed users to weekly roundup videos for project updates.

## Action Items

### Technical

- **Fix agent_skill_instructions provider crash** where skill.description.toLowerCase is not a function in @elizaos/plugin-agent-skills (Mentioned by: Odilitime)
- **Implement autoban system** for scam support tickets (Mentioned by: azsxdc)
- **Post weekly ElizaOS update videos** to dedicated channel using jintern (Mentioned by: jin)

### Feature

- **Generate organic promotional content** similar to the OpenClaw/MoltBot AI LinkedIn post (Mentioned by: DorianD)
- **Leverage Joe McCann's post** to generate attention for Eliza project (Mentioned by: Broccolex)
- **SillyTavern character cards plugin** for openclaw (Mentioned by: Vega)
- **Cardano wallet integration** for ElizaOS (Mentioned by: Wes)
- **Optimize elizacloud.ai UX** for prompt-only (zero coding) users including visual generation optimization, refer-to-friends offers, external agent interaction options, and crypto transfers without wallet connect (Mentioned by: yojo)
- **Create certified/recommended plug-in-and-play section** for elizacloud.ai to enable non-technical users to create use cases (Mentioned by: yojo)
- **Implement different up-selling packages** for elizacloud.ai users who prefer not to search for plugins themselves (Mentioned by: yojo)

### Documentation

- **Review weekly roundup** of elizaos updates video for potential documentation updates (Mentioned by: jin)
- **Clarify official position** on Korean exchange delisting situation (AI16Z vs ELIZAOS) (Mentioned by: davidhq, paolin)
- **Provide clear communication** about token migration deadline and options for users who missed it (Mentioned by: ufw)
- **Establish regular team updates** and communication channels for token holders (Mentioned by: Gem Hunter, averma, Rainman)
- **Clarify token utility** and use cases for token holders beyond open-source development (Mentioned by: averma)