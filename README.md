# OpsAgent — AI Operations Copilot

> **"Talk to your infrastructure like you talk to a human operator."**

OpsAgent is a production-grade AI operations agent that converts natural language into real business actions. It is **not** a chatbot or a dashboard — it is a decision-making system that understands intent, routes commands, and executes real-world operations.

---

## Live Demo

🚀 **[https://harry-api.onrender.com](https://harry-api.onrender.com)**

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
| `What can you do?` | Explains capabilities |

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
        ├── create_task  → Trello API (create card)
        ├── update_task  → Trello API (move card)
        ├── analyze      → Groq LLM (data analysis)
        └── chat         → Groq LLM (conversation)
        │
        ▼
   Structured JSON Response
        │
        ▼
   Frontend (renders result)
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

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI |
| AI / LLM | Groq API — llama-3.3-70b-versatile |
| Task Management | Trello API |
| Frontend | HTML + CSS + Vanilla JS |
| Deployment | Render |

---

## Project Structure

```
ops-agent/
├── main.py                  # FastAPI app entry point
├── requirements.txt
├── Procfile                 # Render deployment config
├── .env                     # API keys (never committed)
│
├── routers/
│   ├── chat.py              # POST /chat
│   ├── router_agent.py      # POST /route  ← main engine
│   └── ops.py               # POST /analyze
│
├── services/
│   ├── groq_service.py      # LLM calls (chat + routing)
│   └── trello_service.py    # Trello card create/move
│
├── utils/
│   ├── memory.py            # Session state (options, last task)
│   └── logger.py            # Activity log
│
└── templates/
    └── index.html           # Frontend UI
```

---

## API Endpoints

### `POST /route` — Main Engine
Accepts natural language, detects intent, executes action.

```bash
curl -X POST https://harry-api.onrender.com/route \
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

### `POST /chat` — AI Conversation
```bash
curl -X POST https://harry-api.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is a deployment pipeline?"}'
```

---

### `POST /analyze` — Data Analysis
```bash
curl -X POST https://harry-api.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{"data": "Server CPU at 94%, memory at 87%, 3 failed deploys today"}'
```

---

### `GET /health` — System Status
```bash
curl https://harry-api.onrender.com/health
```
```json
{ "status": "ok", "version": "1.0.0" }
```

---

## Supported Intents

| Intent | Trigger | Action |
|---|---|---|
| `create_task` | "create", "add task", "new ticket" | Creates Trello card with priority |
| `update_task` | "move", "update", "mark as done" | Moves card between lists |
| `analyze` | "analyze", "insights", "what does this mean" | AI analysis of ops data |
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
source venv/bin/activate  # Windows WSL: source venv/bin/activate
pip install -r requirements.txt
```

### 3. Create `.env`
```env
GROQ_API_KEY=your_groq_api_key
TRELLO_API_KEY=your_trello_api_key
TRELLO_TOKEN=your_trello_token
TRELLO_BOARD_ID=your_board_id
```

Get your keys:
- Groq: [console.groq.com](https://console.groq.com)
- Trello: [trello.com/app-key](https://trello.com/app-key)

### 4. Run
```bash
uvicorn main:app --reload --port 8000
```

Open **http://localhost:8000**

---

## Deployment (Render)

1. Push to GitHub
2. Connect repo on [render.com](https://render.com)
3. Set environment variables in Render dashboard
4. Deploy — `Procfile` handles the rest

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## Portfolio Value

This project demonstrates:

- **AI system design** — LLM-based intent detection and routing
- **API architecture** — clean FastAPI with separated concerns
- **Real-world automation** — live Trello integration
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
