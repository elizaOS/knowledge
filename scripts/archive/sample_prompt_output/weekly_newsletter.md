# ElizaOS Weekly Newsletter
## April 27 - May 4, 2025

![ElizaOS Banner](https://eliza.how/img/logo.png)

## Executive Summary

The past week has been transformative for the ElizaOS ecosystem, with major developments on both technical and community fronts:

- **ElizaOS v2 Nears Completion**: Shaw confirmed that ElizaOS v2 with multi-agent capabilities will be finalized in the coming weeks, bringing significant enhancements to the framework.

- **Auto.fun Launch Success**: The open-source token launchpad Auto.fun has generated impressive activity with $12 million in volume within its first 12 hours. The platform is now actively launching partner projects, including FightFi and SQUID by Allora Network.

- **Core Framework Improvements**: This week saw 29 merged PRs with significant enhancements to knowledge management, plugin functionality, and developer experience.

## Development Updates

### Framework Enhancements

- **Scopable Knowledge Implementation**: A major feature addition enables more granular control over knowledge resources, allowing agents to have context-specific information access ([PR #4390](https://github.com/elizaos/eliza/pull/4390)).

- **Plugin Integration Improvements**: 
  - Added typing indicator support in Discord plugin ([PR #4364](https://github.com/elizaos/eliza/pull/4364))
  - Implemented API key validation for Anthropic plugin ([PR #4383](https://github.com/elizaos/eliza/pull/4383))
  - Fixed Twitter client integration errors ([PR #4373](https://github.com/elizaos/eliza/pull/4373))

- **Developer Experience Updates**:
  - Enhanced CLI command instructions ([PR #4381](https://github.com/elizaos/eliza/pull/4381))
  - Added automatic rebuilding of core components in monorepo context ([PR #4388](https://github.com/elizaos/eliza/pull/4388))
  - Improved documentation with clearer quickstart guides ([PR #4379](https://github.com/elizaos/eliza/pull/4379))

### Technical Challenges

- **Hardware Limitations**: Users reported challenges running local models, particularly noting that LLAMA 3 8B requires 20+ GB of VRAM, making it impractical for standard consumer hardware.

- **Node.js Compatibility**: Issues were identified with dynamic requires not being supported in Node.js 23+, requiring architectural adjustments.

- **Auto.fun Platform Issues**: Some users experienced problems with DexScreener not updating for certain token launches (FightAlgo and FightBrawl), which impacted momentum. The team also addressed a significant issue with the $QUILL token, where a bug incorrectly displayed token pricing that allowed someone to drain the LP pool. The team has committed to refunding affected users.

## Community Spotlight

### Mental Health Application

Community member Cliff shared details about an impressive mental health application built on ElizaOS. The project features:

- Integration with a smart ring to track physical activities and mood
- Mobile applications for both Android and iOS (iOS approval pending)
- AI-powered therapy and coaching functionality

This project demonstrates the versatility of the ElizaOS framework beyond typical chatbot applications, showing its potential in specialized healthcare contexts.

### OpenRouter Integration

Jin highlighted successful implementation of OpenRouter's web search feature to enhance content for elizaOS partners, providing more up-to-date and relevant information to users.

### Discord Community Engagement

The community has been actively troubleshooting and sharing knowledge about ElizaOS v2 implementations. Notable assistance includes:

- Hardware guidance for running local models within resource constraints
- Integration support for connecting ElizaOS to external frontend applications
- Plugin configuration assistance for Twitter, Discord, and other services

## Token Economics

### Exchange Listings

- **Bithumb Listing**: Community member Avanc shared that ai16z has been listed on Bithumb, Korea's second-largest cryptocurrency exchange, potentially expanding the token's reach.

### Price Discussions

- **Market Cap Targets**: Community members discussed near-term price targets for the ELI5 token between $10-50 million market cap by the end of Q2, with some suggesting an ambitious $30M target within the week.

### Branding Consolidation

- Discussions continued around consolidating ai16z (token) and ElizaOS (platform) under a single name for better brand recognition, with some members proposing a 1:1.11 swap ratio for early adopters during any potential migration.

## Coming Soon

### ElizaOS v2

- The framework's v2 version with multi-agent capabilities is expected to be completed in the coming weeks, as mentioned by shaw.

### Auto.fun Partner Projects

- The team has scheduled launch partner spotlights with one launch per day over the next two weeks, starting with FightFi and continuing with other vetted projects.

### Platform Improvements

- UI enhancements are planned for Auto.fun, including timeframe options for charts similar to TradingView
- The team is working on a staking mechanism for ai16z on Auto.fun
- Image upload support will be added to AI Create over time

## Resources

### Documentation

- [ElizaOS Documentation](https://eliza.how) - Official documentation for setting up and using ElizaOS
- [ElizaOS GitHub Repository](https://github.com/elizaos/eliza) - Source code and issue tracking
- [Auto.fun Platform](https://auto.fun) - Token launch platform built on ElizaOS

### Community Links

- [Discord Server](https://discord.gg/ai16z) - Main community hub for discussions and support
- [Weekly Demo Signup](https://tally.so/r/nrYKXR) - Share your ElizaOS-based projects in weekly demos

---

*This newsletter is compiled based on public information and community discussions. For questions or to submit news for the next issue, please contact the team on Discord.*
