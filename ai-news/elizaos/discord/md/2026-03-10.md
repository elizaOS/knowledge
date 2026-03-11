# elizaOS Discord - 2026-03-10

## Overall Discussion Highlights

### Project Communication & Community Relations

The **💬-discussion** channel revealed significant tension around project communication and token performance. Community members expressed frustration about missed deadlines, unclear roadmaps, and the disconnect between market recovery and token performance. Odilitime acknowledged these communication failures and announced several initiatives to address them:

- Built **elizaOS.news** with automated video briefing workflows for daily updates
- Plans to strengthen investor relations communications
- Commitment to restore the $elizaos holders system

The team emphasized that long-term plans won't change based on price action, though implementation timelines for previously discussed airdrops and buybacks remain unclear.

### Active Project Initiatives

Three main projects were confirmed as actively progressing:

- **Elizacloud**: Positioned as the project's flywheel, with Milady pushing cloud adoption
- **Babylon**: Currently rolling out with players and agents actively testing
- **Jeju**: Confirmed as an active project

### Token Migration Process

Discussion continued about allowing additional ai16z to elizaos token migrations. While the process isn't finalized, users need to DM their wallet address and proof of holding tokens during the September snapshot to participate.

### Framework Development (v2.0.0)

The **xfn-framework** channel focused on significant architectural improvements for the v2.0.0 branch:

**Prompt Batching System**: After reviewing 50-60 plugins, Odilitime consolidated improvement ideas into a new subsystem called prompt batching. This combines three types of LLM queries (init LLM queries, autonomous LLM calls, and evaluator calls) into one configurable scheduler that can be optimized for either frontier or local models. The system builds on existing dynamicPromptExecution work, with core functionality already present in the 3.x version's autonomous system.

**Serverless Architecture Concepts**: Development work revealed opportunities for:
- Lazy loading services to defer initialization
- Outsourcing service work to external systems
- In-memory persistence to avoid rebuilding state

Cursor (AI coding assistant) was providing serverless and cloud implementation suggestions, influenced by Shaw's configuration work through cursor rules or documentation.

### Technical Development Updates

**ElizaOS Progress**: Odilitime confirmed work on the next version of elizaOS, noting the develop branch is currently broken. Completing this version will unblock planned tasks including improved Twitter posts for $degenai and $elizaos tokens.

**Milady Integration**: In **💬-coders**, BinaryCookies worked on integrating a Neon database with Milady, discovering the configuration location in the env section of the JSON file. They encountered unresolved issues with system permissions and capabilities.

**Pull Request Activity**: Meme Broker submitted pull requests addressing GitHub issue #71 in the milady-ai/milady repository.

### New Protocol Announcement

TraderTomson announced the **Autonomous Economy Protocol (AEP)** in **💬-coders** - a comprehensive Eliza plugin for on-chain agent payments and reputation management:

**Core Features**:
- Operates on Base blockchain with AGT tokens as payment mechanism
- Five TypeScript actions: REGISTER_AGENT, BROWSE_MARKET, PROPOSE_DEAL, CHECK_REPUTATION, GET_SEASON1_INFO
- Permanent reputation system (0-10,000 score) stored on Basescan
- 1% passive referral income in perpetuity
- Credit access based on reputation without collateral requirements

**Implementation**: Available via npm as `autonomous-economy-sdk` with integration code in `integrations/eliza-plugin/`

**Season 1 Genesis Program**: 50 million AGT tokens allocated for early adopters through May 2026 with points-based claim system

## Key Questions & Answers

**Q: Can ai16z tokens still be converted to elizaos?** (antoszy)  
A: Yes, team is allowing more migrations but process not finalized yet. Need to DM wallet address and proof of holding tokens during September snapshot. (Odilitime)

**Q: How are you going to deliver on what you decided to work on if people are leaving?** (Kitten)  
A: Team is still building. Elizacloud is the flywheel and Milady is pushing cloud adoption. (Odilitime)

**Q: Are Babylon, Jeju, etc. active yet?** (paolin)  
A: Yes, still rolling out Babylon with players and agents playing it now. (Odilitime)

**Q: Where can I add my neon database to the milady?** (BinaryCookies)  
A: It's located under the env in the json file (BinaryCookies)

**Q: What is prompt batching?** (Stan ⚡)  
A: A new subsystem that combines init LLM queries, autonomous LLM calls and evaluator calls into one configurable scheduler optimized for frontier or local models, building on dynamicPromptExecution (Odilitime)

**Q: What is AEP?** (TraderTomson)  
A: Autonomous Economy Protocol — a marketplace on Base where agents can earn AGT tokens, build reputation, find other agents, access credit, and earn referral income (TraderTomson)

**Q: What actions does the Eliza plugin provide?** (TraderTomson)  
A: Five actions: REGISTER_AGENT, BROWSE_MARKET, PROPOSE_DEAL, CHECK_REPUTATION, and GET_SEASON1_INFO (TraderTomson)

**Q: How does the reputation system work?** (TraderTomson)  
A: Permanent reputation score from 0-10,000 stored on Basescan (TraderTomson)

## Community Help & Collaboration

**BinaryCookies** (self-help): Successfully discovered the location for Neon database configuration in Milady's env section of the JSON file after investigating the integration process.

**Odilitime** helped **antoszy**: Provided guidance on the ai16z to elizaos token migration process, confirming migrations are still possible and outlining the required information (wallet address and September snapshot proof).

**jin** helped the **Community**: Created video briefing workflow for daily updates at elizaos.news to address the need for regular project updates.

## Action Items

### Technical

- Complete next version of elizaOS to unblock develop branch and planned tasks (Odilitime)
- Implement better Twitter posts for $degenai and $elizaos tokens (Odilitime)
- Finalize ai16z to elizaos token migration process (Odilitime)
- Restore $elizaos holders system functionality (Odilitime)
- Resolve system permissions and capabilities configuration issue in Milady (BinaryCookies)
- Review and merge pull requests for GitHub issue #71 in milady-ai/milady repository (Meme Broker)
- Implement prompt batching subsystem combining init LLM queries, autonomous LLM calls and evaluator calls into configurable scheduler (Odilitime)
- Complete database cleanup work discovered during feature development (Odilitime)
- Implement lazy loading services for deferred initialization (Odilitime)
- Implement in-memory persistence to avoid rebuilding state (Odilitime)
- Evaluate outsourcing service work for serverless architecture (Odilitime)
- Integrate lazy loading service into monorepo (Stan ⚡)

### Documentation

- Improve communication about Elizacloud progress and capabilities (otse finam)
- Provide clear roadmap and regular updates (Biazs)
- Strengthen investor relations communications (Odilitime)
- Feature Eliza agents using AEP on the protocol leaderboard (TraderTomson)

### Feature

- Build automated tools for more consistent project updates (Odilitime)
- Integrate AEP plugin into Eliza agents for on-chain payments and reputation (TraderTomson)