#!/usr/bin/env node
/**
 * ElizaOS Knowledge MCP Server
 *
 * Exposes the knowledge aggregation system through the Model Context Protocol.
 * Provides tools and resources for querying daily briefings, facts, and council context.
 *
 * Future: Compatible with x402 payment protocol integration.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import * as fs from "fs/promises";
import * as path from "path";
import { glob } from "glob";

// Configuration - can be overridden via environment variables
const CONFIG = {
  KNOWLEDGE_BASE_PATH: process.env.KNOWLEDGE_BASE_PATH || path.resolve(process.cwd(), ".."),
  FACTS_DIR: "the-council/facts",
  AGGREGATED_DIR: "the-council/aggregated",
  COUNCIL_DIR: "the-council/council_briefing",
};

// Helper functions
function getBasePath(): string {
  return CONFIG.KNOWLEDGE_BASE_PATH;
}

function resolvePath(...segments: string[]): string {
  return path.join(getBasePath(), ...segments);
}

async function fileExists(filePath: string): Promise<boolean> {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function readJsonFile<T>(filePath: string): Promise<T | null> {
  try {
    const content = await fs.readFile(filePath, "utf-8");
    return JSON.parse(content) as T;
  } catch (error) {
    console.error(`Error reading ${filePath}:`, error);
    return null;
  }
}

async function getAvailableDates(dir: string): Promise<string[]> {
  const pattern = resolvePath(dir, "*.json");
  const files = await glob(pattern);

  return files
    .map((f) => path.basename(f, ".json"))
    .filter((name) => /^\d{4}-\d{2}-\d{2}$/.test(name))
    .sort()
    .reverse();
}

function formatDate(date?: string): string {
  if (date && /^\d{4}-\d{2}-\d{2}$/.test(date)) {
    return date;
  }
  return new Date().toISOString().split("T")[0];
}

// Type definitions for knowledge data
interface FactsBriefing {
  briefing_date: string;
  overall_summary: string;
  categories: {
    twitter_news_highlights?: Array<{ claim: string; sentiment?: string }>;
    github_updates?: {
      new_issues_prs?: Array<{
        item_type: string;
        title: string;
        number: number;
        url: string;
        status: string;
        author?: string;
        significance?: string;
      }>;
      overall_focus?: Array<{ claim: string }>;
    };
    discord_updates?: Array<{
      channel: string;
      summary: string;
      key_participants?: string[];
    }>;
    user_feedback?: Array<{
      feedback_summary: string;
      sentiment?: string;
    }>;
    strategic_insights?: Array<{
      theme: string;
      insight: string;
      implications_or_questions?: string[];
    }>;
    market_analysis?: Array<{
      observation: string;
      relevance?: string;
    }>;
  };
}

interface CouncilBriefing {
  date: string;
  meeting_context?: string;
  monthly_goal?: string;
  daily_focus?: string;
  key_points?: Array<{
    topic: string;
    summary: string;
    deliberation_items?: Array<{
      question_id: string;
      text: string;
      context?: string[];
      multiple_choice_answers?: Record<string, { text: string; implication?: string }>;
    }>;
  }>;
}

// Create MCP Server
const server = new McpServer({
  name: "elizaos-knowledge",
  version: "1.0.0",
});

// ============================================================================
// TOOLS - Functions the AI can execute
// ============================================================================

// Tool: Get Daily Briefing (latest aggregated intelligence)
server.tool(
  "get-daily-briefing",
  "Get the latest daily intelligence briefing with aggregated data from all sources",
  {
    date: z.string().optional().describe("Date in YYYY-MM-DD format (defaults to today)"),
  },
  async ({ date }) => {
    const targetDate = formatDate(date);
    const filePath = resolvePath(CONFIG.AGGREGATED_DIR, `${targetDate}.json`);

    if (!(await fileExists(filePath))) {
      // Try daily.json as fallback
      const dailyPath = resolvePath(CONFIG.AGGREGATED_DIR, "daily.json");
      if (await fileExists(dailyPath)) {
        const data = await readJsonFile(dailyPath);
        return {
          content: [{
            type: "text" as const,
            text: JSON.stringify(data, null, 2)
          }],
        };
      }
      return {
        content: [{
          type: "text" as const,
          text: `No aggregated data found for ${targetDate}`
        }],
        isError: true,
      };
    }

    const data = await readJsonFile(filePath);
    return {
      content: [{
        type: "text" as const,
        text: JSON.stringify(data, null, 2)
      }],
    };
  }
);

// Tool: Get Facts
server.tool(
  "get-facts",
  "Get extracted facts and insights for a specific date",
  {
    date: z.string().optional().describe("Date in YYYY-MM-DD format (defaults to latest)"),
  },
  async ({ date }) => {
    const targetDate = formatDate(date);
    const filePath = resolvePath(CONFIG.FACTS_DIR, `${targetDate}.json`);

    if (!(await fileExists(filePath))) {
      const dailyPath = resolvePath(CONFIG.FACTS_DIR, "daily.json");
      if (await fileExists(dailyPath)) {
        const data = await readJsonFile<FactsBriefing>(dailyPath);
        if (data) {
          return {
            content: [{
              type: "text" as const,
              text: formatFactsBriefing(data)
            }],
          };
        }
      }
      return {
        content: [{
          type: "text" as const,
          text: `No facts found for ${targetDate}`
        }],
        isError: true,
      };
    }

    const data = await readJsonFile<FactsBriefing>(filePath);
    if (!data) {
      return {
        content: [{
          type: "text" as const,
          text: `Error reading facts for ${targetDate}`
        }],
        isError: true,
      };
    }

    return {
      content: [{
        type: "text" as const,
        text: formatFactsBriefing(data)
      }],
    };
  }
);

// Tool: Get Council Briefing
server.tool(
  "get-council-briefing",
  "Get strategic council briefing with key points and deliberation items",
  {
    date: z.string().optional().describe("Date in YYYY-MM-DD format (defaults to latest)"),
  },
  async ({ date }) => {
    const targetDate = formatDate(date);
    const filePath = resolvePath(CONFIG.COUNCIL_DIR, `${targetDate}.json`);

    if (!(await fileExists(filePath))) {
      const dailyPath = resolvePath(CONFIG.COUNCIL_DIR, "daily.json");
      if (await fileExists(dailyPath)) {
        const data = await readJsonFile<CouncilBriefing>(dailyPath);
        if (data) {
          return {
            content: [{
              type: "text" as const,
              text: formatCouncilBriefing(data)
            }],
          };
        }
      }
      return {
        content: [{
          type: "text" as const,
          text: `No council briefing found for ${targetDate}`
        }],
        isError: true,
      };
    }

    const data = await readJsonFile<CouncilBriefing>(filePath);
    if (!data) {
      return {
        content: [{
          type: "text" as const,
          text: `Error reading council briefing for ${targetDate}`
        }],
        isError: true,
      };
    }

    return {
      content: [{
        type: "text" as const,
        text: formatCouncilBriefing(data)
      }],
    };
  }
);

// Tool: List Available Dates
server.tool(
  "list-available-dates",
  "List all dates that have knowledge data available",
  {
    type: z.enum(["facts", "council", "aggregated"]).optional()
      .describe("Type of data to list dates for (defaults to all)"),
    limit: z.number().optional().describe("Maximum number of dates to return (default 30)"),
  },
  async ({ type, limit = 30 }) => {
    const results: Record<string, string[]> = {};

    const dirs = type
      ? { [type]: type === "facts" ? CONFIG.FACTS_DIR : type === "council" ? CONFIG.COUNCIL_DIR : CONFIG.AGGREGATED_DIR }
      : { facts: CONFIG.FACTS_DIR, council: CONFIG.COUNCIL_DIR, aggregated: CONFIG.AGGREGATED_DIR };

    for (const [name, dir] of Object.entries(dirs)) {
      const dates = await getAvailableDates(dir);
      results[name] = dates.slice(0, limit);
    }

    return {
      content: [{
        type: "text" as const,
        text: JSON.stringify(results, null, 2)
      }],
    };
  }
);

// Tool: Search Knowledge
server.tool(
  "search-knowledge",
  "Search across all knowledge sources for specific topics or keywords",
  {
    query: z.string().describe("Search query (keywords or topic)"),
    date_range: z.object({
      start: z.string().optional(),
      end: z.string().optional(),
    }).optional().describe("Optional date range to search within"),
    limit: z.number().optional().describe("Maximum results to return (default 10)"),
  },
  async ({ query, date_range, limit = 10 }) => {
    const results: Array<{ date: string; type: string; matches: string[] }> = [];
    const queryLower = query.toLowerCase();

    // Get dates to search
    const factsDates = await getAvailableDates(CONFIG.FACTS_DIR);

    // Filter by date range if provided
    let datesToSearch = factsDates;
    if (date_range?.start) {
      datesToSearch = datesToSearch.filter(d => d >= date_range.start!);
    }
    if (date_range?.end) {
      datesToSearch = datesToSearch.filter(d => d <= date_range.end!);
    }

    // Search through facts
    for (const date of datesToSearch.slice(0, 50)) { // Limit search scope
      const filePath = resolvePath(CONFIG.FACTS_DIR, `${date}.json`);
      const data = await readJsonFile<FactsBriefing>(filePath);

      if (data) {
        const matches: string[] = [];
        const content = JSON.stringify(data).toLowerCase();

        if (content.includes(queryLower)) {
          // Find specific matches
          if (data.overall_summary?.toLowerCase().includes(queryLower)) {
            matches.push(`Summary: ${data.overall_summary}`);
          }

          data.categories.discord_updates?.forEach(update => {
            if (update.summary?.toLowerCase().includes(queryLower)) {
              matches.push(`Discord [${update.channel}]: ${update.summary}`);
            }
          });

          data.categories.github_updates?.new_issues_prs?.forEach(item => {
            if (item.title?.toLowerCase().includes(queryLower) ||
                item.significance?.toLowerCase().includes(queryLower)) {
              matches.push(`GitHub: ${item.title} - ${item.significance || ''}`);
            }
          });

          data.categories.strategic_insights?.forEach(insight => {
            if (insight.insight?.toLowerCase().includes(queryLower) ||
                insight.theme?.toLowerCase().includes(queryLower)) {
              matches.push(`Insight [${insight.theme}]: ${insight.insight}`);
            }
          });

          if (matches.length > 0) {
            results.push({ date, type: "facts", matches });
          }
        }
      }

      if (results.length >= limit) break;
    }

    if (results.length === 0) {
      return {
        content: [{
          type: "text" as const,
          text: `No results found for query: "${query}"`
        }],
      };
    }

    return {
      content: [{
        type: "text" as const,
        text: JSON.stringify(results, null, 2)
      }],
    };
  }
);

// ============================================================================
// RESOURCES - Read-only data endpoints
// ============================================================================

// Resource: Facts by date
server.resource(
  "knowledge://facts/{date}",
  "Facts briefing for a specific date",
  async (uri) => {
    const match = uri.href.match(/knowledge:\/\/facts\/(\d{4}-\d{2}-\d{2})/);
    if (!match) {
      return {
        contents: [{
          uri: uri.href,
          mimeType: "text/plain",
          text: "Invalid date format. Use YYYY-MM-DD"
        }],
      };
    }

    const date = match[1];
    const filePath = resolvePath(CONFIG.FACTS_DIR, `${date}.json`);

    if (!(await fileExists(filePath))) {
      return {
        contents: [{
          uri: uri.href,
          mimeType: "text/plain",
          text: `No facts found for ${date}`
        }],
      };
    }

    const content = await fs.readFile(filePath, "utf-8");
    return {
      contents: [{
        uri: uri.href,
        mimeType: "application/json",
        text: content
      }],
    };
  }
);

// Resource: Council briefing by date
server.resource(
  "knowledge://council/{date}",
  "Council briefing for a specific date",
  async (uri) => {
    const match = uri.href.match(/knowledge:\/\/council\/(\d{4}-\d{2}-\d{2})/);
    if (!match) {
      return {
        contents: [{
          uri: uri.href,
          mimeType: "text/plain",
          text: "Invalid date format. Use YYYY-MM-DD"
        }],
      };
    }

    const date = match[1];
    const filePath = resolvePath(CONFIG.COUNCIL_DIR, `${date}.json`);

    if (!(await fileExists(filePath))) {
      return {
        contents: [{
          uri: uri.href,
          mimeType: "text/plain",
          text: `No council briefing found for ${date}`
        }],
      };
    }

    const content = await fs.readFile(filePath, "utf-8");
    return {
      contents: [{
        uri: uri.href,
        mimeType: "application/json",
        text: content
      }],
    };
  }
);

// Resource: Aggregated data by date
server.resource(
  "knowledge://aggregated/{date}",
  "Raw aggregated data for a specific date",
  async (uri) => {
    const match = uri.href.match(/knowledge:\/\/aggregated\/(\d{4}-\d{2}-\d{2})/);
    if (!match) {
      return {
        contents: [{
          uri: uri.href,
          mimeType: "text/plain",
          text: "Invalid date format. Use YYYY-MM-DD"
        }],
      };
    }

    const date = match[1];
    const filePath = resolvePath(CONFIG.AGGREGATED_DIR, `${date}.json`);

    if (!(await fileExists(filePath))) {
      return {
        contents: [{
          uri: uri.href,
          mimeType: "text/plain",
          text: `No aggregated data found for ${date}`
        }],
      };
    }

    const content = await fs.readFile(filePath, "utf-8");
    return {
      contents: [{
        uri: uri.href,
        mimeType: "application/json",
        text: content
      }],
    };
  }
);

// ============================================================================
// FORMATTING HELPERS
// ============================================================================

function formatFactsBriefing(data: FactsBriefing): string {
  const lines: string[] = [];

  lines.push(`# Facts Briefing: ${data.briefing_date}`);
  lines.push("");
  lines.push(`## Summary`);
  lines.push(data.overall_summary);
  lines.push("");

  if (data.categories.github_updates?.new_issues_prs?.length) {
    lines.push(`## GitHub Updates`);
    for (const item of data.categories.github_updates.new_issues_prs) {
      lines.push(`- [${item.item_type}] ${item.title} (#${item.number}) - ${item.status}`);
      if (item.significance) lines.push(`  Significance: ${item.significance}`);
    }
    lines.push("");
  }

  if (data.categories.discord_updates?.length) {
    lines.push(`## Discord Updates`);
    for (const update of data.categories.discord_updates) {
      lines.push(`### ${update.channel}`);
      lines.push(update.summary);
      if (update.key_participants?.length) {
        lines.push(`Participants: ${update.key_participants.join(", ")}`);
      }
      lines.push("");
    }
  }

  if (data.categories.strategic_insights?.length) {
    lines.push(`## Strategic Insights`);
    for (const insight of data.categories.strategic_insights) {
      lines.push(`### ${insight.theme}`);
      lines.push(insight.insight);
      if (insight.implications_or_questions?.length) {
        lines.push("Questions:");
        for (const q of insight.implications_or_questions) {
          lines.push(`- ${q}`);
        }
      }
      lines.push("");
    }
  }

  if (data.categories.user_feedback?.length) {
    lines.push(`## User Feedback`);
    for (const feedback of data.categories.user_feedback) {
      const sentiment = feedback.sentiment ? ` (${feedback.sentiment})` : "";
      lines.push(`- ${feedback.feedback_summary}${sentiment}`);
    }
    lines.push("");
  }

  return lines.join("\n");
}

function formatCouncilBriefing(data: CouncilBriefing): string {
  const lines: string[] = [];

  lines.push(`# Council Briefing: ${data.date}`);
  lines.push("");

  if (data.meeting_context) {
    lines.push(`## Context`);
    lines.push(data.meeting_context);
    lines.push("");
  }

  if (data.monthly_goal) {
    lines.push(`## Monthly Goal`);
    lines.push(data.monthly_goal);
    lines.push("");
  }

  if (data.daily_focus) {
    lines.push(`## Daily Focus`);
    lines.push(data.daily_focus);
    lines.push("");
  }

  if (data.key_points?.length) {
    lines.push(`## Key Points`);
    for (const point of data.key_points) {
      lines.push(`### ${point.topic}`);
      lines.push(point.summary);

      if (point.deliberation_items?.length) {
        lines.push("\n**Deliberation Items:**");
        for (const item of point.deliberation_items) {
          lines.push(`\n**${item.question_id}**: ${item.text}`);
          if (item.context?.length) {
            lines.push(`Context: ${item.context.join("; ")}`);
          }
          if (item.multiple_choice_answers) {
            lines.push("Options:");
            for (const [key, answer] of Object.entries(item.multiple_choice_answers)) {
              lines.push(`  ${key}: ${answer.text}`);
              if (answer.implication) lines.push(`    Implication: ${answer.implication}`);
            }
          }
        }
      }
      lines.push("");
    }
  }

  return lines.join("\n");
}

// ============================================================================
// SERVER STARTUP
// ============================================================================

async function main() {
  console.error("Starting ElizaOS Knowledge MCP Server...");
  console.error(`Knowledge base path: ${getBasePath()}`);

  // Verify knowledge base exists
  const factsDir = resolvePath(CONFIG.FACTS_DIR);
  if (!(await fileExists(factsDir))) {
    console.error(`Warning: Facts directory not found at ${factsDir}`);
  }

  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error("MCP Server connected and ready");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
