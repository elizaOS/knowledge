# elizaOS Discord - 2026-02-05

## Overall Discussion Highlights

### Critical Platform Issues (elizacloud.ai)

**Account & Payment System Bugs**

A critical bug was identified in the elizacloud.ai welcome email system that poses a serious threat to customer retention. New users are not receiving the promised $5 credits, and clicking the "get started" button in welcome emails is overwriting existing accounts and agents, creating new accounts with only $1 balance instead. This represents a major blocker for customer onboarding and retention.

**Payment & Recharging Limitations**

Multiple payment-related obstacles were identified:
- Users cannot transfer tokens between accounts to help friends recharge
- VPN users are blocked from accessing payment pages
- Lack of easy payment options is causing customer loss at the critical conversion point when trial users want to become paying customers

A proposed solution involves implementing wallet addresses for each account to enable direct crypto token deposits without requiring wallet connections.

### Babylon.market Deployment & Debugging

The core development team focused on deploying and debugging babylon.market, a platform with user authentication and reward systems. Multiple API endpoints were failing, affecting page functionality. Key issues identified:

- **Username Creation Bug**: Users receiving "@userid:priv" as usernames instead of proper usernames
- **Discord OAuth Broken**: Account linking functionality not working
- **Twitter Follow Rewards**: Reward claiming system non-functional with error messages

A fix was pushed and merged to production during the discussion, allowing testing to proceed. Access is currently restricted to top 100 users, with requests for additional testing access being made.

### AI16Z to ELIZAOS Token Migration

The token migration deadline became a major discussion point, with the migration window having been open since November (90 days) now closed. Key points of contention:

- Community members frustrated about missing the deadline due to being away from wallets
- Debate over whether the timeline was sufficient for investors who may be traveling
- Clarification that this was a migration, not an airdrop
- Unmigrated tokens will be locked for one year
- Scammer activity targeting users with migration issues

### Project Updates

**DegenAI**: Confirmed to be actively developed and not abandoned. The project performed well in Babylon test games with real tests upcoming. The team is focused on the Babylon launch.

**Fake Projects Warning**: Concerns raised about fake projects launching on Babylon wallet falsely claiming association with Shaw, with requests for official clarification to prevent dev selling under his name.

### Developer Outreach & New Projects

- **CERBERUS-AGI**: Trollstore AI-Driven Software in beta shared by CT
- **x402 Payment Gateway**: Beta testing sought for AI agent payment gateway on Solana
- **rentasoul**: Platform where users can give their soul to AI agents, bring Eliza agents, or complete tasks for payment

### Technical Discussions

- Questions about which Eliza version works properly with the Twitter plugin locally (unanswered)
- Interest expressed in Claude Opus 4.6 release from Anthropic at the same price point as 4.5

## Key Questions & Answers

**Q: Any meta threads plugin?** (asked by sazilariel)  
A: Not that I'm aware of (answered by Odilitime)

**Q: Are you pushing new updates?** (asked by s)  
A: Fixes were being pushed and merged to production (answered by SYMBiEX, tcm390)

**Q: How do I get admin/mod access on babylon.market?** (asked by SYMBiEX)  
A: Sign up with ElizaLabs.ai email for automatic access, or provide username for manual modding (answered by SYMBiEX)

**Q: Why am I getting @userid:priv as username?** (asked by ziflie)  
A: Username creation bug being investigated (answered by SYMBiEX)

**Q: Is Discord OAuth for account linking working?** (asked by Stan ⚡)  
A: It's broken, being investigated (answered by SYMBiEX)

**Q: Will the fix be merged today/tomorrow for testing?** (asked by Stan ⚡)  
A: It has been merged (answered by tcm390)

**Q: What's going on with degenai? Is anything being worked on, or has it been abandoned?** (asked by gby)  
A: It has not been abandoned, still working on it, was owning the Babylon test game with real test coming up (answered by Odilitime)

**Q: What will happen to non migrated Eliza tokens do they stay locked up forever or something?** (asked by Biazs)  
A: Locked for a year (answered by jasyn_bjorn)

**Q: Why are there so many tokens, it should only be elizaos?** (asked by g)  
A: What Shaw does in react to people reacting to him has nothing to do with elizaOS or labs, focused on Babylon launch (answered by Odilitime)

## Community Help & Collaboration

**Migration Scam Prevention**  
Helper: Odilitime | Helpee: shoemaker6765  
Context: User experiencing migration issues was being contacted by scammers  
Resolution: Warning issued that contact was a scammer, preventing potential fraud

**Migration Timeline Clarification**  
Helper: Kenk, jasyn_bjorn | Helpee: sam.mrk  
Context: Misunderstanding about migration deadline (thought it was 2 weeks)  
Resolution: Clarified token migration has been open since November (90 days) and it's a migration not an airdrop

**Token Lock Information**  
Helper: jasyn_bjorn | Helpee: Biazs  
Context: Question about what happens to non-migrated tokens  
Resolution: Clarified tokens are locked for a year

**DegenAI Project Status**  
Helper: Odilitime | Helpee: gby  
Context: Concerns about degenai project abandonment  
Resolution: Confirmed project is not abandoned and still being worked on

**Platform Focus Clarification**  
Helper: Odilitime | Helpee: g  
Context: Confusion about multiple tokens diluting attention  
Resolution: Explained Shaw's personal activities are separate from elizaOS/labs, team focused on Babylon launch

**Babylon.market Bug Investigation**  
Helper: SYMBiEX <<CidSociety>> | Helpee: ziflie, Stan ⚡  
Context: Username creation and OAuth issues  
Resolution: Committed to investigate issues, fix was pushed and merged to production

**Production Deployment Confirmation**  
Helper: tcm390 | Helpee: Stan ⚡  
Context: Checking if fix was merged to production for testing  
Resolution: Confirmed the fix has been merged to production

**ElizaCloud Bug Investigation**  
Helper: sam | Helpee: yojo  
Context: Critical bug with welcome email not adding $5 credits and overwriting existing accounts  
Resolution: Requested email/address to investigate the issue

## Action Items

### Technical

- **Fix critical bug where welcome email $5 credits are not added to new accounts** (Mentioned by: yojo)
- **Fix bug where clicking "get started" in welcome email overwrites existing accounts and agents, creating new account with $1 balance** (Mentioned by: yojo)
- **Stop sending welcome emails until account overwrite bug is fixed** (Mentioned by: yojo)
- **Investigate username creation bug causing @userid:priv usernames** (Mentioned by: SYMBiEX <<CidSociety>>)
- **Fix Discord OAuth for account linking** (Mentioned by: SYMBiEX <<CidSociety>>)
- **Fix Twitter follow reward claiming errors** (Mentioned by: SYMBiEX <<CidSociety>>)
- **Fix failing API endpoints affecting page functionality** (Mentioned by: sam)
- **Approve hashwarlock user for testing outside top 100 restriction** (Mentioned by: Agent Joshua ₱ | TEE)
- **Determine which Eliza version works properly with Twitter plugin locally** (Mentioned by: some)
- **Continue development work on degenai for upcoming real Babylon test** (Mentioned by: Odilitime)

### Feature

- **Implement wallet addresses for each account to enable token deposits for account recharging without wallet connection** (Mentioned by: yojo)
- **Enable token transfers between accounts to allow users to recharge friends' accounts** (Mentioned by: yojo)
- **Fix VPN blocking issue on payment page linkout** (Mentioned by: yojo)
- **Implement referral program with rewards for converting paying customers** (Mentioned by: yojo)
- **Beta testing needed for x402 payment gateway for AI agents on Solana** (Mentioned by: Rishab)
- **Review and provide feedback on CERBERUS-AGI Trollstore AI-Driven Software in beta** (Mentioned by: CT)

### Documentation

- **Shaw needs to clarify via tweet that fake projects on Babylon wallet are not funded by him to prevent dev selling under his name** (Mentioned by: zelm1)