# ElizaOS Developer Update
### April 27 - May 4, 2025

## 1. Core Framework

### ElizaOS v2 Nears Completion
Our team is in the final stages of wrapping up ElizaOS v2 with advanced multi-agent capabilities. The latest week delivered significant contributions to core framework stability and performance:

- **Memory Schema Upgrade**: We've overhauled the memory management system with a new schema implementation that provides more flexible and efficient memory operations ([PR #4292](https://github.com/elizaos/eliza/pull/4292)).

- **ESM Module Support**: Fixed type declarations in Core for proper ESM module support, resolving compatibility issues with Node.js 23+ ([PR #4341](https://github.com/elizaos/eliza/pull/4341)).

- **Agent Runtime Improvements**: Several critical fixes to prevent agent crashes and unintended disconnections:
  - Corrected agent deletion process with proper service stop handling
  - Fixed runtime initialization sequence to ensure adapters initialize properly
  - Added null check safeguards to prevent common runtime errors

- **Database Enhancements**: Fixed PostgreSQL integration for Docker containers and improved health checks ([PR #4363](https://github.com/elizaos/eliza/pull/4363), [PR #4382](https://github.com/elizaos/eliza/pull/4382)).

```javascript
// Example of the improved agent runtime initialization sequence
async function initializeRuntime() {
  // First initialize adapters
  await adapter.init();
  
  // Then initialize the rest of the runtime
  await runtime.init();
  
  // Register plugins after initialization
  runtime.registerPlugin(myPlugin);
}
```

## 2. New Features

### Scopable Knowledge
One of our most significant additions this week is the implementation of scopable knowledge ([PR #4390](https://github.com/elizaos/eliza/pull/4390)), allowing agents to access specific knowledge subsets based on context.

```typescript
// Example of scoping knowledge to specific contexts
const knowledgeManager = new KnowledgeManager();

// Add knowledge with scopes
await knowledgeManager.addKnowledge({
  content: "Product pricing information...",
  metadata: {
    source: "pricing_guide.md",
    scopes: ["sales", "support"]
  }
});

// Retrieve knowledge with scope filter
const salesKnowledge = await knowledgeManager.query("pricing", {
  scopes: ["sales"]
});
```

### Enhanced CLI Experience
We've improved the developer experience with updates to the CLI commands:

- Better CLI command instructions ([PR #4381](https://github.com/elizaos/eliza/pull/4381))
- Added a default project template to the `create` command ([PR #4369](https://github.com/elizaos/eliza/pull/4369))
- Automatic rebuild of core and plugin-bootstrap in monorepo context during development ([PR #4388](https://github.com/elizaos/eliza/pull/4388))

```bash
# Example of the improved create command
npx elizaos create my-agent

# The command now includes helpful output:
Creating a new Eliza project in /home/user/my-agent
✅ Project scaffolding complete
✅ Dependencies installed

Next steps:
1. cd my-agent
2. Add your OpenAI API key to .env
3. npx elizaos start
```

### Model/Plugin Name Logging
We've added detailed logging of which model and plugin is being used for each interaction, making debugging and auditing easier ([PR #4394](https://github.com/elizaos/eliza/pull/4394)).

```
[INFO] Using model: gpt-4o-2024-05-14 from plugin: @elizaos/plugin-openai
[INFO] Request tokens: 452, Response tokens: 128
```

## 3. Bug Fixes

### Critical Twitter Integration Fix
We've resolved a major issue with Twitter integration where the `sendStandardTweet` function was undefined, causing agent failures when attempting to post to Twitter ([PR #4373](https://github.com/elizaos/eliza/pull/4373)).

```typescript
// Previously failing code
await twitter.sendStandardTweet(content);  // Would throw "Cannot read properties of undefined"

// Fixed by ensuring the Twitter client properly exports all methods
export class TwitterClient {
  async sendStandardTweet(content: string) {
    // Implementation now properly available
  }
}
```

### Discord Plugin Improvements
Two important fixes for the Discord plugin:

- Added typing indicator functionality to show when the agent is composing a response ([PR #4364](https://github.com/elizaos/eliza/pull/4364))
- Fixed error handling when Discord services are missing to prevent crashes ([PR #4375](https://github.com/elizaos/eliza/pull/4375))

### Disk Space Error Handling
Improved error handling for "no space left on disk" scenarios, providing clearer feedback to users rather than generic error messages ([PR #4389](https://github.com/elizaos/eliza/pull/4389)).

```typescript
try {
  await fs.writeFile(filePath, data);
} catch (error) {
  if (error.code === 'ENOSPC') {
    console.error('Error: No space left on disk. Please free up disk space to continue.');
    // Additional user-friendly handling
  } else {
    throw error;
  }
}
```

## 4. API Changes

### Anthropic Plugin API Key Validation
Added API key validation for Anthropic plugin model calls, ensuring developers receive immediate feedback if their credentials are invalid ([PR #4383](https://github.com/elizaos/eliza/pull/4383)).

```typescript
// New validation in the Anthropic plugin
class AnthropicProvider implements ModelProvider {
  constructor(private apiKey: string) {
    this.validateApiKey();
  }

  private validateApiKey() {
    if (!this.apiKey) {
      throw new Error('ANTHROPIC_API_KEY is required but not provided');
    }
    if (!this.apiKey.startsWith('sk-ant-')) {
      throw new Error('Invalid ANTHROPIC_API_KEY format. Keys should start with "sk-ant-"');
    }
  }
}
```

### Core Crypto Type Checking
Improved type checking for crypto values in the core package, preventing common type-related errors ([PR #4376](https://github.com/elizaos/eliza/pull/4376)).

## 5. Social Media Integrations

### Discord Enhancements
Added typing indicator support to the Discord plugin ([PR #4364](https://github.com/elizaos/eliza/pull/4364)), creating a more natural interaction experience when agents respond to messages.

```typescript
// Example of the new typing indicator implementation
export class DiscordService {
  async sendMessage(channelId: string, content: string) {
    // Start typing indicator
    await this.client.channels.cache.get(channelId).sendTyping();
    
    // Process response (potentially with some delay to simulate typing)
    await new Promise(resolve => setTimeout(resolve, this.calculateTypingTime(content)));
    
    // Send the actual message
    return this.client.channels.cache.get(channelId).send(content);
  }
  
  private calculateTypingTime(content: string): number {
    // Calculate realistic typing time based on message length
    return Math.min(Math.max(content.length * 20, 1000), 10000);
  }
}
```

### Twitter Plugin Fix
Fixed critical issue with the Twitter plugin where `sendStandardTweet` was undefined ([PR #4373](https://github.com/elizaos/eliza/pull/4373)). The fix ensures proper method exposure and error handling when interacting with Twitter.

## 6. Model Provider Updates

### Anthropic Plugin Improvements
- Added API key validation for Anthropic plugin model calls ([PR #4383](https://github.com/elizaos/eliza/pull/4383))
- Increased test coverage and setup ([PR #4370](https://github.com/elizaos/eliza/pull/4370))

### Local LLM Fixes
Fixed issue with local LLM throwing undefined errors ([PR #4396](https://github.com/elizaos/eliza/pull/4396)), improving reliability when using locally hosted models.

## 7. Breaking Changes

### Plugin EVM Removal from Monorepo
We've extracted the EVM plugin from the monorepo ([PR #4386](https://github.com/elizaos/eliza/pull/4386), [PR #4399](https://github.com/elizaos/eliza/pull/4399)). This is a breaking change for developers using the EVM plugin directly from the monorepo.

**Migration Instructions:**
1. Remove any direct imports from the monorepo EVM plugin
2. Install the standalone package:
   ```bash
   npm install @elizaos/plugin-evm
   ```
3. Update your import paths to reference the package instead of local files

### Short Replies Fix
Fixed issues with truncated responses in certain contexts ([PR #4374](https://github.com/elizaos/eliza/pull/4374)). If you've implemented workarounds for this issue, they can now be removed.

---

This update covers the most significant changes from April 27 to May 4, 2025. For a complete list of changes, please refer to our [GitHub repository](https://github.com/elizaos/eliza/pulls?q=is%3Apr+merged%3A2025-04-27..2025-05-04).

For any questions or assistance, join our [Discord community](https://discord.gg/elizaos) or open an issue on GitHub. We're actively monitoring these channels to support our developer community.
