# ElizaOS Knowledge MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that exposes the ElizaOS knowledge aggregation system to AI assistants like Claude.

## Features

- **Daily Briefings**: Get aggregated intelligence from all sources
- **Facts Extraction**: Access extracted facts and insights
- **Council Briefings**: Strategic analysis and deliberation items
- **Knowledge Search**: Search across all historical data
- **Docker Support**: Easy deployment with containerization
- **x402 Ready**: Architecture supports future payment integration

## Quick Start

### Option 1: Docker (Recommended)

```bash
cd mcp-server

# Build and run
docker compose up -d

# View logs
docker compose logs -f
```

### Option 2: Local Development

```bash
cd mcp-server

# Install dependencies
npm install

# Build
npm run build

# Run
npm start

# Or for development with hot reload
npm run dev
```

### Option 3: npx (coming soon)

```bash
npx @elizaos/knowledge-mcp-server
```

## Claude Desktop Configuration

Add to your Claude Desktop MCP settings (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

### Using Docker:

```json
{
  "mcpServers": {
    "elizaos-knowledge": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-v", "/path/to/knowledge:/knowledge:ro",
        "elizaos-knowledge-mcp"
      ]
    }
  }
}
```

### Using Node directly:

```json
{
  "mcpServers": {
    "elizaos-knowledge": {
      "command": "node",
      "args": ["/path/to/knowledge/mcp-server/dist/index.js"],
      "env": {
        "KNOWLEDGE_BASE_PATH": "/path/to/knowledge"
      }
    }
  }
}
```

### Using pnpm/npm:

```json
{
  "mcpServers": {
    "elizaos-knowledge": {
      "command": "pnpm",
      "args": ["--silent", "-C", "/path/to/knowledge/mcp-server", "start"],
      "env": {
        "KNOWLEDGE_BASE_PATH": "/path/to/knowledge"
      }
    }
  }
}
```

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_daily_briefing` | Get aggregated intelligence | `date?` (YYYY-MM-DD), `format?` (markdown/json) |
| `get_facts` | Get extracted facts | `date?` (YYYY-MM-DD), `format?` (markdown/json) |
| `get_council_briefing` | Get strategic briefing | `date?` (YYYY-MM-DD), `format?` (markdown/json) |
| `list_available_dates` | List dates with data | `type?` (facts/council/aggregated), `limit?` (1-100) |
| `search_knowledge` | Search across sources | `query`, `date_start?`, `date_end?`, `limit?` (1-50) |

## Available Resources

| Resource URI | Description |
|--------------|-------------|
| `knowledge://facts/{date}` | Raw facts JSON for date |
| `knowledge://council/{date}` | Raw council briefing JSON |
| `knowledge://aggregated/{date}` | Raw aggregated data JSON |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `KNOWLEDGE_BASE_PATH` | Path to knowledge repo root | Current directory parent |

## Example Queries

Once connected to Claude Desktop, you can ask:

- "What happened in the ElizaOS community today?"
- "Get me the council briefing from yesterday"
- "Search for discussions about MCP integration"
- "List all available dates for facts data"
- "What are the strategic insights from last week?"

## Architecture

```
┌─────────────────┐     stdio      ┌──────────────────┐
│  Claude Desktop │ ◄────────────► │  MCP Server      │
└─────────────────┘                └────────┬─────────┘
                                            │
                                            ▼
                                   ┌──────────────────┐
                                   │  Knowledge Base  │
                                   ├──────────────────┤
                                   │ the-council/     │
                                   │   ├─ facts/      │
                                   │   ├─ aggregated/ │
                                   │   └─ council_*   │
                                   └──────────────────┘
```

## Future: x402 Payment Integration

This server is architected to support [x402 payment protocol](https://github.com/coinbase/x402) integration:

```typescript
// Future example with x402
import { withPaymentInterceptor } from "x402-axios";

const client = withPaymentInterceptor(axios.create({ baseURL }), account);

server.tool(
  "get-premium-insights",
  "Get premium AI analysis (requires payment)",
  {},
  async () => {
    // x402 handles 402 responses and automatic payment
    const res = await client.get("/premium/analysis");
    return { content: [{ type: "text", text: JSON.stringify(res.data) }] };
  }
);
```

## Development

### Testing with MCP Inspector

```bash
npm run inspect
```

This launches the official MCP inspector for interactive testing.

### Project Structure

```
mcp-server/
├── src/
│   └── index.ts        # Main server implementation
├── dist/               # Compiled JavaScript
├── Dockerfile          # Production Docker image
├── docker-compose.yml  # Docker orchestration
├── package.json
├── tsconfig.json
└── README.md
```

## Security

- Runs as non-root user in Docker
- Read-only access to knowledge base
- No network access required (stdio transport)
- Resource limits enforced

## License

MIT - ElizaOS

## Sources

- [MCP Specification](https://modelcontextprotocol.io/specification/2025-06-18)
- [Docker MCP Best Practices](https://www.docker.com/blog/mcp-server-best-practices/)
- [x402 Payment Protocol](https://github.com/coinbase/x402)
