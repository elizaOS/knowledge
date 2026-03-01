# elizaOS Discord - 2026-02-28

## Overall Discussion Highlights

### VPS Orchestration & Infrastructure Projects

The **zeitgaist project** emerged as a significant technical contribution, representing a comprehensive VPS orchestration system. Developed by Meme Broker, this system integrates multiple technologies into a cohesive infrastructure management solution:

- **Conway terminals** serve as the infrastructure provisioning layer for spinning up VPS instances
- **OpenClaw** handles swarm orchestration for managing distributed systems
- **ElizaOS or OpenClaw** provides flexible communication handling between components

The project aims to create an automated swarm deployment system with minimal manual intervention. Two repositories were shared with the community:
- Main project: https://github.com/NewSoulOnTheBlock/zeitgaist
- Conway.tech plugin: https://github.com/NewSoulOnTheBlock/plugin-conway

Despite its technical capabilities, the developer expressed frustration about limited visibility and community engagement with the project.

### ElizaOS Implementation & Version Management

Technical questions arose regarding ElizaOS implementation best practices, specifically around:

- **Version selection**: Uncertainty between using "v2-develop" branch versus "alpha" channel for production implementations
- **Plugin ecosystem**: Active use of multiple plugins including memory, GitHub, Linear, Google Meet Cute, and Google Chat
- **Autonomous behavior**: Questions about implementing cron-like autonomous functionality within ElizaOS 2.0
- **Plugin viability**: Concerns about the testing status and reliability of "plugin-orchestrator" and "plugin-code"

These questions highlight ongoing challenges in navigating ElizaOS's evolving architecture and determining production-ready components.

## Key Questions & Answers

**Q: How should I get more attention for my project?** (asked by Meme Broker)  
**A:** Keep onboarding users one at a time (answered by Skinny)

**Q: What technology does the zeitgaist project use?** (asked by Meme Broker)  
**A:** It uses Conway terminals to spin up VPS's, OpenClaw for swarm orchestration, and either ElizaOS or OpenClaw for communication handling (answered by Meme Broker)

### Unanswered Questions Requiring Community Attention

- Should I use ElizaOS "v2-develop" instead of "alpha" channel? (asked by Julio Holon)
- For autonomous cron-like behavior, do you rely on some plugin, ElizaOS 2.0 autonomy, or did you code something separate? (asked by Julio Holon)
- Did you test "plugin-orchestrator" and "plugin-code"? (asked by Julio Holon)

## Community Help & Collaboration

**Skinny → Meme Broker** (Project Visibility Guidance)  
Context: Meme Broker sought advice on gaining attention for the zeitgaist VPS orchestration project  
Resolution: Skinny provided encouragement and suggested a gradual user onboarding approach, affirming the application's value and recommending patience in building the user base one person at a time

## Action Items

### Technical

- Determine appropriate ElizaOS version/branch (v2-develop vs alpha) for production use | Mentioned by: Julio Holon
- Investigate autonomous cron-like behavior implementation options in ElizaOS 2.0 | Mentioned by: Julio Holon

### Documentation

- Share zeitgaist GitHub repository (https://github.com/NewSoulOnTheBlock/zeitgaist) with community | Mentioned by: Meme Broker
- Share plugin-conway repository (https://github.com/NewSoulOnTheBlock/plugin-conway) for Conway.tech integration | Mentioned by: Meme Broker
- Document testing status and viability of plugin-orchestrator and plugin-code plugins | Mentioned by: Julio Holon

### Feature

- Promote and gain visibility for zeitgaist VPS orchestration project | Mentioned by: Meme Broker