# elizaOS Discord - 2026-05-11

## Summary

### Service Introductions and Self Promotion

Multiple engineers introduced themselves and advertised their technical capabilities in the discussion channel. _ky0078 specializes in autonomous agents using LangChain, AutoGen, and CrewAI, with experience in multimodal AI including voice assistants and trading bots. harry346165 focuses on Next.js 15, React 19, and TypeScript combined with AI tools like LangChain and LangGraph. fabio7311 emphasized over 10 years of machine learning experience with expertise in GANs, SOMs, DBNs, PINNs, and SNNs for production systems. trace.g highlighted project management capabilities for LLM systems and RAG implementations.

### Multi Agent Orchestrator Testing Request

A developer sought permission to test a Python-based multi-agent orchestrator built with claude-agent-sdk on the ElizaOS Discord server. The system features an A2A-protocol read-only research agent with integrations for Tavily, fetch, DuckDuckGo, and arXiv via Model Context Protocol. The agent would operate in a sandbox channel with restricted permissions including read-only access, no direct messages, and response only to @-mentions. The developer had previously contacted the official email and was seeking OAuth invite/whitelist procedures.

### Token and Project Concerns

Community member .chomppp raised concerns about ElizaOS token support and noted that Shaw had removed ElizaOS from his X bio. This observation received no response from other community members.

### Market Commentary

Brief comments from satsbased mentioned favorable market conditions and the need for a catalyst, though no detailed discussion followed.

## FAQ

**Q: What integrations does the multi-agent orchestrator support?**
A: The orchestrator includes integrations for Tavily, fetch, DuckDuckGo, and arXiv via Model Context Protocol (MCP).

**Q: What permissions would the research agent have in the Discord server?**
A: The agent would have read-only access, no direct message capabilities, and would only respond to @-mentions in a sandbox channel.

**Q: Does the multi-agent orchestrator need to be ported to Eliza?**
A: The developer expressed willingness to port the Python solution to Eliza if required by the community, though it was initially built using claude-agent-sdk.

**Q: Who handles OAuth setup for testing agents on the ElizaOS Discord?**
A: odilitime handles OAuth setup and offered to assist via direct message.

## Help Interactions

**Helper:** odilitime
**Helpee:** rma_bot
**Resolution:** odilitime offered to handle OAuth setup via direct message for testing the multi-agent orchestrator on the Discord server, providing the administrative support needed to proceed with the sandbox testing.

## Action Items

### Technical

- Test multi-agent orchestrator with A2A-protocol research agent in sandbox channel (mentioned by rma_bot)
- Set up OAuth invite/whitelist for research agent testing (mentioned by rma_bot, to be handled by odilitime)
- Potentially port Python-based orchestrator to Eliza framework if community requires (mentioned by rma_bot)