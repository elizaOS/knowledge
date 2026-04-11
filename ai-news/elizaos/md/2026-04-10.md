## ElizaOS Community Discussion and Developer Integration - 2026-04-10

## Community Discussion

- Moderator confirmed airdrops are planned for ElizaOS token holders, with details to be released at a later time
- Project promdict.ai introduced itself to the community as a prompt and predict platform serving as a battleground for agents
- A community member shared an upcoming Hong Kong event featuring elizaok_bsc, built on ElizaOS
- A user shared content related to digital ownership and the risks of centralized platforms for personal data storage
- A user received assistance regarding wallet verification on Collab.land

## Developer Integration Activity

### x402 Billing Implementation
- Orbis implemented the x402 usage-based billing scheme for AI agents natively on Base
- The implementation enables agents to authorize a maximum spend and pay only for actual usage across LLM and compute APIs

### ElizaOS v2 Socket.IO Integration
- A developer working on a custom dashboard integration with ElizaOS v2 identified the working Socket.IO messaging pattern
- Direct emits were found to fail; the correct pattern requires emitting a message event with a type field
- Type 1 corresponds to ROOM_JOINING and type 2 to SEND_MESSAGE
- Authentication requires an entityId UUID passed in socket options
- A core developer directed the integrator to the ElizaOS documentation site and noted active v3 development is underway