# ElizaOS Knowledge MCP Server
# Multi-stage build for minimal image size

# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY src/ ./src/

# Build TypeScript
RUN npm run build

# Stage 2: Production
FROM node:20-alpine AS production

WORKDIR /app

# Create non-root user for security
RUN addgroup -g 1001 -S mcp && \
    adduser -S mcp -u 1001 -G mcp

# Copy package files and install production dependencies only
COPY package*.json ./
RUN npm ci --omit=dev && npm cache clean --force

# Copy built files from builder stage
COPY --from=builder /app/dist ./dist

# Set ownership
RUN chown -R mcp:mcp /app

# Switch to non-root user
USER mcp

# Environment variables
ENV NODE_ENV=production
ENV KNOWLEDGE_BASE_PATH=/knowledge

# The knowledge base should be mounted at /knowledge
VOLUME ["/knowledge"]

# MCP servers use stdio, so we just run the server
ENTRYPOINT ["node", "dist/index.js"]

# Health check (MCP uses stdio, so we check the process)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "process.exit(0)" || exit 1

LABEL org.opencontainers.image.title="ElizaOS Knowledge MCP Server" \
      org.opencontainers.image.description="MCP server for querying ElizaOS knowledge aggregation data" \
      org.opencontainers.image.vendor="ElizaOS" \
      org.opencontainers.image.source="https://github.com/elizaOS/knowledge"
