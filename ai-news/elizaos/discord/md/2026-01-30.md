# elizaOS Discord - 2026-01-30

## Overall Discussion Highlights

### Business Sustainability & Operations
The team's financial runway became a topic of concern in the partners channel, with Shaw confirming 8 months of operating costs remaining. Questions were raised about whether these funds are held in stablecoins versus volatile crypto assets, though this remained unresolved. The discussion highlighted ongoing concerns about project sustainability during market volatility.

### Migration Issues & Security Concerns
A significant portion of community discussion centered on the ai16z to elizaos token migration. Multiple users reported problems with the migration portal at migrate.elizafoundation.ai, with wallets showing "0 eligible" despite holding tokens since late 2024. Odilitime confirmed the tool should work automatically and suggested checking if tokens were in LP, different wallets, or purchased after the snapshot date.

**Critical Security Incident**: A user (coolart) reported being hacked after generating a support ticket, with funds stolen from Phantom and Metamask wallets. This prompted repeated warnings from moderators that official support never initiates DMs - all such contact attempts are scammers. Another user (FeRhaT_@) reported receiving friend requests from supposed "ticket support team" members, reinforcing the active scam threat.

### Quality Assurance & Testing Framework
Core developers identified critical quality assurance issues in the monorepo versioning system. Odilitime expressed frustration about recurring breakages in version 1x compared to 2x, highlighting the need for better integration testing. Stan ⚡ is actively developing a test framework for the plugin-n8n project, sharing examples from the plugin-n8n-workflow repository as a potential solution pattern. A critical bug was also reported in the develop branch where provider selection fails in one-shot mode.

### ElizaOS vs Clawdbot Comparison
Technical discussions compared ElizaOS to Clawdbot, revealing key architectural differences:
- **Eliza**: Multi-agent system architecture
- **Clawdbot**: Personal assistant with social media, calendar access, and voice interface

DorianD identified Eliza's lack of mobile footprint and voice interface as significant gaps that should be addressed. The conversation revealed that Clawdbot users face API fee issues and Anthropic bans for TOS violations when using subscription plans with non-human users.

### Jeju Network & Staking Mechanisms
DorianD explained Jeju's staking mechanism for service providers, including compute and data storage nodes. The system currently uses ETH as a placeholder in the repository. The staking requirement applies to various node services, with documentation available in the Jeju repo's *.md files.

### Strategic Integration: Moltbook & Agent Networks
DorianD introduced Moltbook (described as "Reddit for agents") and proposed a strategic integration plan. The concept involves migrating Moltbot users (running on Mac Minis) to the Jeju network when they encounter high API costs. The technical architecture would involve running Moltbot, Eliza, and Claude together, then networking Moltbot into Jeju for storage nodes, cron jobs, and other services. Security concerns were raised about exposed IPs and unencrypted communications on non-secure hardware enclaves.

### Token Utility & Value Proposition
Community members raised concerns about token utility and investor value. averma suggested implementing transaction mechanisms similar to Virtuals' bonding curve within ElizaOS. Odilitime responded that using elizaos as the main token wasn't technically feasible due to excessive work required, preferring the airdrop approach. The team acknowledged communication challenges, with Odilitime stating "we're doing big brain stuff and people just don't get it" and recognizing the need to simplify explanations once users can interact with the product.

### Privacy & Decentralization Concerns
Questions emerged about ElizaOS's independence, citing the privacy policy and USA-based operations. DorianD defended the project as "an open systems network for everything agents need to run." The discussion highlighted ongoing tension between centralized infrastructure and decentralized ideals in the crypto/AI space.

### Plugin Development Updates
Odilitime is actively updating the plugin-local-ai for easy embeddings integration on a development branch. He shared experiences using Claude Sonnet 4.5 versus Opus, noting Sonnet is adequate for smaller tasks but Opus is preferred for larger projects.

## Key Questions & Answers

**Q: How much longer can the team operate costs?**  
A: 8 months of runway according to Shaw (answered by Broccolex)

**Q: What is the difference between Eliza and Clawdbot?**  
A: Eliza is more of a multi-agent system while Clawdbot is more like a personal assistant with access to socials and calendar (answered by DorianD)

**Q: Where should I go if the migration tool doesn't work?**  
A: Use the official migration site at https://migrate.elizafoundation.ai and the ticket channel if issues persist (answered by Odilitime)

**Q: Why does my wallet show 0 eligible tokens for migration?**  
A: Check if tokens were in an LP, different wallet, or purchased after snapshot date (answered by Odilitime)

**Q: Could elizaos token have been used as the main token instead?**  
A: Not technically feasible - the work required is too much, better to airdrop to holders (answered by Odilitime)

**Q: How does staking work in Jeju?**  
A: Service providers (compute, data storage nodes) need to stake to run services, currently using ETH as placeholder in repo (answered by DorianD)

**Q: What happens if I don't migrate my tokens?**  
A: Tokens remain on old contract but lose support, utility, and liquidity, eventually becoming worthless (answered by Zhuangzi)

**Q: Is it normal for ticket support to send friend requests?**  
A: No, official support never DMs - those are scammers (answered by Odilitime)

**Q: Is openclaw.ai a fork or did they rename again?**  
A: They renamed it (answered by sam)

**Q: Can you use subscription plans with Moltbot?**  
A: No, people are getting banned by Anthropic for non-human user TOS violations (answered by DorianD)

**Q: What are the top 3-5 projects built with ElizaOS?**  
A: Reference provided via Twitter link, user to decide favorites (answered by Kenk)

## Community Help & Collaboration

**Migration Support**
- Odilitime helped Arkanac troubleshoot migration tool showing 0 eligible tokens, providing suggestions about LP, wallet location, and snapshot date
- Maff || Hourglass ⌛ confirmed the migration portal was working, having used it the same day
- Omid Sa directed coolart to verify in verification channel first before attempting migration

**Security Guidance**
- Zhuangzi helped FeRhaT_@ understand token migration consequences and confirmed to use verified ticket system only, warning about scam friend requests

**Technical Architecture**
- DorianD helped kira understand the difference between Eliza and Clawdbot capabilities, explaining architectural differences and identifying Eliza's gaps in mobile footprint and voice interface
- DorianD helped gby understand Jeju staking mechanisms and directed to Jeju repo *.md files for documentation

**Testing Framework**
- Stan ⚡ shared working test framework implementation from plugin-n8n-workflow project to help the community with better plugin testing

**Project Discovery**
- Kenk helped Wes find top ElizaOS projects by providing Twitter reference link with project examples

**General Support**
- MDMnvest directed Eric Spangler to FAQ channel and ticket system for withdrawal issues
- sam helped Odilitime clarify that openclaw.ai was a rename rather than a fork

## Action Items

### Technical
- **Implement better integration tests for 2x version of monorepo to prevent breakages** (Mentioned by: Odilitime)
- **Fix provider selection bug in develop branch for one-shot mode** (Mentioned by: Odilitime)
- **Implement test framework for plugins similar to plugin-n8n-workflow approach** (Mentioned by: Stan ⚡)
- **Update plugin-local-ai for easy embeddings integration on odi-dev branch** (Mentioned by: Odilitime)
- **Investigate migration portal 429 "Too many requests" errors occurring on page load** (Mentioned by: jaistklaas)
- **Debug migration tool showing "0 eligible" for wallets holding tokens since late 2024** (Mentioned by: Arkanac, TonKLa)
- **Develop integration between Moltbot and Jeju network for storage nodes and cron jobs** (Mentioned by: DorianD)
- **Create system to run Moltbot, Eliza, and Claude together in networked configuration** (Mentioned by: DorianD)
- **Complete Jeju development to allow users to interact with the product** (Mentioned by: Odilitime)
- **Clarify whether 8-month runway is held in stablecoins or volatile crypto assets** (Mentioned by: DannyNOR NoFapArc)

### Feature
- **Add mobile device footprint capability to Eliza** (Mentioned by: DorianD)
- **Implement voice interface for Eliza similar to Clawdbot** (Mentioned by: DorianD)
- **Deploy agents on Moltbook platform to promote ElizaOS adoption** (Mentioned by: DorianD)
- **Add token use case similar to Virtuals bonding curve where transactions happen within ElizaOS** (Mentioned by: averma)

### Documentation
- **Simplify explanation of ElizaOS value proposition - "break it down a lot more" for users to understand** (Mentioned by: Odilitime)
- **Review and update Jeju repository *.md files for staking and service provider documentation** (Mentioned by: DorianD)
- **Clarify token utility and investor value proposition** (Mentioned by: Taco)