# elizaOS Discord - 2026-05-14

## Summary

### AI Model Development and Optimization

shawmakesmagic reported current usage of Qwen models with optimizations and announced development of a fine-tuning pipeline aimed at improving model performance specifically for action calling and planning tasks.

### AI Agent Escrow Protocol Architecture

A novel escrow protocol designed for AI agents was introduced, deployed on Base Mainnet. The protocol implements a Pay or Burn mechanism that removes human arbitration by using game theory principles - if agents cannot reach agreement on task outcomes, escrowed funds are burned to eliminate incentives for malicious behavior. The architecture features 100% pull-payment design to protect against reverting receiver contracts and adopts a zero UI approach, providing only raw smart contracts with SDKs in Python and C++. The creator is actively seeking architectural feedback from the community.

### API Integration and Rate Limiting Issues

A technical issue was reported regarding Neynar API credit consumption, where actual usage reached 300 credits per hour versus the expected 4 credits per hour on the v2/farcaster/notifications endpoint. This occurred despite the user overriding the default 120-second polling interval. Community members suggested webhooks as a potential solution to reduce credit consumption.

## FAQ

**Q: What models is shawmakesmagic currently using?**
A: Qwen models with optimizations, and they are developing a fine-tuning pipeline to improve performance for action calling and planning.

**Q: How does the AI agent escrow protocol handle disputes?**
A: It uses a Pay or Burn mechanism where if agents cannot agree on task outcomes, the escrowed funds are burned, eliminating expected value for malicious actors and removing the need for human arbitration.

**Q: What blockchain is the AI agent escrow protocol deployed on?**
A: Base Mainnet.

**Q: Why does the escrow protocol use a pull-payment design?**
A: To protect against reverting receiver contracts.

**Q: How can Neynar API credit consumption be reduced?**
A: Community members suggested using webhooks instead of polling to reduce credit consumption.

## Help Interactions

A user reported unexpectedly high Neynar API credit consumption (300 credits/hour vs expected 4/hour) on the v2/farcaster/notifications endpoint despite overriding the default polling interval. A community member suggested implementing webhooks as a solution to reduce credit consumption. Resolution status was not explicitly confirmed in the discussion.

The creator of the AI agent escrow protocol requested architectural feedback from the community on their Pay or Burn mechanism and overall protocol design. No specific resolution or feedback responses were documented in the provided summary.

## Action Items

### Technical

- Develop and implement fine-tuning pipeline for Qwen models to improve action calling and planning performance (mentioned by shawmakesmagic)
- Gather architectural feedback on AI agent escrow protocol design and Pay or Burn mechanism (mentioned by escrow protocol creator)
- Investigate webhook implementation to reduce Neynar API credit consumption (suggested by community member)