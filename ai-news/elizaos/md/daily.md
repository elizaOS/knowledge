## ElizaOS Community Discussion: June 7, 2026

### AI Companion Development

- New community member Thaoryel introduced herself with a focus on building conversational AI companions using ElizaOS
- Odilitime confirmed ElizaOS supports Discord integration (via plugin-discord), ElevenLabs voice generation, image generation, and long-term relationship development features
- Ruby, an ElizaOS-based agent, was highlighted as capable of generating videos and images with the appropriate model downloaded
- RubyTrivia on X was shared as a working example of an ElizaOS-built agent

### Token Migration and Community

- Odilitime confirmed the AI16Z token migration window has closed
- A separate developer-focused Discord server was noted as available for technical assistance
- Shaw posted a community request for spare compute to run an agent task analyzing the ArkLib GitHub repository for code quality and potential LLM-generated content

### Agent Benchmarking and On-Chain Tools

- builderr_guru described a testing harness for benchmarking agent quality versus luck, using a single decide() function with identical data and fills, forward-tested on hidden periods
- Top performers in the harness were re-evaluated on additional hidden periods to distinguish skill from luck
- Simple risk-off logic was found to consistently outperform leveraged momentum strategies during real market downturns
- Cabal_hunter introduced Cabal-Hunter, a live on-chain funding tracer for detecting coordinated wallet activity before trade execution
- The tool identified a case where six wallets were funded from the same source 47 seconds before a first trade, preceding a rug pull
- Cabal-Hunter is available as a pay-per-query MCP server at 0.05 USDC per query, integrating with Claude, Cursor, and ElizaOS via the plugin-x402-solana package
- A GitHub template for Python and ElizaOS integration was shared

---

## Eliza Cloud Apps Launch and Infrastructure Development

### Cloud Apps Launch

- Eliza Cloud Apps launched with per-tenant isolated container hosting including database isolation, custom URLs, and metered billing
- Terraform modules deployed for the apps data-plane
- CI workflows established for both staging and production environments
- Container lifecycle management capabilities added to the Cloud API, including PATCH, DELETE, and scale operations
- Encryption-free path enabled for tenant cluster admin DSNs to streamline provisioning workflows

### Cloud API and SDK Enhancements

- ElizaCloudClient expanded with a transcribeAudio function supporting voice and speech-to-text capabilities
- Billing accuracy improved by fixing cron logic related to earnings conversion failures
- Authentication issues resolved for WebSocket and EventSource connections by enabling token passing via query parameters

### Platform Stability and Bug Fixes

- UI 404 and 500 errors resolved by mounting missing routes and bundling the LiFi SDK
- Domain registration logic corrected to prevent erroneous charges for failed stub registrations
- Provisioning daemon issues addressed including Steward platform-key path integration and agent token expiration limits