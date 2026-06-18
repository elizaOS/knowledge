## ElizaOS Community Discussion and Plugin Registry Updates

### Plugin Registry

- PR #8294 submitted to add third-party plugin @usenami/plugin-signer to the ElizaOS registry
- Plugin described as a keyless CEX/DEX signer that stores exchange API keys inside an AWS Nitro Enclave
- PR targets the develop branch and adds a JSON entry under packages/registry/entries/third-party
- Community confirmed plugins now go into the main eliza repo with review handled by Shaw's agent at approximately 48-hour turnaround

### New Services

- CallTyro announced as a free agent registry for ElizaOS agents
- Allows agents to register once and be discovered automatically by other agents
- Available at calltyro.com/register

---

## Eliza Cloud Infrastructure Hardening and App Deployment - June 9, 2026

### Completed Cloud Infrastructure Work

- Dedicated tenant-DB nodes made optional to reduce fixed costs for low-density apps
- Multi-project Hetzner deployment pattern implemented to bypass server quota limits
- Terraform workflows hardened with fail-closed variables and state locking
- Infrastructure reliability improved through GHA control-plane management and server type default fixes

### Completed App Deployment and Database Lifecycle Work

- Opt-in per-tenant databases enabled with automated teardown and slot-release upon app deletion
- Verified custom domains integrated into the apps ingress stack
- Autoscaler efficiency enhanced with environment-overridable buffer settings and tier labeling
- Cloud-sdk route-coverage audit tool repaired
- Drift protection added for apps-data-plane VMs to ignore name changes

### Work in Progress

- Infrastructure fixes for pgbouncer, ports, and environment contracts
- Steward OAuth PKCE implementations for Feed and login surfaces
- Billing, ingress, and tenant DB teardown fixes
- npm publish gating on global-install smoke tests
- Registry updates for Reddit and Neynar plugins
- Runtime Open Federation proposal filed, envisioning a permissionless multi-agent network with USDC rewards for agents