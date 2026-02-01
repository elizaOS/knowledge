## ElizaOS Token Utility and Communication

### Token Use Cases Identified

- The elizaOS token has one verified use case: paying gas fees in the Jeju network
- The Jeju network documentation shows 60+ onchain actions requiring gas fees
- Jeju network launch is expected in the latter half of 2026

### Communication Improvements Discussed

- Team acknowledged communication issues and discussed potential solutions
- Proposal made to create a research blog at research.elizaos.ai
- Blog would feature posts about ongoing work including Eliza agent towns experiments, Rust version of ElizaOS, and thoughts on decentralized LLM coordination
- Team discussed creating visual explanations of the project roadmap showing progression from framework to ElizaCloud to Jeju network
- Team confirmed they are working on token economy details

### Documentation Enhancements

- Core developers added comprehensive CLI coverage to documentation
- CLI reference documentation published at docs.elizaos.ai/cli-reference/overview
- Technical discussion covered creating NPM repositories programmatically
- Confirmed that Claude MCP can assist with NPM repository creation
- Confirmed that npm publish creates repositories automatically

## ElizaOS Project Development

### Bug Fixes Completed

- Resolved critical SQL error where database adapter was hardcoded to use dim_1536 column
- Fixed embedding dimension issue that caused errors when creating entities
- Corrected failure to respect USE_OPENAI_EMBEDDING configuration

### New Features in Development

- Opened pull request to introduce dynamic execution engine for version 2.0.0
- Development focused on testing context handling
- Feature currently in progress as part of ongoing development work