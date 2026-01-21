# elizaOS Discord - 2026-01-20

## Overall Discussion Highlights

### Token Economics & Migration Concerns

The most significant discussion across channels centered on the ai16z to elizaOS token migration and the lack of clear tokenomics. In **💬-discussion**, community members expressed frustration that the token feels disconnected from the project's roadmap. DorianD explained the migration rationale: the daos.fun contract was closed source, not auditable, and wouldn't be accepted by major exchanges like Coinbase. The migration also created ecosystem funds and liquidity tokens.

However, this technical necessity hasn't translated into clear value propositions for investors. The **🥇-partners** channel saw heated exchanges about a 70% token price decline, with partners arguing that the team's "build, don't talk about the token" approach is being interpreted as disinterest in token development, creating zero demand.

### Token Utility & Use Cases

Two primary use cases emerged from discussions:

**Jeju Network Integration**: DorianD identified this as the primary technical use case, where Shaw is making commits and has demonstrated ElizaOS working in Rust. The Jeju documentation mentions 60+ onchain "actions" requiring gas fees paid in elizaOS tokens. However, the timeline (latter half of 2025 for initial launch, ongoing through 2027) feels distant to investors.

**ElizaCloud Buybacks**: Alexei mentioned Shaw discussed utility including profits from ElizaCloud and other sources doing token buybacks, similar to Binance's BNB model. This would be a significant turning point when confirmed.

### Project Roadmap & Communication Strategy

In **🥇-partners**, Odilitime clarified the project progression path: **Framework → Cloud → Jeju**, with framework in 2024/2025, cloud in 2025/2026, and Jeju initial launch likely in 2026 with ongoing development through 2027. The team acknowledged the roadmap has "trust me bro" elements they can't yet disclose, and that execution/communication need improvement.

DorianD proposed concrete solutions:
- Establish **research.elizaos.ai** blog for thought leadership content showcasing experiments and technical work
- Position core devs as industry thought leaders beyond just developers
- Create regular technical updates that non-devs can understand
- Bottle up Shaw's interviews into articles so people don't need to watch streams to understand the vision

Dr. Neuro volunteered to create visual explanations of the framework-to-Jeju progression.

### Technical Development & Infrastructure

**Agent Behavior Improvements**: In **💬-coders**, Jin identified two key areas for agent improvement: reducing anxiety/chattiness and minimizing hallucinations. DorianD proposed providing the LLM with the last 20 chat messages to help determine if messages are directed at the agent, allowing better decision-making about when inference costs are justified.

**Deployment Infrastructure**: Odilitime discussed a "swarm" deployment - a large elizaOS instance running multiple bots on a single server for Babylon's Discord, offering cost savings when agents share the same environment. Plans exist to eventually integrate swarm technology into the Eliza Cloud platform.

**Documentation Gaps**: In **core-devs**, Odilitime identified missing CLI documentation, specifically upgrade instructions. Stan confirmed the production documentation is synced with the main branch but acknowledged the gap.

**NPM Repository Management**: Shaw provided a solution for creating multiple NPM repositories programmatically, noting that Claude has MCP capabilities and that NPM's publish command automatically creates repositories.

### Platform Development

M I A M I demonstrated "agentic onboarding" in **💬-discussion** - migrating a Twitter profile to "space" (sentient space platform) with a single prompt, showcasing the platform's capabilities.

## Key Questions & Answers

**Q: Why was ai16z migrated to elizaOS?**  
A: The daos.fun contract was closed source, not auditable, and wouldn't be accepted by exchanges like Coinbase; migration also created ecosystem funds and liquidity tokens (DorianD)

**Q: Are there any actual use cases for this token besides paying gas fees in Jeju?**  
A: Jeju network for agent execution with 60+ onchain actions requiring gas fees, ElizaCloud buybacks mentioned (DorianD, Alexei)

**Q: What is the project progression path?**  
A: Framework → Cloud → Jeju, with framework in 2024/2025, cloud in 2025/2026, and Jeju initial launch likely in 2026 with ongoing development through 2027 (Odilitime)

**Q: Why should anyone buy/hold ElizaOS token right now?**  
A: The real value isn't clear because investors need to watch Shaw's streams to understand the vision; what exists isn't "dressed up enough" (Odilitime)

**Q: Is the swarm a way to Ralph wiggum QA testing?**  
A: No, it's a big elizaOS instance on a server running all bots for Babylon's discord (Odilitime)

**Q: Where is the page that lists everything the CLI can do?**  
A: https://docs.elizaos.ai/cli-reference/overview (Stan ⚡)

**Q: Anyone know of an MCP or programmatic utility to make NPM repos?**  
A: Claude has MCP support, and npm publish creates repos automatically (shaw)

**Q: What does "to space" mean in this context?**  
A: Sentient space is the platform, short form is space, users are called spacers (M I A M I)

## Community Help & Collaboration

**DorianD → Community (Token Migration & Utility)**  
Provided comprehensive explanations about the migration rationale, Jeju network integration, and the 60+ onchain actions requiring gas fees. Also proposed the research.elizaos.ai blog solution for better communication.

**Odilitime → Community (Roadmap Clarity)**  
Clarified the Framework → Cloud → Jeju progression path with timeline estimates and acknowledged communication gaps. Engaged constructively with partner concerns.

**DorianD → Team (Communication Strategy)**  
Explained how open source networks like BTC, ETH, Ripple built moats through first-mover advantage despite being open source, helping the team understand crypto network utility.

**Alexei → gby (Token Utility)**  
Mentioned Shaw's discussion of ElizaCloud profits doing buybacks, providing some clarity on future utility mechanisms.

**Stan ⚡ → Odilitime (Documentation)**  
Provided link to CLI reference page and confirmed upgrade info was missing, helping identify documentation gaps.

**shaw → Odilitime (NPM Automation)**  
Explained that npm publish automatically creates repos and Claude MCP can assist, solving the challenge of creating 50-70 repositories.

**Odilitime → jin (Deployment Options)**  
Offered to add jin's agent to the swarm for cost savings, though jin decided to try Eliza Cloud instead.

**Dr. Neuro → Team (Visual Communication)**  
Volunteered to create visual art explaining the framework-to-Jeju progression during travel.

## Action Items

### Documentation

- **Create comprehensive whitepaper for Jeju network** to attract serious investors and clarify vision (DorianD)
- **Improve communications and messaging** around token utility and roadmap integration (DorianD)
- **Clarify and publish official tokenomics** for elizaOS (gby)
- **Rewrite and improve the public roadmap document** to be clearer and better laid out with stronger vision/importance messaging (Odilitime)
- **Bottle up Shaw's interviews into articles and threads** so people don't need to watch streams to understand the vision (Odilitime)
- **Create visual explanations** of the Framework → Cloud → Jeju progression path with timeline (Odilitime, Dr. Neuro)
- **Provide regular small updates** that team is aware things aren't trending right and is working on solutions (Broccolex)
- **Create content explaining current usable features** on cloud that users can see and touch (Odilitime)
- **Develop narrative around framework** as precursor to Jeju with story people can visualize about decentralized AI robots (DorianD)
- **Add CLI upgrade instructions** to documentation (Odilitime)
- **Deploy main branch documentation updates** to production (Odilitime)
- **Address partner concerns** about token allocation and migration structure (Broccolex)

### Feature

- **Create research.elizaos.ai blog** with posts about experiments, technical work, Jeju vision, and token economics to establish thought leadership (DorianD)
- **Implement ElizaCloud buyback mechanism** to support token price (Alexei)
- **Add cost calculator to elizaOS** for estimating running costs based on agent configuration and plugins (ElBru)
- **Integrate swarm technology** into Eliza Cloud platform (Odilitime)
- **Make cloud infrastructure more accessible** and easier for non-devs to interact with and understand (Odilitime)
- **Implement prompting system** that provides LLM with last 20 chat messages for context to determine if messages are directed at agent and if inference cost is justified (DorianD)
- **Create holistic vision** connecting AI agents as open source public resources with token utility (DorianD)

### Technical

- **Complete Jeju network development** with 60+ onchain actions for agent execution (DorianD)
- **Continue Shaw's commits** to Jeju network and ElizaOS Rust implementation (DorianD)
- **Reduce agent anxiety/chattiness and hallucinations** (jin)
- **Investigate if entity tracking** from general chat already exists in codebase (DorianD)
- **Create 50-70 NPM repositories** using automated tooling (Odilitime)
- **Improve messaging and communication** around token utility and why people should buy/hold ElizaOS (Broccolex, DannyNOR NoFapArc)
- **Follow up research blog posts** with X spaces, demos, and screenshares on topics (DorianD)