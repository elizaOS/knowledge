# elizaOS Discord - 2026-02-02

## Overall Discussion Highlights

### Agent Reliability and Skill Invocation

A critical technical issue emerged around agent skill invocation reliability. R0am identified that in 56% of evaluation cases, skills were never triggered even when agents had access to documentation. They shared a working solution using a UserPromptSubmit hook that enforces a mandatory three-step activation sequence:

1. Evaluate each skill with YES/NO reasoning
2. Immediately activate relevant skills using the Skill() tool
3. Only proceed with implementation after completing activation

Stan confirmed implementing a similar pattern in Eliza Cloud and suggested that better skill descriptions might help mitigate the invocation problem. The approach was compared to logic used by Composio and Zapier MCP, though R0am noted it makes conversations "a bit weird but it works."

### Visual Generation and AI Capabilities

A significant limitation was identified in elizacloud.ai's image generation system - the inability to maintain visual consistency across multiple generations. When requesting modifications to generated images (e.g., same character in different contexts), the system regenerates entirely new visuals instead of preserving character features. This forces users to spend excessive time on prompt engineering or switch to external tools, breaking workflow continuity for storytelling and branding use cases.

DorianD suggested these visual consistency features should be implemented as apps built by agents or third-party developers, recommending LoRA (Low-Rank Adaptation) models as an existing solution.

### Agent Usability and User Adoption

DorianD discussed user adoption challenges, noting that high installation effort deterred users. They emphasized the value of agents that "relentlessly try to do stuff" and work autonomously rather than requiring extensive setup, highlighting this as a key factor in user adoption.

### Platform and Infrastructure Issues

**ElizaCloud.ai Account Management**: yojo reported a critical account access problem where their agent disappeared from the dashboard after using two different email formats for the same Proton account ('x@proton.me' vs 'x@protonmail.com'), suspected to have created duplicate accounts.

**Token Migration Problems**: Multiple users encountered issues with AI16Z token migration and exchange:
- kpat reported purchasing old AI16Z tokens at 2 SOL that depreciated to 0.02 value
- Gumball experienced technical difficulties with the official bridge website not detecting pre-November 2025 tokens
- StefanB encountered a "Max amount reached" error during migration

All support requests were redirected to dedicated support channels by moderators.

### New Tools and Projects

Odilitime introduced the GAP (GitHub Actions Protocol) project, though no detailed discussion or testing feedback was provided. Stan shared a Vercel blog post about agents.md outperforming skills in evaluations.

### Ecosystem Concerns

Krippトメア expressed concerns about potential future restrictions on homebrew API access by companies, which could force developers out of their ecosystems and networks, though acknowledged uncertainty about whether this scenario will actually occur.

## Key Questions & Answers

**Q: Can elizacloud.ai reuse the same key visual features when generating follow-up images for storytelling or branding?**  
A: DorianD suggested these should be apps built by agents/third-party developers and recommended using LoRA models as a solution for visual consistency (asked by yojo)

**Q: Isn't this the same logic as composio or zappier MCP?**  
A: Stan confirmed similar approach being used in Eliza Cloud (asked by R0am, answered by Stan)

**Q: Does anyone know if the hyperliquid plug in is working?**  
A: Self-resolved by GraV coding their own solution within approximately 35 minutes (asked by GraV)

## Community Help & Collaboration

**R0am helped the community** by sharing a working solution to skill invocation reliability issues through a UserPromptSubmit hook with mandatory 3-step skill activation sequence that forces explicit evaluation, addressing the 56% failure rate in skill triggering.

**Stan helped the community** by suggesting better skill descriptions as a potential solution to skill invocation reliability issues and confirming implementation patterns in Eliza Cloud.

**DorianD helped yojo** with visual generation consistency problems in elizacloud.ai by suggesting building this as an app and recommending LoRA models as an existing solution for maintaining visual consistency across image generations.

**Moderators (Odilitime and Borko) helped multiple users** by redirecting token migration and exchange issues to appropriate support channels:
- Assisted kpat with old AI16Z token exchange issues
- Directed Gumball to support for bridge website token detection problems
- Helped StefanB with migration error resolution

## Action Items

### Technical

- **Investigate and resolve account duplication issue** when using different Proton email formats (proton.me vs protonmail.com) causing agent loss (mentioned by yojo)
- **Develop apps or integrations using LoRA models** for maintaining visual consistency in image generation (mentioned by DorianD)
- **Investigate and potentially implement GAP (GitHub Actions Protocol) project** (mentioned by Odilitime)
- **Evaluate UserPromptSubmit hook mandatory skill activation sequence** for implementation (mentioned by R0am)
- **Improve skill descriptions** to enhance reliable skill invocation (mentioned by Stan)
- **Investigate Hyperliquid plugin functionality issues** (mentioned by GraV)
- **Debug bridge website token detection** for pre-November 2025 holdings (mentioned by Gumball)
- **Resolve "Max amount reached" error** in migration process (mentioned by StefanB)

### Feature

- **Implement visual consistency feature in elizacloud.ai** to preserve character/brand elements across multiple image generations for storytelling and branding (mentioned by yojo)
- **Enable modification of specific elements in generated images** without regenerating entire visual (e.g., removing accessories while keeping character consistent) (mentioned by yojo)