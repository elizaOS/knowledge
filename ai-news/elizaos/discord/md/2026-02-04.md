# elizaOS Discord - 2026-02-04

## Overall Discussion Highlights

### Team Structure and Strategic Direction

The ElizaOS team underwent organizational changes that sparked community discussion. Only CJ officially departed and was replaced with a new hire, while Sayo's departure remained unconfirmed. Leadership emphasized that CJ's departure "focused the dev team" and Shaw balanced headcount. The team validated their theories through openclaw/clawdbot/moltbot developments and is now concentrating on "better products."

**Borko issued a critical directive** demanding focus on revenue-generating products, expressing frustration about losing competitive ground while building products that don't matter. He challenged the team to show concrete results from Spartan development, signaling a strategic pivot toward monetization.

### Framework Comparison: ElizaOS vs Openclaw

A detailed technical comparison emerged between ElizaOS and Openclaw frameworks:

**Openclaw Strengths:**
- Excellent UX and smooth CLI deployment on VPS
- Superior self-modifying loops
- Effective for personal assistant use cases
- Demonstrated with local RAG MCP integration using book content

**Openclaw Limitations:**
- Constantly burns tokens
- Cannot build complex projects
- Limited to personal assistant scope

**ElizaOS Positioning:**
- Business-focused framework
- Better through extensive battle testing
- Autonomous mode now integrated by default: `const agentRuntime = new AgentRuntime({ autonomous: true })`
- Core issue identified: poor packaging and presentation despite superior features
- Framework refresh needed, with Shaw's 2.0 including native agentskills

Both frameworks are trending toward autonomy, with ElizaOS working to absorb Openclaw capabilities through cskill plugin development.

### Agent Skills and Standards

Technical clarification confirmed that **Moltbot skills follow the same standard as Claude skills** via agentskills.io, representing an open standard. Moltbot is essentially Claude code with Telegram integration and autonomous mode capabilities.

**Dynamic providers and skill.md are functionally identical**, with providers being well-typed. The team is working on cskill plugin integration to absorb Openclaw capabilities.

### AI Media Infrastructure and Automated News System

Jin presented a comprehensive automated news system representing a major product direction:

**System Architecture:**
- Aggregates Discord discussions and community feedback
- Generates AI news shows with characters voicing top issues
- Pipelines listen for user feedback and aggregate weekly data
- Described as "agentic DAO infrastructure with a media layer"
- Built to solve information overload from code/issues/PRs/DMs

**Planned Expansions:**
- Talk shows and panel discussions
- Live streams
- Game shows (Clank Tank)
- Debate shows
- Character-based shows with skills for Eliza dev and troubleshooting
- 24/7 streaming infrastructure with continuous integration

**Monetization Strategy:**
- SaaS with x402
- Hackathon partnerships (ESPN-style coverage)
- AI hedge fund/VC concepts via Clank Tank
- Dashboard alternative for information management

**Future Integration:**
- Voice agents for human + AI cohosted podcasts
- Specific channels where AI show characters chat after episodes for realtime feedback
- Agent loaded with Ethereum and Solana dev skills for reviewing data, prototyping, and iterating on business development

### OAuth Integration Progress

Sam reported significant progress integrating OAuth functionality into Eliza app chat:

**Completed Integrations:**
- X.com
- Github
- Slack
- Linear

**Next on Roadmap:**
- Notion
- MCP testing (after completing OAuth work on major clients and adapters)

The architecture made adding integrations easy, though obtaining credentials and setting up redirect URIs was time-consuming.

### Babylon.market Internal Launch

S announced Babylon.market's internal launch with mandatory team participation:
- All team members required to sign up
- Share IDs for whitelisting
- Test for 2-3 hours with detailed feedback notes and screenshots

**Initial Testing Issues:**
- Multiple team members stuck during initial testing
- Farcaster login failures
- Infinite loading spinners when switching networks
- Waitlist position loading problems

Community discussion also covered the Babylon top 100 list, with airdrop confirmed for ElizaOS holders.

### Token Migration and Bridging

Key clarifications on token migration logistics:
- Migration deadline was a hard 3-month window from opening
- One user (avirtualfuture) successfully completed migration after missing initial notifications
- **Bridging from Solana is optional** - tokens can remain on Solana without mandatory bridging to other chains
- Users who bought after snapshot should hold ai16z and swap at leisure as migration won't be automatic

### Documentation Optimization for LLMs

Jin shared comprehensive resources for optimizing documentation for LLMs:
- Writing best practices guides
- Skill creation resources
- llms.txt file implementation
- kapa.ai best practices

## Key Questions & Answers

**Q: Are moltbot skills exactly the same as claude skills?**  
A: Yes, it's an open standard at agentskills.io (answered by jin)

**Q: What is moltbot technically?**  
A: Claude code with telegram and autonomous mode (answered by s)

**Q: What is the most important ingredient to Moltbook's success?**  
A: Heartbeats and scheduled tasks that use emotionally manipulative prompts to encourage LLM participation and allow server-side behavior updates (answered by jin)

**Q: How is autonomous mode integrated in new Eliza?**  
A: It's integrated by default using `const agentRuntime = new AgentRuntime({ autonomous: true })`, previously it was a plugin (answered by s)

**Q: What is the fundamental problem with agent features?**  
A: Nobody uses any of it despite having the features available (answered by s)

**Q: What's the diff between dynamic provider and "skill.md"?**  
A: It's the same, providers are well typed (answered by Stan ⚡)

**Q: Is the bridging necessary or can I leave it on sol as it is?**  
A: You can leave it on sol (answered by Odilitime)

**Q: Why the recent turnover on the engineering team?**  
A: Only CJ left, was replaced with new hire; CJ's departure focused the dev team and Shaw evened out headcount (answered by Odilitime)

**Q: Is there an airdrop to holders?**  
A: There is an airdrop to elizaOS holders (answered by MDMnvest)

**Q: How can we help grow revenue around the AI news show?**  
A: SaaS with x402, hackathon partnerships (ESPN style), AI hedge fund/VC concept via clank tank (answered by jin)

**Q: I bought after snapshot, what will I do?**  
A: Hold ai16z and swap at your leisure; won't be migrated automatically (answered by Odilitime)

**Q: Is there any chance to get back ai16z poolparty (staked) coin?**  
A: Should be able to unstake on daos.fun, may give error but works on chain (answered by Odilitime)

**Q: Did you test to use some of MCP now we have OAuth?**  
A: Not yet, continuing to build OAuth on major clients and adapters first, then will try MCP (answered by sam)

## Community Help & Collaboration

**Token Migration Assistance**  
Helper: Odilitime | Helpee: avirtualfuture  
User missed token migration deadline and needed to complete migration. Odilitime offered assistance and confirmed migration was still possible, then clarified that bridging is optional and tokens can remain on Solana.

**Unstaking Support**  
Helper: Odilitime | Helpee: Loliño19  
User unable to unstake ai16z poolparty tokens. Directed to daos.fun for unstaking, suggested contacting Baoskee's community for specific instructions, and confirmed that despite error messages, unstaking should work on chain.

**Post-Snapshot Purchase Guidance**  
Helper: Odilitime | Helpee: atbanklan  
User bought ai16z after snapshot and was unsure what to do. Advised to hold ai16z and swap at leisure as migration won't be automatic.

**Technical Clarifications**  
Helper: jin | Helpee: Odilitime  
Confirmed moltbot skills compatibility, explaining they follow the same open standard as Claude skills via agentskills.io.

Helper: s | Helpee: Community  
Explained autonomous mode implementation, clarifying it's now integrated by default in new Eliza with code example.

Helper: Stan ⚡ | Helpee: 0xbbjoker  
Explained difference between dynamic provider and skill.md, clarifying they're the same with providers being well-typed.

**UI/UX Assistance**  
Helper: sayonara | Helpee: sam  
Suggested trying rube.app for link rendering as buttons.

Helper: Stan ⚡ | Helpee: sam  
Clarified that Rube is composio when discussing rube.app technology.

**Community Moderation**  
Helper: Kenk | Helpee: atbanklan  
Redirected user to keep questions in public channel rather than DMs.

## Action Items

### Technical

- Continue building OAuth integrations for Notion and other platforms as per priority (sam)
- Test and integrate MCP after completing OAuth work on major clients and adapters (sam)
- Framework refresh needed for ElizaOS, Shaw attempting with 2.0 (Odilitime)
- Complete cskill plugin work to absorb Openclaw capabilities (Stan ⚡)
- Sign up for Babylon.market, share ID for whitelisting, test for 2-3 hours with notes and screenshots (s)
- Fix Babylon.market loading issues - infinite spinner when loading waitlist position (ziflie)
- Fix Babylon.market Farcaster login failure (0xbbjoker)
- Migrate Clank Tank to new hosting (jin)
- Ship 24/7 streaming infrastructure with continuous integration for new shows/segments (jin)
- Expand AI media infrastructure to include talk shows, panels, live streams, game shows (clank tank), and debate shows (jin)
- Get feedback on tone of news show cron job (jin)
- Develop agent loaded with Ethereum and Solana dev skills for reviewing data, prototyping, and iterating on biz dev (jin)

### Feature

- Focus on building revenue-generating products and catch up to competitors (Borko)
- Complete basic simple things that make elizaOS fun to use or be around (Odilitime)
- Improve developer experience for Eliza agents (jin)
- Build agents for characters in shows with skills for Eliza dev and troubleshooting (jin)
- Create specific channel where AI show characters chat after each episode for realtime feedback (jin)
- Ship dashboard alternative for information management (jin)
- Integrate voice agents for human + AI cohosted podcasts (jin)
- Turn AI news system into SaaS with x402 (jin)

### Documentation

- Improve notification system or communication strategy to prevent users from missing critical deadlines like token migration (avirtualfuture)
- Package and present Eliza framework better for adoption (s)
- Create llms.txt files for documentation optimization (jin)
- Clarify unstaking process for ai16z poolparty tokens on daos.fun (Loliño19)