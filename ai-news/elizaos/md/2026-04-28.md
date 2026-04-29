## ElizaOS Community Discussion - April 28, 2026

### Eliza v3 and Milady Announcement

- Shaw announced the team is nearly finished with Eliza v3 and Milady, describing the coming weeks as exciting
- Shaw committed to posting more updates in the main discussion channel
- Community members responded positively to the announcement

### Token and Infrastructure Integration

- Odilitime confirmed that the $elizaOS token is now the default payment method in x402 for the elizaOS and Milady integration
- The $ELIZA token has been connected to infrastructure utility, enabling users to bill x402 services with $ELIZA

---

## Overall Project Summary - April 28, 2026

### Infrastructure and Dependency Modernization

- Active modernization effort targeting Node.js 24, TypeScript 6, Bun 1.3.13, and React 19.2.5

### Completed Work

- Replaced Vercel AI Gateway with OpenRouter on cloud infrastructure, using OpenAI and Anthropic as failovers
- Resolved CLI authentication hangs by implementing auto-clearing for stale Steward and Privy tokens
- Expanded n8n plugin capabilities with TriggerContext for conversation routing and RuntimeContextProvider for improved data handling
- Hardened security and credential management through disconnect-purge functionality and stricter runtime-fact rules

### Pull Requests in Progress

- Credential mediation layer
- Runtime operations manager and widget host refresh
- Conversation routing propagation to the n8n workflow generator
- n8n runtime-context support for Discord and Gmail
- Credential cache purging on disconnect
- Deep-link banner for connector settings
- Bundling of the build-monetized-app skill
- Fixes for action formatting and cloud provider model drift
- Addition of CREATE_TASK to explicit intent actions
- Push of develop branch to production in elizaos/cloud
- Claude and Codex sub-agent bridge specification design