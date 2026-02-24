# elizaOS Discord - 2026-02-23

## Overall Discussion Highlights

### Major Organizational Restructuring and Revenue Focus

The most significant development was a major strategic pivot announced in the core-devs channel. Due to financial constraints, the organization is restructuring to focus on immediate revenue generation through a venture model with small, focused teams working on fixed budgets rather than traditional daily standups.

**Revenue-Generating Projects Launching:**

- **Agent Arena Duel Betting in Hyperscape** - Launching next week with 2% + 1% fee structure
- **OTC Agent at tradingdesk.fun** - 1% fee model, maintained by 's'
- **Milady** - Free/open source project designed to drive users to Eliza Cloud (primary revenue source)
- **Babylon** - Crypto trading platform with 1% fees, ramping from 1% to 100% user rollout
- **Eliza App** - Shares backend with hosted Milady, needs onboarding completion to begin charging
- **Amelia's subscription-focused project**

The company has received acquisition offers but leadership prefers achieving profitability first for better valuation. The strategy emphasizes shipping working products immediately, avoiding distractions, and making quick kill decisions for underperforming projects.

### Technical Development Updates

**Backend Architecture:** Shadow from Eliza Wakes Up is collaborating on backend work for both Eliza app and Milady, offering two agent options: "workflow" and "full sandbox" modes.

**Roadmap Priorities:** After Milady ships, focus shifts to Babylon/Hyperscape integration, followed by Jeju (a network for agents).

### Technical Optimization Discussions

In the core-devs channel, there was discussion around MCP loading and METATOOL search actions optimization. Odilitime identified that token usage issues primarily stem from recent messages and reflections collecting excessive data rather than from actions themselves. The metatool pattern was considered for providers, though concerns about implementation delays were raised.

### Community Support and Plugin Recommendations

In the discussion channel, guidance was provided on image generation plugins for agents. The plugin-bootstrap package was recommended as it includes an image generation action, providing an alternative to the older plugin-image-generation package.

### Migration and Security Concerns

Community members expressed confusion about token migration processes, with concerns about scam risks. There were warnings about avoiding DM links and fake ticket systems used by scammers.

## Key Questions & Answers

**Q: Is plugin-image-generation okay to use, or are there better alternatives?**  
A: plugin-bootstrap has an image generation action (answered by Odilitime)

**Q: Could the metatool pattern work with providers?**  
A: Possible but the delay might not be worth it, may need to implement eventually (answered by Odilitime)

### Unanswered Questions

- What are the budgets per project?
- Is v2.0.0 still important given it's not listed as a priority project?
- Are you and Shadow taking over cloud or what exactly?

## Community Help & Collaboration

**Stan ⚡ assisting Odilitime** - Offered to share optimization work around MCP loading and METATOOL search actions, suggesting moving the solution into the framework. While Odilitime identified his specific issue was with messages/reflections rather than actions, the collaboration demonstrated willingness to share technical solutions.

**Odilitime assisting BinaryCookies** - Provided plugin recommendation for image generation, directing them to plugin-bootstrap which includes an image generation action.

**Omid Sa assisting de_cryptkeeper** - Clarified community member status and warned about scam prevention, specifically advising not to trust DM links or open ticket links.

## Action Items

### Technical

- **Launch Agent Arena Duel Betting in Hyperscape v1 with 2% + 1% fees next week** - Mentioned by s
- **Ramp Babylon from 1% to 100% user rollout and build crypto trading platform version** - Mentioned by s
- **Complete Eliza App onboarding flow and billing to start charging customers** - Mentioned by s
- **Ship Milady to drive users to Eliza Cloud for revenue** - Mentioned by s
- **Integrate Eliza app with Babylon and Hyperscape after Milady ships** - Mentioned by s
- **Build Jeju network for agents** - Mentioned by s
- **Complete backend work with Shadow for workflow and full sandbox agent options** - Mentioned by s
- **Investigate plugin-bootstrap for image generation action implementation** - Mentioned by BinaryCookies

### Feature

- **Consider moving MCP loading and METATOOL search solution into framework** - Mentioned by Stan ⚡

---

*Note: This summary reflects a pivotal moment in the organization's direction, with a clear shift from development-focused activities to revenue-generating product launches. The emphasis on immediate shipping, budget constraints, and profitability indicates a critical phase in the company's evolution.*