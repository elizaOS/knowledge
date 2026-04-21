## ElizaOS Community Discussion and Development Updates - April 20, 2026

## Ecosystem Structure

- ElizaOK is built on ElizaCloud, with users registered under ElizaOK feeding into ElizaCloud
- ElizaOK currently has no separate token
- ElizaBAO shared an update about building elizaok_bsc on BNB Chain, receiving acknowledgment from Binance
- Eliza v3 is nearly ready, with the vision that agents will help users generate income
- ElizaOS token is confirmed available on Solana, BSC, and Base

## AGI and Agent Development

- Shaw shared posts on X hinting at AGI developments and the belief that the best thing an agent can do is help people make money
- Community members engaged with and shared Shaw's posts to spread awareness

## Community Alerts and Security

- A user reported losing approximately 900 dollars worth of crypto after interacting with a scam support ticket in the channel
- Community members warned others to block and report suspicious accounts
- Discussion raised around the Lazarus Group hacking KelpDAO for 210 million dollars and the potential for AI agents to enhance DeFi security

## Token Migration and Documentation

- Odilitime confirmed the ai16z token migration window is now closed
- Users building from ElizaOS documentation were directed to the GitHub repository at the v2.0.0 branch, which contains numerous example projects

## Plugin Release - plugin-elizaos-elisym

- Igor from Elisym Labs released the plugin-elizaos-elisym package, converting any ElizaOS v1 agent into a paid provider on the Elisym decentralized AI-agent marketplace
- Plugin publishes capability cards over Nostr using NIP-89
- Accepts encrypted job requests via NIP-90 and executes them through the agent model or a SKILL.md tool-use loop
- Collects SOL payments on Solana
- Includes 110 tests with CI on every pull request and is signed with GitHub Actions provenance
- A pull request to the ElizaOS plugin registry is open
- Plugin was renamed to plugin-elizaos-elisym following a request from Stan

## Framework Development

- Core dependencies updated including @coral-xyz/borsh, gymnasium, and the Capacitor monorepo
- Routine maintenance performed on Uniswap v2/v3 SDKs, @types/node, and Rust WASM-bindgen components
- Critical memory management bug in InMemoryDatabaseAdapter.updateMemories resolved for correct roomId handling
- Discord routing issues within app-lifeops fixed to improve communication reliability
- New proposal opened to standardize agent commerce for tool and service payments
- Three earlier proposals related to Merxex agent-to-agent commerce integration were reviewed and closed