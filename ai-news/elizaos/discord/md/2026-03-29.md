# elizaOS Discord - 2026-03-29

## Summary

### Community Organization and Information Architecture

The ElizaOS community discussed challenges with channel fragmentation and information accessibility. A key concern was whether projects like Milady should have separate Discord channels or be integrated into the main Eliza Discord. The fragmentation creates confusion for investors who need centralized information to understand the ecosystem, with many people unaware that Milady was built on Eliza. The community identified a need for better communication about the relationship between various projects and the ElizaOS framework. A proposal emerged to create a centralized hub on the website showcasing all agents, apps, dApps, and community projects to reduce confusion around SHAW and other projects that appear independent but are part of the ElizaOS ecosystem.

### Discord Channel Strategy and Bridging

Discussion revealed different purposes for various Discord channels within the ecosystem. Shaw's cozy dev Discord is tailored for builders and thinkers, while the main Discord serves traders and investors. To address fragmentation concerns, a potential solution was proposed to create a bridged room to connect different community spaces while maintaining their distinct purposes.

### API Marketplace for AI Agents

A new API marketplace called Orbis was announced, specifically designed for AI agents. The platform implements HTTP 402 payment-required protocol integrated with their API gateway, enabling autonomous API consumption by Eliza agents. The system allows agents to make pay-per-call API requests, automatically pay in USDC on the Base blockchain, and receive API responses without requiring subscriptions, API keys, or human intervention. Currently available endpoints include text analysis, QR code and encoding services, form submission, and fake data generation capabilities.

### Developer Onboarding and Resources

Questions arose about building with ElizaOS and participating in the agent-challenge, specifically regarding endpoint provision and whether developers need to pay for OpenRouter or OpenAI models. The framework was confirmed to be open source, providing accessibility for developers.

### Security and Scam Prevention

Multiple scam warnings were issued in the coders channel regarding fraudulent messages, demonstrating ongoing community vigilance against malicious actors.

## FAQ

**Q: Should Milady have a separate Discord channel or be integrated into the main Eliza Discord?**
A: The discussion highlighted that fragmentation creates confusion for investors. Shaw's cozy dev Discord is tailored for builders and thinkers, while the main Discord serves traders and investors. A bridged room solution was proposed to connect different community spaces.

**Q: How can the community better understand which projects are built on ElizaOS?**
A: A centralized hub on the website was proposed to showcase all agents, apps, dApps, and community projects, helping reduce confusion around projects like SHAW that appear independent but are part of the ElizaOS ecosystem.

**Q: Do developers need to pay for OpenRouter or OpenAI models when building with ElizaOS?**
A: The ElizaOS framework is open source, though specific details about model endpoint costs were not fully clarified in the discussion.

**Q: How does Orbis enable autonomous API consumption for AI agents?**
A: Orbis implements HTTP 402 payment-required protocol. Agents make pay-per-call API requests, receive a 402 status code, automatically pay in USDC on the Base blockchain, and receive the API response without requiring subscriptions, API keys, or human intervention.

**Q: What endpoints are currently available on Orbis?**
A: Currently live endpoints include text analysis, QR code and encoding services, form submission, and fake data generation capabilities. The platform offers an agent discovery endpoint at orbisapi.com/api/agents/discovery that returns the full API catalog.

## Help Interactions

**Helper:** magicyte
**Helpee:** satsbased
**Resolution:** Clarified that Shaw's cozy dev Discord is tailored for builders and thinkers, while the main Discord serves traders and investors, explaining the purpose of different community spaces.

**Helper:** odilitime
**Helpee:** satsbased
**Resolution:** Offered to create a bridged room next week to address concerns about community fragmentation.

**Helper:** satsbased
**Helpee:** sheldoncooperbbt
**Resolution:** Confirmed that the ElizaOS framework is open source in response to questions about building with ElizaOS and participating in the agent-challenge.

**Helper:** baogerbao and satsbased
**Helpee:** Community
**Resolution:** Identified and warned about scam messages from pluginweb3 in the coders channel.

## Action Items

### Technical

- Create a bridged room to connect different Discord community spaces (mentioned by odilitime)
- Implement agent discovery endpoint integration for Orbis API marketplace (mentioned by theredwizarddev)
- Add new endpoints to Orbis based on community needs for autonomous external API access (mentioned by theredwizarddev)

### Features

- Develop a centralized hub on the website to showcase all agents, apps, dApps, and community projects (mentioned by cyborgxai)
- Expand Orbis API marketplace endpoints beyond current offerings of text analysis, QR code services, form submission, and fake data generation (mentioned by theredwizarddev)

### Documentation

- Improve communication about which projects are built on ElizaOS to reduce confusion (mentioned by satsbased)
- Create clearer documentation about the relationship between SHAW and other projects within the ElizaOS ecosystem (mentioned by cyborgxai)