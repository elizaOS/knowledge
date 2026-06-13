## ElizaCloud Sign-Up Issue and Ecosystem Integration

### Access Issue
- A user reported being unable to sign up for ElizaCloud due to an invitation-required error on the tenant
- Odilitime confirmed awareness of the issue, noting it had been passed to the team with someone actively working on a fix

### Ecosystem Integration Proposal
- A community member proposed connecting the elizaOS modular agent framework with peaq's machine operating system layer (peaqOS)
- The proposal referenced peaq's network of over 3 million devices using decentralized micro-services on a pay-per-task basis
- The suggestion involved building a native elizaOS plugin for peaq to enable real-world robots, fleets, and devices to use elizaOS as their primary AI backend for autonomous reasoning and decision making

---

## Eliza Cloud Apps Infrastructure Update

### Completed Work
- Ingress for the staging app node was enabled by implementing the Caddy front door in the app-node cloud-init (PR #8394)
- Production migration was streamlined by automating Headscale installation in the control-plane cloud-init (PR #8393)

### In-Progress Work
- One-shot workflow to remove orphaned apps-data-plane state entries (PR #8400)
- Dispatchable workflow to arm the apps daemon without manual SSH (PR #8398)
- Idempotent script for arming the apps-daemon (PR #8397)
- Dependency update for esbuild from 0.28.0 to 0.28.1 (PR #8399)
- Dependency update for pypdf from 6.10.2 to 6.12.0 (PR #8396)
- EvoLink support added to plugin-openai (PR #8395)

### Active Discussions
- Ongoing discussions around issue #8321 focus on resolving scaling and ingress gaps
- Staging verification and node replacement are planned before production deployment