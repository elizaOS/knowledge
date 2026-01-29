# elizaOS Discord - 2026-01-28

## Overall Discussion Highlights

### AI Agent Architecture & Development

The development team made significant progress on core infrastructure improvements. **jin** successfully merged MCP (Model Context Protocol) support and implemented dynamic tracking systems for GitHub repositories and Discord channels. This system automatically monitors active/inactive repos and new/archived channels, moving toward a self-maintaining configuration. The team emphasized improving developer onboarding by creating a bootstrapping skill that connects agents to knowledge repositories, documentation, and GitHub activity data, enabling agents to self-troubleshoot.

**DorianD** proposed building a small local model for intelligent request routing between available models based on complexity, cost, and load parameters. The current system alternates between small/large model selections from providers, but more sophisticated routing could optimize performance and costs.

The **clawdbot** project was analyzed as a successful pattern, highlighting useful features including markdown-based configuration files (BOOTSTRAP.md, SOUL.md), skills integration, and structured home directories. The consensus was that good documentation combined with skills can significantly improve agent performance.

### Technical Infrastructure & Tooling

**Embedding Provider Issues**: Multiple users reported problems with OpenRouter embeddings in the knowledge plugin, with only OpenAI working reliably. **Odilitime** clarified that Ollama, OpenAI, and OpenRouter are supported options, with plans to move embeddings completely to plugins in version 2.x.

**Development Tools**: **sedano.npc** reported issues with Cursor's AUTO mode breaking applications after 8+ hours of troubleshooting. **Odilitime** recommended using Composer 1 instead, which resolved deployment issues instantly.

**SSE Streaming**: Users encountered MIME_TYPE_MISMATCH errors when setting up SSE streaming. **Chucknorris** recommended switching from SSE to socket.io for better results, with issues traced to incorrect backend deployment configuration.

**Git Workflow**: **Odilitime** provided comprehensive guidance on basic Git operations, explaining commit vs pull request workflows, staging files, and branch management for OSS contributions.

### Standards & Tokenization

**satsbased** announced the upcoming ERC-8004 mainnet launch on Ethereum, scheduled for the week. This standard enables agent identity and reputation tracking onchain, allowing verification of whether AI agents are legitimate or "larps" (fake). The implementation aims to bring trustless tokenization to AI agents, positioned as a significant development for the ecosystem.

### Community Concerns & Governance

**DorianD** raised serious concerns about a "hot potato" style FOMO dapp, identifying it as a variation of the Bitcoin Potato game where developers receive vestings of the participation coin, allowing them to profit from sales while having unlimited supply to reset the game without cost. He warned of potential legal risks including lawsuits from participants and government investigation for illegal gambling operations, emphasizing the need for truly decentralized agents to avoid legal liability.

The conversation shifted to constructive feedback about the ElizaOS Twitter presence. **DorianD** recommended that the @elizaos account adopt more personality and "soul" similar to successful AI personas like clawd.atg.eth and pippin, rather than appearing dry and corporate. **Odilitime** responded positively, mentioning they're building a Twitter agent that could fulfill this role.

### Migration & Ecosystem

Multiple users reported that the migration site failed to detect ai16z tokens in Phantom wallets. **Hexx** clarified that ai16z migrated to ElizaOS, and holders from before the November snapshot at 11:40 UTC should use the migration portal to convert tokens. Concerns were raised about token value proposition for investors.

**timcoucou** proposed building a network similar to fetch.ai where members have AI avatars that automatically discover each other through similarity matching, conduct autonomous discussions, and send reports when interesting opportunities arise.

### Plugin Development

**Stan** made progress on the plugin-n8n-workflow (30% complete with regular commits) and coordinated OAuth specifications with team members. **Odilitime** identified a compatibility issue where plugin-anthropic 1.x doesn't work with the develop branch and later curated type fixes for a PR.

### Documentation & Knowledge Management

**sayonara** established a PR workflow for documentation updates through the elizaOS/docs repository. The team discussed renaming the elizaos.github.io repository, debating names like "leaders.elizaos.ai" or "leaderboard" but ultimately deciding against ranking implications in favor of showcasing contributor competencies and codebase evolution. **jin** emphasized treating documentation as code and prompt engineering, with knowledge bundled like game manuals.

## Key Questions & Answers

**Q: What's the difference between commit and pull request?**  
A: Commit is like save changes. Pull request is when working on someone else's OSS repo - you have to fork first. For your own repo, commit and push is sufficient. *(answered by Odilitime)*

**Q: Does OpenRouter embedding work with the knowledge plugin?**  
A: It kept giving errors; only OpenAI has worked so far. *(answered by YogaFlame)*

**Q: Are we forced to use OpenAI for embeddings now?**  
A: Ollama, OpenAI, or OpenRouter are supported. Version 2.x will drop embeddings in runtime and move it completely to plugins. *(answered by Odilitime)*

**Q: How do I fix MIME_TYPE_MISMATCH error with SSE streaming?**  
A: Need to explore routes and understand how Eliza server handles SSE. Switching to socket.io is much better than SSE. *(answered by Chucknorris | ONYX P9 NODE RENT)*

**Q: Does SEARCH_KNOWLEDGE action summarize doc fragments before returning?**  
A: No summarization, it's just a query to fragments returning three most similar. You can easily build custom action to prepare queries and make summaries. *(answered by 0xbbjoker)*

**Q: Should I use Cursor AUTO mode or Composer?**  
A: Don't use AUTO. Composer 1 is better than AUTO and lower cost. *(answered by Odilitime)*

**Q: What happened to ai16z?**  
A: Ai16z migrated to ElizaOS. If holding Ai16z before snapshot time 11:40 UTC November, migrate through the migration portal. *(answered by Hexx 🌐)*

**Q: Are you still the go to person for eliza.how?**  
A: You can send PR to https://github.com/elizaOS/docs and I will merge. *(answered by sayonara)*

**Q: What should we name the repository - leaders.elizaos.ai or leaderboard?**  
A: Neither - don't want it perceived as ranking people, philosophy is to see who is doing what and track codebase changes, will write an article to clarify. *(answered by jin)*

**Q: Does ElizaOS multiplex between models based on request complexity?**  
A: No, we have small/large model selection from a provider but just alternate between those two. *(answered by Odilitime)*

**Q: What is the connection between the FOMO dapp and the Bitcoin Potato game?**  
A: The developer picked a variation of "hot potato" mechanism, similar to the original Bitcoin Potato game from the GitHub repository ripper234/Bitcoin-Potato. *(answered by DorianD)*

**Q: What legal risks does the developer face?**  
A: Potential lawsuits from participants and government investigation for illegal gambling, with possibility of profit clawback from gambling commissions. *(answered by DorianD)*

## Community Help & Collaboration

**Odilitime** provided extensive Git workflow guidance to **Irie_Rubz**, explaining commit vs pull request workflows, staging processes, and confirming successful pushing to main branch.

**Chucknorris | ONYX P9 NODE RENT** helped **sedano.npc** resolve MIME_TYPE_MISMATCH errors with SSE streaming by recommending a switch from SSE to socket.io for better performance.

**0xbbjoker** assisted **Victor Creed** in understanding that SEARCH_KNOWLEDGE action doesn't summarize results, and suggested building custom actions with LLM queries and summaries.

**Odilitime** helped **sedano.npc** resolve Cursor AUTO mode issues that broke the application after 8+ hours of troubleshooting by recommending Composer 1, which fixed redeployment instantly.

**jin** helped the community understand embedding requirements by clarifying that Ollama, OpenAI, and OpenRouter are all supported, with v2.x moving embeddings to plugins.

**Hexx 🌐** assisted **Watcoinerist** by explaining the ai16z to ElizaOS migration and providing instructions for holders before the November snapshot.

**sayonara** directed **Kenk** to send PRs to https://github.com/elizaOS/docs for documentation updates and tutorial publishing.

**DorianD** provided constructive feedback to the ElizaOS team about improving Twitter presence by adopting more personality and soul similar to successful AI personas.

**satsbased** shared detailed positioning strategy with **MATTIOBOY 🇦🇺**, including hyperscape, ERC-8004 launch expectations, and ecosystem tracking approach.

## Action Items

### Technical

- Fix plugin-anthropic 1.x compatibility with develop branch *(Odilitime)*
- Open PR with curated type fixes *(Odilitime)*
- Complete plugin-n8n-workflow development (currently 30% done) *(Stan ⚡)*
- Implement OAuth specifications in coordination with team members *(Stan ⚡)*
- Implement monthly workflow to review and update config based on active/inactive repos *(jin)*
- Test OpenRouter embeddings to verify if issues persist across different users *(jin)*
- Investigate and fix OpenRouter embedding errors in knowledge plugin *(YogaFlame)*
- Complete plugin-autonomous to reduce costs of running multiple agents experiencing same messages *(Odilitime)*
- Integrate Eliza work into ONYX project (relatively heavy work) *(Chucknorris | ONYX P9 NODE RENT)*
- Create custom SEARCH_KNOWLEDGE action with LLM query preparation and summarization *(0xbbjoker)*
- Investigate and fix migration site not detecting ai16z tokens in Phantom wallet *(ai16zbags, Never Broke Again (NBA))*
- Monitor ERC-8004 mainnet launch on Ethereum for agent identity and reputation onchain verification *(satsbased)*
- Ensure AI agents are fully decentralized to avoid legal liability for operators *(DorianD)*

### Feature

- Build Twitter agent with engaging personality for ElizaOS account *(Odilitime)*
- Implement Eliza AI personality on X.com/elizaos account incorporating projective anime elements and soul similar to clawd.atg.eth *(DorianD)*
- Build small local model for intelligent request routing between available models based on complexity, cost, and load *(DorianD)*
- Implement more skills integration following clawdbot patterns *(jin)*
- Build network where AI avatars meet through similarity searching with automatic discussion reports *(timcoucou)*
- Create bootstrapping skill that connects to docs, knowledge repo, ai-news and hiscores *(jin)*
- Implement automatic download of latest knowledge as part of default new user experience after connecting API key or local gateway *(jin)*
- Rename elizaos.github.io repository to better reflect purpose *(jin)*
- Build AI avatar network with automatic similarity matching, autonomous discussions, and meeting pre-qualification system similar to fetch.ai *(timcoucou)*

### Documentation

- Move quick start higher up in docs at https://docs.elizaos.ai/llms.txt *(jin)*
- Write article clarifying philosophy behind the hiscores/tracking system *(jin)*
- Publish 8004-related plugin tutorial *(Kenk)*
- Clarify token value proposition for investors *(Taco)*