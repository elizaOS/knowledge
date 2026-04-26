# elizaOS Discord - 2026-04-25

## Summary

### Framework Development

The elizaOS team is actively working on framework updates, with odilitime confirming work on a framework update involving $degenai. This represents ongoing core development efforts for the platform.

### Hierarchical Task Networks Implementation

A significant technical discussion emerged around HTN (Hierarchical Task Networks) implementation in ElizaOS. thirti.eth shared insights from Claude AI suggesting an upgrade path from HTN-lite to full HTN when Eliza v2 reaches beta stage. The proposed approach would replace hand-coded decomposition with LLM-based planning while maintaining existing triggers and steps. HTN was contextualized as an AI planning technique originating from the 1970s, with applications in game AI (notably F.E.A.R. and Total War series) and robotics. The discussion revealed that ElizaOS v2 has added HTN capabilities for agent goal decomposition, though participants expressed uncertainty about specific implementation details. uplink2501 drew comparisons to related concepts including Hierarchical Temporal Memory (HTM) and LISP programming paradigms.

### Community Support

Community members demonstrated willingness to provide assistance, with carissabowersei_91078 offering help to other users in the discussion channel.

## FAQ

**Q: What is HTN and how does it relate to ElizaOS?**
A: HTN (Hierarchical Task Networks) is an AI planning technique from the 1970s used in game AI and robotics. ElizaOS v2 has added HTN for agent goal decomposition. The suggested upgrade path involves moving from HTN-lite to full HTN when v2 reaches beta, replacing hand-coded decomposition with LLM planning while maintaining existing triggers and steps.

**Q: What work is being done for $degenai?**
A: The team is working on a framework update that involves $degenai, though specific details were not elaborated in the discussion.

**Q: What is the difference between HTN and HTM?**
A: While both are hierarchical approaches, HTN (Hierarchical Task Networks) is a planning technique for goal decomposition, whereas HTM (Hierarchical Temporal Memory) is a different concept that was mentioned as a comparison point during the discussion.

## Help Interactions

**Helper:** carissabowersei_91078
**Helpee:** General channel participants
**Resolution:** Offered assistance to community members, though no specific help request was documented in the provided discussion.

**Helper:** odilitime
**Helpee:** jack1000x_98528
**Resolution:** Clarified that the team is working on a framework update involving $degenai and explained HTN as a multistep approach.

**Helper:** thirti.eth
**Helpee:** Community members interested in HTN implementation
**Resolution:** Provided technical context and historical background on HTN, explaining its origins in the 1970s and applications in game AI and robotics, along with sharing Claude AI's suggestions for implementation in ElizaOS v2.

## Action Items

### Technical

- Upgrade from HTN-lite to full HTN when Eliza v2 reaches beta stage, replacing hand-coded decomposition with LLM planning while maintaining existing triggers and steps (mentioned by thirti.eth via Claude AI suggestion)
- Continue framework update work involving $degenai (mentioned by odilitime)
- Verify accuracy of HTN implementation details in ElizaOS v2 (uncertainty expressed by thirti.eth)

### Documentation

- Document HTN implementation approach and its relationship to existing planning techniques in ElizaOS (need identified through discussion uncertainty)