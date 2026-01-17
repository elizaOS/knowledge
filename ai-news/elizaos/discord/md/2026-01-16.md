# elizaOS Discord - 2026-01-16

## Overall Discussion Highlights

### Security & Authentication Concerns

**GitHub Repository Spoofing Incident**
A significant security concern emerged when community members discovered a suspicious GitHub repository (hash-llm) and Twitter account (@ctrlshifthash) containing commits that appeared to be from legitimate team members. Odilitime clarified this was not evidence of a hack but rather manipulated Git commits, explaining that anyone can use any email when making commits and commits can be moved from other projects. He verified his account security by noting his commits showed PGP signatures and he had MFA enabled. The team emphasized that only announcements in official channels should be trusted.

**Sparta Bot Security Confusion**
Casino raised concerns about Sparta requiring crypto wallet seed phrases and maintaining $100-500 in wallets. Odilitime and Chucknorris clarified this was incorrect, explaining that bots typically only need private keys. Chucknorris recommended using HSM vault for improved security with key pair signing.

### Advanced Trading Infrastructure Development

**Real-Time Solana Trading System**
Chucknorris detailed an extensive real-time Solana trading system built in Rust, featuring:
- gRPC streaming using Yellowstone Dragon's Mouth and Jito's ShredStream for ultra-low latency data ingestion
- Processing ~600 transactions/second with sub-150ms transfer times
- Real-time on-chain data streaming, bundle detection, KOL tracking
- Developer/rug detection, holder analysis, automatic token tracker creation
- Smart exits with trailing stops
- Monitoring 5k Twitter accounts for narrative/trend analysis
- Autonomous token launching based on hot narratives and breaking news

Chucknorris critiqued Sparta as "very utopian" with only API-based data and no real-time on-chain capabilities. The discussion covered database choices (PostgreSQL vs Clickhouse for massive data ingestion) and the role of AI vs algorithmic trading, with AI deemed too slow for decision-making at <0.01ms signing speeds.

### Token Economics & Market Dynamics

**Price Manipulation Analysis**
Significant discussion occurred around token price manipulation and selling pressure. Community members identified approximately $2 million USD worth of tokens being sold by 3 addresses, causing rapid price decline. Biazs shared a trading strategy of selling 80% during pumps and buying back incrementally during dips, gaining 30% more tokens. The consensus was that the token showed unnatural price action with heavy whale manipulation, though Alexei clarified it was not classified as a rug pull but rather serious selling that liquidity couldn't absorb.

### Development Priorities & Project Management

**Core Development Focus**
Shaw clarified development priorities in the core-devs channel, stating that cloud and app creation features must be completed first before launch. Action params and messageService components are already implemented, and freelancers are currently reviewing examples and Rust/Python implementations.

**PR Management Workflow**
Stan ⚡ worked on PR #6366 and PR #6113, successfully rebasing #6113 with working tests. Odilitime indicated that Shaw suggested holding PR #6113 for version 2.x release, putting the merge on hold pending final decision.

### Integration & Feature Development

**ChatVRM + ElizaOS Integration**
Supreem demonstrated a ChatVRM + ElizaOS integration using together.ai for unmoderated models, Tavily web search plugin, and ElevenLabs for TTS.

**3D Character Development**
The Void mentioned creating 3D characters with elizaos agents for Hyperscape integration.

**Project Updates**
M I A M I posted updates about ongoing development work, claiming to set records and encouraging collaboration over competition.

## Key Questions & Answers

**Q: Is the hash-llm GitHub repository legitimate or are team members hacked?**
A: Not hacked - commits are faked/moved from other projects. Only trust official announcements. (Odilitime)

**Q: How can commits appear from team members in a repo they never committed to?**
A: You can use anyone's emails when making commits, and commits can be moved from other projects. PGP signed commits prove authenticity. (Odilitime)

**Q: Does Sparta require giving out seed phrases and maintaining $100-500 in a wallet?**
A: No, bots normally only work with private keys. For improved security, install an HSM vault for key pair signing. (Odilitime and Chucknorris)

**Q: Why is the token dumping?**
A: Token is heavily manipulated by whales, with unnatural price action and forced selling pressure. (Biazs)

**Q: Is this a rug pull?**
A: Not a rug but serious selling going on - liquidity cannot absorb the volume. 3 addresses took about $2 million USD worth of tokens. (Alexei)

**Q: By real-time onchain data do you mean an oracle or indexer?**
A: gRPC streaming using Yellowstone Dragon's Mouth and Jito's ShredStream. (Chucknorris)

**Q: Wouldn't building an MEV solution using this be more profitable?**
A: MEV is more complex and nodes are subsequently banned. (Chucknorris)

**Q: What are you looking into Eliza for?**
A: To automate the process, understand runtime, memory, action, and how an agent functions independently to integrate advanced services. (Chucknorris)

**Q: Do you use any API to retrieve information about tokens/bundlers/patterns, or do you process everything through gRPC and RPC?**
A: Everything from gRPC. RPC is only used for signing, not fetching data. (Chucknorris)

**Q: What is the current development priority?**
A: Cloud and app creation need to be finished first before launch, then other features can be pulled in and reviewed. (Shaw)

**Q: Should PR #6113 be merged now?**
A: Shaw suggested saving it for 2.x, waiting for confirmation before merging. (Odilitime)

## Community Help & Collaboration

**Odilitime → Community (0xfreedom, Bard)**
Addressed confusion about suspicious GitHub repository and potential hack, explaining Git commit manipulation, verifying account security with PGP signatures and MFA, and confirming only official announcements are trustworthy.

**Chucknorris → Casino**
Clarified security concerns about bot wallet access, explaining bots use private keys and recommending HSM vault for improved security.

**Biazs → Community Investors**
Helped community understand token price manipulation and shared successful trading strategy of selling 80% during pumps and buying back during dips for 30% gain.

**Alexei → 거북알**
Addressed concerns about whether token situation was a rug pull, clarifying it's not a rug but identifying 3 addresses with $2M in sells causing liquidity issues.

**Kenk → Chucknorris**
Suggested Eliza is better for subjective trend analysis, citing VAIL's use case analyzing X spaces for alpha. Also informed that Spartan lead is active in channel and launching on Binance Square soon.

**Stan ⚡ → User 580487826420793364**
Provided positive feedback on their PR quality during code review.

**Odilitime → Stan ⚡**
Informed about Shaw's decision to potentially save PR #6113 for 2.x version.

## Action Items

### Technical

- **Add gRPC option to plugin-Solana for real-time on-chain data streaming** (Mentioned by: Odilitime)
- **Complete cloud and app creation features before launch** (Mentioned by: Shaw)
- **Evaluate PostgreSQL vs Clickhouse for massive data ingestion workload** (Mentioned by: Chucknorris)
- **Implement HSM vault for secure key pair signing in bot operations** (Mentioned by: Chucknorris)
- **Integrate Shred forwarding to complete transactions ahead of bundlers and large holders** (Mentioned by: Chucknorris)
- **Review PR #6366** (Mentioned by: Stan ⚡)
- **Final review of rebased PR #6113 with working tests** (Mentioned by: Stan ⚡)
- **Await Shaw's decision on whether to merge PR #6113 or save for 2.x** (Mentioned by: Odilitime)
- **Continue development work on setting records with the project** (Mentioned by: M I A M I)

### Feature

- **Create autonomous launcher agent based on hot trends/narratives with Twitter feed analysis of 5k accounts** (Mentioned by: Chucknorris)
- **Create 3D characters with elizaos agents for Hyperscape integration** (Mentioned by: The Void)

### Documentation

- **Establish clearer communication about official channels and how to verify legitimate team announcements vs spoofs** (Mentioned by: Bard)
- **Freelancers reviewing examples and Rust/Python implementations** (Mentioned by: Shaw)