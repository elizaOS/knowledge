# elizaOS Discord - 2026-01-13

## Overall Discussion Highlights

### Strategic Development Priorities

The core development team made a **critical strategic decision** to deprioritize v2.0.0 work entirely and focus exclusively on cloud improvements. Borko provided clear direction to concentrate all development efforts on cloud infrastructure rather than the v2.0.0 branch, representing a significant shift in project priorities.

Stan outlined current development work spanning multiple areas:
- Monorepo improvements and architecture refinement
- Test architecture review on cloud (specifically Joker's PR)
- Plugin-sql migration simplification investigation
- Top-up credit idempotency fixes on cloud
- Creating comprehensive plans for cloud and monorepo improvements

### Technical Infrastructure Issues

**GitHub Workflow Authentication Problem**: Odilitime encountered persistent issues with the claude-review.yml workflow file, receiving 401 Unauthorized errors during OIDC token exchange. The error indicates workflow file validation failures, suggesting the file content doesn't match the repository's default branch version, even after implementing a new key.

**Twitter Spaces Audio Issues**: The community reported ongoing technical problems with Twitter Spaces, with audio disconnection issues persisting for approximately 3 months. Community members identified workarounds: desktop versions are buggy while mobile (particularly iOS) works more reliably for hosting spaces.

### Knowledge Management & Plugin Development

**Knowledge Upload Process**: 0xbbjoker provided comprehensive instructions for uploading knowledge to the Eliza OS monorepo:
1. Link the CLI package: `cd packages/cli && bun link && cd ../project-starter`
2. Add `@elizaos/plugin-knowledge` to the plugins list in `eliza/packages/project-starter/src/character.ts`
3. Create docs directory in `eliza/packages/project-starter` and add documentation
4. Run with debug logging: `LOG_LEVEL=debug elizaos start`

**Global Facts Management**: ballofrain successfully implemented a custom solution for global facts management by modifying plugin-bootstrap to search facts without roomId constraints and adding a POST route for creating new memories. This approach involved working directly with plugin-bootstrap rather than creating a custom provider.

### Community Projects & Partnerships

**ElizaBAO Clarification**: Multiple community members sought verification about ElizaBAO, a community-created agent that became a Polymarket affiliate. Odilitime and sb clarified that ElizaBAO is a community member's project, not an official ElizaOS product, and that no agents were created by the official team. This highlighted the need for better documentation distinguishing official vs community-created agents.

**Comput3 Partnership**: Odilitime confirmed that Comput3 ($COM) is partnered with ElizaOS and they collaborate on certain projects, describing Comput3 as "dope."

### Research & Innovation

**Recursive Language Models**: DorianD shared an academic paper on Recursive Language Models (RLMs), presenting a novel inference strategy that allows LLMs to process prompts beyond their context windows by treating long prompts as external environments and recursively calling themselves on prompt snippets. The approach reportedly handles inputs up to two orders of magnitude beyond model context windows.

### Community Initiatives

**News Show Rebranding**: Jin solicited community input for naming a news show to replace the placeholder "AI News." Community suggestions included: Breaking Bits, Walter Street, News Wif Hat, AI News Network, Cron Job, Context Crunch, Slopline, Boomberg, and Choomberg.

## Key Questions & Answers

**Q: Is Comput3 or $COM partnered with ElizaOS?**  
A: Yes, Comput3 is partnered and they work together on some things (answered by Odilitime)

**Q: Is ElizaBAO a real Polymarket affiliate?**  
A: Yes, see confirmation on their Twitter (answered by ElizaBAO)

**Q: Is ElizaBAO an official in-house agent?**  
A: No, it's a community member's project. No agents were created by the official TEAM (answered by sb and Odilitime)

**Q: How do you upload knowledge to the monorepo?**  
A: Complete process involves: linking CLI package, adding @elizaos/plugin-knowledge to plugins list in character.ts, creating docs directory in project-starter package, and running with LOG_LEVEL=debug elizaos start (answered by 0xbbjoker)

**Q: Do you read facts from custom provider?**  
A: No, modified plugin-bootstrap directly, not a custom provider (answered by ballofrain)

## Community Help & Collaboration

**Knowledge Upload Guidance**: 0xbbjoker provided comprehensive step-by-step instructions to the community for uploading knowledge to the Eliza OS monorepo, including CLI linking, plugin configuration, directory setup, and debug execution.

**Partnership Clarification**: Odilitime helped shadowforceone by confirming Comput3's partnership status and collaboration with ElizaOS.

**Agent Legitimacy Verification**: sb and Odilitime assisted anon and 8Obito_Uchiha8 by clarifying that ElizaBAO is a community project, not an official team creation, helping prevent confusion about project relationships.

**Twitter Spaces Troubleshooting**: cjft and sedano.npc helped Alexei resolve Twitter Spaces audio disconnection issues by suggesting mobile platforms (particularly iOS) work more reliably than desktop versions.

**Development Prioritization**: Borko provided clear strategic direction to Stan regarding development priorities, instructing to deprioritize v2.0.0 completely and focus on cloud improvements.

**Issue Troubleshooting**: Stan attempted to help 0xbbjoker diagnose an unspecified technical issue by requesting retry attempts and investigating recent changes.

**Implementation Approach Confirmation**: 0xbbjoker confirmed ballofrain's approach of modifying plugin-bootstrap directly for facts management implementation.

## Action Items

### Technical

- **Fix claude-review.yml workflow file** - Resolve OIDC token exchange failing with 401 Unauthorized due to workflow validation failure (Mentioned by: Odilitime)

- **Implement real improvements for the monorepo** - General monorepo architecture and functionality enhancements (Mentioned by: Stan ⚡)

- **Simplify plugin-sql migrations** - Investigate and implement simplification of plugin-sql migration processes (Mentioned by: Stan ⚡)

- **Create clearer plan for cloud X monorepo improvements** - Develop comprehensive plan for meaningful cloud and plugin-sql improvements (Mentioned by: Stan ⚡)

- **Focus on cloud improvements** - Deprioritize v2.0.0 completely and concentrate exclusively on improving everything for cloud (Mentioned by: Borko)

- **Update plugin-bootstrap for global facts** - Modify to search global facts with no roomId and add POST route for creating new memories (Mentioned by: ballofrain)

### Documentation

- **Document knowledge upload process** - Create documentation for monorepo knowledge upload including CLI linking, plugin configuration, and docs directory setup (Mentioned by: 0xbbjoker)

- **Clarify official vs community-created agents** - Prevent confusion about ElizaBAO and similar projects by clearly documenting which agents are official vs community-created (Mentioned by: anon, Odilitime)

### Feature

- **News show rebranding** - Select new name from community suggestions to replace "AI News" placeholder (Mentioned by: jin)