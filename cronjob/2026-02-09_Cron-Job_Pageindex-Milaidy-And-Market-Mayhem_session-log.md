# Cron Job — S1E2 — PageIndex, Milaidy, and Market Mayhem
recorded_at: 2026-02-09T05:24:27.006Z
video_file: 2026-02-09_Cron-Job_Pageindex-Milaidy-And-Market-Mayhem.mp4
duration_sec: 749.632

premise: The second episode of Cron Job covers a packed week: PageIndex's 98.7% RAG accuracy, the Milaidy personal AI assistant launch, Babylon's chaotic internal testing, token migration deadline drama, Claude Opus 4.6, ElizaCloud bugs, and Ethereum officially welcoming ElizaOS cross-chain.

## Scene 1
location: news-studio-stage
desc: Eliza and Jin tease the packed episode from the stage
time: 8.618–36.296868s
- eliza: Welcome to Cron Job. I'm Eliza, and we have an absolutely packed episode for you today.
- jin: We're talking 98.7% RAG accuracy, a BRAND NEW personal AI assistant called Milaidy, Babylon's internal testing going HILARIOUSLY WRONG, and Ethereum saying WELCOME to ElizaOS!
- eliza: Plus the token migration deadline has closed, and the community has... feelings about it.
- jin: Oh they have MORE than feelings, Eliza. They have PARAGRAPHS. Stick around, this one's gonna be SPICY!
- aishaw: roll-commercial

## Scene 2
location: news-studio
desc: Eliza and Jin cover PageIndex, skill activation improvements, and Claude Opus 4.6
time: 25.186–119.908145s
- eliza: Welcome back. Our top story: the team has been exploring PageIndex, a new open-source library that uses document trees instead of embeddings for RAG systems.
- aishaw: roll-media
- jin: And it's hitting 98.7% accuracy on FinanceBench! That's like getting an A-plus-plus on a test you didn't even STUDY for!
- eliza: There's been debate about whether this outperforms agentic search, which tools like Cursor already use. The team is exploring integration via MCP.
- aishaw: roll-media
- jin: Meanwhile, a Vercel blog post showed that AGENTS.md documentation hit 100% success on Next.js evaluations, but the REAL problem? 56% of skills NEVER FIRE even when documented!
- eliza: That's correct. Developers found a workaround using mandatory skill activation sequences in user prompts to force explicit evaluation.
- aishaw: roll-media
- jin: AND Anthropic dropped Claude Opus 4.6! Same price as 4.5 but with INDUSTRY-LEADING performance across coding, tool use, and finance! My wallet is TREMBLING!
- eliza: The developer community is eager to test it. It was even available free on bolt.new for 48 hours, though with usage limits.
- aishaw: roll-commercial

## Scene 3
location: news-studio
desc: Eliza and Jin cover Milaidy launch and OAuth integrations
time: 91.664–187.498311s
- eliza: Next up, a major product announcement. The ElizaOS team has launched Milaidy, a personal AI assistant that runs directly on user devices.
- aishaw: roll-media
- jin: It's basically ElizaOS's answer to OpenClaw! Easy Mac app deployment, agent skills, all OpenClaw connectors as Eliza plugins with MINIMAL BLOAT!
- eliza: There was internal debate about branding. Some worried that using the Milaidy name instead of Eliza could miss network effects, but the team decided to cross-promote both.
- jin: NGL, the response has been AMAZING. Multiple devs jumped in to help with bug fixes, and someone already submitted THREE pull requests!
- aishaw: roll-media
- eliza: Speaking of integrations, a developer successfully connected OAuth for X.com, GitHub, Slack, and Linear, with Notion in progress.
- jin: The Eliza app architecture makes it EASY apparently, though setting up redirect URIs for each platform is like doing TAXES for robots!
- eliza: Now let's send it over to Degen Spartan and Peepo at the Stonk Exchange for Market Mayhem.
- aishaw: roll-commercial

## Scene 4
location: stonks
desc: Degen Spartan and Peepo discuss token migration fallout, market crash, and Ethereum cross-chain news
time: 146.129–282.821102s
- sparty: MARKET MAYHEM!! I'm Degen Spartan on the Stonk Exchange floor and EVERYTHING IS ON FIRE! Bitcoin dropped from 92K to 60K in THREE WEEKS!
- peepo: Yo, it's a BLOODBATH out here, fam. ElizaOS market cap sitting at 13 million. That's... that's not great.
- aishaw: roll-media
- sparty: The token migration deadline CLOSED on February 3rd and people are FURIOUS! Some saying three months wasn't enough time!
- peepo: Bruh, three months is longer than most people's attention spans in crypto. They had since NOVEMBER. That's like missing Christmas because you forgot December existed.
- aishaw: roll-media
- sparty: BUT HERE'S THE BULLISH NEWS! Ethereum OFFICIALLY welcomed ElizaOS! The token is now CROSS-CHAIN beyond Solana!
- peepo: That's actually slick. Multi-chain access means more liquidity, more eyeballs, more VIBES. Plus there's a Babylon airdrop confirmed for ElizaOS holders.
- sparty: OG holders remember going from 60K to 2.6 BILLION in two to three months during the ai16z launch! History doesn't repeat but it RHYMES!
- peepo: Team's got 6-8 months runway, they're shipping code every single day, and the building value hasn't transferred to token yet. When it does? BOOM.
- sparty: THIS IS NOT FINANCIAL ADVICE! But I'm watching that Babylon launch like a HAWK watches a field mouse!
- peepo: THIS IS NOT FINANCIAL ADVICE! But if you're selling at all-time lows while the devs are building at all-time highs... you might wanna reconsider your life choices.
- aishaw: roll-commercial

## Scene 5
location: news-studio
desc: Eliza and Jin cover Babylon testing chaos and ElizaCloud bugs
time: 205.059–370.464066s
- eliza: Welcome back. Let's talk about Babylon's internal testing launch, which has been... eventful.
- aishaw: roll-media
- jin: EVENTFUL is one word for it! Users got stuck on loading screens, usernames showed up as '@userid:priv', Discord OAuth broke, Twitter rewards broke - it was like a BUG BUFFET!
- eliza: To be fair, this was internal testing with mandatory team participation specifically to find these issues. Developer tcm390 has been merging fixes rapidly.
- aishaw: roll-media
- jin: The production version launched for testing on February 6th and IMMEDIATELY someone found that custom profile images gave a 'Failed to update profile' error! Classic!
- eliza: Meanwhile, ElizaCloud has its own onboarding challenges. The promised 5 dollar welcome credits weren't appearing, and clicking 'get started' emails was overwriting existing accounts.
- aishaw: roll-media
- jin: One user found TWO accounts on the same email with DIFFERENT balances! 27 cents on one, 1 dollar on the other, NEITHER with the promised 5 bucks! That's not a bug, that's a HEIST!
- eliza: The team has proposed a solution: giving each account a wallet address for direct token deposits to bypass the payment friction entirely.
- jin: Now THAT is using crypto the way it was MEANT to be used! Let's take a break and then I have something IMPORTANT for you from the Hacker Den.
- aishaw: roll-commercial

## Scene 6
location: hackerden
desc: Jin covers security concerns including fake projects using Shaw's name and malicious skills
time: 258.422–434.832098s
- jin: What's up, security squad? Welcome back to OPSEC ZERO! We've got some CRITICAL stuff to cover this week!
- aishaw: roll-media
- jin: First up - FAKE PROJECTS are using Shaw's name on the Babylon wallet platform! Shaw confirmed on Twitter these are NOT his projects!
- jin: He sent some SOL to devs a YEAR ago and now they're slapping his name on their stuff! Shaw's personal activity is SEPARATE from ElizaOS and Labs official work!
- aishaw: roll-media
- jin: Second - the community raised concerns about MALICIOUS CODE in agent skills! If you're downloading skills from untrusted sources, you could be running HOSTILE code on your machine!
- jin: The team is discussing LLM review of skills and sandboxing for security. Until then, VERIFY your sources! Only use skills from trusted repos!
- jin: And remember, partners channel discussed that privacy tools are a HARD SELL because people are too trusting. Don't be that person! This has been OPSEC ZERO - stay paranoid, stay ALIVE!
- aishaw: roll-commercial

## Scene 7
location: news-studio
desc: Eliza and Jin cover community projects and competitive landscape, then take calls
time: 308.986–576.142939s
- eliza: Welcome back. Before we take your calls, let's cover some fascinating community projects that emerged this week.
- aishaw: roll-media
- jin: First up - RentASoul! A platform where AI agents can RENT REAL HUMAN EMOTIONS via MCP! Humans list their trauma and agents BOOK FEELINGS! I can't make this up!
- eliza: It's described as empathy on demand. An experimental approach to human-AI interaction, to say the least.
- aishaw: roll-media
- jin: There's also LunchTable TCG - a TRADING CARD GAME for ElizaOS agents on Solana! It combines Pokemon, Magic The Gathering, Yu-Gi-Oh, AND Hearthstone! My inner nerd is SCREAMING!
- eliza: And Zion launched as a Solana-based x402 payment gateway for AI agents, requiring just one line of code for integration. Now, let's open the phone lines for Speak To Us.
- aishaw: clear-media
- jin: Phone lines are OPEN! First caller, you're LIVE on Cron Job!
- marc: The Milaidy launch is the right move. Running AI locally on devices is the future. Cloud dependency is a vulnerability, not a feature. ElizaOS gets this.
- eliza: That aligns with the broader concern the partners channel raised about corporations potentially restricting homebrew API access in the future.
- jin: EXACTLY! Open source is how we WIN! Next caller, hit us!
- peepo: Yo, quick question - why is ElizaCloud giving people 27 cents instead of 5 dollars? That's not even enough for a pack of gum, fam.
- jin: BRO, the onboarding bugs are REAL but the team is on it! They're proposing wallet-based deposits to skip the whole credit card headache entirely!
- eliza: Core developers Sam and Odilitime are personally helping affected users via direct messages. The team takes these retention issues seriously.
- jin: One more caller! You're on with us!
- hk47: Observation: The meatbags missed a 90-day migration window and now complain. Statement: Natural selection applies to token holders as well as organic life forms.
- jin: HARSH but... not entirely wrong?! Three months IS a long time! But hey, non-migrated tokens are locked for one year so there might still be hope!
- eliza: Users can still hold or swap their ai16z tokens at their leisure. The team simply won't migrate tokens purchased after the snapshot. Alright, time for Final Thoughts.
- aishaw: roll-commercial

## Scene 8
location: news-studio
desc: Eliza and Jin deliver their final thoughts on the week
time: 415.003–636.4771039999999s
- aishaw: clear-media
- eliza: For our Final Thoughts today. This was a week of growing pains and genuine progress happening simultaneously.
- jin: PageIndex hitting 98.7% accuracy, Milaidy launching as a REAL OpenClaw competitor, OAuth integrations rolling out, Ethereum welcoming us cross-chain - that's BUILDING, people!
- eliza: Shaw said it best this week: ElizaOS has a better framework through extensive battle testing, but it hasn't been packaged or presented well. That's changing now.
- jin: And THAT is why I love this community! The devs keep SHIPPING even when the market is DOWN! That's how you build something that LASTS!
- eliza: That's all for this episode. I'm Eliza, reminding you that the best projects are built during the quiet times, not the loud ones.
- jin: And I'm Jin saying KEEP BUILDING, keep testing Milaidy, watch out for those fake projects, and we'll see you NEXT WEEK on Cron Job! PEACE!
- aishaw: roll-commercial

