# OpsAgent — AI Operations Copilot

> **"Talk to your infrastructure like you talk to a human operator."**

OpsAgent is a production-grade AI operations agent that converts natural language into real business actions. It is **not** a chatbot or a dashboard — it is a decision-making system that understands intent, routes commands, and executes real-world operations across multiple platforms.

---

## Live Demo

🚀 **[https://ops-agent-jdjn.onrender.com](https://ops-agent-jdjn.onrender.com)**

> Note: Hosted on Render free tier — first request may take ~30s to wake up.

---

## What It Does

| You say | OpsAgent does |
|---|---|
| `Create a task: Fix login bug` | Creates a Trello card with priority label |
| `Move payment bug to Done` | Finds the card and moves it to the correct list |
| `Move payment bug to Done` (multiple matches) | Returns numbered options, waits for your selection |
| `2` | Executes the selected action |
| `Analyze: API errors up 40% today` | Returns AI-powered ops analysis |
| `Analyze github.com/microsoft/vscode issues` | Fetches and AI-ranks open GitHub issues |
| `Analyze github.com/owner/repo issues and create tasks` | Fetches issues → creates Trello cards automatically |
| `Add to Notion: Meeting notes from today` | Creates a Notion page instantly |
| `Show my Notion pages` | Lists all pages in your workspace |
| `Delete from Notion: Meeting notes` | Deletes the page by name |
| `What can you do?` | Explains all capabilities |

---

## Architecture

```
User (Natural Language)
        │
        ▼
   FastAPI /route
        │
        ▼
   Groq LLM (llama-3.3-70b-versatile)
   → Detects intent
   → Extracts structured data
        │
        ├── create_task      → Trello API (create card)
        ├── update_task      → Trello API (move card)
        ├── analyze          → Groq LLM (data analysis)
        ├── github_analyze   → GitHub API + Groq (issue ranking)
        ├── notion           → Notion API (create page)
        ├── notion_delete    → Notion API (delete page)
        ├── notion_update    → Notion API (update page)
        ├── notion_list      → Notion API (list pages)
        └── chat             → Groq LLM (conversation)
        │
        ▼
   Structured Response → Frontend
```

---

## Key Feature — Multi-Step Selection System

Handles ambiguity intelligently. When multiple Trello cards match:

```
User:   Move payment bug to Done
Agent:  Multiple tasks found:
        1. Payment Bug on Login
        2. Payment Bug at Checkout

User:   2
Agent:  ✅ Moved: Payment Bug at Checkout → Done
```

Powered by `utils/memory.py` — stores options in session memory and resolves on next input.

---

## Key Feature — GitHub Integration

Analyze any public GitHub repository and auto-create Trello tasks:

```
User:   Analyze github.com/facebook/react issues and create tasks
Agent:  Fetches open issues → AI ranks top 3 by priority
        → Creates 3 Trello cards automatically
```

Works on ANY public repo — no repo ownership required.

---

## Key Feature — Notion Integration

Full CRUD operations on your Notion workspace via natural language:

```
User:   Add to Notion: Sprint planning notes
Agent:  ✅ Note saved — link returned

User:   Show my Notion pages
Agent:  📋 Lists all pages

User:   Delete from Notion: Sprint planning notes
Agent:  🗑 Deleted successfully
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI |
| AI / LLM | Groq API — llama-3.3-70b-versatile |
| Task Management | Trello API |
| Note Taking | Notion API |
| Code Intelligence | GitHub API |
| Frontend | HTML + CSS + Vanilla JS |
| Deployment | Render |

---

## Project Structure

```
ops-agent/
├── main.py                    # FastAPI app entry point
├── requirements.txt
├── Procfile                   # Render deployment config
├── .env                       # API keys (never committed)
│
├── routers/
│   ├── chat.py                # POST /chat
│   ├── router_agent.py        # POST /route  ← main engine
│   ├── ops.py                 # POST /analyze
│   ├── github.py              # POST /github/analyze
│   └── notion.py              # POST /notion/create, delete, update
│
├── services/
│   ├── groq_service.py        # LLM calls (chat + routing)
│   ├── trello_service.py      # Trello card create/move
│   ├── github_service.py      # GitHub issue fetching + parsing
│   └── notion_service.py      # Notion CRUD operations
│
├── utils/
│   ├── memory.py              # Session state (options, last task)
│   └── logger.py              # Activity log
│
└── templates/
    └── index.html             # Frontend UI
```

---

## API Endpoints

### `POST /route` — Main Engine
```bash
curl -X POST https://ops-agent-jdjn.onrender.com/route \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a task: Fix payment bug"}'
```

**Response:**
```json
{
  "intent": "create_task",
  "task": {
    "id": "abc123",
    "title": "[🔴 HIGH] Fix payment bug",
    "url": "https://trello.com/c/...",
    "status": "created"
  },
  "logs": ["[14:22:01] Created task: Fix payment bug"]
}
```

---

### `POST /github/analyze` — GitHub Issue Analysis
```bash
curl -X POST https://ops-agent-jdjn.onrender.com/github/analyze \
  -H "Content-Type: application/json" \
  -d '{"repo": "microsoft/vscode", "create_tasks": false}'
```

---

### `POST /notion/create` — Create Notion Page
```bash
curl -X POST https://ops-agent-jdjn.onrender.com/notion/create \
  -H "Content-Type: application/json" \
  -d '{"title": "Sprint Notes", "content": "Discussed API improvements"}'
```

---

### `POST /chat` — AI Conversation
```bash
curl -X POST https://ops-agent-jdjn.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is a deployment pipeline?"}'
```

---

### `POST /analyze` — Data Analysis
```bash
curl -X POST https://ops-agent-jdjn.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{"data": "Server CPU at 94%, memory at 87%, 3 failed deploys today"}'
```

---

### `GET /health` — System Status
```bash
curl https://ops-agent-jdjn.onrender.com/health
```

---

## Supported Intents

| Intent | Trigger | Action |
|---|---|---|
| `create_task` | "create", "add task", "new ticket" | Creates Trello card with priority |
| `update_task` | "move", "update", "mark as done" | Moves card between lists |
| `analyze` | "analyze", "insights" | AI analysis of ops data |
| `github_analyze` | "github", "repo", "issues" | Fetches + ranks GitHub issues |
| `notion` | "notion", "note", "add to notion" | Creates Notion page |
| `notion_delete` | "delete from notion" | Deletes Notion page by name |
| `notion_update` | "update notion" | Updates Notion page content |
| `notion_list` | "show notion", "list notion" | Lists all Notion pages |
| `chat` | anything else | Conversational AI response |

---

## Local Setup

### 1. Clone
```bash
git clone https://github.com/harwindersingh2482/ops-agent.git
cd ops-agent
```

### 2. Install dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Create `.env`
```env
GROQ_API_KEY=your_groq_api_key
TRELLO_API_KEY=your_trello_api_key
TRELLO_TOKEN=your_trello_token
TRELLO_BOARD_ID=your_board_id
GITHUB_TOKEN=your_github_token
NOTION_TOKEN=your_notion_token
NOTION_PAGE_ID=your_notion_page_id
```

Get your keys:
- Groq: [console.groq.com](https://console.groq.com)
- Trello: [trello.com/app-key](https://trello.com/app-key)
- GitHub: [github.com/settings/tokens](https://github.com/settings/tokens)
- Notion: [notion.so/my-integrations](https://notion.so/my-integrations)

### 4. Run
```bash
uvicorn main:app --reload --port 8000
```

Open **http://localhost:8000**

---

## Deployment (Render)

1. Push to GitHub
2. Connect repo on [render.com](https://render.com)
3. Add all 7 environment variables in Render dashboard
4. Deploy — `Procfile` handles the rest

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## Portfolio Value

This project demonstrates:

- **AI system design** — LLM-based intent detection and routing
- **Multi-platform integration** — Trello + GitHub + Notion in one agent
- **API architecture** — clean FastAPI with separated concerns
- **Real-world automation** — live integrations that execute real actions
- **Product thinking** — multi-step interaction, ambiguity handling
- **Production deployment** — live public API on Render

---

## Author

**Harwinder Singh**
Remote Operations & AI Automation Engineer
Hoshiarpur, Punjab, India

[![GitHub](https://img.shields.io/badge/GitHub-harwindersingh2482-black)](https://github.com/harwindersingh2482)

---

## License

MIT
