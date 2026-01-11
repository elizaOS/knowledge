# elizaOS Discord - 2026-01-10

## Overall Discussion Highlights

### Infrastructure & Platform Development

**Jeju Layer Launch Announcement**
The most significant announcement was the planned launch of Jeju, a new layer targeting deployment by H2 2026 (potentially sooner). The design emphasizes utility, adoption, and agent activity, with gas fees denominated in $elizaOS tokens while supporting additional tokens for gas payments.

**ElizaCloud Progress**
ElizaCloud continues to evolve with new capabilities:
- Weather data API integration now enabled
- Payment infrastructure operational with first cloud payment transactions completed
- Daily updates being performed by cloud agents
- Users reporting positive experiences with platform access and plugin functionality

**Decentralized Infrastructure Cost Analysis**
Partners discussed developing a sophisticated cost calculator for decentralized infrastructure that goes beyond simple AWS pricing comparisons. The proposed methodology incorporates:
- Revenue loss calculations from system downtime
- Reputational damage multipliers derived from public company financial data
- Example framework: analyzing annual AWS spend against total revenue to calculate business impact of outages

### Agent Technology & Game Automation

**LLM-Free Agent Architecture**
Shaw demonstrated significant technical innovations in agent design:
- Rust implementation of Eliza
- LLM-free agents using text/state parsing instead of language models
- 40 agents running simultaneously in Game of Life simulation using in-memory database
- Agents playing adventure games including Tamagotchi simulations

**Hyperscape Project**
The Hyperscape project (github.com/hyperscapeai/hyperscape) showcases agents playing MMO games including RuneScape and Roblox. A novel anti-detection technique for World of Warcraft was presented: encoding game API calls into pixels via Lua addon and decoding 200 screenshots per second to bypass traditional bot detection.

### Token Economics & Branding

**Token Value Proposition Concerns**
Critical questions emerged about token economics:
- Current token utility limited to planned (but not yet implemented) gas fees
- Daily minting of additional tokens for contributors creating structural downward price pressure
- Community concerns about multiple token deployments and reputational impact

**Branding Discussion**
Multiple suggestions emerged for clarifying the "ElizaOS" naming:
- Emphasis on "open system" vs "operating system" to highlight open-source nature
- Proposal for "Eliza Open Systems" (plural) reflecting multiple OSI stack layers
- Alternative suggestion to keep it simple as "Just Eliza, like Linux"
- Note that "Eliza" alone is trademarked by Shaw

### Technical Challenges

**Agent Behavior Issues**
A significant problem was identified where agents continuously reintroduce themselves instead of following defined prompts in character.ts, failing to progress through intended 5-phase flows (engage to execute). This appears to be a prompt engineering or state management issue requiring investigation.

**Enterprise Adoption Barriers**
Discussion acknowledged limitations in targeting existing enterprise customers, particularly large organizations where CIOs resist AI agent-driven code replacement due to complexity and risk aversion.

## Key Questions & Answers

**Q: What is Jeju and when will it launch?**
A: A new layer targeting launch by H2 2026 (potentially sooner) with gas fees denominated in $elizaOS tokens, designed with emphasis on utility, adoption, and agent activity.

**Q: How should the cost calculator account for downtime beyond AWS pricing?**
A: Factor in lost revenues from outages and include a multiplier for reputational losses, calculated by analyzing company's annual revenue against AWS spending.

**Q: Are the Game of Life agents using LLMs?**
A: No, they use text/state parsing without LLM calls, enabling 40 agents to run simultaneously.

**Q: How are you avoiding detection in World of Warcraft?**
A: Using a Lua addon that encodes every public game API into pixels, then decoding 200 screenshots per second to bypass traditional bot detection methods.

**Q: Can existing enterprise customers be convinced to switch to decentralized infrastructure?**
A: Probably not the large ones - it's too complicated and CIOs won't let AI agents rip and replace code.

**Q: Is elizaos the only official account?**
A: Yes, elizaos is the only official account (clarifying confusion about multiple accounts).

## Community Help & Collaboration

**Token Clarification**
- **Helper:** e | **Helpee:** ElizaBAO
- Explained gudtek token spike to 170-200k market cap with no links, identified as possible larp

**Account Verification**
- **Helper:** ElizaBAO | **Helpee:** shadowforceone
- Clarified that elizaos is the only official account on X.com

**MMO Bot Development Collaboration**
- **Helper:** shaw | **Helpee:** Stan ⚡
- Shared Hyperscape project for MMO game bots, offering collaboration opportunity for World of Warcraft development

**Enterprise Migration Reality Check**
- **Helper:** DorianD | **Helpee:** shaw
- Acknowledged that large enterprises are unlikely targets due to complexity and CIO resistance to AI-driven code replacement

## Action Items

### Technical

- **Deploy Jeju layer by H2 2026** with $elizaOS denominated gas fees and support for additional tokens | *Mentioned by: stoikol*

- **Investigate and fix agent behavior issue** where agents continuously reintroduce themselves instead of following character.ts prompts and progressing through 5-phase flow | *Mentioned by: MRT0B13*

- **Complete AI project deployment** (first step completed) | *Mentioned by: aicodeflow*

- **Develop methodology to calculate revenue loss multiplier** using public company financial data and AWS spending | *Mentioned by: DorianD*

- **Continue development on Hyperscape agents** for MMO games, needs more focus and love | *Mentioned by: shaw*

- **Complete World of Warcraft bot** using Lua addon pixel encoding/decoding technique | *Mentioned by: Stan ⚡*

- **Implement gas fee functionality** using $elizaOS token as currently only planned but not active | *Mentioned by: gby*

### Feature

- **Build cost calculator** that factors revenue loss and reputational damage multipliers for downtime, not just AWS pricing comparison | *Mentioned by: DorianD*

- **Build macOS menu bar widget** for Eliza after browser widget completion | *Mentioned by: R0am | tip.md*

- **Share game bots powered by Eliza decisions** once completed | *Mentioned by: Stan ⚡*

### Documentation

- **Clarify token value proposition and economics** given current minting for contributors without gas fee implementation | *Mentioned by: gby*

- **Document weather data API integration** and usage in ElizaCloud | *Mentioned by: ElizaBAO*

- **Rebrand from "operating system" to "OpenSystems"** to highlight difference from proprietary solutions | *Mentioned by: DorianD*