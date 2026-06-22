## ElizaOS Community Discussion - June 15, 2026

### Development Update
- Odilitime confirmed all work has been moved to the Eliza repository
- Community members expressed interest in testing current builds

### Scam Warning
- A suspicious message circulated instructing users to connect wallets via a third-party dApp using a so-called Blockchain Diagnostics Tool
- Community members identified and flagged the message as a scam
- The user confirmed no official migration link was found and that the migration window had closed

### Developer Opportunity - Intuition x MetaMask Bounty Missions
- Collaboration announced between Intuition and MetaMask using the ERC-7710 Delegation Framework and Intuition Knowledge Graph
- Five bounty missions totaling 7500 USDC:
  - M09: Tutorial mission - 1000 USDC
  - M10: Liquid Democracy proof of concept - 1000 USDC
  - M11: Production-ready Liquid Democracy implementation - 3000 USDC (gated on M10 completion)
  - M12: Intuition Skill Delegation - 500 USDC
  - M13: Caveat Enforcers Registry - 2000 USDC
- Applications open at intuition.box/missions with screening beginning June 22
- Joint Twitter Space scheduled for June 16 at 11am ET with MetaMask Dev
- Poster expressed interest in collaborating with elizaOS

### Community Activity
- A project bridging crypto and non-crypto users was shared with a Telegram reservation link
- Ruby Trivia game results shared, with scores of 9/10 and 5/10 reported by community members

---

## Eliza Cloud Apps Platform - Launch Stabilization Update

### Completed Work
- Enabled build-from-repo functionality allowing the platform to build user repositories directly
- Activated APPS_DEPLOY_ENABLED on the arm deployment path
- Automated CI/CD for the headscale cloud service
- Standardized Steward OAuth PKCE across all login surfaces, resolving production login failures
- Updated model catalog to use healthy Cerebras defaults for improved gateway stability
- Implemented idempotent container-billing cron job to prevent double-debiting
- Adjusted organization credit balance defaults to $0 to stop unintended free credit allocation
- Improved CI efficiency with label-gated path classifiers for expensive test lanes

### Pull Requests in Progress
- Enabling APPS_DEPLOY_ENABLED for production
- Fixing staging frontend proxy alias
- Configuring HEADSCALE_PUBLIC_URL via CI
- Wiring apps deployment and tenant-DB end-to-end tests into CI
- Adding optional per-tenant database support to the edad example app

### Platform Status
- Team is in final stages of staging-to-production cutover
- Core platform features verified and ready for deployment
- edad app serving as primary test subject for Cloud Apps scaling and ingress discussions
- Two critical blockers identified: NPM_TOKEN permissions issue (#8428) and Cloud 10-user launch tracking issue (#8434)