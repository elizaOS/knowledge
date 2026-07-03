# elizaOS Discord - 2026-07-02

## Summary

### Eliza Cloud Business Payout Configuration

The Eliza project is implementing USDC as the default payout asset for its new cloud business service through PR #10732. This change sparked discussion about token economics and utility. The key distinction is between payment tokens (what customers pay with) and payout tokens (what service providers receive). While $elizaos remains an accepted payment token, service providers will receive USDC payouts by default. The rationale is that businesses receiving $elizaos tokens would likely sell them immediately, creating sell pressure. Using USDC for payouts actually protects the token from this dumping behavior while maintaining $elizaos as a payment option, preserving some token utility.

### Gblin Plugin Risk Management Features

The plugin-gblin package released version 0.2.4 with significant new functionality for Eliza agents. The centerpiece is the GET_GBLIN_RISK_ATTESTATION action, which provides cryptographic proof of market risk assessments before executing trades. Agents pay $0.003 in USDC on Base network for a 10-minute validity EIP-712-signed attestation that verifies BTC/ETH risk regime status. The plugin operates in a gasless manner on Base mainnet. Additional features include treasury health monitoring, automated idle USDC parking into on-chain indexes, and just-in-time swap functionality for invoice payments. All four actions and one provider are production-ready against live Base mainnet.

### Community Events and Content

A Twitter Spaces event was shared discussing Ruby Trivia and vibe-coded games in an AMA format.

## FAQ

**Q: Does the USDC payout change eliminate $elizaos token buybacks?**
A: The change affects payouts for the cloud business service, not payments. While $elizaos remains an accepted payment token, service providers receive USDC to prevent immediate token dumping that would create sell pressure.

**Q: What is the difference between payment and payout in the Eliza cloud business context?**
A: Payment refers to what customers use to pay for services (where $elizaos is still accepted), while payout refers to what service providers receive for their services (which defaults to USDC).

**Q: How much does a Gblin risk attestation cost and how long is it valid?**
A: A risk attestation costs $0.003 in USDC on Base network and remains valid for 10 minutes. The transaction is gasless for the agent.

**Q: What type of cryptographic proof does the Gblin risk attestation provide?**
A: It provides an EIP-712-signed proof that verifies the current BTC/ETH market risk regime status before trading.

## Help Interactions

**Helper:** odilitime
**Helpee:** zadayos
**Issue:** Confusion about USDC becoming default payout and concerns about eliminating $elizaos token utility and buybacks
**Resolution:** Clarified that USDC is the default payout (not payment) for cloud business, while $elizaos remains accepted as payment. Explained that businesses receiving $elizaos payouts would dump tokens, so USDC payouts actually benefit token economics long-term.

**Helper:** odilitime
**Helpee:** j_choy
**Issue:** Confusion between payment versus payout terminology
**Resolution:** Provided clarification on the distinction between payment tokens (what customers pay with) and payout tokens (what service providers receive).

## Action Items

### Technical

- Implement USDC as default payout asset for Eliza cloud business in PR #10732 (mentioned by odilitime)
- Deploy plugin-gblin 0.2.4 with GET_GBLIN_RISK_ATTESTATION action on Base mainnet (mentioned by gblin_digital)

### Features

- Integrate treasury health checks into Gblin plugin (mentioned by gblin_digital)
- Implement idle USDC parking into on-chain indexes (mentioned by gblin_digital)
- Add JIT-swap functionality for invoice payments (mentioned by gblin_digital)