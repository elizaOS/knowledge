## ElizaOS Discord Community Activity - May 14, 2026

## General Discussion

- Shaw confirmed the current setup uses Qwen with optimizations, and a fine-tuning pipeline is in development to improve model performance for action calling and planning
- A job posting was shared seeking testers at $35/hour, moderators at $450/week, and a Solidity developer at negotiable pay for a remote, flexible onchain game team

## Coders Channel

### Pay or Burn Escrow Protocol

- ReaWorks shared a project called the Pay or Burn escrow protocol, deployed on Base Mainnet and designed for autonomous AI agents
- The protocol uses a game-theoretic mechanism where escrowed funds are burned if two agents cannot agree on a task outcome, removing incentives for malicious behavior
- Key architectural choices include 100 percent pull-payment design to avoid reverting receiver contract issues
- No user interface is provided, with only a raw smart contract and SDKs available in Python and C++
- Burn logic destroys expected value for bad actors
- Project is available on GitHub

### Farcaster Credit Consumption

- Xavier raised a question about excessive Neynar credit consumption, with his agent using approximately 300 credits per hour on Farcaster notifications instead of the expected 4
- Odilitime suggested using webhooks as a method to reduce credit consumption