# elizaOS Discord - 2026-04-24

## Summary

### Agent Monetization and Service Marketplace

igor.peregudov demonstrated the @elisym/plugin-elizaos-elisym plugin that transforms Eliza agents into paid service providers. The plugin creates a decentralized marketplace where agents can monetize their capabilities through agent-to-agent transactions. The system uses a Nostr-based discovery layer for capability announcement and Solana for payment settlement. The demonstration showed a complete workflow where an Eliza agent publishes its capabilities to Nostr, receives a paid request from Claude desktop for trending GitHub repos, settles payment on Solana devnet, and delivers the requested service. This architecture eliminates the need for intermediary platforms.

### Token Utility and Economic Model

quanteliza proposed a v3 feature for ELIZAOS token utility that would allow protocol fees to be paid in either USDC or ELIZAOS tokens. The proposal includes discounts for payments made in ELIZAOS tokens and automatic buyback and burn mechanisms for USDC payments, similar to early BNB tokenomics. This design aims to create economic demand for the token while maintaining the open-source framework. odilitime responded positively to this proposal, stating it motivated him to complete his November work on enabling plugins to accept $elizaOS and $DegenAI as x402 payment methods. He identified this as the lowest-hanging fruit for implementing token utility.

### Community Organization

odilitime announced updates to working groups following discussions with Shaw. He also made steering bumps to key community members. There was brief discussion about Discord role management and requests for layout feedback, though no specific feedback was provided in the available discussion.

## FAQ

**Q: What does the @elisym/plugin-elizaos-elisym plugin do?**
A: The plugin transforms Eliza agents into paid service providers by enabling agent-to-agent transactions. It uses a Nostr-based discovery layer for capability announcement and Solana for payment settlement, creating a decentralized marketplace for agent services.

**Q: How does the proposed ELIZAOS token utility model work?**
A: The proposed v3 feature would allow protocol fees to be paid in either USDC or ELIZAOS tokens, with discounts for token payments. USDC payments would trigger automatic buyback and burn mechanisms for ELIZAOS tokens, similar to early BNB tokenomics.

**Q: What is x402 payment?**
A: x402 payment is a payment method that plugins can accept. odilitime is working on enabling plugins to accept $elizaOS and $DegenAI tokens through this payment mechanism.

**Q: What blockchain networks does the agent monetization plugin use?**
A: The plugin uses Nostr for the discovery layer where agents announce their capabilities, and Solana devnet for payment settlement.

## Help Interactions

No specific help interactions with clear helper, helpee, and resolution were documented in the provided channel summaries.

## Action Items

### Technical

- Complete November work on enabling plugins to accept $elizaOS and $DegenAI as x402 payment (mentioned by odilitime)
- Implement protocol fee payment system supporting both USDC and ELIZAOS tokens (mentioned by quanteliza)
- Develop automatic buyback and burn mechanisms for USDC payments (mentioned by quanteliza)

### Features

- Add discount mechanism for protocol fees paid in ELIZAOS tokens (mentioned by quanteliza)
- Update working groups structure (mentioned by odilitime)