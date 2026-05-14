# elizaOS Discord - 2026-05-13

## Summary

### Eliza v3 Development and Architecture

mahmoudamer7645 raised critical questions about the current development focus of Eliza v3, specifically whether efforts are concentrated on infrastructure stabilization or approaching public release of the full autonomous agent workflow stack. They also inquired about the integration status of the new identity/AgentID system in the upcoming architecture, highlighting concerns about the direction and priorities of the v3 development roadmap.

### Eliza-1 Model Series Release

zadayos announced the latest Eliza-1 model series based on Qwen3.5, featuring a comprehensive range of models from 0.6B to 27B-1M parameters. The series includes a 0.6B model optimized for mobile deployment with offline capability, a new 0.8B model currently training on H200 hardware, and a 27B-1M variant with million token context windows. The technical specifications demonstrate a strategic approach to model deployment across various hardware constraints, from phones to servers, with different models scaled for specific deployment scenarios.

### GODL Protocol Integration Proposal

blankey1717 introduced GODL, a gamified on-chain mining protocol on Solana, proposing integration with elizaOS. The protocol exposes system functionality through SDKs, websocket streams, automation hooks, and a skill.md file designed for agent/tool integrations. GODL enables autonomous agents to interact with mining and staking mechanics, including autonomous strategies, agent-managed wallets, competing mining behaviors, and public leaderboards with performance tracking. odilitime confirmed that elizaOS can use the skill.md format directly, indicating compatibility with existing agent architecture.

## FAQ

**Q: What is the current development focus of Eliza v3?**
A: mahmoudamer7645 raised this question, asking whether development prioritizes infrastructure stabilization or is approaching public release of the full autonomous agent workflow stack. The question remains unanswered in the provided discussions.

**Q: What is the integration status of the new identity/AgentID system in Eliza v3?**
A: mahmoudamer7645 inquired about this, but no response was provided in the available discussion logs.

**Q: What models are included in the new Eliza-1 series?**
A: The Eliza-1 model series based on Qwen3.5 includes models ranging from 0.6B (mobile-optimized with offline capability) to 27B-1M (with million token context). A new 0.8B model is currently training on H200 hardware.

**Q: Can elizaOS use GODL's skill.md format directly?**
A: Yes, odilitime confirmed that elizaOS can use the skill.md format as-is, indicating compatibility with their existing agent architecture.

**Q: What capabilities does GODL enable for autonomous agents?**
A: GODL enables autonomous mining and staking strategies, agent-managed wallets, competing mining behaviors, and public leaderboards with performance tracking through SDKs, websocket streams, and automation hooks.

## Help Interactions

**Helper:** odilitime
**Helpee:** blankey1717
**Resolution:** odilitime confirmed that elizaOS can use GODL's skill.md format directly as-is, validating the compatibility of GODL's integration approach with elizaOS's existing agent architecture.

## Action Items

### Technical

- Clarify whether Eliza v3 development is focused on infrastructure stabilization or approaching public release of the full autonomous agent workflow stack (mentioned by mahmoudamer7645)
- Complete training of the 0.8B Eliza-1 model on H200 hardware (mentioned by zadayos)
- Integrate GODL protocol with elizaOS using skill.md format and SDK/websocket setup (mentioned by blankey1717)

### Features

- Implement autonomous mining and staking strategies for agents using GODL protocol (mentioned by blankey1717)
- Enable agent-managed wallets for GODL integration (mentioned by blankey1717)
- Develop competing agent strategies and public leaderboards for GODL mining behaviors (mentioned by blankey1717)

### Documentation

- Provide status update on the new identity/AgentID system integration in Eliza v3 architecture (mentioned by mahmoudamer7645)
- Share GODL links and agent information with elizaOS team (mentioned by blankey1717)