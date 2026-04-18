# elizaOS Discord - 2026-04-12

## Summary

### Tokenomics and Communication Strategy

The ElizaOS project faced significant concerns about tokenomics clarity and communication effectiveness. chulylooly emphasized that vague tokenomics kill projects quickly and stressed the critical need for clear messaging that connects dots for investors. joshisgood77 questioned the connection between the product and token, which odilitime acknowledged exists but admitted people don't like how it's connected. odilitime took responsibility for communication failures and announced plans for a call with Shaw next week to restructure Discord and X account management. rainman1001 suggested allowing trusted community members to handle social media admin, citing success on another project.

### Exchange Listing and Trading Volume

A BitGet delisting situation emerged during discussions. ellince8 explained the delisting was due to low trading volume (10-50k per day) rather than scam concerns, noting that market makers need sufficient trading fees to maintain listings. The situation highlighted the importance of maintaining adequate trading activity for exchange relationships.

### Local Model Implementation Challenges

0xnemian encountered persistent JSON parsing errors with Ollama text generation, showing repeated failures in XML parsing and missing required fields including thought and actions across multiple retry attempts. The error manifested as 'Invalid JSON response' with the system unable to extract structured data from LLM responses. odilitime provided recommendations for local model parameters, suggesting Gemma, gptoss, and Qwen as working alternatives, and mentioned ongoing development of improved technology for local model support.

### Quantum-Safe Authentication Integration

huzaiii_founder presented and announced a quantum-safe authentication gateway for AI agents on Solana using ML-KEM-768 (NIST FIPS 203). The production-ready PQC (Post-Quantum Cryptography) authentication layer for ElizaOS agents is available via the bridgebase-sdk, offering quantum-safe identity with minimal integration code. The solution is deployed and accessible via Railway with live demo and SDK available.

### Project Merchandise and Branding

The team discussed merchandise initiatives, with baogerbao creating elizaOK merch using elizacloud. This represented community-driven branding efforts for the project.

### Migration Status

odilitime confirmed that the migration period from ai16z to elizaos has ended, marking a significant transition milestone for the project.

## FAQ

**Q: Why was ElizaOS delisted from BitGet?**
A: The delisting was due to low trading volume (10-50k per day) rather than scam concerns. Market makers need sufficient trading fees to maintain listings, and the current volume was insufficient.

**Q: What is the connection between the ElizaOS product and token?**
A: According to odilitime, a connection exists but people don't like how it's currently structured. The team acknowledged this as a communication issue that needs addressing.

**Q: Which local models work well with ElizaOS?**
A: odilitime recommended Gemma, gptoss, and Qwen as working alternatives for local model implementation.

**Q: Has the migration from ai16z to elizaos ended?**
A: Yes, odilitime confirmed that the migration period has ended.

**Q: What is the quantum-safe authentication solution for ElizaOS?**
A: huzaiii_founder developed a PQC authentication layer using ML-KEM-768 (NIST FIPS 203) available via bridgebase-sdk, providing quantum-safe identity for AI agents on Solana with minimal integration code.

## Help Interactions

**Helper:** odilitime
**Helpee:** 0xnemian
**Resolution:** Provided recommendations for local model parameters, suggesting Gemma, gptoss, and Qwen as working alternatives to address JSON parsing errors with Ollama. Also mentioned ongoing development of improved technology for local model support. Inquired about branch specifics for further investigation.

**Helper:** ellince8
**Helpee:** Community (regarding BitGet delisting)
**Resolution:** Explained that the delisting was due to low trading volume (10-50k per day) rather than scam concerns, clarifying that market makers need sufficient trading fees to maintain listings.

**Helper:** odilitime
**Helpee:** Community (regarding communication issues)
**Resolution:** Took responsibility for communication failures and announced plans for a call with Shaw next week to restructure Discord and X account management.

## Action Items

### Technical

- Develop improved technology for local model support to address JSON parsing and structured data extraction issues (mentioned by odilitime)
- Investigate branch specifics related to Ollama text generation errors (mentioned by odilitime)
- Integrate bridgebase-sdk for quantum-safe authentication in ElizaOS agents (mentioned by huzaiii_founder)

### Features

- Implement quantum-safe authentication gateway for AI agents on Solana using ML-KEM-768 (mentioned by huzaiii_founder)

### Documentation

- Clarify tokenomics messaging and create clear documentation connecting product to token value (mentioned by chulylooly)
- Restructure Discord and X account management following call with Shaw (mentioned by odilitime)
- Consider allowing trusted community members to handle social media admin responsibilities (mentioned by rainman1001)