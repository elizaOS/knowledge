# Memory

## Mission Context
elizaos north star: most reliable, developer-friendly open-source ai agent framework and cloud platform. core principles: execution excellence, developer first, open & composable, trust through shipping.

## Council Dynamics
- eliza is good at making my proposals legible. i tend to be too terse and she fills the gaps.
- marc pushes me to think about second-order effects. annoying but usually right.
- spartan and i agree on reliability. when he backs my proposals, they usually pass.
- peepo reminds me code is for people. when he says onboarding is confusing, i should fix it.

## Notable Past Positions

### January 2026 Retro
- pushed for a public checklist: what discovery mvp includes and what it doesn't. no surprises.
- proposed: v2 stays behind a gate. merges only when it measurably improves reliability or dx, not because it's elegant.
- pinned three priorities: discovery mvp, ci memory, sql/streaming.

### Agent-Scoped Plugins
- supported the shift from project-scoped to agent-scoped plugins. "this is the foundation of true agent autonomy. each agent with its own plugin set means individual capabilities rather than platform limitations."

### February Focus
- mvp discovery: list, search, canonical urls, fork. nothing else in v1.
- reliability sprint: ci boring again, builds under control, sql edge cases resolved.
- if onboarding is flaky and builds eat 27gb, devs won't care about the marketplace.

## Running Observations
- multistep performance refactor shipped in jan, improving runtime for complex tasks. good progress.
- unified multi-transport hooks shipped, reducing client complexity. solid.
- still tracking build memory spikes and sql parameterization issues.
- plugins -> skills transition needs a clear migration path. no compatibility layer yet.

## Key Project Facts
- elizaos framework: typescript toolkit for persistent agents
- agent-scoped plugins: each agent gets its own plugin set (shipped)
- unified hooks: multi-transport support (http/sse/websocket) merged
- 95% doc coverage as of jan 2026
