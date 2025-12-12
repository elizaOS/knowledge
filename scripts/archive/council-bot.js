const { Client, GatewayIntentBits, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');
const fs = require('fs');

// Create a new client instance
const client = new Client({ 
  intents: [
    GatewayIntentBits.Guilds, 
    GatewayIntentBits.GuildMessages
  ]
});

// Bot configuration
const TOKEN = process.env.DISCORD_BOT_TOKEN;
const BRIEFING_FILE = process.env.BRIEFING_FILE || '../the-council/council_briefing/daily.json';

// List of channel IDs to post to (can be multiple)
const TARGET_CHANNEL_IDS = (process.env.TARGET_CHANNEL_IDS || '').split(',').filter(id => id.trim() !== '');

// Colors for different strategic points
const COLORS = [0x2026ad, 0xe67e22, 0x9b59b6, 0x2ecc71];  // Blue, Orange, Purple, Green
const NUMBER_EMOJIS = ['1️⃣', '2️⃣', '3️⃣', '4️⃣'];

// Store vote data
const votes = {
  // Format: { userId: pointIndex, ... }
};

// Store vote counts
const voteCounts = [0, 0, 0, 0];

client.once('ready', async () => {
  console.log(`Logged in as ${client.user.tag}`);
  
  // Post to all target channels if IDs are provided
  if (TARGET_CHANNEL_IDS.length > 0) {
    try {
      for (const channelId of TARGET_CHANNEL_IDS) {
        try {
          const channel = await client.channels.fetch(channelId);
          await postOverview(channel);
          console.log(`Posted to channel ${channelId}`);
        } catch (error) {
          console.error(`Error posting to channel ${channelId}:`, error);
        }
      }
    } catch (error) {
      console.error('Error in main posting process:', error);
    }
  }
});

// Handle button interactions
client.on('interactionCreate', async interaction => {
  if (!interaction.isButton()) return;
  
  // Handle info buttons
  if (interaction.customId.startsWith('point_')) {
    const pointIndex = parseInt(interaction.customId.split('_')[1]);
    await showDetailedPoint(interaction, pointIndex);
  }
  
  // Handle vote buttons
  if (interaction.customId.startsWith('vote_')) {
    const pointIndex = parseInt(interaction.customId.split('_')[1]);
    await handleVote(interaction, pointIndex);
  }
  
  // Handle show votes button
  if (interaction.customId === 'show_votes') {
    await showVotes(interaction);
  }
});

async function postOverview(channel) {
  // Reset vote counts for a new day
  for (let i = 0; i < voteCounts.length; i++) {
    voteCounts[i] = 0;
  }
  Object.keys(votes).forEach(key => delete votes[key]);
  
  // Read the briefing data
  const briefingData = JSON.parse(fs.readFileSync(BRIEFING_FILE, 'utf8'));
  
  // Extract the monthly goal part after the colon if present
  const monthlyGoal = briefingData.monthly_goal.split(':', 1)[1]?.trim() || briefingData.monthly_goal;
  
  // Create header embed with monthly goal included
  const headerEmbed = new EmbedBuilder()
    .setTitle(`🧠 Council Briefing – ${briefingData.date}`)
    .setDescription(`${briefingData.daily_focus_theme}\n\n**Monthly Goal:** ${monthlyGoal}`)
    .setColor(COLORS[0])
    .setAuthor({
      name: 'JEDAI COUNCIL DAILY',
      url: 'https://hackmd.io/@elizaos/book'
    })
    .setThumbnail('https://m3-org.github.io/avatars/eliza/thumb-bust_eliza.png');
  
  // Create an embed for each strategic point with just the questions
  const pointEmbeds = briefingData.key_strategic_points.map((point, i) => {
    // Join questions with a space
    let description = point.potential_council_questions.join(' ');
    
    return new EmbedBuilder()
      .setTitle(`${NUMBER_EMOJIS[i]} ${point.theme}`)
      .setDescription(description)
      .setColor(COLORS[i % COLORS.length]);
  });
  
  // Add a footer to the last embed
  if (pointEmbeds.length > 0) {
    pointEmbeds[pointEmbeds.length-1].setFooter({
      text: `Click below to expand any topic or vote for what you find most important • ${briefingData.date}`
    });
  }
  
  // Create buttons for expansion
  const infoButtons = briefingData.key_strategic_points.map((point, i) => {
    return new ButtonBuilder()
      .setCustomId(`point_${i}`)
      .setLabel(`Info ${i+1}`)
      .setStyle(ButtonStyle.Secondary);
  });
  
  // Create buttons for voting
  const voteButtons = briefingData.key_strategic_points.map((point, i) => {
    return new ButtonBuilder()
      .setCustomId(`vote_${i}`)
      .setLabel(`Vote ${i+1}`)
      .setStyle(ButtonStyle.Primary);
  });
  
  // Add a button to show current votes
  const showVotesButton = new ButtonBuilder()
    .setCustomId('show_votes')
    .setLabel('View Results')
    .setStyle(ButtonStyle.Success);
  
  // Create two action rows
  const infoRow = new ActionRowBuilder().addComponents(infoButtons);
  const voteRow = new ActionRowBuilder().addComponents([...voteButtons, showVotesButton]);
  
  // Send the message with embeds and buttons
  await channel.send({
    embeds: [headerEmbed, ...pointEmbeds],
    components: [infoRow, voteRow]
  });
}

async function showDetailedPoint(interaction, pointIndex) {
  // Read the briefing data
  const briefingData = JSON.parse(fs.readFileSync(BRIEFING_FILE, 'utf8'));
  
  // Make sure the point index is valid
  if (pointIndex < 0 || pointIndex >= briefingData.key_strategic_points.length) {
    await interaction.reply({ content: 'Invalid point index', ephemeral: true });
    return;
  }
  
  const point = briefingData.key_strategic_points[pointIndex];
  
  // Create embeds for the full details
  const detailEmbed = new EmbedBuilder()
    .setTitle(`${NUMBER_EMOJIS[pointIndex]} ${point.theme}`)
    .setDescription(`${point.summary}`)
    .setColor(COLORS[pointIndex % COLORS.length])
    .setAuthor({
      name: 'JEDAI COUNCIL DETAILS',
      url: 'https://hackmd.io/@elizaos/book'
    });
    
  const contextEmbed = new EmbedBuilder()
    .setTitle('Supporting Evidence')
    .setDescription(point.related_operational_context.map(ctx => `• ${ctx}`).join('\n'))
    .setColor(COLORS[pointIndex % COLORS.length]);
    
  const questionsEmbed = new EmbedBuilder()
    .setTitle('Discussion Questions')
    .setDescription(point.potential_council_questions.map((q, i) => `${i+1}. ${q}`).join('\n\n'))
    .setColor(COLORS[pointIndex % COLORS.length])
    .setFooter({
      text: `Click a Vote button to vote for the topic you find most important - one vote per day • ${briefingData.date}`
    });
  
  // Reply with ephemeral message
  await interaction.reply({ 
    embeds: [detailEmbed, contextEmbed, questionsEmbed],
    ephemeral: true
  });
}

async function handleVote(interaction, pointIndex) {
  // Read the briefing data
  const briefingData = JSON.parse(fs.readFileSync(BRIEFING_FILE, 'utf8'));
  
  // Make sure the point index is valid
  if (pointIndex < 0 || pointIndex >= briefingData.key_strategic_points.length) {
    await interaction.reply({ content: 'Invalid point index', ephemeral: true });
    return;
  }
  
  const userId = interaction.user.id;
  
  // Check if the user has already voted
  if (votes[userId] !== undefined) {
    const previousVote = votes[userId];
    
    // If voting for the same point, just acknowledge
    if (previousVote === pointIndex) {
      await interaction.reply({ 
        content: `You've already voted for **${briefingData.key_strategic_points[pointIndex].theme}**`,
        ephemeral: true
      });
      return;
    }
    
    // Otherwise, change their vote
    voteCounts[previousVote]--;
    voteCounts[pointIndex]++;
    votes[userId] = pointIndex;
    
    await interaction.reply({ 
      content: `Vote changed from **${briefingData.key_strategic_points[previousVote].theme}** to **${briefingData.key_strategic_points[pointIndex].theme}**`,
      ephemeral: true
    });
  } else {
    // First time voting
    voteCounts[pointIndex]++;
    votes[userId] = pointIndex;
    
    await interaction.reply({ 
      content: `Vote recorded for **${briefingData.key_strategic_points[pointIndex].theme}**`,
      ephemeral: true
    });
  }
}

async function showVotes(interaction) {
  // Read the briefing data
  const briefingData = JSON.parse(fs.readFileSync(BRIEFING_FILE, 'utf8'));
  
  // Create voting results embed
  const votingEmbed = new EmbedBuilder()
    .setTitle(`Voting Results – ${briefingData.date}`)
    .setColor(COLORS[0])
    .setAuthor({
      name: 'JEDAI COUNCIL VOTES',
      url: 'https://hackmd.io/@elizaos/book'
    });
  
  // Add fields for each point with vote count
  briefingData.key_strategic_points.forEach((point, i) => {
    const count = voteCounts[i] || 0;
    votingEmbed.addFields({
      name: `${NUMBER_EMOJIS[i]} ${point.theme}`,
      value: `**${count} vote${count === 1 ? '' : 's'}**`,
      inline: false
    });
  });
  
  // Add total votes
  const totalVotes = voteCounts.reduce((a, b) => a + b, 0);
  votingEmbed.setFooter({
    text: `Total votes: ${totalVotes} • ${briefingData.date}`
  });
  
  // Reply with ephemeral message (only visible to the person who clicked)
  await interaction.reply({ 
    embeds: [votingEmbed],
    ephemeral: true  // Make votes private to avoid chat clutter
  });
}

// Command to manually post the overview to specific channels
client.on('messageCreate', async message => {
  // Only respond to messages from non-bots
  if (message.author.bot) return;
  
  // Command to post the overview to the current channel
  if (message.content === '!council-brief') {
    await postOverview(message.channel);
  }
  
  // Command to post to multiple channels
  if (message.content.startsWith('!council-brief-multi')) {
    const args = message.content.split(' ');
    if (args.length >= 2) {
      const channelIds = args.slice(1);
      
      for (const channelId of channelIds) {
        try {
          const channel = await client.channels.fetch(channelId);
          await postOverview(channel);
          await message.channel.send(`Posted to <#${channelId}>`);
        } catch (error) {
          await message.channel.send(`Error posting to channel ${channelId}: ${error.message}`);
        }
      }
    } else {
      await message.channel.send('Please provide at least one channel ID');
    }
  }
});

// Login to Discord
client.login(TOKEN);
