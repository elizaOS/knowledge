# elizaOS Discord - 2026-02-07

## Overall Discussion Highlights

### Milaidy Project Launch & Development

A significant new project called **milaidy** emerged as the central technical focus across multiple channels. This Eliza-based version of openclaw is being developed as a Mac-native application with several key architectural decisions:

- **Architecture**: Runs as a simple .app on Mac with minimal bloat through plugin-based design
- **Features**: Uses agent skills similar to openclaw, includes all openclaw connectors as Eliza plugins
- **Technical Stack**: Uses openclaw with "pi agent" under the hood
- **Repository**: https://github.com/milady-ai/milaidy

The project sparked immediate community engagement with multiple developers volunteering for testing and bug fixes. Wes demonstrated initiative by creating 3 pull requests to address bugs, though he paused further contributions pending clarification on the contribution workflow process.

### Branding Strategy Debate

A critical strategic discussion emerged regarding the milaidy project's branding. Borko raised concerns that using Milaidy branding instead of Eliza branding would divert mindshare away from the core Eliza ecosystem and miss opportunities to capture brand and network effects. The compromise solution proposed by Odilitime was to maintain separate brands while implementing cross-promotion strategies to ensure both projects benefit each other rather than competing for attention.

### Community Testing & Recruitment

Strong community response to recruitment for testing next-generation Eliza software, with volunteers offering diverse technical backgrounds:
- Prolific Mind (built autonomous framework with ERC-8004)
- Wes (ElizaOS agents, Lang Graph, RAG apps experience)
- One Frequency United (25 years tech experience)
- Maarmapa (self-identified bug hunter)

### Technical Implementations & Use Cases

**SpacetimeDB Integration**: metalhorse233 successfully integrated Eliza into their game using SpacetimeDB as the database/backend, reporting surprisingly quick setup time. This represents a concrete use case of the Eliza framework in game development.

**Opus 4.6 Access**: Odilitime announced that Opus 4.6 is available free on bolt.new for 48 hours, though with some unspecified limitations.

### Security & Infrastructure Concerns

DigitalDiva raised critical concerns about malicious code in skills and vulnerabilities in the setup, though no specific details or solutions were provided in the discussion.

### Marketing & Token Economics Discussion

Community members debated ElizaOS token price performance and marketing strategy:
- Concerns raised about price performance and need for marketing push with upcoming launches
- Debate about whether the team prioritizes price - conflicting perspectives on team's stance
- Historical context provided: ai16z grew from 60k to 2.6b market cap in 2-3 months
- Positive feedback on marketing efforts with upcoming merchandise mentioned

### Infrastructure Strategy

Discussion of scaling strategy for milaidy: keeping one instance hot and paying per usage for efficiency, with reference to sprites.dev as a model.

## Key Questions & Answers

**Q: What is milaidy?**  
A: An Eliza version of openclaw that runs as a Mac app, uses agent skills, includes openclaw connectors as plugins, with minimal bloat (answered by s)

**Q: What does openclaw use under the hood?**  
A: Pi agent (answered by s)

**Q: Why not call it Eliza?**  
A: Need something memetic; pi is cool but not memetic, whereas the lobster has memetic appeal (answered by s)

**Q: Should this be Eliza branded?**  
A: We should cross-promote and keep them separate but helping each other (answered by Odilitime)

## Community Help & Collaboration

**Milaidy Project Support**  
- **Helper**: s | **Helpee**: Community  
- **Context**: Requested help squashing bugs and getting milady.ai project to production  
- **Resolution**: Multiple volunteers responded offering testing and development assistance

**Testing Volunteer Coordination**  
- **Helper**: Kenk | **Helpee**: Testing volunteers  
- **Context**: Multiple people asking how to participate in testing  
- **Resolution**: Directed them to jump into a specific location

**Active Contributors**  
- Wes created 3 pull requests for bug fixes and demonstrated proactive engagement
- Multiple developers (! Alex !, aicodeflow) offered services for project development and collaboration

## Action Items

### Technical

- **Squash bugs in milady.ai project and get to production** (Mentioned by: s)
- **Review 3 pull requests submitted to milady repository** (Mentioned by: Wes)
- **Complete Mac .app implementation for milaidy** - needs a couple days (Mentioned by: s)
- **Implement agent skills like openclaw in milaidy** (Mentioned by: s)
- **Port all openclaw connectors as Eliza plugins** (Mentioned by: s)
- **Investigate and fix malicious code in skills and setup vulnerabilities** (Mentioned by: DigitalDiva)

### Documentation

- **Clarify contribution process for milady repository** - issue logging and PR workflow (Mentioned by: Wes)
- **Clarify branding strategy between Milaidy and Eliza products** (Mentioned by: Borko)
- **Document SpacetimeDB integration with Eliza for game development** (Mentioned by: metalhorse233)

### Feature

- **Implement cross-promotion strategy between Milaidy and Eliza brands** (Mentioned by: Odilitime)
- **Implement marketing push for upcoming launches** (Mentioned by: Biazs)