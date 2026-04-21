# elizaOS Discord - 2026-04-20

## Summary

### Token Migration and Scam Incidents

The ai16z token migration period has officially closed, leaving some community members unable to complete their migrations. nelsonlopes_ was unable to migrate approximately $700-900 worth of tokens and subsequently fell victim to a scam through a fraudulent support ticket, resulting in additional fund losses. Community members advised blocking and reporting the scammers involved in the incident.

### ElizaOS Product Ecosystem Clarification

Significant clarification was provided regarding the relationship between ElizaOS products. ElizaOK is built with elizacloud and currently has no separate token. All users registered under elizaok flow into elizacloud. The token deployment exists on Solana, BSC, and Base chains. Detailed business model explanations were deferred to odilitime for future discussion.

### ElizaOS v3 Development

satsbased announced that ElizaOS v3 is nearly ready for release and will enable agents to generate revenue, marking a significant milestone in the platform's development.

### Elisym Plugin Integration

igor.peregudov released @elisym/plugin-elizaos, a plugin integrating ElizaOS v1 agents with the Elisym decentralized AI-agent marketplace. The plugin enables agents to become paid providers by publishing capability cards over Nostr using NIP-89, accepting encrypted job requests via NIP-90, executing them through the agent's model or SKILL.md tool-use loop, and collecting SOL payments on Solana. The implementation includes 110 tests with CI on every PR and is signed with GitHub Actions provenance.

### Technical Support and Documentation

cacophonousstrife sought guidance on building examples from ElizaOS documentation and was directed to the GitHub examples directory. A request for minimax token plan key integration as a provider plugin remained unresolved. Community engagement initiatives emphasized interaction with Shaw's posts and sharing development updates.

## FAQ

**Q: Has the ai16z token migration period closed?**
A: Yes, odilitime confirmed that the migration period has closed, and users who did not migrate during the window are unable to do so now.

**Q: What is the relationship between ElizaOK and elizacloud?**
A: ElizaOK is built with elizacloud and has no separate token currently. All users registered under elizaok flow into elizacloud.

**Q: On which chains is the token deployed?**
A: The token is deployed on Solana, BSC, and Base chains.

**Q: Where can I find ElizaOS building examples?**
A: Building examples are available in the GitHub examples directory at github.com/elizaOS/eliza/tree/v2.0.0/examples.

**Q: What does the @elisym/plugin-elizaos plugin do?**
A: The plugin integrates ElizaOS v1 agents with the Elisym decentralized AI-agent marketplace, enabling agents to become paid providers by publishing capability cards over Nostr, accepting encrypted job requests, executing them, and collecting SOL payments on Solana.

**Q: When will ElizaOS v3 be released?**
A: satsbased announced that ElizaOS v3 is nearly ready and will enable agents to generate revenue, though no specific release date was provided.

## Help Interactions

**Helper:** odilitime  
**Helpee:** cacophonousstrife  
**Resolution:** Directed to the GitHub examples directory at github.com/elizaOS/eliza/tree/v2.0.0/examples for building examples from ElizaOS documentation.

**Helper:** Community members  
**Helpee:** nelsonlopes_  
**Resolution:** Advised to block and report scammers after falling victim to a fraudulent support ticket scam. Confirmed that token migration period has closed and no further migration is possible.

**Helper:** baogerbao  
**Helpee:** Community  
**Resolution:** Clarified that ElizaOK is built with elizacloud, has no separate token, and all users registered under elizaok flow into elizacloud. Deferred detailed business model explanations to odilitime.

**Helper:** igor.peregudov  
**Helpee:** stan0473  
**Resolution:** Implemented naming convention change for the plugin as requested by stan0473, changing to either plugin-elisym or plugin-elizaos-elisym.

## Action Items

### Technical

- Review PR to the registry (#346) for @elisym/plugin-elizaos integration (mentioned by igor.peregudov)
- Resolve minimax token plan key integration as a provider plugin (mentioned by community member)

### Features

- Complete and release ElizaOS v3 with revenue generation capabilities for agents (mentioned by satsbased)

### Documentation

- Provide detailed business model explanations for ElizaOS, ElizaOK, and elizacloud relationship (mentioned by baogerbao, deferred to odilitime)