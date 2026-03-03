# elizaOS Discord - 2026-03-02

## Overall Discussion Highlights

### Token Economics and Market Strategy

**Venice VVV Analysis and Tokenomics Proposal:**
DorianD provided comprehensive analysis of Venice VVV's market performance, noting its growth from a 1:1 market cap ratio in October to significant gains. The success was attributed to over 1 million users and Erik Voorhees' commercialization expertise from his Satoshi Dice background. Venice's tokenomics model includes a 50% supply airdrop to Base and AI community addresses, with stakers receiving free inference compute credits. This creates a freemium model where power users either pay API pricing or stake more tokens for additional compute access. With only 30% of token holders staking, 70% of network capacity remains available for commercial sale.

DorianD proposed applying a similar model to "Jeju," suggesting a mechanism where stakers receive proportional access to network inference tokens (1% stake = 1% of daily/block inference allocation). Compute providers would also stake and earn fees based on node utilization, creating economic pressure for hardware upgrades to maximize fee earnings. This dual-sided marketplace would balance compute supply and demand through staking mechanics.

**ElizaOS Token Clarification:**
Significant confusion emerged around the correct ElizaOS token between Solana and Base chains. Odilitime clarified that ElizaOS is cross-chain and provided the official Solana contract address: DuMbhu7mvQvqQHGcnikDgb4XegXJRyhUBfdU22uELiZA. The token was noted to be at a low price point, though market direction remained uncertain.

### Plugin Development and Technical Integration

**New Plugin Contributions:**
Meme Broker contributed three significant plugins to the elizaOS ecosystem:

1. **Heartbeat Plugin:** Functions as an internal cron job, similar to OpenClaw's implementation. After feedback from Odilitime, this was updated to integrate with plugin-bootstrap's task service rather than operating independently.

2. **MEM0 Integration:** A self-updating RAG system that processes all responses through a database layer before answering, enabling persistent conversations. MEM0 operates as a base URL for inference, routing every response through the database first, providing what Meme Broker describes as "super mega persistent convos."

3. **Skill-Loader Plugin:** Converts OpenClaw skill or skill.md files into elizaOS plugins, intended to bridge the gap between elizaOS and clawhub.

**APEX Oracle v0.5.0 Launch:**
Vlt9 introduced APEX Oracle v0.5.0, a deep-market analytics layer for Solana trading agents. The system addresses limitations of standard security checks (Mint Renounced, Freeze Authority) which are easily bypassed by Sybil clusters and wash-trading bots. Key features include:

- **Organic Absorption Ratio (OAR):** Detects volume recycling in developer-controlled clusters using Helius transaction history
- **Funding DNA Analysis:** Traces ancestor wallets to identify Sybil farms
- **Jito/MEV Toxicity Monitoring:** Tracks slot density and sandwich attack risks
- **ElizaOS Plugin:** Includes APEX_TOKEN_SCAN action with structured JSON output optimized for LLM context

The system seeks 5 developers for v0.5.0 API stress-testing.

### Community Updates and Platform Issues

**Content and Documentation:**
Jin announced the release of "Cron Job" episodes covering the last month of ElizaOS updates from GitHub and Discord, available on YouTube and m3org.com, with plans to add a development updates segment.

**Platform Technical Issues:**
Multiple users reported stuck balances on the auto.fun platform. Patatapicasa confirmed experiencing the same issue but successfully resolved it, though specific solutions were not detailed. Additionally, concerns were raised about an incorrect Milady agent running, with the BSC version noted to be building a solid base despite potentially being the wrong version.

**Community Signals:**
Burtiik noted Shaw's continued support for ElizaOS as a positive signal for the project.

## Key Questions & Answers

**Token and Market Questions:**

Q: Which token is the right one, sol or base?  
A: ElizaOS is cross-chain, see the token channel for details. The current Solana CA is DuMbhu7mvQvqQHGcnikDgb4XegXJRyhUBfdU22uELiZA (Odilitime)

Q: Is it a good time to invest?  
A: It's pretty low but the market does what it wants (Odilitime)

**Venice VVV Analysis:**

Q: What's pumping?  
A: Venice VVV took off, with market cap significantly higher than the 1:1 ratio from October (DorianD)

Q: How many users does Venice have?  
A: Over 1 million users (DorianD)

Q: What percentage of Venice supply was airdropped?  
A: 50% of supply airdropped on Base and AI community addresses (DorianD)

Q: What do stakers get from Venice?  
A: Free inference compute credits (DorianD)

Q: What percentage of people stake?  
A: Only 30%, leaving 70% network capacity for commercial sale (DorianD)

**Technical Questions:**

Q: Is there a chat where people are more active that requires a specific role?  
A: Not really, things are just quiet right now. Gave you the github contributors role (Odilitime)

Q: How can I edit the heartbeat plugin to use eliza tasks under the hood?  
A: It needs to integrate with plugin-bootstrap which has the task service (Odilitime)

Q: Is MEM0 any good?  
A: It's incredible - works as a base URL for inference, every response goes through the database first, provides super mega persistent convos, comparable to RAG but self-updating (Meme Broker)

Q: Is there anyone here whose balance is stuck in auto.fun?  
A: Yes, but got it sorted out (patatapicasa)

## Community Help & Collaboration

**Plugin Architecture Guidance:**
Odilitime assisted Meme Broker with improving the heartbeat plugin architecture, suggesting the use of eliza tasks under the hood via plugin-bootstrap's task service instead of an independent implementation. This guidance led to a more integrated and maintainable solution.

**Token Clarification Support:**
Odilitime provided crucial clarification to iory regarding token confusion between Solana and Base chains, explaining ElizaOS's cross-chain nature and providing the official Solana contract address to prevent potential scams or incorrect investments.

**Platform Issue Resolution:**
Patatapicasa confirmed experiencing the same auto.fun balance stuck issue as FlipZero💨 and indicated successful resolution, providing validation that the problem was solvable even though specific steps weren't detailed.

**APEX Oracle Integration:**
Vlt9 initiated collaboration with Meme Broker for APEX Oracle v0.5.0 integration, providing screening questions and documentation to facilitate proper implementation and testing.

## Action Items

### Technical

- **Update heartbeat plugin to integrate with plugin-bootstrap task service** (Mentioned by: Odilitime)
- **Stress-test APEX Oracle v0.5.0 API with trading agents and provide feedback on win rate impact** (Mentioned by: Vlt9)
- **Integrate APEX_TOKEN_SCAN action into agent decision-making flow for deep-market analytics** (Mentioned by: Vlt9)
- **Investigate why the wrong Milady agent is running** (Mentioned by: g)
- **Address auto.fun balance stuck issues for users** (Mentioned by: FlipZero💨)
- **Implement hardware upgrade incentive mechanism through utilization-based fee distribution for compute providers** (Mentioned by: DorianD)

### Feature

- **Implement Venice-style tokenomics for Jeju with proportional staking rewards (1% stake = 1% inference tokens)** (Mentioned by: DorianD)
- **Create dual-sided staking mechanism where compute providers stake and earn fees based on node utilization** (Mentioned by: DorianD)
- **Design freemium model using token staking to provide free inference compute with paid API pricing for power users** (Mentioned by: DorianD)
- **Integrate MEM0 plugin for persistent conversation management in elizaOS agents** (Mentioned by: Meme Broker)
- **Implement skill-loader plugin to convert OpenClaw skills into elizaOS plugins** (Mentioned by: Meme Broker)

### Documentation

- **Create segment covering development updates for Cron Job series** (Mentioned by: jin)