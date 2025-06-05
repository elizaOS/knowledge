# Social Media User Analysis Tool

This tool analyzes social media content (tweets/messages) from a SQLite database and generates user analyses using the Akash Chat API.

## Features

- Extracts user messages from a SQLite database
- Analyzes content using the Akash Chat API
- Generates markdown reports for each user
- Tracks analyzed users to avoid duplicates
- Supports custom analysis prompts

## Prerequisites

- Python 3.8+
- SQLite database with the required schema (see Database Setup below)
- Akash Chat API key (for cloud-based analysis) or Ollama (for local analysis)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd RAG_Processing
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### For Akash Chat API (Cloud-based):
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Edit the `.env` file and add your Akash Chat API key:
   ```
   AKASH_CHAT_API_KEY=your_api_key_here
   AKASH_MODEL=Qwen3-235B-A22B-FP8
   ```

### For Local Ollama (Alternative):
1. Install Ollama from [ollama.ai](https://ollama.ai/)
2. Pull the desired model (e.g., `ollama pull qwen3:4b`)
3. Update the script to use the local Ollama endpoint by modifying the API URL in `analyze_users_akash.py`

**Note:** The current version is configured for Akash Chat API. To switch to Ollama, you'll need to modify the API endpoint and authentication in the script.

## Database Setup

1. **Using the existing database (recommended):**
   - Copy the `db.sqlite` file from the `agent/data/` directory to the root of this project
   - The script will automatically use this database file

2. **Or create a new database** with the following schema:

```sql
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL
);

CREATE TABLE memories (
    id INTEGER PRIMARY KEY,
    userId INTEGER,
    type TEXT,
    content TEXT,
    createdAt TIMESTAMP,
    FOREIGN KEY (userId) REFERENCES accounts(id)
);
```

## Usage

1. Run the analysis script:
   ```bash
   python analyze_users_akash.py
   ```

2. The script will:
   - Find and process new users
   - Generate markdown reports in the `user_analyses_md` directory
   - Create an index of all analyzed users in `user_analyses_md/README.md`

## Customization

### Analysis Prompt

You can modify the analysis prompt in the `get_akash_analysis` function in `analyze_users_akash.py` to change what aspects of the content are analyzed.

### Configuration Options

- `AKASH_CHAT_API_KEY`: Your Akash Chat API key
- `AKASH_MODEL`: The model to use for analysis (default: Qwen3-235B-A22B-FP8)

## Output

Analysis results are saved as individual markdown files in the `user_analyses_md` directory, with one file per user. Each file includes:

- User overview
- Analysis of content themes and styles
- Key insights and patterns
- Generated tags for categorization

## Troubleshooting

- **API Key Errors**: 
  - For Akash: Ensure your API key is correctly set in the `.env` file
  - For Ollama: Make sure the Ollama service is running and the model is downloaded
- **Database Connection**: 
  - Verify the `db.sqlite` file exists in the root directory
  - Ensure you have read/write permissions for the database file
- **Empty Results**: 
  - Check if the database contains the expected data
  - Verify the database schema matches the expected structure
- **Version Compatibility**: 
  - Akash version: Uses cloud-based API with Qwen3-235B-A22B-FP8 model
  - Ollama version: Uses local models (e.g., qwen3:4b) with local processing

## License

[Specify your license here]
