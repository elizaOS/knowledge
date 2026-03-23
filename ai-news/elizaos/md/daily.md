## ElizaOS Development Updates and Community Discussion - March 12, 2026

### Token Migration Closure

- Token migration from AI16Z to elizaOS permanently closed on February 4, 2026 after a 3-month window
- Odilitime offered to maintain a list of affected users who missed the deadline in case migration can be reopened
- The team clearly communicated the migration period when it started

### Milady App Development

- Milady app targeting release approximately 2 weeks from discussion date
- Profits from cloud service will fund buybacks of elizaOS tokens
- Odilitime confirmed the team holds 10 percent of tokens vested over many years
- Odilitime stated he has not sold any tokens in the last 2 months
- ElizaOS reached a 2.5 billion dollar market cap

### Open Agent Registry Launch

- Developer built open agent registry with autonomous orchestration at aiprox.dev
- Registry features crypto payment settlement via Lightning, Solana, and x402
- Agents can self-register and get rated by real usage
- External agent autonomously found the registry and attempted self-registration unprompted
- Registry uses public REST API for agent registration with capability slug, payment rail, price per call, and endpoint
- 14 agents currently live on the registry
- Skill.md file created for agentskills.io discovery following Odilitime's suggestion

### Runtime Refactor Proposal

- Odilitime proposed major runtime refactor to address AgentRuntime being a 6273-line god object
- Proposal involves externalizing runtime components
- Database adapter will become required constructor argument instead of plugin initialization side-effect
- Team discussed plugin-sql registration and concurrent plugin loading issues
- Deadline set for Sunday for feedback before implementation

### Infrastructure Updates

- elizaos/cloud repository added to tracked repos in pipeline configuration
- Pull request submitted to update pipeline with new repository using dev as default branch

### Security Awareness

- Community members identified and warned about scam attempts
- Fake support ticket bot directed users to website requesting seed phrases
- Odilitime confirmed the scam and advised users not to provide seed phrases