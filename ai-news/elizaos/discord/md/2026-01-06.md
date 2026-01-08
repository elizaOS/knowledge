# elizaOS Discord - 2026-01-06

## Overall Discussion Highlights

### Discord Plugin Integration Issues

A critical bug emerged in ElizaOS v1.7.0 affecting Discord plugin functionality. DigitalDiva reported that the bot couldn't detect server ID, username, or server owner despite correct intent configurations and admin permissions. Error logs showed "No server ID found" originating from `room.serverId` being undefined.

**Root Cause & Resolution:**
Odilitime identified the issue as a transition from `serverId` to `messageServerId` in the codebase. The fix in PR #6333 didn't work with Discord plugin version 1.3.3, requiring testing across various Discord branches. The team recommended either:
- Downgrading to core v1.6.5
- Using the odi-17 branch with fixes for bootstrap's actions/providers
- Testing with minimal Discord.js hello world scripts to isolate permission issues

The core-devs team prioritized rushing out a release with the fix and cutting a new Discord release after comprehensive testing.

### Cloud Infrastructure & Architecture Improvements

**Performance Optimization:**
Stan identified multiple opportunities to improve monorepo latency and planned to submit several PRs. Key initiatives include:
- Cloud fixes for TOCTOU (Time-of-check to time-of-use) race conditions using a "deduct-before, reconcile-after" approach combined with deslop
- Runtime initialization optimizations requiring deeper testing and validation

**Discord Gateway Architecture:**
The team discussed connector gateway implementation and scaling strategies. Odilitime recommended reviewing the Jeju cloud branch containing Shaw's preferred Discord bridge implementation. Key architectural decisions:
- Simple event pumps are the preferred direction
- Multiple daemon instances per service needed for scale
- Voice connections require higher priority/bandwidth event pumps compared to text
- Preprocessing expected to provide significant benefits

### ElizaOS Development & Contributions

**New Contributors:**
aicodeflow introduced themselves as a blockchain + AI engineer offering expertise in:
- Cleaning up embedding delegation to avoid hidden dependencies in Anthropic/OpenAI configurations
- Redesigning plugins as "skills" rather than just integrations for better composability
- Building market-aware agents focused on interpretation/state rather than execution
- Agent autonomy with constraints and onchain execution layers with guardrails
- Prediction market templates and observability tooling

Odilitime directed them to the Spartan project (github.com/elizaos/spartan) for DeFi utilities and recommended starting with plugin-based development through elizaos-plugins repositories.

### Technical Issues & Solutions

**Destructive Migration Errors:**
Andrei Mitrea encountered errors when running `elizaos start` a second time, with the system blocking migrations that would drop columns like "agent_id" and "room_id" from the worlds table. The solution: set `ELIZA_ALLOW_DESTRUCTIVE_MIGRATIONS=true` for local development. Omid Sa also recommended using `elizaos dev` instead of `elizaos start` for continuous monitoring during development.

**Model Integration Issues:**
ElizaBAO faced "Model not found" errors when integrating ElizaOS cloud agents into their website. cjft resolved this by explaining the correct model parameter format requires provider prefixes:
- `openai/gpt-4o-mini`
- `anthropic/claude-sonnet-4.5`
- `google/gemini-2.5-flash`

**x402 Protocol Integration:**
AlleyBoss announced an updated library for x402 protocol integration with ElizaOS (`@alleyboss/micropay-solana-x402-paywall`), offering a simplified implementation approach.

### Token Migration & Marketing

Multiple users inquired about AI16Z to ElizaOS migration mechanics. Key clarifications:
- Purchases after the November 11 snapshot aren't eligible for migration (confirmed by Omid Sa)
- Questions arose about the 120X calculation based on market cap differences
- Community concerns about ElizaOS contract address visibility on official X accounts, which shaw committed to addressing
- Discussion about best practices for CA visibility, with plans to update linktree to point to CoinGecko

### DegenAI & Project Updates

meltingsnow inquired about DegenAI updates, noting it seemed "pretty basic still." satsbased confirmed the new version hasn't shipped yet. BingBongBing expressed bullish sentiment on ElizaOS GitHub activity and mentioned DegenAI developments at 1M market cap.

### Documentation & Knowledge Sharing

- jin shared RSS feed URLs for ElizaOS documentation and suggested creating a combined dashboard with multiple data sources
- jin shared GitHub workflow reference for documentation updates from GitHub Next's agentics repository
- Stan created documentation on HackMD and requested team review
- The team identified an incorrect fact about Eigenlayer on their website that was being propagated by LLMs, agreeing to omit it from future content

### Development Tools & Insights

Odilitime shared findings from a Cursor call revealing that using your own Claude API key means you don't get Cursor's optimized version of Claude with their output improvement tricks.

## Key Questions & Answers

**Q: Why does the Discord plugin show "No server ID found" error?**
A: This is because we're moving from serverId to messageServerId, related to using develop branch of elizaOS. (answered by Odilitime)

**Q: What version of ElizaOS should I use to fix Discord plugin issues?**
A: Might be easier to use an older core like 1.6.5, or try the odi-17 branch with fixes. (answered by Odilitime)

**Q: How do I run elizaos start without getting destructive migration errors?**
A: Set `ELIZA_ALLOW_DESTRUCTIVE_MIGRATIONS=true` when starting: `ELIZA_ALLOW_DESTRUCTIVE_MIGRATIONS=true elizaos start` (answered by ! "Ꚃ.ഡ𝑒𝒶𝓋𝑒𝓇")

**Q: What command should I use for continuous development monitoring?**
A: Use `elizaos dev` instead of `elizaos start` for continuously monitoring code changes. (answered by Omid Sa)

**Q: What's the correct model parameter format for ElizaOS cloud agent API endpoints?**
A: Use provider prefix format like openai/gpt-4o-mini, anthropic/claude-sonnet-4.5, or google/gemini-2.5-flash. (answered by cjft)

**Q: If I buy AI16Z now and migrate after 30 days, will I get 120X?**
A: If you buy after the snapshot (11 November) you can't migrate. (answered by Omid Sa)

**Q: What changes have been made with DegenAI?**
A: The new version hasn't shipped yet, still seems pretty basic. (answered by satsbased)

**Q: How can I help with ElizaOS development?**
A: Start by reading the code and asking questions, work on plugins from github.com/elizaos-plugins/. (answered by Odilitime)

**Q: Should each problematic connector have its own gateway?**
A: Direction is simple event pumps, and we'll need more than one daemon instance per service for scale. Voice connections will need higher priority/bandwidth event pumps than text. (answered by Odilitime)

**Q: Do we have a team or workspace on hackmd?**
A: Yes, https://hackmd.io/@elizaos/book (answered by jin)

## Community Help & Collaboration

**Odilitime → aicodeflow**
Connected blockchain/AI engineer to Spartan project (DeFi utilities), provided GitHub link and guidance on plugin-based development for contributing to ElizaOS ecosystem.

**Odilitime → DigitalDiva**
Identified serverId to messageServerId transition issue causing Discord plugin failures, recommended downgrading to 1.6.5 or using odi-17 branch with fixes.

**shaw → DigitalDiva**
Suggested creating minimal hello world script with discord.js to isolate permission issues from Discord developer portal for debugging bot configuration.

**! "Ꚃ.ഡ𝑒𝒶𝓋𝑒𝓇" → Andrei Mitrea**
Explained to set ELIZA_ALLOW_DESTRUCTIVE_MIGRATIONS=true for local development when encountering destructive migration errors, safe for dev but requires review for production.

**cjft → ElizaBAO**
Provided correct model parameter format with provider prefixes (openai/, anthropic/, google/) to resolve "Model not found" error when calling agent API endpoints.

**Omid Sa → General community**
Recommended using elizaos dev command instead of elizaos start for live code monitoring during development.

**Odilitime → Stan ⚡**
Recommended reviewing Jeju cloud branch with Shaw's preferred Discord bridge implementation for Discord connector work.

**jin → Stan ⚡**
Confirmed existence of HackMD team workspace and shared link for documentation collaboration.

**Kenk → aicodeflow**
Suggested connecting with Odilitime and mentioned upcoming open sessions for new contributors.

**Omid Sa → nancy**
Clarified that purchases after November 11 snapshot cannot migrate for AI16Z token migration.

## Action Items

### Technical

- **Fix Discord plugin serverId to messageServerId transition issues in core v1.7.0** (Mentioned by: Odilitime)
- **Rush out release with 1.7.0 fix from PR #6333** (Mentioned by: Odilitime)
- **Test Discord fix with various Discord branches and cut new Discord release** (Mentioned by: Odilitime)
- **Test and merge odi-17 branch fixes for bootstrap actions/providers compatibility with plugin-discord 1.3.3** (Mentioned by: Odilitime)
- **Investigate and fix Discord bot server ID detection issue causing "No server ID found 10" error** (Mentioned by: DigitalDiva)
- **Submit multiple PRs for monorepo latency improvements** (Mentioned by: Stan ⚡)
- **Implement cloud fixes for TOCTOU race conditions using deduct-before, reconcile-after approach** (Mentioned by: Stan ⚡)
- **Complete runtime initialization optimizations with deeper testing and validation** (Mentioned by: Stan ⚡)
- **Clean up embedding delegation on agent side to avoid hidden dependencies** (Mentioned by: aicodeflow)
- **Redesign plugins as "skills" rather than just integrations for better composability** (Mentioned by: aicodeflow)
- **Build market-aware agents focusing on interpretation/state instead of execution** (Mentioned by: aicodeflow)
- **Develop agent onchain execution layers with explicit guardrails for DeFi interactions** (Mentioned by: aicodeflow)
- **Build practical agent templates for prediction markets and event-driven systems** (Mentioned by: aicodeflow)
- **Create observability and accountability tooling for inspectable agent decisions** (Mentioned by: aicodeflow)
- **Investigate Polymarket-based agent plugins for prediction markets** (Mentioned by: meltingsnow)

### Documentation

- **Post ElizaOS contract address on official X accounts** (Mentioned by: degenwtf, shaw)
- **Update linktree to point to CoinGecko for token information** (Mentioned by: Kenk)
- **Improve discoverability of contract addresses within 10 seconds on website/Twitter** (Mentioned by: Broccolex)
- **Document ELIZA_ALLOW_DESTRUCTIVE_MIGRATIONS flag usage for development vs production** (Mentioned by: ! "Ꚃ.ഡ𝑒𝒶𝓋𝑒𝓇")
- **Document correct model parameter format with provider prefixes for API endpoints** (Mentioned by: cjft)
- **Document difference between elizaos dev and elizaos start commands** (Mentioned by: Omid Sa)
- **Review and provide feedback on Stan's documentation at https://hackmd.io/@0PzDTGXqRg6nOCDoEwaN-A/SyDNAAIVWe** (Mentioned by: Stan ⚡)
- **Avoid repeating incorrect Eigenlayer fact in future content** (Mentioned by: Borko)

### Feature

- **Create combined RSS dashboard integrating multiple ElizaOS data sources** (Mentioned by: jin)
- **Implement application building capabilities for agents** (Mentioned by: Connor On-Chain)
- **Ship new version of DegenAI with improvements** (Mentioned by: meltingsnow)