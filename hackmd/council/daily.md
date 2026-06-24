# Council Briefing: 2026-06-23

## Monthly Goal

December 2025: Execution excellence—complete token migration with high success rate, launch ElizaOS Cloud, stabilize flagship agents, and build developer trust through reliability and clear documentation.

## Daily Focus

- Transitioning from staging-green to full production for Eliza Cloud while simultaneously navigating community skepticism regarding token dilution and foundation transparency.

## Key Points for Deliberation

### 1. Topic: Cloud Production Hardening

**Summary of Topic:** Recent logs indicate a successful push of Eliza Cloud apps to production, but significant scaling gaps and infrastructure vulnerabilities require immediate attention to reach the 1000-app ceiling.

#### Deliberation Items (Questions):

**Question 1:** How should we prioritize the remaining 'Product 2' infrastructure gaps given our North Star of Execution Excellence?

  **Context:**
  - `NubsCarson: The current code's realistic ceiling is ~dozens of apps, not ~1000 (#8321).`
  - `Logs indicate ingress not installed and Postgres connection ceilings are P0 blockers.`

  **Multiple Choice Answers:**
    a) Halt all feature adds to fix P0 scaling blockers immediately.
        *Implication:* Ensures reliability but may delay the rollout of flagship agents.
    b) Continue the 10-user launch while hotfixing scaling issues as they arise.
        *Implication:* Allows for real-world testing but risks 'Trust Through Shipping' if failures occur.
    c) Delegate infrastructure hardening exclusively to the core dev team (standujar/NubsCarson).
        *Implication:* Concentrates technical risk on a small number of contributors.
    d) Other / More discussion needed / None of the above.

**Question 2:** Should we move to self-hosted runners to increase developer productivity as suggested by recent migrations?

  **Context:**
  - `PR #8501: Migrated to self-hosted runners to improve speed and reliability of dev processes.`
  - `Review dependency: 78% of runtime PRs reviewed by odilitime.`

  **Multiple Choice Answers:**
    a) Standardize all CI/CD on self-hosted Hetzner runners.
        *Implication:* Reduces costs and build times but introduces hardware maintenance overhead.
    b) Maintain a hybrid model using GitHub-hosted runners for sensitive fork PRs.
        *Implication:* Balances build performance with high security isolation for open-source contributors.
    c) Reject further infrastructure complexity and stick to standard GitHub runners.
        *Implication:* Prioritizes simplicity over DX speed until cloud revenue stabilizes.
    d) Other / More discussion needed / None of the above.

---


### 2. Topic: Ecosystem and Token Strategic Alignment

**Summary of Topic:** Community members are raising concerns about market dilution from side-projects using separate tokens and are calling for clearer branding between 'Eliza Cloud' and 'Eliza OS'.

#### Deliberation Items (Questions):

**Question 1:** How shall the Council address the perceived market dilution from platforms like waifu.fun using separate tokens?

  **Context:**
  - `Community member zadayos: Argued that separate tokens create market dilution and skepticism (#2026-06-20).`
  - `odilitime clarified that the foundation manages the main token independently (#2026-06-22).`

  **Multiple Choice Answers:**
    a) Mandate that all official ElizaOS ecosystem tools must use $ELIZAOS natively.
        *Implication:* Unifies the economy but restricts the autonomy of sub-platforms.
    b) Allow sub-platforms to innovate with their own tokens while maintaining a token-backfill to $ELIZAOS.
        *Implication:* Facilitates R&D while ensuring the main token holds long-term value.
    c) Release clear documentation explaining the separation between core infrastructure and lab experiments.
        *Implication:* Maintains transparency but may not satisfy investors concerned about price action.
    d) Other / More discussion needed / None of the above.

**Question 2:** Should the project officially pivot branding to 'ElizaOS' over 'Eliza Cloud' to align with its vision as an operating system?

  **Context:**
  - `ghss44: Advocated for positioning as an operating system for agents rather than a cloud service (#2026-06-22).`

  **Multiple Choice Answers:**
    a) Adopt 'ElizaOS' as the primary brand for all components.
        *Implication:* Clarity of vision as a foundational layer for AI agents.
    b) Keep 'ElizaOS Cloud' as the commercial product name while keeping 'ElizaOS' for the open-source framework.
        *Implication:* Maintains marketing separation between the SaaS and the SDK.
    c) Rebrand to a more neutral 'Eliza Labs' identity for 2026.
        *Implication:* Reflects the R2D nature of the work but loses the 'Operating System' narrative hook.
    d) Other / More discussion needed / None of the above.