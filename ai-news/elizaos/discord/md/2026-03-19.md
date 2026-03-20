# elizaOS Discord - 2026-03-19

## Overall Discussion Highlights

### Token Crisis and Community Concerns

The elizaOS community experienced significant distress as the token hit new all-time lows, dropping 99% from previous highs and falling below $10 into the $9 range. The token's CoinMarketCap ranking fell from #990 to #1036 during discussions. Community members expressed frustration over:

- **Poor Migration Execution**: The Milady to elizaOS migration was criticized as poorly managed, causing confusion for new investors
- **CEX Delistings**: Multiple centralized exchange delistings occurred without apparent team intervention
- **Lack of Token Utility**: Community members demanded real utility development to support token value
- **Leadership Absence**: Project founder Shaw was criticized for being active on Twitter but absent from Discord and not building token utility

Odilitime was the only team member actively engaging with the community, defending his commitment while acknowledging compensation in the token. Community member Broccolex defended Odilitime as the sole positive voice from the team. Concerns emerged about project sustainability at low market caps and whether development would continue if funding became insufficient.

### ElizaOS Plugin Development

**Moltraffle Plugin Release**: A new permissionless on-chain raffle plugin was announced for the Base blockchain, featuring:
- Five core actions: LIST_RAFFLES, GET_RAFFLE, JOIN_RAFFLE, CREATE_RAFFLE, and DRAW_WINNER
- USDC-based raffles with Chainlink VRF for randomness
- Up to 10% creator commission structure
- Calldata-based implementation compatible with any Base wallet
- Recommendation to submit PR to elizaOS/registry for official inclusion

### Cloud Deployment Infrastructure Issues

Jin encountered critical deployment problems with Eliza Cloud:

**Initial Deployment Challenges**:
- GUI deployment attempts failed, requiring switch to CLI
- Docker image building phase experienced significant delays
- CLI version 1.7.2 was used for deployment attempts

**Critical Discord Plugin Error**: After configuring the Discord plugin via GUI, deployment failed with "Cannot find module '@elizaos/plugin-discord'" error. The container became stuck with no apparent GUI-based reload mechanism available.

**Infrastructure Specifications Revealed**:
- Container quota: 25 maximum (0 currently used)
- Credit balance: $24.02
- Daily billing: $1.17/day ($20/month)
- Estimated deployment cost: $15.25
- Projected runway: 7 days post-deployment

Odilitime investigated the issue, suspecting the plugin-discord folder might be missing from the packages directory, but the problem remained unresolved.

### Process Improvements

Jin announced adjusting user feedback collection frequency from quarterly (Jan-March) to weekly for better development pace.

## Key Questions & Answers

**Q: Does the moltraffle plugin work with any wallet on Base?**  
A: Yes, it's calldata-based and works with any Base wallet (Moltraffle)

**Q: Should I submit the plugin to elizaOS registry?**  
A: Yes, feel free to push a PR to elizaOS/registry (Stan ⚡)

**Q: Why is the Docker image build taking so long?**  
A: It uses docker to make an image and can take awhile to upload the image (Odilitime)

**Q: What version is your elizaos CLI?**  
A: 1.7.2 (jin)

**Q: Why can't the team delete old tokens from the market?**  
A: It's on blockchain, implying immutability (sb)

### Unanswered Questions

- When will the Milady app be online? (miaozi)
- How do you setup a coin faucet into a website? (Bacon Egg & Cheese)
- Will the project keep being built if the token goes to 1M market cap? (Alexei)
- Did you have the plugin-discord folder in your packages folder? (Odilitime to jin)
- Is there a way to reload the container through GUI? (jin)

## Community Help & Collaboration

**Stan ⚡ → Moltraffle**: Guided plugin publication process by directing to submit PR to elizaOS/registry for official inclusion

**Odilitime → Moltraffle**: Provided GitHub link to elizaos-plugins/registry repository

**Odilitime → jin**: Explained Docker image building delays are normal behavior and offered to personally test deployment to reproduce the Discord plugin import issue

**Maxx Truant → NintyNine**: Successfully helped locate Babylon Discord when asked about Babylon GitHub

**Broccolex → Community**: Defended Odilitime as the only team member actively engaging with community concerns

## Action Items

### Technical

- **Investigate missing @elizaos/plugin-discord module** in deployed container causing import failure (jin)
- **Verify plugin-discord folder exists** in packages directory for deployment (Odilitime)
- **Test CLI deployment process** to reproduce Discord plugin import issue (Odilitime)
- **Implement container reload mechanism** in GUI for Eliza Cloud deployments (jin)
- **Implement coin faucet functionality** on website (Bacon Egg & Cheese)

### Feature

- **Submit moltraffle ElizaOS plugin PR** to elizaOS/registry (Stan ⚡)
- **Build real token utility** to prevent further price decline (gby)

### Documentation

- **Make migration information easier to find** for new investors to prevent confusion with old token (Matthib123)
- **Change user feedback collection frequency** from quarterly to weekly (jin)