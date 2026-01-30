# elizaOS Discord - 2026-01-29

## Overall Discussion Highlights

### Token Economics and Migration Concerns

The community raised significant concerns about token utility and distribution following the ai16z to elizaos migration. Key issues included:

- **Token Allocation Controversy**: Community members questioned the 40% team allocation after a 1:10 token increase, where the community received only 6 tokens while the team received 40%
- **Migration Technical Issues**: Users reported 98% losses when attempting to swap ElizaOS tokens on the ETH chain back to ETH or USDT due to zero liquidity
- **Utility Clarification**: Odilitime clarified that the token serves as the accepted currency in their products, provides gas fees for Jeju, and includes buy-back mechanisms from credit card rail revenue
- **Migration Rationale**: The migration from ai16z to elizaos was necessary for rebranding and multichain accessibility

### AI Routing and Framework Development

DorianD led an extensive exploration of AI model routing systems, proposing the creation of "ElizaRouter":

- **Existing Solutions Identified**: RouteLLM (Python-based for prompt complexity analysis), Latitude.so (prompt engineering platform), and MasRouter (multi-agent system management)
- **Proposed Architecture**: Distributed routing mechanism where receiving nodes select optimal nodes with time decay for Quality of Service
- **Model Evaluation**: Small open-source models considered include Microsoft Phi-4 Mini (3.8B-14B), Qwen2.5/Qwen3 (1.5B-7B), Mistral 7B, and DeepSeek-Coder for code-specific tasks
- **Implementation Plan**: Rewrite existing routing frameworks to Rust or TypeScript

### Social Media Integration Development

The core development team discussed implementing social media connection functionality:

- **Connection Page Feature**: Sam announced plans to build a connection page where users can link social accounts before being redirected back to the bot
- **Composio Integration**: The team explored using Composio, an open-source tool for authentication and social integrations
- **Existing Resources**: Stan revealed he had created a Composio plugin months earlier and offered to share it along with an RFC document containing implementation ideas

### Critical Bug in Eliza Framework

Victor Creed identified a significant bug in Eliza 1.7.2 affecting action callback execution:

- **Expected Behavior**: Callbacks should send messages sequentially: (1) initial feedback, (2) structured return text, (3) detailed callback message
- **Actual Behavior**: Messages are sent in reverse order with the detailed callback first, then initial feedback, and the structured return message is completely omitted
- **Impact**: Affects custom plugins using `plugin-sql`, `plugin-openai`, and `plugin-bootstrap`
- **Status**: Remains unresolved with no community solutions provided

### Market Analysis

DorianD provided cryptocurrency market outlook suggesting the market is entering the final phase of a bear market, with an estimated 6 months until bottom, followed by 6-12 months of sideways movement, with potential recovery activity beginning in 2027.

## Key Questions & Answers

**Q: Why should anyone buy elizaos token?** (asked by gby)  
**A:** Token is the currency accepted in products including gas for Jeju, with credit card revenue going into buy backs (answered by Odilitime)

**Q: Why was the migration from ai16z to elizaos necessary?** (asked by gby)  
**A:** Had to rebrand the token and wanted to go multichain for easier access (answered by Odilitime)

**Q: What is the actual use case for the token beyond Jeju gas fees?** (asked by gby)  
**A:** Currency accepted in products, gas for Jeju, and buy-back mechanisms from credit card rails (answered by Odilitime)

**Q: Why did hyperscape and babylon get their own tokens instead of using elizaos token?** (asked by g)  
**A:** They're on-chain tokens for the currency in those games (answered by Odilitime)

**Q: How to fix "Cannot find module '@elizaos/plugin-web-search'" error after plugin installation?** (asked by DigitalDiva)  
**A:** Edit the project's package.json to include proper module resolution, try installing with bun (answered by Odilitime)

**Q: Should we use Composio for our authentication needs?** (asked by sam)  
**A:** Stan shared that he created a plugin months ago and is writing an RFC with ideas on it (answered by Stan ⚡)

**Q: Is your question regarding swaps on eth facing slippage or is it a migration question?** (asked by Kenk)  
**A:** It's about 98% loss when converting ElizaOS tokens back to ETH or USDT (answered by Sarthak)

**Q: How to bridge & migrate ElizaOS tokens from ETH chain when liquidity went zero?** (asked by Sarthak)  
**A:** Check the migration channel for instructions (answered by MDMnvest)

### Unanswered Questions

- Are the wallets holding 40% of the supply known and do they have a vesting schedule? (asked by Jayzen)
- Why did team get 40% when it is open source after the 1:10 token increase? (asked by averma)
- What existing frameworks are available for AI model routing based on prompt complexity? (asked by DorianD)
- What small open-source models are best for routing decisions? (asked by DorianD)
- Why are action callbacks in Eliza 1.7.2 executing in reverse order compared to documentation? (asked by Victor Creed)

## Community Help & Collaboration

**Stan ⚡ → sam**  
Context: Sam was exploring Composio for social authentication implementation  
Resolution: Stan shared his existing Composio plugin repository (github.com/standujar/plugin-composio) and offered to share an RFC document with implementation ideas

**MDMnvest → Sarthak**  
Context: ElizaOS tokens on ETH chain showing zero liquidity and unable to migrate  
Resolution: Directed to migration channel for assistance

**Kenk → Sarthak**  
Context: Unclear whether issue was slippage or migration related  
Resolution: Helped clarify the specific problem (98% loss on conversion)

**Odilitime → DigitalDiva**  
Context: Plugin web-search installation failing with module resolution error  
Resolution: Suggested editing package.json and trying bun installation, directed to dev-support channel

**Chiko → joaointech**  
Context: Looking for smart contract developers  
Resolution: Directed to private DM conversation

## Action Items

### Technical

- **Fix callback execution order bug in Eliza 1.7.2** where messages are sent in reverse order and structured return text is omitted (Mentioned by: Victor Creed)
- **Fix module resolution for @elizaos/plugin-web-search plugin installation** (Mentioned by: DigitalDiva)
- **Work on connection page for social media integration** with redirect flow back to bot (Mentioned by: sam)
- **Review Stan's existing Composio plugin** at github.com/standujar/plugin-composio (Mentioned by: Stan ⚡)
- **Rewrite existing routing frameworks** (RouteLLM, Latitude.so, MasRouter) to Rust or TypeScript (Mentioned by: DorianD)

### Feature

- **Create ElizaRouter with distributed node selection** and time decay for QoS (Mentioned by: DorianD)
- **Implement routing system using small models** like Phi-4 Mini, Qwen2.5, or Mistral 7B for prompt complexity analysis (Mentioned by: DorianD)
- **Evaluate Composio for in-chat authentication implementation** (Mentioned by: sam)

### Documentation

- **Provide clear migration instructions** for ETH chain ElizaOS tokens with zero liquidity (Mentioned by: Sarthak)
- **Clarify token utility beyond Jeju gas fees** and explain buy-back mechanisms (Mentioned by: gby)
- **Disclose wallet addresses holding 40% supply** and vesting schedule (Mentioned by: Jayzen)
- **Explain token distribution rationale** after 1:10 increase where community got 6 and team got 40% (Mentioned by: averma)
- **Complete and share RFC document** about Composio implementation ideas (Mentioned by: Stan ⚡)