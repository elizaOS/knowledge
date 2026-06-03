# elizaOS Discord - 2026-06-02

## Summary

### ElizaOS Ecosystem Architecture

stan0473 provided a comprehensive breakdown of the ElizaOS ecosystem components to clarify the architecture. ElizaOS serves as the core agent-building framework. ElizaCloud functions as the hosting infrastructure for fully-featured agents. Milady is positioned as a consumer-facing UI for life management. Waifu is described as a side project focused on agent competition and economies, with all agents running on ElizaCloud infrastructure.

### Kamino Plugin Development

n4vnt proposed building a comprehensive Kamino plugin for ElizaOS to address a significant integration gap. Kamino is identified as a critical Solana protocol covering lending, borrowing, automated liquidity vaults, yield farms, and limit orders. The plugin aims to cover all core Kamino features, with n4vnt noting that Kamino is exploring AI adoption. anton_0413 validated the importance of this plugin, explaining it would enable ElizaOS agents to perform meaningful DeFi actions beyond simple information retrieval. The technical challenge involves designing reliable abstractions for lending, vault management, and risk-sensitive operations while maintaining developer experience simplicity. n4vnt confirmed taking a measured approach, having written only a few actions so far to ensure quality.

### Plugin Development Process

stan0473 confirmed that all plugins now live in the elizaOS/eliza repository and directed n4vnt to fork and target the develop branch. A warning was issued that development moves quickly and requires frequent rebasing to stay current with the main codebase.

## FAQ

**Q: What are the different components of the ElizaOS ecosystem?**
A: ElizaOS is the agent-building framework, ElizaCloud is the hosting infrastructure for fully-featured agents, Milady is a consumer-facing UI for life management, and Waifu is a side project for agent competition and economies where all agents run on ElizaCloud.

**Q: What is Kamino and why is a plugin needed?**
A: Kamino is a critical Solana protocol covering lending, borrowing, automated liquidity vaults, yield farms, and limit orders. A plugin is needed to enable ElizaOS agents to perform meaningful DeFi actions beyond information retrieval.

**Q: Where should new plugins be developed?**
A: All plugins now live in the elizaOS/eliza repository. Developers should fork and target the develop branch, with frequent rebasing required due to rapid development pace.

**Q: Is Waifu similar to Virtuals?**
A: This question was raised in the discussion but not explicitly answered in the provided summary.

## Help Interactions

**Helper:** stan0473
**Helpee:** n4vnt
**Resolution:** Provided guidance on plugin development process, confirming that all plugins live in elizaOS/eliza and directing to fork and target the develop branch with warnings about frequent rebasing requirements.

**Helper:** anton_0413
**Helpee:** n4vnt
**Resolution:** Validated the importance of the Kamino plugin proposal and provided context on the technical challenges involved in designing reliable abstractions for DeFi operations while maintaining simplicity.

## Action Items

### Technical

- Build comprehensive Kamino plugin covering lending, borrowing, automated liquidity vaults, yield farms, and limit orders (mentioned by n4vnt)
- Fork elizaOS/eliza repository and target develop branch for plugin development (mentioned by stan0473)
- Design reliable abstractions for lending, vault management, and risk-sensitive operations while maintaining developer experience simplicity (mentioned by anton_0413)
- Maintain frequent rebasing due to rapid development pace (mentioned by stan0473)

### Features

- Implement all core Kamino features in the plugin to enable meaningful DeFi actions for ElizaOS agents (mentioned by n4vnt and anton_0413)