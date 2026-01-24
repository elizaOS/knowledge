# elizaOS Discord - 2026-01-23

## Overall Discussion Highlights

### Token Launch Controversies and Community Concerns

The day was dominated by significant controversy around token launches, particularly the **GOLD token** associated with Hyperscape. Community members identified multiple red flags including a 40% dev wallet, insider trading patterns with wallets funded 3 days prior to launch, and approximately $150k extracted through coordinated early entries. The launch followed a suspicious pattern of silence during speculation followed by CA confirmation only after price movement. Shaw later clarified this was a "gold presale" token, not the main Hyperscape token, and acknowledged critical issues with liquidity pool management that "rekt" the token supply. The main Hyperscape token will have fixed tokenomics and won't launch on pump.fun.

**CJFT token** was confirmed as official by Odilitime, with the creator engaging in content creation including YouToy integration and live streaming. **BAGS token** was mentioned as a Hyperscape funding token/creator token for ElizaOS projects, though details remained unclear.

### Project Direction and Value Proposition Concerns

Significant community frustration emerged regarding the **ai16z project** direction. One member reported losses from $28k to $800, criticizing the team for building multiple projects without focusing on monetization and user acquisition. Key concerns included:
- Lack of clarity on how new projects translate to value for Eliza OS token holders
- Need for focus on **Eliza Cloud** as a resource-intensive priority
- Calls for transparency on project monetization strategy and customer acquisition

### Platform and Infrastructure Updates

**Hyperfy Platform Sunset**: Hyperfy announced the shutdown of their legacy hyperfy.io hosted platform on April 1st, 2026. The platform has transitioned to a fully open-source, self-hosted model. World NFT holders already received $HYPER token airdrops, completing the transition from the NFT-based platform model. Users can self-host or use providers like hyperworld.host, and must download content and data before the shutdown date.

**ElizaCloud Development**: ElizaBAO discussed elizacloud website updates and expressed interest in building a competitive prediction agent similar to Polymarket, questioning whether elizacloud uses OpenAI GPT-4 and proposing a multi-AI competition model.

### Technical Developments

**Discord Plugin Issues Resolved**: DigitalDiva encountered critical errors including missing audit log permissions and private field access errors in the recent messages provider. The solution was updating to Discord plugin version 1.3.8 using `bun add @elizaos/plugin-discord`, which resolved server functionality. However, DM issues persisted with role provider errors showing "User has no name or username, skipping."

**Migration Agent Implementation**: The Migration Agent uses **Claude Sonnet** as the underlying model, noted for well-structured responses and human-like emoji interactions in context.

**Sportradar Integration**: sedano.npc released the **Sportradar ElizaOS Plugin v.01**, providing live NBA data access for prediction agents. The plugin was shared on GitHub and confirmed to work well, offering real-time sports data integration capabilities.

**Channel Configuration Clarification**: Odilitime explained that channel IDs act as filters while listen channels bypass filtering and generate events for custom filtering logic.

### Airdrop Tax Optimization Strategy

DorianD proposed an innovative technical solution to avoid tax implications on airdrops. Instead of distributing tokens directly to individual wallets (triggering 1099 income tax), tokens would be sent to a single smart contract. This contract would use a price oracle to automatically buy and burn ElizaOS tokens based on a predetermined supply curve as the airdropped token appreciates. Key requirements:
- Contract must be immutable with no admin permissions
- Potentially deployed from a favorable tax jurisdiction
- Creates long-term alignment without individual tax events
- Differs from bond desk functionality, which operates as a vesting contract with delayed purchases at discounted rates

## Key Questions & Answers

**Q: Is the CJFT meme token official?** (asked by Collector_g)  
A: Yes, CJFT launched a token today, make sure you have the right one (answered by Odilitime)

**Q: What is the underlying model used for the Migration agent?** (asked by moosh_malone)  
A: Claude Sonnet (answered by Odilitime)

**Q: Do you guys offer grants for AI agents?** (asked by sogol_malek)  
A: Write up a pitch, no promises but doesn't hurt to try (answered by Odilitime)

**Q: How do you fix the Discord plugin private field access error?** (asked by DigitalDiva)  
A: Run `bun add @elizaos/plugin-discord` to update to version 1.3.8 (answered by 0xbbjoker)

**Q: What's the difference between channel IDs and listen channels?** (asked by implicit)  
A: Channel IDs are filters, listen channels bypass that and generate events for custom filtering (answered by Odilitime)

**Q: How does the bond desk agent work?** (asked by DorianD)  
A: It has a purchase with a delay that's negotiated, with a discount proportional to the delay - essentially a vesting contract (answered by Odilitime)

**Q: Is this the main Hyperscape token?** (asked by implied context)  
A: No, this is a gold presale token - the main Hyperscape token won't be a pump.fun launch and will have fixed tokenomics (answered by shaw)

**Q: What's up with the BAGS token you just claimed?** (asked by Donjuliotrader)  
A: It's the Hyperscape funding token / creator token for ElizaOS projects (answered by Odilitime, Ramith.V)

## Community Help & Collaboration

**Discord Plugin Resolution**: 0xbbjoker helped DigitalDiva resolve critical Discord plugin errors by instructing them to update to v1.3.8 using the bun add command, successfully fixing server functionality.

**Channel Configuration Guidance**: Odilitime clarified the distinction between channel IDs and listen channels for implicit, explaining filtering behavior and event generation.

**Token Authenticity Verification**: Odilitime confirmed CJFT token authenticity for Collector_g and rose, preventing potential scam losses.

**Grant Application Guidance**: Odilitime advised sogol_malek on the grant application process for AI agents, suggesting they write up a pitch.

**Security Warnings**: 
- Jeburek12 warned the community about migration scams, identifying support requests asking to send tokens as fraudulent
- Legz warned about GOLD token risks, identifying the 40% dev wallet as a red flag
- hans reported dev selling supply on DLMM

**Wallet Tracking**: Momo helped ElizaBAO track wallet funding sources, identifying that a suspicious wallet was funded by Shaw a year ago.

**Sports Data Integration**: sedano.npc shared the Sportradar ElizaOS Plugin with ElizaBAO and the community, providing live NBA data integration for prediction agents.

**Bond Desk Explanation**: Odilitime explained bond desk agent functionality to DorianD in the context of airdrop mechanisms.

## Action Items

### Technical

- **Investigate and fix DM functionality issues** with role provider showing "User has no name or username" error (Mentioned by: DigitalDiva)
- **Integrate Sportradar plugin** for live NBA data access in prediction agents (Mentioned by: sedano.npc)
- **Implement smart contract for airdrop tokens** that automatically buys and burns ElizaOS based on price oracle and supply curve, with no admin permissions (Mentioned by: DorianD)
- **Fix liquidity pool issues** on pump.fun token launch that damaged token supply (Mentioned by: shaw)
- **ElizaBAO video content competition** for community engagement (Mentioned by: ElizaBAO)
- **Pump.fun hackathon participation** requiring 10% token holdings (Mentioned by: ElizaBAO)

### Documentation

- **Clarify how new projects translate to value** for Eliza OS token holders (Mentioned by: V33)
- **Provide transparency on project monetization strategy** and customer acquisition (Mentioned by: Scrapy Coco)
- **Official announcement and clarification needed** for GOLD token launch (Mentioned by: Community consensus)
- **Clarify BAGS token purpose** and relationship to ElizaOS projects (Mentioned by: Donjuliotrader)
- **Users need to download content and data** from hyperfy.io platform before April 1st, 2026 shutdown (Mentioned by: Hyperfy)

### Feature

- **Focus resources on Eliza Cloud project** development and marketing (Mentioned by: Scrapy Coco)
- **Build prediction agent** with multi-AI competition model similar to Polymarket (Mentioned by: ElizaBAO)
- **Consider tying airdrop mechanism** to bond desk agent functionality (Mentioned by: Odilitime)
- **Use burned ElizaOS coins** to subsidize network usage by airdrop projects if Jeju network was operational (Mentioned by: DorianD)