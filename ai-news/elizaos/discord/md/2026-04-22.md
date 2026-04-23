# elizaOS Discord - 2026-04-22

## Summary

### Communication and Transparency Concerns

Community members expressed significant frustration about the lack of official statements regarding an ongoing lawsuit. hide.o.n requested proactive communication from the team to prevent potential exchange delistings. odilitime explained that limited access to official accounts and legal counsel advice contributed to the silence. The ElizaOS X account has been inactive for nearly a month, raising concerns about community engagement. alexeill noted that lawsuits typically reduce company communications as a standard practice.

### Token Migration Issues

aeropedro discovered their self-custodied AI16Z tokens could not be migrated to ELIZAOS because the migration window had closed. odilitime offered to add them to a waitlist but acknowledged it was a longshot. This highlighted ongoing challenges for token holders who missed the migration deadline.

### Project Viability and Community Sentiment

Mixed sentiment emerged regarding project viability. lordwallet accused the team of fraud and token dumping, while odilitime defended Shaw and pointed to continued GitHub activity as evidence of ongoing development. odilitime cited openclaw and hermes as proof of market demand, suggesting the token narrative damaged the project more than the underlying technology.

### Version Stability and Migration Planning

vslappyx inquired about v2.x/v3 stability for agent development, with stan0473 confirming readiness and explaining the versioning convention where 0.x represents the first version, 1.x the second, and 2.x the third. odilitime merged elisym into the elizaOS ecosystem, with stan0473 identifying v3 porting as the next quest. igor.peregudov confirmed v2 porting feasibility and inquired about stable release timing for v2, which is currently in alpha.

### Security Incident

igor.peregudov lost 100k ai16z tokens to a wallet drainer at bulkdao.co/allocation, serving as a community warning about phishing attacks. The transaction was documented on Solscan for community awareness.

### LemonCake Payment Plugin Launch

lemoncake03027 introduced an open-source MIT-licensed payment solution for autonomous agents to handle API paywalls. The plugin provides spend-capped, time-boxed, revocable Pay Tokens using USDC/JPYC on Polygon. Integration requires one line in ElizaOS v2 using eliza-plugin-lemoncake. Features include 32 paid APIs, auto-idempotency keys, structured receipts, QuickBooks/Xero/Zoho/freee integration, and a KYA tier system. The plugin is also available for MCP (Claude/Cursor/Cline) and Dify Marketplace, with sandbox mode available for testing. odilitime approved the implementation.

### Discord Technical Issues

Discord experienced technical issues with posts being auto-deleted without appearing in audit logs, affecting multiple users including flykite and nusko_. odilitime could not identify the cause but manually reposted affected content.

### Community Agent Development

nusko_ shared experience building a Jinx AI agent using ElizaOS that achieved 9M impressions and 3.3K followers before encountering Twitter bans, demonstrating practical application of the platform despite challenges.

## FAQ

**Q: Is ElizaOS v2.x/v3 stable enough for agent development?**
A: Yes, according to stan0473, it is ready for development. The versioning convention follows 0.x as first version, 1.x as second, and 2.x as third version. v2 is currently in alpha.

**Q: Can I still migrate AI16Z tokens to ELIZAOS?**
A: The migration window has closed. odilitime can add late requests to a waitlist, but acknowledged it is a longshot for successful migration.

**Q: Why has the ElizaOS X account been inactive?**
A: odilitime explained limited access to official accounts and that legal counsel advised silence during the ongoing lawsuit. alexeill noted that reduced communications during lawsuits is standard practice.

**Q: How do I integrate LemonCake payment plugin with ElizaOS?**
A: Integration requires one line in ElizaOS v2 using eliza-plugin-lemoncake. The plugin is open-source under MIT license and provides spend-capped, time-boxed, revocable Pay Tokens using USDC/JPYC on Polygon.

**Q: What is the current status of v3 migration?**
A: odilitime merged elisym into the elizaOS ecosystem. stan0473 identified porting to v3 as the next quest, and igor.peregudov confirmed v2 porting is feasible.

**Q: Is the ElizaOS project still viable?**
A: odilitime pointed to continued GitHub activity and cited openclaw and hermes as proof of market demand, suggesting the technology remains sound despite token narrative challenges.

## Help Interactions

**Helper:** odilitime | **Helpee:** aeropedro | **Resolution:** Added to waitlist for token migration after missing the migration window, though acknowledged it was a longshot.

**Helper:** stan0473 | **Helpee:** vslappyx | **Resolution:** Confirmed v2.x/v3 stability for agent development and explained versioning convention.

**Helper:** odilitime | **Helpee:** flykite, nusko_ | **Resolution:** Manually reposted content that was auto-deleted by Discord technical issues, though could not identify root cause.

**Helper:** igor.peregudov | **Helpee:** Community | **Resolution:** Shared security incident details about losing 100k ai16z tokens to phishing attack at bulkdao.co/allocation as a warning.

**Helper:** lemoncake03027 | **Helpee:** Community | **Resolution:** Provided comprehensive documentation and integration instructions for LemonCake payment plugin, with odilitime approving the implementation.

**Helper:** igor.peregudov | **Helpee:** stan0473 | **Resolution:** Confirmed v2 porting feasibility and inquired about stable release timing for planning purposes.

## Action Items

### Technical

- Port elisym to v3 following ecosystem merge (mentioned by stan0473)
- Investigate Discord auto-deletion issue affecting multiple users without audit log entries (mentioned by odilitime)
- Release stable version of v2, currently in alpha (mentioned by igor.peregudov)

### Features

- Implement proactive communication strategy to prevent exchange delistings during lawsuit (mentioned by hide.o.n)
- Process waitlist for late AI16Z to ELIZAOS token migrations (mentioned by odilitime)

### Documentation

- Document security warning about bulkdao.co/allocation phishing attack (mentioned by igor.peregudov)
- Create integration guide for LemonCake plugin with ElizaOS v2 (mentioned by lemoncake03027)