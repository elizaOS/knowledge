# elizaOS Discord - 2026-01-22

## Overall Discussion Highlights

### Token Launch Crisis & Best Practices

A critical situation emerged when cjft launched a token with 75% of supply held by the developer, violating current crypto standards and creating rug pull concerns. Shaw provided urgent guidance on proper token launch practices:

- **Never sell tokens directly** - developers should rely on 2% creator fees from trading volume instead
- **Burn excess supply** - 70% of the 75% held should be burned, not locked
- **Wallet tracking consequences** - selling even 1 token marks the chart with "dev sold" and triggers bot dumping
- **Fee-based revenue model** - Shaw demonstrated viability by earning $80k in fees this week from a token someone else launched

The issue was resolved with cjft burning 70% of tokens using sol-incinerator.com after exporting private keys from bags.fm wallet to Phantom wallet.

### Token Migration Issues & Security Concerns

Multiple users encountered problems migrating AI16Z tokens to the new contract:

- **Robinhood wallet issue** - ryanb.btc transferred tokens from Robinhood wallet (lacking dapp browser) to another wallet, causing migration eligibility problems. Successfully resolved through support ticket system.
- **Scam attempt identified** - Jeburek12 reported being asked to send AI16Z tokens to a wallet address for migration. Kenk confirmed this was a scam, clarifying that legitimate migration doesn't require sending tokens to external addresses.

### Technical Infrastructure Issues

**elizacloud Server Problems:**
- Multiple users (untitled, xyz and ElizaBAO) reported "Application error: a server-side exception has occurred" preventing login
- Issues appeared intermittent with temporary resolution through hard refresh

**Database Migration Failures:**
- DigitalDiva encountered persistent "CREATE SCHEMA IF NOT EXISTS migrations" errors with both local and Aiven cloud Postgres databases
- Successfully resolved by switching to Neon database after troubleshooting pgvector image compatibility with 0xbbjoker

**Discord Integration Issues (v1.7.2):**
- Errors in recentMessagesProvider: "Cannot access invalid private field (evaluating 'this.#conversationLength')"
- Agent failed to respond in both channels and DMs
- 0xbbjoker investigating and clarified that CHANNEL_IDS serves as a channel whitelist

### Distributed Computation Concepts for Jeju

DorianD proposed innovative distributed computation architecture:

- **P2pool-style mining** - nodes working together with computation layers distributed across nodes and results compared to prevent cheating
- **Idle device utilization** - using iPhones with 8GB RAM to provide compute cycles when devices are idle (90%+ battery)
- **Anti-cheating mechanisms** - Chucknorris suggested ZKP (Zero-Knowledge Proofs), though DorianD noted only one Bittensor subnet (Omron) currently uses ZKP with limited commercial scalability
- **Data marketplace concept** - phone app to collect user data with local LLM extraction and sell valuable data on marketplace

### Community Concerns & Project Direction

Frustration emerged regarding project focus:

- **Multiple token launches** - DannyNOR NoFapArc and Jayzen criticized the team for launching multiple tokens instead of focusing on core infrastructure
- **Resource allocation** - Jayzen noted concerns about "scatterbrained decision-making" and spreading resources thin over tokens not directly tied to the underlying platform
- **ElizaOS liquidity concerns** - The Three Words expressed concerns about ElizaOS's low liquidity (110k LP) on Solana

### Platform Development Insights

Discussion comparing Second Life and Roblox as case studies for hyperscape development:

- Both platforms launched ~20 years ago, offering lessons for virtual world development
- **Roblox paradox** - despite billions in revenue and 380M MAU, platform remains unprofitable
- **User metric skepticism** - DorianD noted concerns about inflation from duplicate accounts and bot activity
- **Economic model concerns** - Odilitime characterized Roblox as a "jobs program," highlighting issues with platforms relying on unpaid/minimally compensated user labor

### Development Updates

- **RLM plugin** - Momo announced work on an RLM plugin for Eliza v2 after discussions with Shaw, marking their first major open-source contribution
- **GitHub repository cleanup** - Jin identified API issue showing 7-month-old .cursor repository in elizaOS repos
- **Cursor feature** - Parallel agents feature now supported
- **ElizaBAO competition** - Organizing video creator competition for ElizaBAO content involving ElizaOS and Polymarket, with Kenk advising to structure as clear challenge with bounties

## Key Questions & Answers

**Q: What should developers do with tokens instead of selling?**
A: Take 30% of fees for buybacks when token dips, keep rest for cloud/otaku pumps, do burns on app milestones like signups (shaw)

**Q: What happens if developers sell tokens?**
A: Wallet is tracked, all bots dump immediately, token dies (shaw)

**Q: Should tokens be locked or burned?**
A: Burn them, don't lock unless they burn (shaw)

**Q: How much can be made from creator fees?**
A: Shaw made $80k in fees this week from a token someone else launched (shaw)

**Q: Support is asking to send AI16Z to a wallet address for migration. Can the team publicly confirm this is legitimate?**
A: This is a scam; legitimate migration doesn't require sending tokens to external addresses (Kenk)

**Q: I bought ai16z before the crash in a Robinhood wallet without dapp browser. After transferring to another wallet, migration shows not eligible. Am I screwed?**
A: Issue resolved through support ticket system (Kenk)

**Q: Can you use distributed computation layers across nodes for Jeju to stop cheating nodes or spread workload?**
A: Use ZKP to avoid cheating (Chucknorris | ONYX P9 NODE RENT)

**Q: Is ZKP actually easy to implement currently and can you run that on consumer iPhones?**
A: Only one Bittensor subnet (Omron) uses ZKP with app-specific solution, not commercially scalable currently (DorianD)

**Q: Which postgres image are you using for local database?**
A: Aiven cloud Postgres with pgvector extension enabled (DigitalDiva)

**Q: Is CHANNEL_IDS= and DISCORD_LISTEN_CHANNEL_IDS the same thing?**
A: CHANNEL_IDS is a channel whitelist; without it agent will be in all channels (0xbbjoker)

**Q: How to access tokens from bags.fm for burning?**
A: Export private key from bags.fm/settings/wallets and import into Phantom (sayonara)

**Q: What tool should be used to burn tokens?**
A: sol-incinerator.com (sayonara)

## Community Help & Collaboration

**Token Launch Crisis Resolution:**
- **shaw → cjft**: Provided comprehensive guidance on proper token launch practices, explaining fee-based model, importance of not selling, and consequences of dev selling. Advised to burn 70% of tokens and rely on 2% creator fees.
- **sayonara → cjft**: Provided technical assistance with burning process, sharing sol-incinerator.com link and instructions to export private key from bags.fm/settings/wallets to import into Phantom.

**Migration Support:**
- **Kenk → Jeburek12**: Confirmed suspicious migration request was a scam attempt and directed to proper support channel.
- **Kenk → ryanb.btc**: Successfully resolved token migration eligibility issue after transferring from Robinhood wallet through support ticket system.

**Database Migration Troubleshooting:**
- **0xbbjoker → DigitalDiva**: Successfully resolved database migration failing with "CREATE SCHEMA IF NOT EXISTS migrations" error by switching to Neon database instead of Aiven.

**Discord Integration Issues:**
- **0xbbjoker → DigitalDiva**: Investigating Discord agent not responding after 1.7.2 update with recentMessagesProvider error, clarified CHANNEL_IDS configuration.

**Cloud Access Issues:**
- **Odilitime → untitled, xyz**: Confirmed elizacloud was working on their end during server-side errors, issue appeared intermittent.

**Migration Support:**
- **Odilitime → ParaTroop**: Directed to migration support channel for Base wallet migration issues.

**Security Warning:**
- **Arceon → The Three Words**: Successfully warned user not to engage with DM offer from Pebbles (scam attempt).

**Competition Organization:**
- **Kenk → ElizaBAO**: Advised to structure video creator competition as clear challenge with small bounties, acknowledging content creation complexity.

**Distributed Computation Discussion:**
- **Chucknorris | ONYX P9 NODE RENT → DorianD**: Suggested using ZKP (Zero-Knowledge Proofs) as solution for preventing cheating nodes in distributed computation.

## Action Items

### Technical

- **Burn 70% of launched token supply using sol-incinerator.com** (shaw, sayonara)
- **Investigate and fix elizacloud server-side exception errors preventing user login** (untitled, xyz)
- **Fix recentMessagesProvider error "Cannot access invalid private field (evaluating 'this.#conversationLength')" in version 1.7.2** (DigitalDiva)
- **Resolve Discord agent not responding in both channels and DMs after 1.7.2 update** (DigitalDiva)
- **Address token migration eligibility issues for users transferring from wallets without dapp browsers** (ryanb.btc)
- **Complete RLM plugin development for Eliza v2** (Momo)
- **Implement distributed computation layers across Jeju nodes similar to p2pool mining with result comparison to prevent cheating** (DorianD)
- **Implement ZKP (Zero-Knowledge Proofs) for Jeju to prevent node cheating** (Chucknorris | ONYX P9 NODE RENT)
- **Create networking/routing system for ad hoc clusters of devices with redundant compute and validators** (DorianD)
- **Transfer .cursor repository from elizaOS GitHub account to personal account as it's outdated (7 months old)** (jin)
- **Implement 30% fee buyback strategy when token dips** (shaw)
- **Set up token burns tied to app milestones like signup numbers** (shaw)
- **Research and analyze lessons from Second Life and Roblox's 20-year history to apply to hyperscape development** (DorianD)
- **Investigate sustainable business models for virtual world platforms that avoid Roblox's unprofitability despite massive scale** (DorianD)
- **Develop strategies to prevent user metric inflation from duplicate accounts and bots in hyperscape platform** (DorianD)
- **Delete promotional video about token with improper tokenomics** (shaw)
- **Delete all media related to improper token launch** (shaw)

### Feature

- **Focus development resources on core infrastructure rather than multiple token launches** (Jayzen)
- **Organize ElizaBAO video creator competition with clear challenges and bounties** (ElizaBAO)
- **Explore using idle iPhones (8GB RAM, 90%+ battery) to provide compute cycles for distributed processing** (DorianD)
- **Develop phone app to collect user data with local LLM extraction and sell valuable data on marketplace, plus process data during sleep** (DorianD)

### Documentation

- **Clarify legitimate migration process to prevent scam confusion regarding token transfers** (Jeburek12)
- **Create support ticket system for elizacloud issues** (untitled, xyz)
- **Create clear value proposition copy-paste message for token to avoid community backlash** (shaw)