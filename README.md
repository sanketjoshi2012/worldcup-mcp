# FIFA World Cup 2026 AI Assistant

A conversational AI assistant for FIFA World Cup 2026 built with Claude and the Model Context Protocol (MCP). Ask about today's matches, group standings, results, and get journalist-style match summaries.

**Live demo:** https://worldcup-mcp-gjg7.onrender.com

## What is MCP?

Model Context Protocol (MCP) is a standard that lets AI models like Claude connect to external data sources and tools. Instead of Claude only knowing what's in its training data, MCP lets it fetch live data and take actions — like reading today's World Cup scores.

## Features

- Live match scores and fixtures for today
- Group stage standings (calculated from results)
- Match results with goalscorers and times
- Filter results by round (e.g. Quarter-final, Group A)
- Journalist-style match summaries powered by Claude
- Web chat UI with FIFA-themed design

## Project Structure

```
worldcup-mcp/
├── mcp_server.py     # MCP server — tools and prompts
├── api.py            # FastAPI backend + WebSocket chat
├── main.py           # Terminal chat client
├── static/
│   └── index.html    # Web UI (navy + gold FIFA theme)
├── render.yaml       # Render deployment config
└── pyproject.toml    # Python dependencies
```

## MCP Primitives Used

| Primitive | Name | Description |
|-----------|------|-------------|
| Tool | `get_todays_matches` | Fetch today's World Cup matches with scores |
| Tool | `get_standings` | Calculate group stage standings from results |
| Tool | `get_match_result` | Get result and goals for a specific match |
| Tool | `get_all_results` | Get all results, optionally filtered by round |
| Prompt | `summarize_match` | Write an exciting journalist-style match summary |

## Data Source

Match data comes from [openfootball/world-cup.json](https://github.com/openfootball/world-cup.json) — a free, open-source dataset with no API key required.

## Setup

### Prerequisites

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) package manager
- Anthropic API key ([get one here](https://console.anthropic.com))

### Run locally

1. Clone the repo:
```bash
git clone https://github.com/sanketjoshi2012/worldcup-mcp.git
cd worldcup-mcp
```

2. Install dependencies:
```bash
uv sync
```

3. Create a `.env` file:
```
ANTHROPIC_API_KEY="your-api-key-here"
```

4. Run the web app:
```bash
uv run uvicorn api:app --port 8000 --reload
```

Then open http://localhost:8000 in your browser.

Or run the terminal version:
```bash
uv run main.py
```

## Deployment

This project is configured for deployment on [Render](https://render.com) via `render.yaml`.

1. Push to GitHub
2. Connect repo on Render
3. Add `ANTHROPIC_API_KEY` as an environment variable
4. Deploy

## Built With

- [Anthropic Claude](https://anthropic.com) — AI model
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) — Model Context Protocol
- [FastAPI](https://fastapi.tiangolo.com) — Web backend
- [uv](https://github.com/astral-sh/uv) — Python package manager
- [openfootball](https://github.com/openfootball/world-cup.json) — World Cup data
