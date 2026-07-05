# elizaOS Discord - 2026-07-04

## Summary

### Project Status and Development Activity

The project remains actively developed with daily commits visible on GitHub. When questioned about whether the project was dead, community members confirmed ongoing development work and directed users to monitor the GitHub repository for proof of continued activity.

### Trading Agent Security and Risk Detection

A new plugin called cabal-hunter was introduced to address security vulnerabilities in trading agents. The plugin performs on-chain wallet graph analysis to identify malicious actors, risky token structures, bundled buyers, serial-rug deployers, and honeypot liquidity pools including freeze authority and token-2022 traps. This addresses a critical blind spot where price and volume data alone cannot detect dangerous token structures.

### LMstudio Integration

Discussion about connecting to LMstudio was resolved through the official plugin available in the elizaOS repository.

### Spam and Off-Topic Activity

The discussion channel experienced spam messages about rugpull schemes and job postings unrelated to technical development.

## FAQ

**Q: Is the elizaOS project still active?**
A: Yes, the project has daily development activity that can be verified by checking the GitHub repository for recent commits.

**Q: How do I connect to LMstudio?**
A: Use the official plugin available at github.com/elizaOS/eliza/tree/develop/plugins/plugin-lmstudio.

**Q: What is the cabal-hunter plugin?**
A: It is a trading agent plugin that performs on-chain wallet graph analysis to identify malicious actors, risky token structures, bundled buyers, serial-rug deployers, and honeypot LPs. It provides a verdict that agents can use to gate buy decisions.

**Q: How do I integrate the cabal-hunter plugin?**
A: Install it via npm as elizaos-plugin-cabal-hunter. Integration requires approximately 3 lines of code, and the first 100 scans are free.

**Q: What security risks does cabal-hunter detect?**
A: It detects holder clusters, funding sources, bundled buyers, serial-rug deployers, honeypot LPs, freeze authority, and token-2022 traps that price and volume data alone cannot identify.

## Help Interactions

**Helper:** om1d_sa
**Helpee:** nekiyk
**Resolution:** Confirmed the project is actively developed daily and directed the user to check GitHub for proof of ongoing development activity.

**Helper:** tcgkylee (self-resolved)
**Helpee:** tcgkylee
**Resolution:** Found the official LMstudio plugin independently at github.com/elizaOS/eliza/tree/develop/plugins/plugin-lmstudio.

## Action Items

### Technical

- Gather feedback from trading agent operators on additional signals to incorporate before buy decisions (mentioned by paulf76)

### Features

- Evaluate and test the cabal-hunter plugin for trading agent security (mentioned by paulf76)