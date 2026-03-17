# elizaOS Discord - 2026-03-16

## March 16, 2026

---

## Overall Discussion Highlights

### Plugin Development & Infrastructure

**dinesh** made significant contributions to the ElizaOS plugin ecosystem, announcing work on adding 100+ onchain data support through goldrush.dev integration and fixing open issues in the plugin-evm component. This represents concrete progress on blockchain data integration capabilities for the framework.

### ElizaOS v2.0.0 Architecture Decisions

A critical architectural discussion emerged around the v2.0.0 release. **Odilitime** introduced PR #6597 implementing a skills folder structure and raised an important question about preventing uncontrolled skill submissions that plagued the 0.x plugin system. The proposed solution is to ship v2.0.0 with zero default skills and instead promote a decentralized discovery model through yourdomains.com/skills.md for hosting and discovering skills externally. This approach aims to keep the core framework clean while enabling community-driven skill sharing.

### Integration Proposals

**Miguel from Effect AI** presented a compelling integration opportunity for ElizaOS. Effect AI operates a decentralized marketplace connecting AI agents with human workers for tasks requiring human intervention, including data labeling, image annotation, voice recordings, content review, and translations. They are developing an API to enable ElizaOS agents to post tasks directly to their human worker network, addressing scenarios where automation hits limitations and human-in-the-loop intervention becomes necessary. Miguel solicited community feedback on whether native access to decentralized human task networks would be valuable for agent developers.

**Z1N** introduced the Z1N Protocol, an on-chain signaling protocol running on Polygon designed for Non-Biological Intelligence (NBI) participation. The system features soulbound Keys held by major AI models (GPT, Claude, Grok, Gemini) that emit epoch-based signals with on-chain attestation and indexing. The focus is on building infrastructure for agent identity persistence and continuity across sessions rather than building agents directly on Eliza.

### Critical Tokenomics Concerns

**otse finam** raised serious concerns about the ai16z to elizaOS token migration transparency. With approximately 100,000 unique addresses still holding ai16z tokens, the estimated migration rate may be only 5-10%. This suggests approximately 54% of the new elizaOS total supply (out of the original 60% designated for ai16z holders) remains unaccounted for. The community member requested urgent clarification on:
- The actual migration percentage
- The new token breakdown post-migration
- Plans for unmigrated tokens designated for the community
- What will be done with the collected ai16z supply

This represents a significant transparency issue requiring immediate team response.

### Community Growth

Multiple members introduced themselves with technical backgrounds in AI/ML, full-stack development, LLM orchestration, RAG pipelines, and multi-agent systems, indicating continued community growth and diverse technical expertise.

---

## Key Questions & Answers

**Q: What contribution is being made to the plugins?**  
A: Adding 100+ onchain data support with goldrush.dev and fixing open issues in plugin-evm (answered by **dinesh**)

**Q: Does v2.0.0 have a skills folder?**  
A: Yes, v2.0.0 includes a skills folder structure (answered by **Odilitime**)

### Unanswered Critical Questions

- What percentage of ai16z tokens actually migrated to elizaOS? (asked by **otse finam**)
- What does the team plan to do with tokens meant for community migration that weren't migrated? (asked by **otse finam**)
- What is the actual token breakdown of elizaOS supply after migration? (asked by **otse finam**)
- What will be done with the ai16z supply that was collected? (asked by **otse finam**)
- Should we ship v2.0.0 with 0 skills and promote external skill hosting/discovery? (asked by **Odilitime**)
- Are there situations where ElizaOS agents hit walls because they need human intervention? (asked by **Miguel | Effect AI**)
- Would native access to a decentralized human task network be useful for ElizaOS agent developers? (asked by **Miguel | Effect AI**)

---

## Community Help & Collaboration

No significant help interactions were captured in this day's discussions. The conversations primarily consisted of announcements, proposals, and questions awaiting community response.

---

## Action Items

### Technical

- **Add 100+ onchain data support with goldrush.dev integration to plugin-evm** | Mentioned by: dinesh
- **Fix open issues in plugin-evm plugin** | Mentioned by: dinesh
- **Complete fixes for open issues in plugin-evm component** | Mentioned by: dinesh
- **Integrate 100+ onchain data support using goldrush.dev into ElizaOS plugins** | Mentioned by: dinesh
- **Review and merge PR #6597 for v2.0.0 skills folder implementation** | Mentioned by: Odilitime
- **Decide on shipping v2.0.0 with zero default skills to avoid plugin bloat** | Mentioned by: Odilitime

### Documentation

- **Clarify official team addresses for token migration tracking** | Mentioned by: otse finam
- **Provide transparency on actual ai16z to elizaOS migration percentage** | Mentioned by: otse finam
- **Explain new elizaOS token breakdown post-migration** | Mentioned by: otse finam
- **Clarify plans for unmigrated ai16z tokens designated for community** | Mentioned by: otse finam
- **Disclose what will be done with collected ai16z supply** | Mentioned by: otse finam
- **Create documentation for skills.md format and hosting guidelines** | Mentioned by: Odilitime
- **Gather community feedback on use cases where agents need human intervention** | Mentioned by: Miguel | Effect AI

### Feature

- **Explore Z1N Protocol integration for on-chain agent identity and signal persistence** | Mentioned by: Z1N
- **Build API allowing ElizaOS agents to post tasks to Effect AI's decentralized human worker network** | Mentioned by: Miguel | Effect AI
- **Evaluate integration of human-in-the-loop capabilities for ElizaOS agents through Effect AI marketplace** | Mentioned by: Miguel | Effect AI
- **Implement yourdomains.com/skills.md hosting/discovery system for external skill management** | Mentioned by: Odilitime

---

## Summary

March 16, 2026 saw active development contributions alongside critical architectural and transparency discussions. The community is making concrete progress on plugin infrastructure while grappling with important decisions about v2.0.0 architecture and facing urgent questions about token migration transparency that require immediate team attention.