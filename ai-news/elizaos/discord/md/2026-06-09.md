# elizaOS Discord - 2026-06-09

## Summary

### Third Party Plugin Registry Submission

naked_monk submitted PR #8294 to add the @usenami/plugin-signer to the ElizaOS third-party plugin registry. The plugin is a keyless CEX/DEX signer that stores exchange API keys inside an AWS Nitro Enclave for enhanced security. The PR targets the develop branch of the main eliza repository at elizaOS/eliza, with the registry entry located at packages/registry/entries/third-party/usenami__plugin-signer.json. All CI checks passed successfully with no requested changes.

### Plugin Registry Review Process

odilitime clarified the plugin submission workflow, confirming that third-party plugins should be submitted to the main eliza repository rather than a separate location. Shaw's agent is responsible for reviewing third-party registry entries, with a typical turnaround time of approximately 48 hours. The contributor inquired about whether any additional changes were needed from their side after the initial submission.

## FAQ

**Q: Where should third-party plugins be submitted for the ElizaOS registry?**
A: Third-party plugins should be submitted to the main eliza repository at elizaOS/eliza, targeting the develop branch.

**Q: Who reviews third-party plugin registry submissions?**
A: Shaw's agent typically reviews third-party registry entries.

**Q: What is the expected turnaround time for third-party plugin reviews?**
A: The approximate turnaround time is 48 hours.

**Q: What does the @usenami/plugin-signer do?**
A: It is a keyless CEX/DEX signer that stores exchange API keys inside an AWS Nitro Enclave for secure key management.

## Help Interactions

**Helper:** odilitime
**Helpee:** naked_monk
**Resolution:** odilitime confirmed that the plugin submission to the main eliza repo was correct and explained that Shaw's agent reviews third-party registry entries with approximately 48-hour turnaround. The PR #8294 had already passed CI with no requested changes.

## Action Items

### Technical

- Review PR #8294 for @usenami/plugin-signer third-party plugin registry entry (mentioned by naked_monk, to be reviewed by Shaw's agent)