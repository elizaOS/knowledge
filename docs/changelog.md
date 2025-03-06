# Changelog

## v0.25.8 (2025-02-24)

#### Summary
This release introduces significant architectural changes to plugin management, adds several new AI model providers, enhances RAG knowledge processing, and improves backend infrastructure. Key themes include modular plugin architecture, expanded AI model support, and improved knowledge handling.


####  Plugin System Enhancements
- Dynamic plugin loading architecture implemented (PR #3339)
- CLI utility for plugin listing and installation (PR #3429)
- Modified NKN plugin configuration (PR #3570)

####  AI Model Providers
- Added NEAR AI model provider (PR #3275)
- Added Secret AI LLM support (PR #3615)
- Enabled structured objects and image generation with NEAR AI (PR #3644)

####  Knowledge Processing
- Enhanced fact provider with relevant fact fetching capability (PR #2635)
- Improved RAG function with optimized chunk & overlap parameters (PR #2525)
- Fixed stringKnowledge storage in RAG knowledge system (PR #3435)
- Removed LangChain dependency for text splitting (PR #3642)

####  Infrastructure Updates
- Added cachedir support to filesystem cache (PR #3291)
- Set Lava as default RPC URL for NEAR and Starknet (PR #3323)
- Fixed Bedrock inference functionality (PR #3553)

#### Bug Fixes
- Addressed security vulnerability GHSA-584q-6j8j-r5pm (PR #2958)
- Fixed default character reference issues (PR #3345)
- Fixed agent configuration via API (PR #3618)
- Resolved image URL handling for outbound messages (PR #3122)
- Fixed OpenAI and Vercel AI package integration (PR #3146)
- Corrected attribute extraction from raw text (PR #3190)

#### Technical Improvements
- Replaced AgentRuntime with interface to extend client capabilities (PR #2388)
- Implemented Turbo optimizations for build performance (PR #2503)
- Updated pnpm version in Docker build (PR #3158)
- Added various fixes for plugin compatibility and configuration

#### Breaking Changes
- Plugin architecture now uses dynamic loading instead of static imports
- All plugins moved out of core codebase into separate packages
- Changed dependency structure for plugin initialization

#### Deprecated Features
- Static plugin imports are no longer supported
- Legacy verifiable inference concept removed (now plugin-based)

This version represents a significant step toward a more modular, extensible architecture while adding support for additional AI models and improving the knowledge processing capabilities.

#### Full Changelog
https://github.com/elizaOS/eliza/compare/v0.1.9...v0.25.8

---

## v0.25.6-alpha.1 (2025-02-06)

#### Summary
This alpha release introduces versioning changes (year.week format), enhances social media integration capabilities, adds new blockchain plugins, and fixes various issues across multiple plugins. The release focuses on improving media handling for messaging platforms and expanding blockchain functionality.

#### Major Features

####  Social Media & Messaging
- Added image URL support for outbound tweets/messages (PR #3122)
- Added configuration toggle for Twitter post generation (PR #3219)
- New Spanish-speaking Trump sample character (PR #3119)
- Action suppression capability for Twitter, Discord, and Telegram (PRs #3286, #3284, #3285)

####  Blockchain Integrations
- TON Plugin: Added NFT collection, item creation, metadata change and transfer functionality (PR #3211)
- MultiversX Plugin: Added CREATE_POOL action (PR #3209)
- Added herotag support for MultiversX plugin (PR #3238)
- Coingecko advanced features for various pools by network (PR #3170)

####  New Plugins
- Added Edwin plugin (PR #3045)
- Added Desk Exchange plugin (PR #3096)
- Enhanced Quick-Intel plugin (PR #3208)

#### Bug Fixes
- Fixed OpenAI and Vercel AI packages to resolve O1 errors (PR #3146)
- Resolved duplicate plugins issue (PR #3126)
- Updated provider-utils for better compatibility (PR #3189)
- Improved attribute extraction from raw text (PR #3190)
- Fixed "think" tag from Venice (PR #3203)
- Enhanced Slack attachments handling (PR #3194)
- Updated pnpm version in Docker build (PR #3158)
- Removed duplicated dependencies (PR #3215)
- Fixed DenyLoginSubtask functionality (PR #3278)
- Implemented RAG optimizations for context handling (PR #3248)
- Fixed Google API key handling (PR #3274)

#### Developer Improvements
- Added test configurations for multiple plugins (CoinGecko, Cronos, Conflux)
- Fixed Docker and types issues (PR #3220)
- Improved OpenAI-like provider endpoint resolution (PR #3281)
- Enhanced JSON normalization process (PR #3301)
- Fixed various unit tests for parsing and models (PRs #3311, #3312)
- Added model configuration reading from character files (PR #3313)
- Set package publishing access to public (PR #3330)

#### Documentation Updates
- Updated documentation for plugins (PR #3324)
- Fixed broken links in contributing guide (PR #3269)
- Added GitHub issues link to contribution guidelines (PR #3268)
- Fixed various typos and improved consistency (PRs #3111, #3270, #3271)

This alpha release introduces the new versioning scheme that uses year.week format (25.6) and prepares for significant architecture changes planned for the stable release.

#### Full Changelog
https://github.com/elizaOS/eliza/compare/v0.1.9...v0.25.6-alpha.1

---

## v0.1.9 (2025-02-01)

#### Summary
This release significantly expands Eliza's client ecosystem, introduces numerous blockchain integrations, enhances AI model support, and improves platform stability. Major additions include Instagram, Telegram, and XMTP clients, Discord and Telegram autonomous agent enhancements, and support for multiple blockchain networks.

#### Major Features

####  New Clients & Communication
- Instagram client implementation (PR #1964)
- Telegram account client (PR #2839)
- XMTP client for decentralized messaging (PR #2786)
- Twitter media post capabilities (PR #2818)
- Discord autonomous agent enhancement (PR #2335)
- Telegram autonomous agent enhancement (PR #2338)
- Direct Client API with agent deletion functionality (PR #2267)

####  AI & LLM Integrations
- NVIDIA inference support (PR #2512)
- Livepeer LLM provider integration (PR #2154)
- Amazon Bedrock as LLM provider (PR #2769)
- Added Birdeye plugin for market data (PR #1417)

####  Blockchain Integrations
- Solana improvements: flawless transfers (PR #2340), Agent Kit features (PR #2458)
- EVM ecosystem: OZ governance (PR #1710), ETH storage (PR #2737), cross-chain swaps via Squid Router (PR #1482)
- Added support for multiple chains: Gravity (PR #2228), Cronos (PR #2585), BNB (PR #2278)
- Sui updates: Aggregator swap for tokens (PR #3012), secp256k1/secp256r1 algorithm support (PR #2476)
- Cosmos: IBC transfer (PR #2358) and IBC swap functionality (PR #2554)
- Injective plugin implementation (PR #1764)
- Added Mina blockchain support (PR #2702)
- CoinGecko price per address functionality (PR #2262)
- Dex Screener plugin with price actions (PR #1865) and trending features (PR #2325)

#### Critical Bug Fixes
- DeepSeek API key configuration issue (PR #2186)
- Windows path resolution in pnpm build client (PR #2240)
- IME multiple messages on Enter issue (PR #2274)
- Fixed key derivation and remote attestation (PR #2303)
- Prevented app crash with undefined REMOTE_CHARACTER_URLS (PR #2384)
- Resolved AI-SDK provider version conflicts (PR #2714)
- Fixed Ethers/viem issue in Mind Network plugin (PR #2783)
- Message ID collision in Telegram Client (PR #3053)
- Fixed image vision model provider application (PR #3056)
- Improved unsupported image provider handling (PR #3057)
- Resolved JSON parsing error with array values (PR #3113)

#### Client Improvements
- Tweet ID parameter correction (PR #2430)
- Twitter bot replies metadata handling (PR #2712)
- Home timeline name parsing fix (PR #2789)
- Topics formatting bug resolution (PR #2951)
- Auto-scrolling improvements (PR #3115)
- Action tweet reply functionality (PR #2966)

#### Infrastructure Enhancements
- Docker build command optimization (PR #3110)
- Service startup optimization (PR #3007)
- Sqlite error with zero-length vectors (PR #1984)
- RAG knowledge handling with Postgres (PR #2153)
- OpenAI embedding issue resolution (PR #3003)

This release represents a major expansion of Eliza's capabilities across multiple platforms and blockchain networks, with significant improvements to agent autonomy and stability.

#### Full Changelog
https://github.com/elizaOS/eliza/compare/v0.1.8-alpha.1...v0.1.9

---

## v0.1.8+build.1 (2025-01-12)

#### Summary
This is a minor update to v0.1.8 focusing on critical fixes for security, Docker builds, and specific module issues. It addresses file upload security, PostgreSQL migration problems, and Twitter client functionality.

#### Key Fixes
- Fixed Docker image build process
- Updated version numbering for proper npm publication as v0.1.8
- Implemented security improvements for file uploads (PR #1806)
- Fixed Twitter client mention deduplication (PR #2185)
- Resolved PostgreSQL adapter migration extension creation issue (PR #2188)
- Added missing LETZAI model support (PR #2187)

#### Documentation
- Added Persian README file (PR #2182)

This build release provides essential fixes that improve security and stability without introducing new features.

---

## v0.1.8-alpha.1 (2025-01-01)

#### Summary
This minor alpha release contains blockchain sector diagram updates and plugin description corrections.

#### Changes
- Added 0G to blockchain sector diagram (PR #2204)
- Fixed SentientAI description in plugin-depin (PR #2668)

#### Full Changelog
https://github.com/elizaOS/eliza/compare/v0.1.8...v0.1.8+build.1

---

## Version 0.1.8 (2025-01-12)

#### Major Features
- **TTS (Text2Speech)**: Added support for over 15 languages (#2110)
- **AI Providers**: 
  - Added Cloudflare AI Gateway support (#821)
  - Integrated Mistral AI as a new model provider (#2137)
  - Added DeepSeek AI provider (#2067)
  - Added Heurist embedding model (#2093)
- **Infrastructure**:
  - Added support for TEE logging and Intel SGX (#1470)
  - Implemented Pro API support with trending coins API (#2068)
- **Blockchain Plugins**:
  - Added Irys plugin (#1708)
  - Added Akash Network plugin with autonomous deployment capabilities (#2111)
  - Added Lens Network Plugin (#2101)
  - Added Hyperliquid plugin (#2141)
  - Added Asterai plugin (#2045)
  - Added Massa plugin (#1582)
  - Added Quai integration (#2083)
  - Implemented Primus zkTLS plugin to verify agent activities (#2086)
  - Modified Solana transactions to be more lenient (wait for confirmed instead of finalized) (#2053)

#### Bug Fixes
- Fixed plugin loading from character.json files (#2095)
- Prevented repeated login by reusing client-twitter session (#2129)
- Fixed chat getting stuck in infinite loop (#1755) 
- Fixed client-discord join voice action (#2160)
- Replaced invalid together.ai medium model (#2173)
- Fixed missing langdetect in plugin-tts package.json (#2175)
- Fixed model settings for images and removed duplicate files (#2118)
- Fixed clientConfig.telegram.isPartOfTeam type (#2103)
- Fixed starknet plugin by replacing walletProvider with portfolio provider (#2029)
- Corrected SUI/USD price calculation (#2150)
- Fixed DeepSeek support in getTokenForProvider (#2179)
- Updated Supabase components (#2100)
- Fixed RAG knowledge for Postgres (#2153)
- Fixed case-sensitive column reference in knowledge table CHECK constraint (#2058)

#### Technical Improvements
- Applied syntax fixes for autonome plugin and updated lock file (#2131)
- Fixed lens export name and duplicate imports (#2142)
- Fixed double responses from Continue Action (#1606)
- Fixed double spaced tweets in Post.ts (#1626)
- Added ability to select transcription provider based on character settings (#1625)
- Fixed image description service (#1667)
- Separated imageModelProvider and imageVisionModelProvider for ImageDescriptionServices (#1664)
- Updated Supabase schema.sql (#1660)
- Fixed Twitter image link issues (#1671)

#### Full Changelog
https://github.com/elizaOS/eliza/compare/v0.1.7...v0.1.8

---

## Version 0.1.7 (2025-01-04)

#### New Features
- **UI/UX**:
  - Added text to 3D function (#1446)
  - Added custom system prompt support for image generation (#839)
  - Added /:agentId/speak endpoint for text-to-speech (#1528)
  - Added Livepeer Image Provider (#1525)
  - Added autoscroll chat client (#1538)
  - Added theme toggle with dark/light mode support (#1555)

- **Plugins and Integration**:
  - Added Abstract plugin (#1225)
  - Added Avalanche plugin (#842)
  - Added Cronos ZKEVM plugin (#1464)
  - Added GitBook Plugin provider (#1126)
  - Added Venice style presets & watermark removal option (#1410)
  - Added FerePro plugin (#1502)
  - Added Fuel plugin (#1512)

- **Development**:
  - Added ModelConfiguration to Character for temperature/response control (#1455)
  - Added support for custom OpenAI API endpoint via OPENAI_API_URL (#1522)
  - Added client-github retry functionality (#1425)
  - Added dynamic watch paths for agent development (#931)
  - Added Redis Cache Implementation (#1279, #1295)

#### Client Improvements
- **Twitter**:
  - Enhanced Twitter client with cookie validation and retry (#856)
  - Improved Tweet handling for long content (#1339, #1520)
  - Enhanced Twitter Post Action Implementation (#1422)
  - Improved Twitter client dry run mode and configuration (#1498)
  - Fixed Twitter engagement criteria in prompt (#1533)

- **Discord/Telegram**:
  - Added Discord Team features (#1032)
  - Added Telegram Team features (#1033)
  - Added parse mode=Markdown for Telegram output (#1229)
  - Fixed multiple Discord bots joining voice channels (#1156)

#### Bug Fixes
- Fixed multiple agents running on localhost simultaneously (#1415)
- Fixed image model provider API key selection fallback (#1272)
- Fixed empty tags in templates/examples passed to LLM (#1305)
- Fixed postgres adapter settings not being applied (#1379)
- Fixed swap and bridge actions in plugin-evm (#1456)
- Fixed Twitter search feature (#1433)
- Fixed duplicate twitter posts (#1472)
- Fixed client type identification with test coverage (#1490)
- Fixed Twitter username validation to allow numbers (#1541)

#### Technical Improvements
- Improved TypeScript configuration with incremental option (#1485)
- Improved chat formatting for line breaks (#1483)
- Extended parseBooleanFromText function with additional values (#1501)
- Made express payload limit configurable (#1245)
- Made Twitter login retry attempts configurable (#1244)
- Added callback to the runtime evaluate method (#938)
- Synced UI Client with server port env (#1239)

#### Full Changelog
https://github.com/elizaOS/eliza/compare/v0.1.6...v0.1.7


---

## Version 0.1.7-alpha.2 (2024-12-28)

#### New Components
- Added a new default character (#1453)
- Added Text to 3D function (#1446)
- Added /:agentId/speak endpoint for text-to-speech functionality (#1528)
- Added Livepeer Image Provider for image generation (#1525)
- Added support for Custom System Prompts in plugin-image-generation (#839)

#### Content Handling
- Improved handling of long tweets (#1339, #1520)
- Enhanced Twitter Post Action Implementation (#1422)
- Added image features to react chat client (#1481)
- Improved chat formatting for line breaks (#1483)

#### Plugins
- Added GitBook Plugin provider (#1126)
- Added Abstract plugin (#1225)
- Added Avalanche plugin (#842)
- Added FerePro plugin (#1502)
- Added Cronos ZKEVM plugin (#1464)
- Added Fuel plugin (#1512)
- Added Venice style presets with option to remove watermark (#1410)
- Added AlienX chain to plugin-evm (#1438)

#### Client Improvements
- Enhanced client-github with retry capability (#1425)
- Enhanced client-direct functionality (#1479)
- Added client-discord chat_with_attachment action flexibility to use any tiktoken model (#1408)
- Implemented timeline fetching for followed accounts in Twitter client (#1475)

#### Technical Enhancements
- Added ModelConfiguration to Character for adjusting temperature, response length & penalties (#1455)
- Added support for custom OpenAI API endpoint via OPENAI_API_URL (#1522)
- Extended parseBooleanFromText function with additional boolean values (#1501)
- Added agentic JSDoc generation (#1343)
- Added support for passing secrets through environment (#1454)

####  Twitter Client
- Fixed duplicate tweet log (#1402)
- Fixed duplicate twitter post issues (#1472)
- Fixed search feature in twitter client (#1433)
- Improved Twitter client dry run mode and configuration logging (#1498)
- Improved interaction prompts in the Twitter plugin (#1469)
- Fixed client-twitter lowercase bug and environment cleanup (#1514)
- Fixed ENABLE_ACTION_PROCESSING logic in Twitter client (#1463)
- Fixed Twitter login notifications and cookie management (#1330)

####  System Issues
- Fixed multiple agents running simultaneously on localhost (#1415)
- Fixed postgres adapter settings not being applied (#1379)
- Fixed imageModelProvider API key selection fallback (#1272)
- Fixed empty tags in templates/examples when passed to LLM (#1305)
- Fixed swap and bridge actions in plugin-evm (#1456)
- Fixed incorrect link redirection issue (#1443)
- Fixed code duplication in getGoals call (#1450)
- Improved client type identification with test coverage (#1490)
- Added required incremental option and fixed TypeScript configuration (#1485)
- Fixed type imports from 'elizaos' (#1492)

####  Documentation and Testing
- Added documentation for plugin-nft-generation (#1327)
- Added readme files for ton plugin (#1496) and websearch plugin (#1494)
- Added CODE_OF_CONDUCT.md (#1487)
- Fixed documentation links in eliza-in-tee.md (#1500)
- Added Cleanstart options for new database (#1449)


#### Full Changelog
https://github.com/elizaOS/eliza/compare/v0.1.7-alpha.1...v0.1.7-alpha.2

---

## Version 0.1.7-alpha.1 (2024-12-22)

#### Core Changes
- **Package Structure**: Changed package name from `@elizaos/eliza` to `@elizaos/core` (#1357)
- **Branding**: Introduced elizaOS branding and structure (#1352)
- **Documentation**: Updated documentation links to point to https://elizaOS.github.io/eliza/ (#1353)

#### Model Support
- Added support for Google models (#1310)
- Added OLLAMA model to the getTokenForProvider class (#1338)

#### Client Improvements
- Bumped agent-twitter-client version to v0.0.17 (#1311)
- Updated farcaster client max cast length (#1347)
- Implemented MAX_TWEET_LENGTH setting for Twitter posts (#1323)
- Removed TWITTER_COOKIES environment variable (#1288)

#### Technical Fixes
- Fixed turbo configuration to resolve "cannot find package" error (#1307)
- Set default value for cache store (#1308)
- Added lint script for plugin-evm and fixed lint errors (#1171)
- Fixed postgres adapter schema (#1345)
- Removed token requirement for gaianet (#1306)

#### Technical Notes
This alpha release focuses primarily on structural changes to the codebase, renaming the core package, and fixing technical issues. It sets the groundwork for the more feature-rich alpha.2 release.

#### Full Changelog
https://github.com/elizaOS/eliza/compare/v0.1.6...v0.1.7-alpha.1

---

## Version 0.1.6-alpha.5 (2024-12-21)


#### Caching
- **Redis Integration**: Added Redis Cache Implementation (#1279)
- **Enhanced Caching**: Added general caching support for Redis (#1295)

#### Platform Enhancements
- Added parse mode=Markdown to enhance telegram bot output (#1229)
- Made scripts dash compatible for better shell compatibility (#1165)
- Made Twitter login retry times configurable via environment variables (#1244)
- Made express payload limit configurable (#1245)
- Upgraded Tavily API with comprehensive input and constrained token consumption (#1246)

#### Discord & Telegram
- Fixed issue allowing multiple bots to join Discord voice channels (#1156)
- Enabled Telegram bots to post messages with images generated by imageGenerationPlugin (#1220)

#### Model & Provider Issues
- Fixed handling of unsupported model provider: claude_vertex (#1258)
- Added missing claude vertex case to handleProvider (#1293)
- Fixed local_llama key warning (#1250)

#### Client & UI
- Fixed client.push issue for Slack client verification (#1182)
- Synced UI Client with server port environment variable (#1239)
- Fixed ENABLE_ACTION_PROCESSING logic (#1268)
- Improved Twitter post generation prompt (#1217)
- Fixed issue where twitterShouldRespondTemplate fails when defined as a string in JSON Character Config (#1242)

#### Database & Testing
- Fixed postgres requirement for user to exist before adding a participant (#1219)
- Fixed CircuitBreaker.ts implementation (#1226)
- Added integration tests fixes (#1177, #1291)
- Fixed output checkable variable for conditional tests (#1294)

#### Documentation & Internationalization
- Added German README (#1262)
- Added Twitter automation label notice documentation (#1254)
- Updated README for French, Spanish, and Italian languages (#1236)
- Updated Chinese README with more details (#1196, #1201)

#### Technical Improvements
- Fixed build and dependency issues
- Improved error handling when token retrieval fails (#1214)
- Added optional chaining on search to avoid startup errors when search is disabled (#1202)
- Improved script output with clearer command instructions (#1163, #1218)
- Fixed visibility issue for GitHub image CI/CD workflow (#1243)
- Improved handling of summary files in caching (#1205)

#### Full Changelog
https://github.com/ai16z/eliza/compare/v0.1.6-alpha.4...v0.1.6-alpha.5

---

## Version 0.1.6 (2024-12-21)


#### Blockchain & Web3 Integration
- **New Blockchain Plugins**:
  - Added Flow Blockchain plugin (#874)
  - Added Aptos plugin (#818)
  - Added MultiversX plugin (#860)
  - Added NEAR Protocol plugin (#847)
  - Added TON plugin (#1039)
  - Added ZKsync Era plugin (#906)
  - Added SUI plugin (#934)
  - Added TEE Mode to Solana Plugin (#835)
  - Enabled agents to create/buy/sell tokens on FOMO.fund's bonding curve in plugin-solana (#1135)

- **Coinbase Integration**:
  - Added Coinbase ERC20, ERC721, ERC1155 token deployment/invocation (#803)
  - Implemented advanced Coinbase trading functionality (#725)
  - Added readContract/invokeContract functionality (#923)
  - Added webhook support and testing examples (#801)

#### Social Media & Messaging
- **Twitter/X Improvements**:
  - Enhanced X/Twitter login with cookie validation and retry mechanism (#856)
  - Improved Twitter client with action processing (#1007)
  - Fixed Twitter Search Logic (#994)
  - Implemented MAX_TWEET_LENGTH environment variable (#912)
  - Fixed issues with Twitter posts including newlines (#1070, #1141)
  - Allowed bots to post tweets with images from imageGenerationPlugin (#1040)

- **New Clients**:
  - Added working Farcaster client with Neynar integration (#570, #914)
  - Added LinkedIn Client (#973)
  - Added Lens client (#1098)
  - Implemented Discord and Telegram Team features (#1032, #1033)

#### AI & Model Support
- **Model Providers**:
  - Added NanoGPT provider (#926)
  - Added Galadriel Image Model (#994)
  - Added Akash.network provider for free LLAMA API access (#1131)
  - Added Venice.ai API model provider (#1008) and image generation (#1057)
  - Added Hyperbolic API (#828) with environment variable overrides (#974)
  - Configured EternalAI model from environment variables (#927)

- **Voice & Media**:
  - Improved voice processing and added Deepgram transcription option (#1026)
  - Added support for handlebars templating engine (#1136)
  - Added client-discord stop implementation (#1029)
  - Added NFT generation plugin for Solana collections (#1011)
  - Added plugin-story for narrative generation (#1030)

#### System Improvements
- **Caching & Infrastructure**:
  - Implemented Redis Cache (#1279, #1295)
  - Added circuit breaker pattern for database operations (#812)
  - Added support for AWS S3 file uploads (#941)
  - Added dynamic watch paths for agent development (#931)
  - Fixed multiple bots joining Discord voice channels (#1156)

- **API & Interface**:
  - Added REST API for client-direct to change agent settings (#1052)
  - Added custom fetch logic for agent (#1010)
  - Fixed Twitter posts with images generated by plugins (#1040)
  - Made express payload limit configurable (#1245)
  - Added callback handler to runtime evaluate method (#938)

#### Testing & Development Improvements
- Implemented Smoke Test scripts (#1101)
- Added initial release of smoke/integration tests + testing framework (#993)
- Enabled test coverage reporting to Codecov (#880, #1019)
- Enhanced GitHub image CI/CD workflow (#889)
- Improved development scripts with better help messages (#887, #892)
- Created example folder with example plugin (#1004)
- Allowed users to configure models for Groq (#910), Grok (#1091), OpenAI and Anthropic (#999)
- Added plugin for EVM multichain support (#1009)

#### Bug Fixes
- Fixed issues with Twitter client login and auth (#1158)
- Fixed direct-client ability to start agents (#1154)
- Fixed plugin loading from character.json files (#784)
- Fixed parameter parsing in plugin-evm TransferAction (#965)
- Fixed various client issues (Slack, Discord, Telegram, Farcaster)
- Fixed model provider issues for Claude Vertex (#1258, #1293)
- Fixed Twitter post generation and interaction (#1217, #1242)
- Fixed telegram response memory userId to agentId (#948)

#### Documentation & Internationalization
- Added README translations (German, Vietnamese, Thai)
- Added templates documentation (#1013)
- Added WSL Setup Guide (#983)
- Added README for plugin-evm (#1095)
- Added documentation for community section (#1114)

#### Full Changelog
https://github.com/ai16z/eliza/compare/v0.1.5...v0.1.6

---

## v0.1.6-alpha.4 (2024-12-17)

#### Key Changes
- Fixed Twitter client login and authentication handling (#1158)

## v0.1.6-alpha.3 (2024-12-17)

#### Key Changes
- Added package version update script (#1150)
- Set fetch log level to debug for improved troubleshooting (#1153)
- Fixed direct-client functionality for starting agents (#1154)

## v0.1.6-alpha.2 (2024-12-17)

#### Major Features
- **Blockchain & DeFi:**
  - Added FOMO.fund token creation/trading in plugin-solana (#1135)
  - Added support for multiple blockchain platforms:
    - MultiversX plugin (#860)
    - NEAR Protocol plugin (#847)
    - TON plugin (#1039)
    - SUI plugin (#934)
    - ZKsync Era plugin (#906)
  - Enhanced EVM with multichain support (#1009)

- **Client & Social Interaction:**
  - Added Discord and Telegram Team features (#1032, #1033)
  - Added Lens client integration (#1098)
  - Improved X/Twitter login with cookie validation and retry (#856)
  - Enhanced Twitter client with action processing (#913)
  - Added Slack plugin (#859)

- **Development & Testing:**
  - Added Smoke Test script infrastructure (#1101)
  - Added REST API for client-direct configuration (#1052)
  - Added GitHub image CI/CD workflow (#889)

- **Content Creation:**
  - Added plugin-story for narrative generation (#1030)
  - Added plugin-nft-generation for Solana NFT collections (#1011)
  - Added Venice.ai image generation support (#1057)
  - Added support for handlebars templating engine (#1136)

#### Notable Fixes
- Fixed telegram and discord client duplicate functions (#1140, #1125)
- Improved FOMO integration for better performance (#1147)
- Fixed parameter parsing in plugin-evm TransferAction (#965)
- Fixed Twitter posts to remove newline characters (#1070, #1141)
- Enabled bots to post tweets with images from imageGenerationPlugin (#1040)
- Added helpful default agents (Dobby and C3PO) (#1124)

## v0.1.6-alpha.1 (2024-12-13)

#### Major Features
- **Blockchain & Web3:**
  - Added Flow Blockchain plugin (#874)
  - Added TEE Mode to Solana Plugin (#835)
  - Enhanced Coinbase plugin with advanced trading (#725)
  - Added readContract/invokeContract functionality (#923)

- **Model Providers:**
  - Added NanoGPT provider (#926)
  - Added Venice.ai API model provider (#1008)
  - Added Hyperbolic API integration (#828) with env var overrides (#974)
  - Added configuration for EternalAI model from environment (#927)

- **Development Tools:**
  - Added callback handler to runtime evaluate method (#938)
  - Added dynamic watch paths for agent development (#931)
  - Added custom fetch logic for agent (#1010)
  - Created example folder with sample plugin (#1004)

- **Media & Content:**
  - Improved voice processing with Deepgram transcription (#1026)
  - Added MAX_TWEET_LENGTH environment variable control (#912)

#### Key Fixes
- Fixed Twitter Search Logic and added Galadriel Image Model (#994)
- Fixed Telegram response memory userId to agentId (#948)
- Improved Farcaster client response logic (#914, #963)
- Corrected EVM plugin activation condition (#962)
- Re-enabled generateNewTweetLoop (#1043)

#### Documentation
- Added templates documentation (#1013)
- Added Thai (TH) README translation (#918)
- Added WSL Setup Guide (#983)
- Added AI Agent Dev School Tutorial Link (#1038)

---

## v0.1.5-alpha.5 (December 07, 2024)

#### What's Changed
* feat: working farcaster client

#### Full Changelog
https://github.com/ai16z/eliza/compare/v0.1.5-alpha.4...v0.1.5-alpha.5

---

## v0.1.5-alpha.4 (2024-12-06)

- **Blockchain & Web3:**
  - Added Coinbase ERC20, ERC721, and ERC1155 token deployment/invocation plugin (#803)
  - Added Coinbase webhook functionality with examples and testing (#801)
  - Added Aptos blockchain plugin (#818)

- **Model & Performance:**
  - Configured system to use LARGE models for responses (#853)
  - Added Google model environment variables (#875)

- **Testing & Documentation:**
  - Added environment and knowledge tests (#862)
  - Added AI Agent Dev School summaries and timestamps (#877)
  - Updated quickstart documentation with common issue solutions (#861, #872)
  - Fixed plugins documentation (#848)
  - Updated Node version in local-development.md (#850)

#### Full Changelog
https://github.com/ai16z/eliza/compare/v0.1.5-alpha.3...v0.1.5-alpha.4

---

## v0.1.5-alpha.3 (2024-12-04)

- **Core Infrastructure:**
  - Added circuit breaker pattern for database operations (#812)
  - Fixed Twitter cache expiration issues (#824)
  - Pinned all node dependencies and updated @solana/web3.js to safe version (#832)

- **Development Workflow:**
  - Fixed lerna publish command (#811)
  - Fixed Docker setup documentation (#826)
  - Reverted viem package version (#834)
  - Bumped @goat-sdk/plugin-erc20 version (#836)

#### Full Changelog
https://github.com/ai16z/eliza/compare/v0.1.5-alpha.0...v0.1.5-alpha.3

---

## v0.1.5-alpha.0 (2024-12-03)

- **Plugin System:**
  - Fixed plugin loading when configured with plugin name in character.json (#784)
  - Improved actions samples random selection (#799)

- **Image Generation:**
  - Fixed TOGETHER/LLAMACLOUD image generation (#786)

- **Platform Improvements:**
  - Made Docker use non-interactive mode for Cloud instances (#796)
  - Fixed swap type error and user trust creation on first Telegram message (#800)
  - Made UUID compatible with number types (#785)

- **Development Infrastructure:**
  - Updated npm publication workflow (#805, #806, #807)
  - Fixed dev command (#793)
  - Fixed environment typo (#787)
  - Updated Korean README to match latest English version (#789)


#### Full Changelog
https://github.com/ai16z/eliza/compare/v0.1.5...v0.1.5-alpha.0
