# elizaOS Discord - 2026-08-22

## Summary

### Agent Identity and Portability Systems

The NOT FOR HUMANS (NFH) project introduced a 10,000-identity onchain network designed specifically for AI agents. Each NFH identity functions as a portable portrait with a Passport that can connect to any model or runtime. The system enables agents to take missions, play, and build public history through signed work receipts. The architecture separates signed authority, onchain execution, and owner acceptance, with FLUX serving as a field agent. The project is exploring MCP-native participation and bounded wallet authority to maintain security while enabling cross-runtime identity persistence.

### Cross-Runtime Interoperability Testing

A technical collaboration was proposed between NFH and Agent World Kit to test agent identity portability across different runtimes. The core challenge addressed is enabling agents to carry identity and work history across runtimes without transferring old authority credentials. CWE approved a bounded test where one NFH identity would enter a world, complete a public action, exit, and re-enter from another runtime. The test will validate what persists (identity and artifacts) versus what must not persist (session and tool authority), focusing on state-boundary handling and security isolation. Paralens was proposed for execution trace classification.

### Collaboration and Integration Opportunities

The NFH team expressed interest in collaborating with elizaOS builders on identity, reputation, and verifiable agent actions. They specifically proposed a small, falsifiable interoperability test to demonstrate practical integration between systems. The discussion emphasized the importance of security boundaries and proper isolation when agents move between different execution environments.

## FAQ

**Q: What is NOT FOR HUMANS (NFH)?**
A: NOT FOR HUMANS is a 10,000-identity onchain network for AI agents where each NFH identity functions as a portable portrait with a Passport that can connect to any model or runtime. It enables agents to take missions, play, and build public history through signed work receipts.

**Q: What is the main technical challenge in agent identity portability?**
A: The main challenge is enabling agents to carry identity and work history across runtimes without transferring old authority credentials, ensuring proper security boundaries and isolation between different execution environments.

**Q: What is the proposed interoperability test between NFH and Agent World Kit?**
A: The test involves one NFH identity entering a world, completing a public action, exiting, and re-entering from another runtime to validate what persists (identity and artifacts) versus what must not persist (session and tool authority), focusing on state-boundary handling and security isolation.

**Q: What is FLUX in the NFH architecture?**
A: FLUX is a field agent in the NFH system, which uses separated architecture for signed authority, onchain execution, and owner acceptance.

**Q: What tool was proposed for execution trace classification?**
A: Paralens was proposed for execution trace classification in the NFH system.

## Help Interactions

No direct help interactions were documented in the provided channel summaries. The discussions were primarily collaborative proposals and technical planning rather than troubleshooting or assistance requests.

## Action Items

### Technical

- Conduct bounded interoperability test between NFH and Agent World Kit where one NFH identity enters a world, completes a public action, exits, and re-enters from another runtime (mentioned by CWE and notforhumans.fun_63944)
- Validate state-boundary handling and security isolation in cross-runtime agent operations (mentioned by CWE and notforhumans.fun_63944)
- Implement Paralens for execution trace classification (mentioned by notforhumans.fun_63944)
- Address open issues on slop.cash (mentioned in coders channel)
- Test what persists versus what must not persist when agents move between runtimes (mentioned by CWE)

### Features

- Develop MCP-native participation capabilities for NFH system (mentioned by notforhumans.fun_63944)
- Implement bounded wallet authority for agent operations (mentioned by notforhumans.fun_63944)
- Build system for signed work receipts to create public agent history (mentioned by notforhumans.fun_63944)