# elizaOS Discord - 2026-04-21

## Summary

### Legal Matters

The community discussed a lawsuit against the project that was shared via Twitter link. Odilitime explained that the team will respond through their lawyers and emphasized they have code documentation to prove they built everything promised. He characterized the lawsuit as without merit and specifically referenced "number 3" of the lawsuit. The team expressed confidence in their legal position based on their development work and code documentation.

### Plugin Development

Stan0473 mentioned plans to build a plugin for scammers. Odilitime offered to share a plugin he had already started working on for this purpose.

### CI/CD Infrastructure Issues

A workflow configuration problem was identified affecting PR #346 in the elizaos-plugins/registry repository. The claude-code-action workflow is failing to fetch an OIDC token due to missing permissions - either the id-token: write permission or github_token is not properly configured. This is a repository configuration issue rather than a code problem.

### Community Security

Multiple scam warnings were issued by community members targeting suspicious users in the discussion channel.

## FAQ

**Q: How will the team respond to the lawsuit?**
A: The team will respond through their lawyers. They have code to prove they built everything promised and consider the lawsuit to be without merit.

**Q: What is causing the CI pipeline failure on PR #346?**
A: The claude-code-action workflow cannot fetch an OIDC token because of missing permissions - either the id-token: write permission or github_token is not properly configured. This is a repository configuration issue.

**Q: Which repository is affected by the CI/CD issue?**
A: The elizaos-plugins/registry repository, specifically PR #346.

## Help Interactions

**Helper:** odilitime
**Helpee:** stan0473
**Issue:** Stan0473 mentioned plans to build a plugin for scammers
**Resolution:** Odilitime offered to share a plugin he had already started working on

**Helper:** stan0473
**Helpee:** odilitime
**Issue:** Odilitime asked for clarification about which repository was affected by the CI/CD issue
**Resolution:** Stan0473 provided the direct link to the problematic PR #346

## Action Items

### Technical

- Fix the claude-code-action workflow configuration by adding proper id-token: write permission or github_token configuration for PR #346 in elizaos-plugins/registry (mentioned by igor.peregudov)