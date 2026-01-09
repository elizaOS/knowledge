# elizaOS Discord - 2026-01-07

## Overall Discussion Highlights

### Critical Bug Fixes and Version 1.7.0 Issues

The development team identified and addressed critical compatibility issues in ElizaOS version 1.7.0. **Odilitime** discovered that the bootstrap plugin had incomplete fixes causing "No server ID found 10" errors related to serverId to messageServerId migration. An urgent release (PR #6333) was prepared to address these issues, though compatibility problems persisted with Discord plugin version 1.3.3.

**Odilitime** created a fix branch (odi-17) on GitHub with patches for bootstrap's actions and providers to resolve compatibility issues. Users experiencing problems were advised to either downgrade to core version 1.6.5 or wait for the fixes to be tested and merged. The team planned to test the Discord fix across various branches before cutting a new Discord release.

### Architectural Decisions and Scaling Strategy

A significant architectural discussion emerged around connector gateways and scaling considerations. **Odilitime** proposed **simple event pumps** as the direction forward for handling multiple service connections. Key architectural decisions included:

- **Multiple daemon instances per service** to handle scale requirements
- **Differentiated event pump priorities** for voice connections (requiring higher bandwidth/priority) versus text connections
- **Preprocessing as an optimization strategy** for improved performance
- Review of the Jeju cloud branch containing Shaw's preferred Discord bridge implementation

### Cloud Infrastructure and Race Condition Fixes

**Stan** provided a comprehensive standup update detailing work on cloud fixes addressing **TOCTOU (Time-of-Check-Time-of-Use) race conditions** using a deduct-before, reconcile-after approach. Runtime initialization optimizations were also completed, with corresponding Linear tickets created for tracking.

### API Integration and Model Configuration

A technical issue was resolved regarding ElizaOS cloud agent integration. Users attempting to integrate agents into websites using agent IDs and API endpoints encountered "Model not found" errors. **cjft** provided the solution: model parameters must use provider prefix format such as `openai/gpt-4o-mini`, `anthropic/claude-sonnet-4.5`, or `google/gemini-2.5-flash`.

### Community and Documentation Improvements

Multiple discussions highlighted the need for better visibility and documentation:

- **Contract address discoverability**: Community members noted difficulty finding the official ElizaOS contract address on X/Twitter accounts. The team committed to posting the CA across all official accounts and refreshing the linktree to point to CoinGecko.
- **Documentation workspace**: Confirmation that the team has a HackMD workspace, with the ElizaOS book documentation available at https://hackmd.io/@elizaos/book
- **Workflow documentation**: A valuable GitHub resource from githubnext/agentics regarding workflow documentation was shared for potential implementation.

### Discord Bot Integration Troubleshooting

**DigitalDiva** experienced Discord bot integration issues with ElizaOS 1.7.0, where the bot failed to recognize server IDs despite having admin permissions. Multiple community members provided debugging assistance:

- **Shaw** suggested creating a minimal hello world script with discord.js to isolate whether the issue was Discord portal permissions or code-related
- **Casino** recommended limiting bot permissions and incrementally adding features back to isolate the problem
- **Odilitime** diagnosed the root cause as compatibility issues between the bootstrap plugin and plugin-discord 1.3.3

## Key Questions & Answers

**Q: How should I format the model parameter when calling agent API endpoints?** (asked by ElizaBAO)  
A: Use provider prefix format like `openai/gpt-4o-mini`, `anthropic/claude-sonnet-4.5`, or `google/gemini-2.5-flash` (answered by cjft)

**Q: What version of ElizaOS should I use to avoid the server ID errors?** (asked by DigitalDiva)  
A: Either downgrade to version 1.6.5 or use the odi-17 branch with fixes, though it's still being tested (answered by Odilitime)

**Q: Why does the agent need admin privileges?** (asked by Odilitime)  
A: DigitalDiva gave admin permissions when the bot wouldn't respond or see server ID and usernames (answered by DigitalDiva)

**Q: Do we have a team or workspace on HackMD?** (asked by Stan ⚡)  
A: Yes, available at https://hackmd.io/@elizaos/book (answered by jin)

**Q: So each problematic connector would need its own gateway?** (asked by Stan ⚡)  
A: Direction is simple event pumps, and we'll need more than one daemon instance per service due to scale (answered by Odilitime)

**Q: Why hasn't the ElizaOS contract address been posted across all official X accounts?** (asked by degenwtf)  
A: The team will get on it (answered by shaw)

**Q: If I buy ai16z now and migrate after 30 days, will I get 120X?** (asked by nancy)  
A: If you buy after the snapshot (November 11) you can't migrate (answered by Omid Sa)

**Q: Is the Babylon that a16z invested in made by ElizaOS?** (asked by ElizaBAO)  
A: Nope (answered by degenwtf)

## Community Help & Collaboration

**Odilitime → DigitalDiva**: Diagnosed "No server ID found 10" error with ElizaOS 1.7.0 and bootstrap plugin, identifying serverId to messageServerId migration issues. Created GitHub branch (odi-17) with fixes for bootstrap's actions/providers and recommended either downgrading to 1.6.5 or using the fix branch.

**shaw → DigitalDiva**: Provided debugging strategy for Discord bot not responding or seeing server IDs. Suggested creating minimal hello world script with discord.js to isolate permission issues, recommended logging env vars and checking Discord dev portal permissions.

**Casino → DigitalDiva**: Offered troubleshooting approach for Discord bot permission problems by suggesting limiting scope/permissions and incrementally working back to desired features.

**cjft → ElizaBAO**: Resolved "Model not found" error when building elizaoscloud agents into website by providing correct model parameter format using provider prefixes (openai/, anthropic/, google/).

**Odilitime → Stan ⚡**: Recommended reviewing Jeju cloud branch with Shaw's preferred Discord bridge implementation at https://github.com/elizaOS/eliza-cloud-v2/tree/jeju/apps/discord-gateway for connector gateway work.

**jin → Stan ⚡**: Confirmed HackMD team/workspace availability and shared link to ElizaOS book documentation.

**Broccolex → Community**: Flagged issue that contract address is too hard to find and advocated for better discoverability on website/Twitter.

**Kenk → S_ling Clement**: Directed to connect with specific user for liquidity management partnership discussions.

**The Light → henry**: Directed to migration support channel for help migrating tokens held in Tangem at snapshot time.

## Action Items

### Technical

- **Rush out release with fix from PR #6333 for version 1.7.0** (Mentioned by: Odilitime)
- **Test Discord fix with various Discord branches to resolve compatibility issues with Discord 1.3.3** (Mentioned by: Odilitime)
- **Cut new Discord release after branch testing** (Mentioned by: Odilitime)
- **Test and merge odi-17 branch fixes for bootstrap plugin compatibility with plugin-discord 1.3.3** (Mentioned by: Odilitime)
- **Complete serverId to messageServerId migration across ElizaOS codebase** (Mentioned by: Odilitime)
- **Implement cloud fixes for TOCTOU race conditions using deduct-before, reconcile-after approach** (Mentioned by: Stan ⚡)
- **Complete runtime initialization optimizations** (Mentioned by: Stan ⚡)
- **Design scaling architecture for event pumps with multiple daemon instances per service** (Mentioned by: Odilitime)
- **Implement differentiated event pump priorities for voice (higher bandwidth) vs text connections** (Mentioned by: Odilitime)

### Documentation

- **Post ElizaOS contract address across all official X accounts** (Mentioned by: degenwtf, shaw)
- **Refresh linktree to point to CoinGecko for token information** (Mentioned by: Kenk)
- **Improve discoverability of official contract addresses on website/Twitter within 10 seconds** (Mentioned by: Broccolex)
- **Review documentation at https://hackmd.io/@0PzDTGXqRg6nOCDoEwaN-A/SyDNAAIVWe** (Mentioned by: Stan ⚡)
- **Review and potentially implement patterns from githubnext/agentics workflow documentation for updating docs** (Mentioned by: jin)

### Feature

- **Explore Polymarket-based agent plugins following Predict post mention** (Mentioned by: meltingsnow)