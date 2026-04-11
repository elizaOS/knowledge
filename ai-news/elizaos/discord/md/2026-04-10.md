# elizaOS Discord - 2026-04-10

## Summary

### ElizaOS v2 Socket.IO Integration

Shah0406 worked through Socket.IO messaging protocol challenges for ElizaOS v2, discovering the correct pattern uses socket.emit with message types (type: 1 for ROOM_JOINING, type: 2 for SEND_MESSAGE) and requires entityId UUID for authentication. They are running a custom dashboard setup with ElizaOS v2 using @elizaos/plugin-openai, local Qwen3.5 via Nosana GPU on port 3001, and a dashboard on port 8080 with Socket.IO and HTTP polling fallback.

### Token Economics and Project Updates

Community members raised questions about ElizaOs token utility, airdrops, buybacks, and Jeju gas fee implementation. Odilitime confirmed some airdrops are planned but details are not yet available, with no additional plans beyond what was previously announced. Community expressed frustration about lack of clarity on buyback timing and gas fee implementation.

### Technical Support Issues

Huey79ng encountered wallet verification problems with Collab.land and sought support. The issue remained unresolved in the discussion segment.

### Development Focus

The team is currently prioritizing ElizaOS v3 development, with Odilitime noting this as the current focus area when responding to v2 documentation requests.

## FAQ

**Q: Are there any airdrops planned for ElizaOs token holders?**
A: Odilitime confirmed that some airdrops are planned, but specific details are not yet available.

**Q: What is the correct Socket.IO messaging pattern for ElizaOS v2?**
A: Use socket.emit('message', {type: 1, payload: {...}}) for ROOM_JOINING and type: 2 for SEND_MESSAGE. Authentication requires {entityId: UUID} in socket options.

**Q: Where can I find documentation for ElizaOS Socket.IO message types?**
A: Odilitime suggested checking https://docs.elizaos.ai and using Cursor AI to query the codebase directly for complete message type enums and payload field specifications.

**Q: What are the plans for buybacks and Jeju gas fees?**
A: Odilitime stated there are no plans beyond what was previously laid out, with no additional details on timing or implementation.

## Help Interactions

**Helper:** Odilitime
**Helpee:** Shah0406
**Issue:** Needed documentation for ElizaOS v2 Socket.IO message types, required vs optional payload fields, and programmatic DM channel creation
**Resolution:** Directed to https://docs.elizaos.ai and suggested using Cursor AI to query the codebase directly, though noted team focus is currently on v3 development

**Helper:** None
**Helpee:** Huey79ng
**Issue:** Wallet verification problems with Collab.land
**Resolution:** Unresolved in the discussion segment

**Helper:** Odilitime
**Helpee:** Community members
**Issue:** Questions about airdrops, buybacks, and Jeju gas fees
**Resolution:** Confirmed some airdrops planned but no details available yet, no additional plans beyond previous announcements

## Action Items

### Technical

- Complete Socket.IO message type enum documentation including all required and optional payload fields (mentioned by shah0406)
- Document programmatic DM channel creation without official UI (mentioned by shah0406)

### Documentation

- Provide canonical documentation for ElizaOS v2 Socket.IO messaging protocol (mentioned by shah0406)
- Clarify token utility, airdrop details, and buyback timeline (mentioned by community members)
- Document Jeju gas fee implementation details (mentioned by community members)