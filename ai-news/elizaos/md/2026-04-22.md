## ElizaOS Community Discussion: April 22, 2026

### Community Concerns and Team Response

- Community members raised allegations related to the AI16Z token launch and migration, including claims of token dumping and misappropriation during migration
- Odilitime, core developer and moderator, defended the project and Shaw personally, citing tools like OpenClaw and Hermes as evidence of real market demand for ElizaOS
- Odilitime speculated that legal counsel had advised the team against public statements regarding the ongoing lawsuit
- A community member identified the law firm filing the lawsuit as also pursuing a class action against pump.fun

### Token Migration

- Odilitime confirmed the AI16Z to ELIZAOS migration window has closed
- A waitlist option was offered to users who missed the migration window, described as a longshot for potential future reopening

### Developer Activity

- Stan confirmed ElizaOS v2.x is stable enough for active development
- Stan clarified versioning: 0.x was the first version, 1.x the second, and 2.x the third
- A scam warning was issued after a user lost 100,000 AI16Z tokens via a fraudulent site at bulkdao.co/allocation; moderators were alerted

### New Plugins and Projects

- LemonCake plugin introduced for ElizaOS v2, MIT-licensed, enabling autonomous agents to pay for API services using spend-capped, time-boxed, revocable pay tokens
  - Supports USDC and JPYC on Polygon
  - Integrates with 32 paid APIs including search, scraping, LLM, and image services
  - Auto-journals transactions to QuickBooks and Xero
- DailyBite mental health app shared, developed with two licensed psychologists, offering CBT-based daily tasks targeting anxiety and stress
  - Available free on iOS and Android during beta
  - Developer built the app using skills gained from running an ElizaOS-powered AI agent on Twitter

---

## ElizaOS Development Digest: April 22, 2026

### Completed Work

- Milady CI pipeline restored, recovering website blocker and Telegram export functionality
- Method collisions in the LifeOps signal client resolved
- Broad dependency hardening completed across Rust crates, Python benchmarks, and JavaScript/TypeScript packages
- Infrastructure updates applied to mobile and Supabase Postgres components
- Cloud platform authorization flows migrated to Steward
- Native Ethereum and Solana login buttons introduced for identity management
- Billing classification error for image-generation model pricing resolved
- Plugin registry expanded with addition of the @elisym/plugin-elizaos package

### Work in Progress

- Local inference hub with provider switcher and agent local probes
- 2.x/v3 codebase cleanup and prompt bloat reduction
- Ongoing dependency maintenance
- Fixes for tenant ID formatting and session expiry handling in the cloud platform
- Journal drift repair
- Solana escrow and reputation plugin from Holdfast Protocol pending registry addition
- Follow-up required on Telegram read receipt optimization for message ID fetching