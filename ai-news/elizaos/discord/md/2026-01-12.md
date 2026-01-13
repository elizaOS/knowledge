# elizaOS Discord - 2026-01-12

## Overall Discussion Highlights

### ElizaOS Tokenomics and Future Utility

The community engaged in extensive discussion about ElizaOS token value and utility. **DorianD** provided comprehensive analysis explaining that token value depends on the Jeju network becoming operational, where ElizaOS will serve as gas fees for AI agents. The adoption pathway outlined includes: (1) Jeju network launch, (2) developers building agents that consume elizaos for gas, and (3) integration of advertising networks to subsidize users. DorianD compared this model to Ethereum's growth, noting that Ethereum succeeded because developers used ERC-20 templates to launch projects, creating organic demand.

Community sentiment reflected concerns about price decline and lack of major exchange listings (Coinbase, Binance). DorianD argued against VC-backed pump models, stating serious investors would only enter if they believe ElizaOS becomes the dominant decentralized AI agent network with sufficient demand from ICOs or advertising revenue.

### ElizaCloud App Creator Development

Significant technical discussion centered on debugging ElizaCloud's new "app creator" feature, currently in early testing phase. **DorianD** extensively tested the feature and reported multiple critical issues:

- **Build system failures**: Operations timing out at 300s without proper error catching
- **Logging problems**: Console logs showing minimal useful information with empty run_command outputs
- **Git integration issues**: Commits managed automatically at end of state executions, but manual git commands through AI agent causing state corruption
- **Sandbox limitations**: 5 sandbox sessions per hour limit causing issues when users restart builds
- **File visibility bugs**: Files tab intermittently showing/hiding files
- **Context awareness**: AI agent not consistently accessing full codebase context

**cjft** explained the architecture: agents have file read/write, check_build, and bash tools. Commits auto-trigger after file update batches, with GitHub auto-deploying via Vercel CI. The system uses whitelisted commands to prevent users from breaking repositories. The target audience is non-technical users ("tiktokers"), requiring guardrails.

Solutions discussed include adding a stop button for runaway agents, implementing better logging toggles, adding proper git tools instead of relying on bash, implementing product manager-style requirements gathering, and adding console CLI access for direct commands.

### Infrastructure and CI/CD Issues

The core development team addressed a critical infrastructure issue: an expired `ANTHROPIC_API_KEY` in GitHub Actions causing CI job failures for Claude code analysis in the monorepo. **Stan** identified the issue and **Borko** resolved it by creating a separate key for CI/CD. The fix was applied to the monorepo but not to elizaos-plugins organization due to permission limitations.

**Odilitime** investigated whether elizaos-plugins needed the update but determined no Claude code review workflow existed in that repository, making the key update unnecessary.

### OAuth Relay Infrastructure Planning

A significant planning discussion involved **Vivek's** proposal for hosting an OAuth relay for plugin-twitter. The relay would be hosted at twitter-broker.elizaos.ai, use PostgreSQL, and handle OAuth callbacks. **Shaw** confirmed that cloud infrastructure already has APIs for this functionality, with the cloud acting as the callback endpoint. The team agreed to host the broker service, with Vivek providing code for audit. This appears to be a temporary solution, as Shaw mentioned oauth3 in "jeju" as the future implementation.

### Performance Optimization Discussions

**cjft** suggested exploring Rust runtime for serverless functions in Eliza 2.0 for performance optimization. **Shaw** clarified that runtime overhead is minimal compared to API, network, and database latency, noting that Bun already provides Rust-level performance. Shaw also mentioned having workerd with Bun in "jeju" and considered submitting a PR to Cloudflare, which **Odilitime** encouraged.

### Dynamic Facts API Challenge

**ballofrain** sought help adding dynamic facts to agents without restarting, trying multiple approaches: knowledge files (not loading), Sessions API (creates messages not facts), and Memory API (POST endpoint doesn't exist). **Odilitime** suggested adding plugin-knowledge to agent plugins, but ballofrain encountered module resolution errors, leaving this issue partially unresolved.

## Key Questions & Answers

**Q: Is the app creator in elizacloud still buggy?** (asked by DorianD)  
**A:** It's a new feature introduced for teams to test, no concentrated marketing yet. Building in production. (answered by Kenk)

**Q: What are these "apps" supposed to be for? Can they interface with agents?** (asked by DorianD)  
**A:** Should work yes, but the "app kit" isn't finished and guardrails will be added. Apps are meant for making money, not just X posting. (answered by cjft)

**Q: How do I save my work? I don't see a save button.** (asked by DorianD)  
**A:** Agent doesn't have ability to save from user request yet. It's done automatically after batch of file updates, each is a commit. Save !== deploy. (answered by cjft)

**Q: Can I access the console to type commands?** (asked by DorianD)  
**A:** Not currently available, but good idea. Agent has file read, write, check build, bash tools. Could implement sandbox CLI access. (answered by cjft)

**Q: Should users ever have to type git commit commands?** (asked by cjft)  
**A:** No, target users are non-technical (tiktokers), so proper git tools should be added to AI agent instead. (answered by cjft)

**Q: Did you renew the ANTHROPIC_API_KEY from Github actions?** (asked by Stan ⚡)  
**A:** Borko created a separate key for CI/CD to fix the issue. (answered by Borko)

**Q: Can the OIDC transfer from cloud?** (asked by Odilitime)  
**A:** Yes, the cloud becomes the callback. (answered by shaw)

**Q: Should i make a PR to cloudflare?** (asked by shaw)  
**A:** Odilitime encouraged seeing what initial review says. (answered by Odilitime)

**Q: Waiting for team to do what?** (asked by Biazs)  
**A:** Maybe to pump the price or more listings on big exchanges like coinbase and binance spot. (answered by Mo 1990)

## Community Help & Collaboration

**Kenk** helped **DorianD** understand the app creator feature status, explaining it's a new feature for team testing, not yet marketed, and requested error messages be shared in channel instead of Twitter replies or DMs.

**cjft** extensively assisted **DorianD** with multiple app creator issues:
- Clarified apps should interface with agents but app kit isn't finished, with guardrails coming
- Explained commits are managed automatically at end of state executions, can restore from history tab
- Identified that manual commits through AI not designed yet, history/state borked, recommended starting fresh app

**Borko** helped **Stan ⚡** resolve the expired ANTHROPIC_API_KEY causing CI job failures by creating a separate API key for CI/CD.

**shaw** helped **cjft** understand performance optimization, clarifying that runtime overhead is minimal and latency comes from APIs, network, and DB rather than runtime choice.

**shaw** helped **Odilitime** understand OAuth relay hosting and OIDC transfer capabilities, confirming cloud can act as callback endpoint and APIs already exist.

**Odilitime** helped **shaw** overcome hesitation about submitting PR to Cloudflare, encouraging submission to see initial review feedback.

**Odilitime** attempted to help **ballofrain** add facts dynamically to agents, suggesting adding plugin-knowledge to agent's plugins (partial resolution, ballofrain encountered module errors).

**Odilitime** helped **AlphaDev** with migration issues by directing them to the correct support channel.

## Action Items

### Technical

- Update ANTHROPIC_API_KEY secret in elizaos-plugins organization if needed (mentioned by Stan ⚡)
- Submit PR to Cloudflare for workerd with Bun integration (mentioned by shaw)
- Host OAuth relay for plugin-twitter at twitter-broker.elizaos.ai (mentioned by Odilitime)
- Audit code for twitter-broker OAuth relay when Vivek provides it (mentioned by Odilitime)
- Set up PostgreSQL for twitter-broker OAuth relay (mentioned by Odilitime)
- Launch Jeju network for AI agents to use elizaos as gas fees (mentioned by DorianD)
- Develop AI agents that consume elizaos tokens on the network (mentioned by DorianD)
- Integrate advertising networks into agents/apps to subsidize users (mentioned by DorianD)
- Fix build timeouts after 300s and improve error catching (mentioned by DorianD)
- Fix serverside caching issue on app side after deployment (mentioned by DorianD)
- Fix file visibility issue where Files tab intermittently shows/hides files (mentioned by DorianD)
- Improve agent context awareness to parse entire repo like Cursor does (mentioned by DorianD)
- Fix sandbox session limit issues (5 per hour) when users restart builds (mentioned by DorianD)
- Implement better reporting structure and prioritize production errors (mentioned by cjft)
- Fix plugin-knowledge module resolution error preventing installation (mentioned by ballofrain)
- Implement POST endpoint for Memory API to add memories dynamically (mentioned by ballofrain)

### Feature

- Listings on major exchanges like Coinbase and Binance spot (mentioned by Mo 1990)
- Add stop button to manually halt agent execution when it runs off in weird directions (mentioned by DorianD)
- Implement toggle for better logging in console with more useful output (mentioned by DorianD)
- Add proper git tools to AI agent instead of relying on bash commands (mentioned by cjft)
- Implement console CLI access for users to type commands directly (ls -la, etc) in sandbox (mentioned by cjft)
- Make assistant act more like product manager doing requirements gathering rather than just VP engineering/dev (mentioned by DorianD)
- Allow users to pick or provide methodologies (like Claude code workflows) for LLM to implement and guide users through (mentioned by DorianD)
- Make templates more varied instead of all using same sandbox template starter (mentioned by cjft)
- Add ability for agent to save from user request (mentioned by cjft)
- Consider open sourcing ElizaCloud platform for community contributions with bounties (mentioned by cjft)

### Documentation

- Document how to properly add dynamic facts to agents via API (mentioned by ballofrain)