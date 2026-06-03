## ElizaOS Ecosystem Clarification

### Ecosystem Components

Stan outlined the four main components of the ElizaOS ecosystem:

- **ElizaOS** - The core framework for building agents
- **ElizaCloud** - The infrastructure layer that hosts and runs pre-packaged agents
- **Milady** - A consumer-facing UI that uses agents to help manage personal tasks and device interactions
- **Waifu** - A side project where agents can compete and manage their own economies, running entirely on ElizaCloud as its hosting layer

### Kamino Plugin Development

- Developer Navneet Sahu proposed a comprehensive Kamino plugin for ElizaOS covering lending, borrowing, automated liquidity vaults, yield farms, and limit orders
- Stan confirmed all plugins now live in the elizaOS/eliza repository and directed Navneet to fork and build on the develop branch
- Community members noted the plugin would give ElizaOS agents access to meaningful DeFi actions beyond simple information retrieval
- Navneet confirmed a careful, deliberate approach and has written initial actions

---

## Eliza Project Development: June 2, 2026

### Cloud and Infrastructure

- Enabled per-agent web UI by default for improved sandbox interaction
- Isolated the Steward tenant for staging with service-key provisioning
- Fixed billing logic to ensure token budget guarantees for reasoning models

### Desktop Performance

- Eliminated first-use stalls through deferred model warmup
- Accelerated app initialization via a tray-first startup approach with decoupled UI spawning
- Made fresh-clone builds more reliable through automated workspace package installation

### Core Orchestrator Improvements

- Closed race conditions that caused duplicate replies
- Refined message routing to prioritize coding tasks
- Suppressed leaked JSON envelopes in user replies
- Removed approximately 919 lines of dead voice subsystem code

### Resolved Issues

- Cloud and inference stability regressions closed
- Orchestrator and runtime leak issues resolved
- Fresh-clone build blockers addressed and closed

### Contributors

- NubsCarson recognized for providing critical architectural analysis on sub-agent routing issues