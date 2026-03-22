# FILE: README.md
# AI Research Agent

A full-stack AI research assistant powered by Kimi K2.5 (via OpenRouter), Brave Search, and FastAPI.

## Features

- **Intelligent Research**: Breaks down complex questions into sub-queries
- **Web Search**: Uses Brave Search API to find relevant sources
- **Content Extraction**: Scrapes full article content from URLs
- **Streaming Responses**: Real-time word-by-word response streaming
- **Source Citations**: Inline citations with source cards
- **Dark Mode UI**: Modern, responsive dark interface

## Architecture

```
ai-research-agent/
├── backend/          # FastAPI + Claude/Kimi agent
│   ├── main.py       # API endpoints
│   ├── agent.py      # Agent loop logic
│   ├── tools.py      # Search & scrape tools
│   ├── prompts.py    # System prompt
│   └── models.py     # Pydantic models
├── frontend/         # React + Vite
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── App.jsx
│   └── index.html
└── README.md
```

## Environment Variables

| Variable | Description | Get From |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | OpenRouter API key | https://openrouter.ai/keys |
| `BRAVE_API_KEY` | Brave Search API key | https://brave.com/search/api/ |

## Setup Commands

### Terminal 1 — Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your keys to .env, then:
uvicorn main:app --reload --port 8000
```

### Terminal 2 — Frontend

```bash
cd frontend
npm install
npm run dev
```

### Open Browser

Navigate to: http://localhost:5173

## Potential Issues & Fixes

### 1. CORS Errors
**Symptom**: Frontend shows "Network Error" or CORS blocked
**Fix**: Already configured in `main.py`. If issues persist:
- Check `allow_origins=["http://localhost:5173"]` matches your frontend URL
- Try `allow_origins=["*"]` temporarily for debugging

### 2. Streaming Buffering
**Symptom**: Full response appears at once instead of streaming
**Fix**: Already configured in `main.py` with headers:
```python
{"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
```
- Avoid using `curl` for testing (buffers)
- Use browser Network tab → Response tab to see streaming

### 3. API Key Errors
**Symptom**: "Authentication failed" or 401 errors
**Fix**: 
- Ensure `.env` file is in `backend/` directory
- Restart uvicorn after editing `.env`
- Check key format (no quotes needed: `KEY=value`)

### 4. Module Not Found Errors
**Symptom**: `ImportError: No module named 'anthropic'`
**Fix**:
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

### 5. Brave Search Rate Limits
**Symptom**: Empty search results or 429 errors
**Fix**:
- Free tier: 2000 queries/month
- Check dashboard: https://api.search.brave.com/app/dashboard

### 6. Scraping Failures
**Symptom**: "Error in scrape_page" in terminal
**Fix**:
- Some sites block scrapers (returns empty content)
- This is expected; agent continues with search snippets

### 7. SSE Connection Drops
**Symptom**: Stream stops mid-response
**Fix**:
- Check uvicorn logs for errors
- Increase timeout in `httpx.AsyncClient()` if needed
- Some LLM responses may timeout; check OpenRouter status

## Usage

1. Enter any research question in the search bar
2. The agent will:
   - Plan sub-queries
   - Search the web
   - Scrape relevant pages
   - Compose a comprehensive answer
3. Watch the response stream in real-time
4. Click source links to verify information

## Example Queries

- "What are the latest AI breakthroughs in 2025?"
- "Explain quantum computing in simple terms"
- "What is the current state of nuclear fusion energy?"

## Tech Stack

- **Backend**: FastAPI, Anthropic SDK, httpx, BeautifulSoup4
- **Frontend**: React 18, Vite, Tailwind CSS, react-markdown
- **AI**: Kimi K2.5 via OpenRouter
- **Search**: Brave Search API

## License

MIT
