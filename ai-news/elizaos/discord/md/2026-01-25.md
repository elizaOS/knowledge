# elizaOS Discord - 2026-01-25

## Overall Discussion Highlights

### MCP Integration & API Development

The primary technical focus was on Model Context Protocol (MCP) integration with Eliza Cloud. SATA explored adding external MCP servers to agents for AI Red Teaming with human-in-the-loop functionality. SOLOMON VANDY provided detailed guidance on registering external MCP servers through the Eliza Cloud API using the `POST /api/v1/mcps` endpoint, enabling Eliza to proxy calls to those endpoints for agent reasoning and task execution. Kenk requested adding Eliza MCP functionality to the channel, which Odilitime indicated was feasible.

### Self-Hosting & Infrastructure

LarpsAI shared insights about community deployment patterns, noting users are deploying Eliza on mini PCs to avoid keeping main systems running 24/7. A blog post was referenced detailing Oracle Cloud free tier deployment with specifications of 4 vCPU and 24GB RAM. This discussion highlighted growing interest in accessible self-hosting options for the community.

### Security & Scam Prevention

A security incident was identified involving a "Create A Ticket" bot requesting wallet addresses from users. SATA reported receiving suspicious links after posting questions in the channel. Odilitime confirmed this as a scam operation, likely using automated astroturfing tactics, and warned the community.

### Community Engagement & Resources

In the core-devs channel, Odilitime shared two GitHub repositories: supermemory (a memory management tool) and hindsight (by vectorize-io). Discussion touched on Vivek, a consultant engaging with the team through DMs and community spaces, who recommended obtaining an enterprise Twitter API key for the project. There was also brief observation about Twitter's web platform now using shadcn UI component library.

### Product Development & Adoption

Skinny raised important questions about Eliza agent use cases, wondering why there aren't more specialized, single-purpose agents being deployed despite the framework's availability. This suggests potential concerns about adoption barriers or unclear value propositions for developers that remain unaddressed.

### Token & Ecosystem Questions

Alexei asked about the relationship between various tokens and ElizaOS, specifically whether they impact the core project or operate independently. This question went unanswered, indicating a need for clearer documentation about the token ecosystem. Brief discussion about $STUDIO token occurred, with The Void and MDMnvest expressing confidence based on developer activity.

## Key Questions & Answers

**Q: Is it possible to give an agent created within Eliza Cloud access to an external MCP?**  
*Asked by: SATA*  
**A:** You can add external MCP servers by registering them through the Eliza Cloud API using POST /api/v1/mcps, and once registered, Eliza can proxy calls to those MCP endpoints.  
*Answered by: SOLOMON VANDY*

**Q: Can we add eliza mcp here?**  
*Asked by: Kenk*  
**A:** Probably no reason why we can't.  
*Answered by: Odilitime*

**Q: Why would support bot need wallet address?**  
*Asked by: SATA*  
**A:** It's a scam.  
*Answered by: Odilitime*

**Q: Does Eliza Town have its own Discord channel?**  
*Asked by: Slothify⚡*  
**A:** This is the discord channel.  
*Answered by: Never Broke Again (NBA)*

**Q: Who is the person doing interesting stuff?**  
*Asked by: sayonara*  
**A:** Vivek, a consultant similar to aiflow who attended spaces with Shaw and Odilitime.  
*Answered by: Odilitime and Kenk*

## Community Help & Collaboration

**MCP Integration Support**  
SOLOMON VANDY provided comprehensive assistance to SATA regarding external MCP server integration with Eliza Cloud agents for AI Red Teaming. The helper provided specific API endpoint information (`POST /api/v1/mcps`) and explained the proxy functionality, enabling SATA to move forward with their implementation.

**Self-Hosting Guidance**  
LarpsAI helped the general community with self-hosting questions by suggesting mini PCs for 24/7 operation and referencing an Oracle Cloud free tier deployment guide with detailed specifications (4 vCPU and 24GB RAM), providing accessible infrastructure options.

**Security Alert**  
Odilitime protected SATA and the broader community by confirming suspicious wallet address requests from the "Create A Ticket" bot as a scam and warning about astroturfing tactics, preventing potential security incidents.

**Community Navigation**  
Never Broke Again (NBA) assisted Slothify⚡ in finding the correct Discord channel for Eliza Town discussions, clarifying that they were already in the appropriate location.

**Consultant Identification**  
Kenk and Odilitime collaborated to provide sayonara with background information about Vivek, a consultant engaging with the team, helping to clarify community connections and ongoing initiatives.

## Action Items

### Technical
- **Investigate Oracle Cloud free tier deployment for Eliza** (4 vCPU, 24GB RAM configuration)  
  *Mentioned by: LarpsAI*

### Documentation
- **Check documentation around /api/v1/mcps** for external MCP server registration  
  *Mentioned by: SATA*

- **Clarify relationship between various tokens and ElizaOS** core project  
  *Mentioned by: Alexei*

### Feature
- **Add Eliza MCP functionality** to the channel  
  *Mentioned by: Kenk*

- **Obtain an enterprise Twitter API key**  
  *Mentioned by: Odilitime (via Vivek)*

- **Investigate and address barriers** to creating specialized single-purpose Eliza agents  
  *Mentioned by: Skinny*