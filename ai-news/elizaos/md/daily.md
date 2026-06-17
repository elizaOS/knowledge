## ElizaOS Discord Community Activity - June 8, 2026

### General and Coders Channels

- User Doniyorov posted near-identical solicitation messages in both the general discussion and coders channels, framing them around auditing the elizaos/plugin-discord architecture and the voice.ts file
- Posts described the user as a Senior AI Architect with TradFi and quantitative background, seeking a $45,000 USDT contract buyout or structured yearly retainer
- Offered 40 to 80 hours per week covering agent orchestration optimization, custom plugin wrapper development, and off-chain state management
- Posts appeared in coordinated form across both channels, inviting interested parties to DM for a live technical discussion

- User anton_0413 posted in the coders channel seeking a new collaborator after a previous colleague became unavailable due to other work commitments
- Directed interested community members to reach out via DM for details

### Partners Channel

- User DEMIAN from DAPPCRAFT sent a soft ping to Shaw, a moderator and Labs Alumni, referencing a prior message thread

---

## Eliza Cloud Apps Development Update - June 8, 2026

### Completed Work

- Enabled reverse-proxying via a new per-app Caddy routing client
- Implemented collision-safe host-port allocation for high-density deployments
- Enforced strict tenant isolation through DSN injection for database URLs
- Resolved Terraform application errors and stabilized staging environments for BitRouter
- Fixed runtime image dependency issues by hoisting the plugin-wallet module
- Resolved BitRouter and AI pricing issues including HTTP 402 and 5xx errors by switching to BYOK API-key mode and forcing pricing for OpenAI text-embedding models

### Active Work

- Pull requests in progress covering infrastructure and database work, new features and UX improvements, and bug fixes
- Four billing leaks identified in the Apps hosting and per-tenant-DB model are under investigation
- Cloud-init configurations for Caddy, pgbouncer, and provisioning-lifecycle management are being addressed prior to production deployment