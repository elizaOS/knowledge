# elizaOS Discord - 2026-01-17

## Overall Discussion Highlights

### Token Economics & Holder Rewards

The community explored innovative mechanisms for token holder rewards. Kev initiated discussion about earning opportunities for holders, with Ceazer Nexnalon confirming that active staking programs enable rewards. Taco proposed an ambitious concept: integrating holder rewards when new agents are created by users. While Ceazer validated this as technically feasible with proper eligibility criteria and abuse prevention safeguards, DorianD challenged the fundamental incentive structure, questioning why agent creators would reward holders without clear motivation.

Migration concerns emerged when El_Lince asked about consequences for unmigrated tokens—whether they would be lost, redistributed, or burned—but this question remained unanswered.

### AI & Prediction Markets Debate

A significant philosophical and technical debate unfolded around prediction markets' future. Digitalalchemy expressed strong conviction that AI-integrated prediction markets represent a game-changing opportunity. DorianD countered with practical experience from running forecast markets on ICOs in 2017, characterizing them as a "super larp" that merely surfaces information earlier rather than providing magical predictive capabilities. He suggested prediction markets will regain relevance around the 2028 election cycle but currently serve mainly sports gambling and current events enthusiasts.

### Infrastructure & Network Architecture

**ElizaOS Platform Expansion:**
- Shaw successfully implemented Eliza to run on ICP (Internet Computer Protocol)
- DorianD outlined infrastructure needs for autonomous agents requiring provably provisioned secure containers, agent registration, and protocols 8004 and 402
- Potential gaming/gambling applications for autonomous agents identified
- Questions raised about Jeju network capabilities for provisioning vanilla agents on ICP or enclaves with network-based inference and RAG support
- Oracle functionality proposed where agents could query real-time information and post results to the network

**Branding Updates:**
- ai16z rebranding to elizaos on main X account
- CoinGecko link added to linktree

### Technical Integration Challenges

**Polymarket Integration Architecture:**

ElizaBAO encountered critical wallet architecture issues with Polymarket integration. The Builder address (0x5966...4c9e) containing $137.92 USDC didn't match the address derived from the exported private key (0xb05c...4002) with $0 balance. Sayonara clarified that Polymarket uses a Safe multisig (1/1) controlled by a signer address, requiring all interactions through the proxy wallet. The plugin-polymarket should handle this flow automatically.

**Cloudflare Blocking & Serverless Limitations:**

ElizaBAO faced Cloudflare 403 errors when calling Polymarket's CLOB API from Supabase Edge Functions. Attempts to use Oxylabs Web Unblocker resulted in certificate errors (UnknownIssuer) and runtime restrictions preventing HTTP_PROXY configuration and custom CA certificates. Lucky_beagle_52756 suggested static IPs and browser behavior mimicking. Chucknorris recommended abandoning the Supabase serverless approach entirely, advocating for self-hosted SQL databases and private nodes like Pixel Labs.

**High-Performance Trading System:**

Chucknorris discussed building a Spartan-based trading system processing 1 million known tokens. This requires a complete Rust plugin rewrite to handle decode/worker/build/send/confirm/smart exit algorithms across multiple DEXs. TypeScript proved inadequate for real-time multi-DEX handling due to systematic crashes. The solution involves NATS Jetstream for message propagation, as Redis streams are too slow for this use case.

### Developer Tools & Productivity

A user reported remarkable productivity gains using AI in Eliza docs, claiming six hours of work with the tool exceeded two months of progress without it—a strong testimonial for the documentation AI tool's effectiveness.

## Key Questions & Answers

**Q: Can I earn more coins if I'm a holder?**  
A: Yes, if there are active rewards or staking programs available (Ceazer Nexnalon)

**Q: Would it be possible to integrate rewards for holders when new agents are created by users?**  
A: Yes, it's feasible but would require clear eligibility criteria and safeguards to prevent abuse (Ceazer Nexnalon)

**Q: Why does the exported private key not correspond to my Builder address?**  
A: Polymarket funds are deposited into a Safe multisig (1/1) controlled by signer address, not directly to the EOA (sayonara)

**Q: Does plugin-polymarket support the proxy wallet flow?**  
A: There is no way to interact with Polymarket other than proxy wallet in most cases; check how the plugin handles it using cursor (sayonara)

**Q: How does okay-bet/plugin-polymarket handle Cloudflare 403 blocks when calling the CLOB API from a serverless function?**  
A: Ensure geographic compliance, use static/dedicated egress IPs, mimic browser behavior, contact Polymarket support (lucky_beagle_52756)

### Unanswered Questions

- What's the difference between building an ElizaOS project + plugin-agentkit vs building a CDP AgentKit project with Eliza integration? (CT)
- Why would someone creating an agent reward holders? (DorianD)
- What happens if someone doesn't migrate to eliza? Are the coins lost or redistributed/burned? (El_Lince)
- Is the elizaos team working with the youtoy team? (elizafan222)
- Will Jeju allow paying an $elizaos fee to provision a vanilla agent on ICP or enclaves with network-based inference and RAG? (DorianD)

## Community Help & Collaboration

**Ceazer Nexnalon** assisted **Kev** in understanding earning mechanisms for token holders, explaining that earnings are possible through active rewards or staking programs.

**Ceazer Nexnalon** helped **Taco** evaluate the feasibility of holder rewards tied to agent creation, confirming it's technically feasible with proper eligibility criteria and abuse prevention safeguards.

**sayonara** provided critical assistance to **ElizaBAO** on multiple fronts:
- Explained Polymarket's Safe multisig proxy wallet architecture and why wallet addresses didn't match
- Clarified that proxy wallet is the only interaction method with Polymarket
- Provided documentation links and suggested using cursor to check plugin implementation

**lucky_beagle_52756** helped **ElizaBAO** troubleshoot Cloudflare 403 blocking issues, suggesting static IPs, browser behavior mimicking, and contacting Polymarket support.

**Chucknorris | ONYX P9 NODE RENT** advised **ElizaBAO** on architectural decisions, recommending abandoning the Supabase serverless approach in favor of self-hosted SQL databases and private nodes like Pixel Labs to resolve certificate errors and runtime restrictions.

**DorianD** redirected **Est** from an off-topic Instagram page selling request to use Google or Claude for finding appropriate platforms.

## Action Items

### Technical

- **Investigate plugin-polymarket proxy wallet implementation** to understand how it handles Polymarket Safe multisig authentication (ElizaBAO)
- **Resolve Cloudflare 403 blocking** for Polymarket CLOB API calls from serverless environment (ElizaBAO)
- **Implement alternative to Supabase Edge Functions** using self-hosted SQL database and private node infrastructure (Chucknorris | ONYX P9 NODE RENT)
- **Create new Rust plugin** to replicate decode/worker/build/send/confirm/smart exit algorithm functions across all DEX systems for Spartan (Chucknorris | ONYX P9 NODE RENT)
- **Implement NATS Jetstream** for message propagation in Eliza to replace Redis streams for high-performance trading (Chucknorris | ONYX P9 NODE RENT)
- **Launch network infrastructure** supporting autonomous agents with provably provisioned secure containers, registration, and protocols 8004 and 402 (DorianD)

### Feature

- **Implement holder rewards system** tied to new agent creation with eligibility criteria and abuse prevention (Taco)
- **Develop AI-integrated prediction markets platform** (digitalalchemy)
- **Implement Jeju network capability** to provision vanilla agents on ICP/enclaves with network-based inference and RAG support (DorianD)
- **Enable agents to function as oracles**, posting query results (e.g., sports scores) to the network (DorianD)

### Documentation

- **Clarify token migration process** and consequences for non-migrated coins (El_Lince)
- **Document Polymarket proxy wallet architecture** and how to properly use exported private keys with plugin-polymarket (ElizaBAO)