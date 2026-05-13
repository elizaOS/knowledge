# elizaOS Discord - 2026-05-12

## Summary

### Plugin Registry Infrastructure

The v2 registry infrastructure for third-party Eliza plugins encountered technical issues. Plugin-undesirables@2.0.3 was prepared for submission with generated JSON metadata, but attempts to access the elizaos-plugins/registry repository and plugins.elizacloud.ai resulted in 404 errors. The plugin uses BUSL-1.1 licensing which prevents direct PRs to the monorepo. Investigation into the registry access issues is ongoing, with potential policy changes being considered to revert back to PRs directly to the elizaOS/eliza repository.

### Community Introductions

New community members introduced themselves in the discussion channel. One member shared their background in AI and full-stack development, emphasizing expertise in practical problem-solving, clean code practices, and production-ready systems with focus on efficiency, accuracy, user experience, maintainability, and security.

### Security Concerns

Discord server security issues were identified with compromised admin accounts and ongoing scammer activity requiring attention from moderators.

## FAQ

**Q: How do I submit a plugin to the v2 registry?**
A: The v2 registry submission process is currently under investigation due to 404 errors when accessing the elizaos-plugins/registry repo and plugins.elizacloud.ai. A potential policy change may revert the process back to PRs directly to the elizaOS/eliza repository.

**Q: Can I submit a plugin with BUSL-1.1 licensing to the monorepo?**
A: No, BUSL-1.1 licensing prevents direct PRs to the monorepo. Alternative submission methods through the v2 registry are being developed.

**Q: Why am I getting 404 errors when trying to access the plugin registry?**
A: This is a known issue currently under investigation by the development team. The registry infrastructure may have been accidentally affected.

## Help Interactions

**Helper:** odilitime
**Helpee:** thegreatluna8713
**Resolution:** Acknowledged the 404 errors on elizaos-plugins/registry repo and plugins.elizacloud.ai. Investigation initiated to determine if the issue was accidental. Mentioned potential policy change to revert to PRs directly to elizaOS/eliza repository. Resolution pending.

## Action Items

### Technical

- Investigate 404 errors on elizaos-plugins/registry repo and plugins.elizacloud.ai (mentioned by odilitime)
- Address compromised admin accounts and scammer activity in Discord server (mentioned by shrektwo, odilitime)
- Determine final policy for plugin submission process between v2 registry and direct PRs (mentioned by odilitime)

### Documentation

- Clarify plugin submission process for BUSL-1.1 licensed plugins once registry issues are resolved (mentioned by thegreatluna8713)