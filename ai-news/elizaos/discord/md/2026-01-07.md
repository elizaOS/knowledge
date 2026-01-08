# elizaOS Discord - 2026-01-07

## Overall Discussion Highlights

### Critical Bug Fixes and Version Compatibility

**ElizaOS 1.7.0 Discord Integration Issues**

A critical bug was identified in ElizaOS version 1.7.0 affecting Discord bot integration. DigitalDiva reported persistent "No server ID found 10" errors related to the bootstrap plugin, with the bot failing to recognize server IDs despite having admin permissions. Odilitime diagnosed the root cause as incomplete serverId to messageServerId migration in the codebase, creating compatibility issues between the bootstrap plugin's actions/providers and plugin-discord 1.3.3.

**Resolution Path**

Odilitime created a fix branch (odi-17) on GitHub with patches addressing the bootstrap compatibility issues. He recommended either downgrading to core version 1.6.5 or waiting for the fixes to be tested and merged. An urgent release (PR #6333) was planned to address the 1.7.0 issues, though additional testing across multiple Discord branches would be required before cutting a new Discord release.

### Architectural Decisions and Scaling Strategy

**Connector Gateway Architecture**

A significant architectural discussion emerged in the core-devs channel regarding connector gateways and scaling. Odilitime proposed moving toward simple event pumps as the primary direction, emphasizing the need for multiple daemon instances per service to handle scale. The conversation highlighted different requirements for voice connections (requiring higher bandwidth/priority event pumps) versus text connections, with preprocessing identified as a valuable optimization strategy.

Odilitime recommended reviewing the Jeju cloud branch containing Shaw's preferred Discord bridge implementation as a reference for connector architecture.

### Cloud Infrastructure Improvements

Stan provided a standup update detailing work on cloud fixes addressing TOCTOU (Time-of-Check-Time-of-Use) race conditions using a deduct-before, reconcile-after approach. Runtime initialization optimizations were also implemented, with corresponding Linear tickets created for tracking.

### API Integration and Model Configuration

ElizaBAO encountered "Model not found" errors when integrating elizaoscloud agents into their website using agent IDs and API endpoints. cjft provided the solution: using provider prefix formats for the model parameter (e.g., openai/gpt-4o-mini, anthropic/claude-sonnet-4.5, or google/gemini-2.5-flash). This format (provider/model-name) was confirmed as the recommended approach.

### Community and Documentation

**Contract Address Visibility**

Multiple community members raised concerns about the difficulty of finding the official ElizaOS contract address (CA) on X/Twitter accounts. Broccolex and others noted that the current discoverability flow doesn't work well for most users. Kenk mentioned the linktree is being refreshed to point to CoinGecko for token information, and shaw confirmed the team would improve CA visibility across official channels.

**Documentation Resources**

Jin shared valuable documentation resources including the ElizaOS book on HackMD and a GitHub resource from githubnext/agentics regarding workflow documentation. Stan submitted documentation for review alongside plugin PRs for Telegram and Discord.

### Token Migration Clarification

Nancy asked about token migration eligibility, specifically whether buying ai16z now would qualify for the 120X migration after 30 days. Omid Sa clarified that purchasing after the November 11 snapshot means ineligibility for migration.

## Key Questions & Answers

**Q: How should I format the model parameter when calling agent API endpoints?**  
A: Use provider prefix format like openai/gpt-4o-mini, anthropic/claude-sonnet-4.5, or google/gemini-2.5-flash (answered by cjft)

**Q: What version of ElizaOS are you using?**  
A: Version 1.7.0 (answered by DigitalDiva)

**Q: Does that mean I can keep this version?**  
A: You could try cloning the odi-17 branch which should work with plugin-discord 1.3.3, but still testing (answered by Odilitime)

**Q: Why does the agent need admin privileges?**  
A: DigitalDiva gave admin permissions when the bot wouldn't respond or see server ID and usernames (answered by DigitalDiva)

**Q: If I buy ai16z now and migrate after 30 days, will I get 120X?**  
A: If you buy after the snapshot (November 11) you can't migrate (answered by Omid Sa)

**Q: Do we have a team or workspace on hackmd?**  
A: Yes (answered by jin, sharing https://hackmd.io/@elizaos/book)

**Q: So each problematic connector would need its own gateway?**  
A: Direction is simple event pumps, and we'll need more than one daemon instance per service due to scale (answered by Odilitime)

**Q: Why hasn't the ElizaOS contract address been posted across all official X accounts?**  
A: The team will get on it (answered by shaw)

**Q: Is the Babylon that a16z invested in by ElizaOS?**  
A: Nope (answered by degenwtf)

## Community Help & Collaboration

**Odilitime → DigitalDiva**  
Context: "No server ID found 10" error with ElizaOS 1.7.0 and Discord bot  
Resolution: Diagnosed serverId to messageServerId migration issue, created fix branch (odi-17) on GitHub, suggested downgrading to 1.6.5 or waiting for fixes

**shaw → DigitalDiva**  
Context: Discord bot not responding or seeing server IDs  
Resolution: Suggested creating minimal hello world script with discord.js to isolate permission issues, recommended checking Discord dev portal permissions and logging env vars

**Casino → DigitalDiva**  
Context: Discord bot permission problems  
Resolution: Suggested limiting scope/permissions and incrementally working back to desired features

**cjft → ElizaBAO**  
Context: "Model not found" error when building elizaoscloud agents into website with agent IDs and API endpoints  
Resolution: Provided correct model parameter format using provider prefix (e.g., openai/gpt-4o-mini, anthropic/claude-sonnet-4.5, google/gemini-2.5-flash)

**Odilitime → Stan ⚡**  
Context: Stan working on Discord connector implementation  
Resolution: Recommended reviewing Jeju cloud branch with Shaw's preferred Discord bridge implementation at elizaOS/eliza-cloud-v2/tree/jeju/apps/discord-gateway

**jin → Stan ⚡**  
Context: Stan asking about HackMD team workspace availability  
Resolution: Confirmed existence and shared link to https://hackmd.io/@elizaos/book

**Omid Sa → nancy**  
Context: Confusion about token migration eligibility and timing  
Resolution: Clarified that buying after November 11 snapshot means ineligible for migration

**Kenk → S_ling Clement**  
Context: Looking to connect with person responsible for liquidity management  
Resolution: Directed to connect with specific user for partnership discussion

## Action Items

### Technical

- **Rush out release with 1.7.0 fix from PR #6333** - Mentioned by Odilitime
- **Test Discord fix with various Discord branches and cut new Discord release** - Mentioned by Odilitime
- **Complete serverId to messageServerId migration across ElizaOS codebase** - Mentioned by Odilitime
- **Test and merge odi-17 branch fixes for bootstrap plugin compatibility with plugin-discord 1.3.3** - Mentioned by Odilitime
- **Review Telegram plugin PR #22** - Mentioned by Stan ⚡
- **Review Discord plugin PR #41** - Mentioned by Stan ⚡
- **Implement cloud fixes for TOCTOU race conditions using deduct-before, reconcile-after approach** - Mentioned by Stan ⚡
- **Optimize runtime initialization** - Mentioned by Stan ⚡
- **Plan scaling architecture for event pumps with consideration for voice vs text priority/bandwidth requirements** - Mentioned by Odilitime

### Documentation

- **Review agentics workflow documentation for updating docs at github.com/githubnext/agentics** - Mentioned by jin
- **Review documentation at https://hackmd.io/@0PzDTGXqRg6nOCDoEwaN-A/SyDNAAIVWe** - Mentioned by Stan ⚡
- **Refresh linktree to point to CoinGecko for token information** - Mentioned by Kenk
- **Improve discoverability of ElizaOS contract address on official channels** - Mentioned by Broccolex, shaw, degenwtf

### Feature

- **Explore Polymarket-based agent plugins following Predict post mention** - Mentioned by meltingsnow