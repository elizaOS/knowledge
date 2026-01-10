# elizaOS Discord - 2026-01-09

## Overall Discussion Highlights

### Platform Architecture & Development

**Eliza 2.0 Major Redesign Proposal**

Shaw proposed a significant architectural overhaul for Eliza 2.0, eliminating the current API, server, CLI, and projects structure. The new design would feature a Claude-friendly documented runtime with consistent abstractions across TypeScript, Rust, and Python, including FFI plugin interoperability between languages. Shaw indicated they already have a working port on a branch, suggesting this is an active development effort rather than just a proposal.

**Plugin Interoperability Initiative**

Jin initiated a cross-channel collaboration to convert ElizaOS plugins into skills, aiming to achieve interoperability between ElizaOS and other agent tools. The focus targets popular plugins including Discord and blockchain integrations. R0am volunteered to collaborate, sharing their technical approach: structuring skills as folders containing .md instructions and deterministic scripts in any language. A key technical challenge identified was getting Claude to use skills implicitly rather than explicitly, which R0am claims to have solved using hooks.

**Multi-Step Skill Workflows**

Agent Joshua described challenges with building effective workflows for chaining skills together. Their example workflow involved: specialized skill collecting user information → PDF skill filling out forms → filesystem skill storing files with summarization → PDF skill displaying results. R0am referenced a successful implementation of linked subagents from the ClaudeCode subreddit as a potential solution.

### Cloud Infrastructure & Services

**Eliza Cloud Status and Updates**

ElizaBAO reported operational failures with the elizacloud app creator feature. Cjft confirmed the feature is functional but noted it's an early-stage implementation. Later discussion revealed the cloud platform received updates including a new billing page for credit top-ups, indicating active development of the hosted infrastructure. Stan mentioned ongoing cloud cleanups and optimizations.

**Solana 8004 Standard Integration**

Kenk announced an upcoming Twitter Space scheduled for January 13th at 7pm UTC with Solana Foundation, PayAI, and Quantu to discuss the 8004 standard and its integration with Eliza Cloud. Jin highlighted significant academic interest in this standard, noting Stanford cryptographer Dan Boneh's involvement, suggesting important cryptographic implications for the protocol.

### AI Agent Applications & Use Cases

**Mental Health Monitoring Integration**

DorianD shared information about the "Dopa One" AI algorithm by Behavidence, which monitors brain dopamine levels through mobile phone and wearable device interactions to detect mental health fluctuations related to ADHD, depression, and anxiety. He proposed integrating this capability into a future ElizaOS Phone app, noting that AI agents could monitor users' mental health while they interact with the app. DorianD observed that 5 years of LLM progress and improved smartwatch technology could make dopamine monitoring more feasible now.

**Computer Vision Classification Agents**

DorianD proposed a specific AI agent application for image-based classification. Jin provided a technical starting point using the DeepFace library (serengil/deepface on GitHub) for implementing computer vision-based classification agents.

### Technical Exploration

**Advanced AI Model Testing**

R0am explored Minimax M2's "interleaved thinking" approach for long-running tasks and reported a successful VPS deployment running Claude Code with Kimi K2 accessible via Happy on iOS.

### Community & Events

**Jeju Platform Context**

DorianD explained that Jeju is a Korean island typically used for testing new technology before Korea-wide rollout, providing context for the platform naming.

## Key Questions & Answers

**Q: Is the elizacloud app creator functioning?**
- Asked by: ElizaBAO
- Answered by: cjft
- Answer: Yes, it's working but it's an early feature

**Q: Why is the platform named JEJU?**
- Asked by: Skullcross
- Answered by: DorianD
- Answer: Jeju is a Korean island where they usually use for running new stuff before they roll out the tech in the rest of Korea

**Q: What does it take to convert elizaos plugins into skills and make them interoperable?**
- Asked by: jin
- Answered by: R0am | tip.md
- Answer: It's a folder with .md instructions and tools in scripts (whatever language) to make them deterministic. The real challenge is getting Claude to use skills without saying explicitly, but there's a solution using hooks

**Q: How do you build effective workflows to ensure skills can be called back and forth?**
- Asked by: Agent Joshua ₱ | TEE
- Answered by: R0am | tip.md
- Answer: Reference to a successful implementation of linked subagents from Reddit ClaudeCode community

### Unanswered Questions

- **How do I set Discord Timer/Interval Settings for my elizaos agents in discord?** (asked by DigitalDiva)
- **Do you need Twitter API to use Eliza to run a Twitter agent?** (asked by Psyxh)
- **Has anyone played coding with minimax m2 here?** (asked by R0am | tip.md)

## Community Help & Collaboration

**ElizaCloud Troubleshooting**
- Helper: cjft
- Helpee: ElizaBAO
- Context: ElizaBAO experiencing operation failures with elizacloud app creator
- Resolution: Confirmed feature is working but noted it's an early feature, suggested retry

**Plugin Interoperability Collaboration**
- Helper: R0am | tip.md
- Helpee: jin
- Context: Converting elizaos plugins into skills for interoperability
- Resolution: Volunteered to collaborate and shared technical approach using folders with .md instructions and deterministic scripts

**Workflow Development Guidance**
- Helper: R0am | tip.md
- Helpee: Agent Joshua ₱ | TEE
- Context: Building workflows for chaining skills together
- Resolution: Provided reference to successful subagent linking implementation from Reddit ClaudeCode community

**AI Agent Development Support**
- Helper: jin
- Helpee: DorianD
- Context: Looking for technical approach to build AI agent for image classification
- Resolution: Provided GitHub repository link to DeepFace library as starting point

**Platform Context Explanation**
- Helper: DorianD
- Helpee: Skullcross
- Context: Question about JEJU platform naming origin
- Resolution: Explained that Jeju is a Korean island used for testing new technology before Korea-wide rollout

## Action Items

### Technical

- **Collaborate on experiment converting elizaos plugins (Discord + blockchain) into skills for interoperability testing** - Mentioned by: jin
- **Implement hooks solution for getting Claude to use skills implicitly** - Mentioned by: R0am | tip.md
- **Complete cloud cleanups and optimizations** - Mentioned by: Stan ⚡
- **Investigate and resolve elizacloud app creator operational failures** - Mentioned by: ElizaBAO
- **Evaluate Minimax M2's interleaved thinking approach for long-running tasks** - Mentioned by: R0am | tip.md

### Feature

- **Develop Eliza 2.0 with TS/Rust/Python support, FFI plugin interop, no API/server/CLI/projects, Claude-friendly runtime** - Mentioned by: shaw
- **Integrate Dopa One AI algorithm (mental health monitoring via mobile interaction patterns) into future ElizaOS Phone app to monitor users' dopamine levels and mental well-being** - Mentioned by: DorianD
- **Implement AI agent for image-based classification using DeepFace library** - Mentioned by: DorianD

### Documentation

- **Twitter Space event scheduled for January 13th at 7pm UTC with Solana Foundation, PayAI, and Quantu to discuss 8004 and Eliza Cloud utilization** - Mentioned by: Kenk
- **Publish blog post on elizaos leaderboard updates as part 2 of the meritverse article** - Mentioned by: jin
- **Document Twitter API requirements for running Twitter agents with Eliza** - Mentioned by: Psyxh