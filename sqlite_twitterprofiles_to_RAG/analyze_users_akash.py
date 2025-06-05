import pandas as pd
import requests
import json
from collections import defaultdict
import aiosqlite
import asyncio
import os
import glob
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
USE_OLLAMA = os.getenv('OLLAMA_ENABLED', 'false').lower() == 'true'
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen3:4b')
OLLAMA_API_URL = os.getenv('OLLAMA_API_URL', 'http://localhost:11434/api/generate')
AKASH_API_URL = os.getenv('AKASH_API_URL', 'https://chatapi.akash.network/api/v1/chat/completions')

async def get_user_tweets():
    async with aiosqlite.connect('db.sqlite') as db:
        cursor = await db.execute('''
            SELECT a.username, m.content 
            FROM memories m 
            JOIN accounts a ON m.userId = a.id 
            WHERE m.type IN ('tweets', 'messages')
            ORDER BY m.createdAt DESC
        ''')
        rows = await cursor.fetchall()
        return rows

def get_analysis(text):
    prompt = f"""Analyze the following tweets/messages and provide a brief summary of:
1. Main topics/themes discussed
2. Language style and tone
3. Evaluation of legitness
4. Which Ecosystem or project the account advertises, if applicable
5. Evaluation of the author's character, including:
   - Personality traits evident from communication style
   - Potential motivations and values
   - Emotional patterns and tendencies
   - Decision-making approach
Put some tweets from the person into bigger context of his intentions.

Content:
{text}

Keep the response concise and focused on the most distinctive patterns.
Generate and append 5 matching keywords/tags for better postprocessing"""
    
    if USE_OLLAMA:
        return get_ollama_analysis(prompt)
    else:
        return get_akash_analysis(prompt)

def get_akash_analysis(prompt):
    try:
        headers = {
            'Authorization': f'Bearer {os.getenv("AKASH_CHAT_API_KEY")}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': os.getenv('AKASH_MODEL', 'gpt-4'),
            'messages': [
                {'role': 'system', 'content': 'You are a helpful assistant that analyzes social media content.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.7
        }
        
        response = requests.post(AKASH_API_URL, headers=headers, json=data)
        response_json = response.json()
        
        if 'error' in response_json:
            print(f"Akash API error: {response_json['error']['message']}")
            return None
            
        return response_json['choices'][0]['message']['content']
        
    except Exception as e:
        print(f"Error calling Akash Chat API: {str(e)}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response content: {e.response.text}")
        return None

def get_ollama_analysis(prompt):
    try:
        data = {
            'model': OLLAMA_MODEL,
            'prompt': prompt,
            'stream': False
        }
        
        response = requests.post(OLLAMA_API_URL, json=data)
        response.raise_for_status()
        response_json = response.json()
        
        if 'error' in response_json:
            print(f"Ollama API error: {response_json['error']}")
            return None
            
        return response_json.get('response', '')
        
    except Exception as e:
        print(f"Error calling Ollama API: {str(e)}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response content: {e.response.text}")
        return None

async def main():
    # Get tweets/messages from database
    rows = await get_user_tweets()
    print(f"Found {len(rows)} messages/tweets in total")
    
    # Group messages by account
    user_messages = defaultdict(list)
    for row in rows:
        account_name, message_content = row
        if message_content:  # Check if message_content is not null
            # Limit to 50 messages per user to avoid overwhelming the analysis
            if len(user_messages[account_name]) < 50:
                user_messages[account_name].append(message_content)

    print(f"Found messages from {len(user_messages)} unique users")
    
    # Create a directory for markdown files if it doesn't exist
    os.makedirs('user_analyses_md', exist_ok=True)
    
    # Get list of already analyzed users
    existing_analyses = set()
    for file in glob.glob('user_analyses_md/*.md'):
        username = os.path.basename(file).replace('.md', '')
        existing_analyses.add(username)
    
    print(f"Found {len(existing_analyses)} existing user analyses")
    
    # Filter out already analyzed users
    users_to_analyze = {user: msgs for user, msgs in user_messages.items() 
                       if len(msgs) > 0 and 
                       user.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '').replace(':', '').replace('|', '').replace('#', '').replace('>', '').replace('<', '') not in existing_analyses}
    
    print(f"Found {len(users_to_analyze)} new users to analyze")
    
    # Analyze each user's messages and save immediately
    user_analyses = {}
    total_users = len(users_to_analyze)
    current_user_count = 0
    
    for user, messages in users_to_analyze.items():
        current_user_count += 1
        print(f"[{current_user_count}/{total_users}] Analyzing user: {user} ({len(messages)} messages)")
        
        # Combine messages for analysis
        combined_text = '\n\n'.join(messages)
        analysis = get_analysis(combined_text)
        
        if analysis:
            user_analyses[user] = analysis
            
            # Clean username for filename and save immediately
            safe_username = user.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '').replace(':', '').replace('|', '').replace('#', '').replace('>', '').replace('<', '')
            filename = f'user_analyses_md/{safe_username}.md'
            
            # Double check file doesn't exist (just in case of race condition)
            if not os.path.exists(filename):
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"# User Analysis: {user}\n\n")
                    f.write("## Overview\n\n")
                    f.write(analysis)
                print(f"✓ Saved analysis for user {user} to {filename}")

    # Create an index file
    with open('user_analyses_md/README.md', 'w', encoding='utf-8') as f:
        f.write("# User Analyses Index\n\n")
        f.write("This directory contains individual analysis files for each user.\n\n")
        f.write("## Users Analyzed\n\n")
        for user in user_analyses.keys():
            safe_username = user.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '').replace(':', '').replace('|', '').replace('#', '').replace('>', '').replace('<', '')
            f.write(f"- [{user}](./{safe_username}.md)\n")

    print(f"Analysis complete! Processed {current_user_count}/{total_users} users. Results saved to user_analyses_md directory with individual markdown files")

if __name__ == '__main__':
    asyncio.run(main())
