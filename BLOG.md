# How I Built a Live FIFA World Cup 2026 AI Assistant with MCP and Claude

I'm not a professional developer. But today I built a fully working AI-powered World Cup assistant, deployed it live on the internet, and pushed it to GitHub — all in one session.

Here's how it happened, what I learned, and how you can build something similar.

---

## What I Built

A web app where you can chat with Claude about the FIFA World Cup 2026. Ask it:

- "What matches are today?"
- "Show me the group standings"
- "What was the result of France vs Morocco?"
- "Write me a match summary for Brazil vs Argentina"

It fetches **live data**, reasons about it, and answers in plain English.

**Live demo:** https://worldcup-mcp-gjg7.onrender.com
**Source code:** https://github.com/sanketjoshi2012/worldcup-mcp

---

## What is MCP?

Before I started, I had no idea what MCP was. Here's how I now explain it.

Claude is a very smart AI, but out of the box it's locked in a room. It only knows what it learned during training. It can't see today's scores, your files, or anything happening in the real world right now.

**MCP (Model Context Protocol)** is like a helper that passes notes between Claude and the outside world.

```
You ask Claude: "What matches are today?"
        ↓
Claude thinks: "I need to fetch today's matches"
        ↓
MCP fetches the data from the source
        ↓
Claude gets the data and answers you
```

Without MCP, you'd have to manually write all the integration code every time Claude needs to access something new. With MCP, you define it once as a **server** and Claude knows how to use it automatically.

---

## The Three MCP Primitives

MCP has three core building blocks:

### 1. Tools — things Claude can DO
Like buttons Claude can press. Our tools:
- `get_todays_matches` — fetch today's World Cup scores
- `get_standings` — calculate group tables
- `get_match_result` — look up a specific match
- `get_all_results` — get all results filtered by round

```python
@mcp.tool()
def get_todays_matches() -> str:
    """Get all FIFA World Cup 2026 matches happening today."""
    # fetch and return data
```

### 2. Resources — data Claude can READ
Like a filing cabinet. We used resources to expose documents in the `cli_project` practice app:
- `docs://documents` — list all document IDs
- `docs://documents/{doc_id}` — get a specific document's content

### 3. Prompts — shortcuts users can trigger
Like slash commands. Type `/summarize deposition.md` and a pre-built prompt fires automatically:

```python
@mcp.prompt()
def summarize_match(team1: str, team2: str) -> str:
    """Write an exciting journalist-style match summary."""
    return f"Get the result for {team1} vs {team2} and write an exciting summary..."
```

---

## The Architecture

```
Browser (chat UI)
      ↓  WebSocket
FastAPI backend (api.py)
      ↓  stdio
MCP Server (mcp_server.py)
      ↓  HTTP
openfootball GitHub (free World Cup data)
      ↑
Anthropic Claude API
```

The client sends a message over WebSocket. FastAPI passes it to Claude with the available tools. Claude decides which tool to call. The MCP server fetches the data. Claude uses the data to answer. The answer goes back to the browser.

---

## What I Used

| Tool | Purpose |
|------|---------|
| Python + MCP SDK | Build the MCP server |
| FastAPI | Web backend + WebSocket |
| Anthropic API | Claude AI model |
| openfootball | Free World Cup 2026 data (no API key!) |
| uv | Python package manager |
| Render | Free deployment |
| GitHub | Version control |

---

## The Biggest Lessons

**1. MCP separates concerns cleanly**
The server handles data. Claude handles reasoning. You handle the question. Each layer does one thing.

**2. The client/server model clicked for me with a restaurant analogy**
- You = the hungry person
- MCP client = the waiter (takes your order)
- MCP server = the kitchen (has the food)
- Data source = the ingredients

**3. Unofficial APIs break**
We first tried FotMob's unofficial API — it returned 404s. We pivoted to openfootball, a free open-source dataset on GitHub. Always have a backup data source.

**4. WebSockets need wss:// on HTTPS**
Classic gotcha. Locally it's `ws://`, but once deployed on HTTPS it needs `wss://`. One line fix, but easy to miss.

**5. You don't need to be a pro developer**
I learned what a client and server was today. I learned what MCP was today. And by the end of the day I had a live app deployed on the internet. The tools have gotten good enough that curiosity matters more than expertise.

---

## Try It Yourself

1. Clone the repo: `git clone https://github.com/sanketjoshi2012/worldcup-mcp`
2. Add your Anthropic API key to `.env`
3. Run `uv sync` then `uv run uvicorn api:app --port 8000`
4. Open http://localhost:8000

Or just visit the live demo: https://worldcup-mcp-gjg7.onrender.com

---

## What's Next

Some ideas to extend this:
- Add player stats and top scorers
- Push score notifications
- Support for other tournaments (Champions League, Premier League)
- Voice input using Web Speech API

If you build something with MCP, I'd love to see it!
