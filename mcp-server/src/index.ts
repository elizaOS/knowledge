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

// ============================================================================
// CONFIGURATION
// ============================================================================

const CONFIG = {
  KNOWLEDGE_BASE_PATH: process.env.KNOWLEDGE_BASE_PATH || path.resolve(process.cwd(), ".."),
  FACTS_DIR: "the-council/facts",
  AGGREGATED_DIR: "the-council/aggregated",
  COUNCIL_DIR: "the-council/council_briefing",
};

const CHARACTER_LIMIT = 50000; // Maximum response size

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

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

function truncateResponse(text: string, limit: number = CHARACTER_LIMIT): string {
  if (text.length <= limit) {
    return text;
  }
  return text.slice(0, limit) + "\n\n[Response truncated. Use date filters or pagination to reduce results.]";
}

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

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
// CREATE MCP SERVER
// ============================================================================

const server = new McpServer({
  name: "elizaos-knowledge",
  version: "1.0.0",
});

// ============================================================================
// TOOLS
// ============================================================================

// Tool: Get Daily Briefing
server.tool(
  "get_daily_briefing",
  "Get aggregated intelligence briefing from all ElizaOS knowledge sources for a specific date. Returns Discord discussions, GitHub activity, AI news, and community updates.",
  {
    date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional()
      .describe("Date in YYYY-MM-DD format (defaults to today)"),
    format: z.enum(["markdown", "json"]).default("markdown")
      .describe("Output format: 'markdown' for human-readable or 'json' for raw data"),
  },
  async ({ date, format }) => {
    const targetDate = formatDate(date);
    const filePath = resolvePath(CONFIG.AGGREGATED_DIR, `${targetDate}.json`);

    let data: unknown = null;
    let actualDate = targetDate;

    if (await fileExists(filePath)) {
      data = await readJsonFile(filePath);
    } else {
      const dailyPath = resolvePath(CONFIG.AGGREGATED_DIR, "daily.json");
      if (await fileExists(dailyPath)) {
        data = await readJsonFile(dailyPath);
        actualDate = "latest";
      }
    }

    if (!data) {
      return {
        content: [{
          type: "text" as const,
          text: `No aggregated data found for ${targetDate}. Use list_available_dates to see available dates.`
        }],
        isError: true,
      };
    }

    const textContent = format === "json"
      ? JSON.stringify(data, null, 2)
      : `# Daily Briefing: ${actualDate}\n\n${JSON.stringify(data, null, 2)}`;

    return {
      content: [{ type: "text" as const, text: truncateResponse(textContent) }],
    };
  }
);

// Tool: Get Facts
server.tool(
  "get_facts",
  "Get extracted facts and insights from the ElizaOS knowledge system. Returns LLM-processed intelligence including GitHub updates, Discord summaries, strategic insights, and user feedback.",
  {
    date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional()
      .describe("Date in YYYY-MM-DD format (defaults to latest available)"),
    format: z.enum(["markdown", "json"]).default("markdown")
      .describe("Output format: 'markdown' for formatted briefing or 'json' for structured data"),
  },
  async ({ date, format }) => {
    const targetDate = formatDate(date);
    const filePath = resolvePath(CONFIG.FACTS_DIR, `${targetDate}.json`);

    let data: FactsBriefing | null = null;

    if (await fileExists(filePath)) {
      data = await readJsonFile<FactsBriefing>(filePath);
    } else {
      const dailyPath = resolvePath(CONFIG.FACTS_DIR, "daily.json");
      if (await fileExists(dailyPath)) {
        data = await readJsonFile<FactsBriefing>(dailyPath);
      }
    }

    if (!data) {
      return {
        content: [{
          type: "text" as const,
          text: `No facts found for ${targetDate}. Use list_available_dates to see available dates.`
        }],
        isError: true,
      };
    }

    const textContent = format === "json"
      ? JSON.stringify(data, null, 2)
      : formatFactsBriefing(data);

    return {
      content: [{ type: "text" as const, text: truncateResponse(textContent) }],
    };
  }
);

// Tool: Get Council Briefing
server.tool(
  "get_council_briefing",
  "Get strategic council briefing with key discussion points and deliberation items. Returns high-level strategic analysis designed for leadership decision-making.",
  {
    date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional()
      .describe("Date in YYYY-MM-DD format (defaults to latest available)"),
    format: z.enum(["markdown", "json"]).default("markdown")
      .describe("Output format: 'markdown' for formatted briefing or 'json' for structured data"),
  },
  async ({ date, format }) => {
    const targetDate = formatDate(date);
    const filePath = resolvePath(CONFIG.COUNCIL_DIR, `${targetDate}.json`);

    let data: CouncilBriefing | null = null;

    if (await fileExists(filePath)) {
      data = await readJsonFile<CouncilBriefing>(filePath);
    } else {
      const dailyPath = resolvePath(CONFIG.COUNCIL_DIR, "daily.json");
      if (await fileExists(dailyPath)) {
        data = await readJsonFile<CouncilBriefing>(dailyPath);
      }
    }

    if (!data) {
      return {
        content: [{
          type: "text" as const,
          text: `No council briefing found for ${targetDate}. Use list_available_dates to see available dates.`
        }],
        isError: true,
      };
    }

    const textContent = format === "json"
      ? JSON.stringify(data, null, 2)
      : formatCouncilBriefing(data);

    return {
      content: [{ type: "text" as const, text: truncateResponse(textContent) }],
    };
  }
);

// Tool: List Available Dates
server.tool(
  "list_available_dates",
  "List all dates that have knowledge data available in the system. Use this to discover what historical data is available before querying specific dates.",
  {
    type: z.enum(["facts", "council", "aggregated"]).optional()
      .describe("Filter by data type (defaults to all types)"),
    limit: z.number().int().min(1).max(100).default(30)
      .describe("Maximum number of dates to return (1-100, default: 30)"),
  },
  async ({ type, limit }) => {
    const results: Record<string, string[]> = {};

    const dirs = type
      ? { [type]: type === "facts" ? CONFIG.FACTS_DIR : type === "council" ? CONFIG.COUNCIL_DIR : CONFIG.AGGREGATED_DIR }
      : { facts: CONFIG.FACTS_DIR, council: CONFIG.COUNCIL_DIR, aggregated: CONFIG.AGGREGATED_DIR };

    for (const [name, dir] of Object.entries(dirs)) {
      const dates = await getAvailableDates(dir);
      results[name] = dates.slice(0, limit);
    }

    return {
      content: [{ type: "text" as const, text: JSON.stringify(results, null, 2) }],
    };
  }
);

// Tool: Search Knowledge
server.tool(
  "search_knowledge",
  "Search across all knowledge sources for specific topics, keywords, or discussions. Performs full-text search across facts briefings.",
  {
    query: z.string().min(2).max(200)
      .describe("Search query - keywords or topic to search for (2-200 characters)"),
    date_start: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional()
      .describe("Start date for search range (YYYY-MM-DD format)"),
    date_end: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional()
      .describe("End date for search range (YYYY-MM-DD format)"),
    limit: z.number().int().min(1).max(50).default(10)
      .describe("Maximum results to return (1-50, default: 10)"),
  },
  async ({ query, date_start, date_end, limit }) => {
    const results: Array<{ date: string; type: string; matches: string[] }> = [];
    const queryLower = query.toLowerCase();

    const factsDates = await getAvailableDates(CONFIG.FACTS_DIR);

    let datesToSearch = factsDates;
    if (date_start) {
      datesToSearch = datesToSearch.filter(d => d >= date_start);
    }
    if (date_end) {
      datesToSearch = datesToSearch.filter(d => d <= date_end);
    }

    for (const date of datesToSearch.slice(0, 50)) {
      const filePath = resolvePath(CONFIG.FACTS_DIR, `${date}.json`);
      const data = await readJsonFile<FactsBriefing>(filePath);

      if (data) {
        const matches: string[] = [];
        const content = JSON.stringify(data).toLowerCase();

        if (content.includes(queryLower)) {
          if (data.overall_summary?.toLowerCase().includes(queryLower)) {
            matches.push(`Summary: ${data.overall_summary.slice(0, 200)}...`);
          }

          data.categories.discord_updates?.forEach(update => {
            if (update.summary?.toLowerCase().includes(queryLower)) {
              matches.push(`Discord [${update.channel}]: ${update.summary.slice(0, 150)}...`);
            }
          });

          data.categories.github_updates?.new_issues_prs?.forEach(item => {
            if (item.title?.toLowerCase().includes(queryLower) ||
                item.significance?.toLowerCase().includes(queryLower)) {
              matches.push(`GitHub: ${item.title} - ${item.significance?.slice(0, 100) || ''}`);
            }
          });

          data.categories.strategic_insights?.forEach(insight => {
            if (insight.insight?.toLowerCase().includes(queryLower) ||
                insight.theme?.toLowerCase().includes(queryLower)) {
              matches.push(`Insight [${insight.theme}]: ${insight.insight.slice(0, 150)}...`);
            }
          });

          if (matches.length > 0) {
            results.push({ date, type: "facts", matches: matches.slice(0, 5) });
          }
        }
      }

      if (results.length >= limit) break;
    }

    if (results.length === 0) {
      return {
        content: [{
          type: "text" as const,
          text: `No results found for query: "${query}". Try different keywords or broader date range.`
        }],
      };
    }

    const textContent = results.map(r =>
      `## ${r.date}\n${r.matches.map(m => `- ${m}`).join("\n")}`
    ).join("\n\n");

    return {
      content: [{ type: "text" as const, text: textContent }],
    };
  }
);

// ============================================================================
// RESOURCES
// ============================================================================

server.resource(
  "facts/{date}",
  "knowledge://facts/{date}",
  async (uri) => {
    const match = uri.href.match(/knowledge:\/\/facts\/(\d{4}-\d{2}-\d{2})/);
    if (!match) {
      return {
        contents: [{
          uri: uri.href,
          mimeType: "text/plain",
          text: "Invalid date format. Use knowledge://facts/YYYY-MM-DD"
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

server.resource(
  "council/{date}",
  "knowledge://council/{date}",
  async (uri) => {
    const match = uri.href.match(/knowledge:\/\/council\/(\d{4}-\d{2}-\d{2})/);
    if (!match) {
      return {
        contents: [{
          uri: uri.href,
          mimeType: "text/plain",
          text: "Invalid date format. Use knowledge://council/YYYY-MM-DD"
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

server.resource(
  "aggregated/{date}",
  "knowledge://aggregated/{date}",
  async (uri) => {
    const match = uri.href.match(/knowledge:\/\/aggregated\/(\d{4}-\d{2}-\d{2})/);
    if (!match) {
      return {
        contents: [{
          uri: uri.href,
          mimeType: "text/plain",
          text: "Invalid date format. Use knowledge://aggregated/YYYY-MM-DD"
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
// SERVER STARTUP
// ============================================================================

async function main() {
  console.error("Starting ElizaOS Knowledge MCP Server...");
  console.error(`Knowledge base path: ${getBasePath()}`);

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
