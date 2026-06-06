# A2A Support Pilot

Pilot project built with **Google ADK**, **A2A protocol**, **MCP**, and **RAG**.

A user chats about a **login** or **billing** issue. The **router agent** (Google ADK) classifies intent and delegates to the correct **specialist agent over A2A**. The specialist searches the **knowledge base (RAG)** and returns troubleshooting guidance. If the issue remains unresolved, the specialist hands off to **ticket_specialist** (also via **A2A**), which creates a **P1 Jira ticket** using the **Jira MCP** server.

```
User → Router (ADK) ──A2A──► Login / Billing Specialist (RAG)
                                      │
                               unresolved
                                      │
                                      ▼
                            Ticket Specialist ──MCP──► Jira (P1)
```

**Architecture & user flows:** [design.md](design.md)

**Demo video:** [docs/demo.webm](docs/demo.webm) — live login flow through router → specialist → Jira ticket

## Prerequisites

- Python 3.11+ ([download](https://www.python.org/downloads/) — check "Add Python to PATH")
- [Gemini API key](https://aistudio.google.com/apikey) (free tier)
- [Jira Cloud Free](https://www.atlassian.com/software/jira/free) account + API token

## Setup

### 1. Install dependencies

```powershell
cd "A2A Pilot"
.\scripts\check_setup.ps1
```

This creates `.venv`, installs packages, and checks for `.env`.

### 2. Configure environment

```powershell
copy .env.example .env
```

Edit `.env` with your Gemini key and Jira credentials.

### 3. Jira project setup

1. Create a free Jira Cloud site
2. Create project with key `SUPPORT` (or update `JIRA_PROJECT_KEY`)
3. Ensure issue type `Bug` exists (or set `JIRA_ISSUE_TYPE=Task`)
4. Create API token at https://id.atlassian.com/manage-profile/security/api-tokens

### 4. Index knowledge base

```powershell
python scripts/ingest_kb.py
```

KB articles live in `kb/login/`, `kb/billing/`, and `kb/escalation/`.

### 5. Start all services

```powershell
.\scripts\start_all.ps1
```

Or start manually in separate terminals:

```powershell
uvicorn agents.login_specialist.agent:a2a_app --host 127.0.0.1 --port 8001
uvicorn agents.billing_specialist.agent:a2a_app --host 127.0.0.1 --port 8002
uvicorn agents.ticket_specialist.agent:a2a_app --host 127.0.0.1 --port 8003
uvicorn chat_api.main:app --host 127.0.0.1 --port 8080
```

### 6. Open chat UI

http://127.0.0.1:8080

## How each technology is used

| Technology | Where | Role in the pilot |
|------------|-------|-------------------|
| **Google ADK** | All agents + `chat_api/main.py` | Orchestrates router, specialists, and ticket agent; runs tools and sub-agent transfers |
| **A2A protocol** | Router → specialists; specialists → ticket_specialist | Remote agents communicate via HTTP agent cards (ports 8001–8003) |
| **RAG** | `shared/rag.py` + `search_*_kb` tools | Specialists retrieve KB articles before answering the user |
| **MCP** | `mcp_servers/jira_server/` | Ticket specialist calls `create_support_ticket` over stdio MCP |

## Example flows

Start all services with `.\scripts\start_all.ps1`, then open http://127.0.0.1:8080.

Each message runs: **Router (ADK) → A2A specialist (RAG) → ticket_specialist (MCP → Jira P1)**. Allow 10–30 seconds per reply.

**Login** — "Login issue" → router delegates to `login_specialist` → RAG suggests fixes → if still broken, specialist escalates via A2A → P1 Jira ticket.

**Billing** — "Billing dispute" → router delegates to `billing_specialist` → RAG + intake → escalate via A2A → P1 Jira ticket for fraud/large charges.

**Tips**
- Keep all four services running (ports 8001–8003 + 8080).
- Refresh the page between flows for a clean session.
- Gemini free tier is shared across agents (~2–3 API calls per message). If you hit rate limits, wait a minute or use `ADK_MODEL=gemini-2.5-flash-lite` in `.env`.

## Verify A2A agent cards

- http://127.0.0.1:8001/.well-known/agent-card.json
- http://127.0.0.1:8002/.well-known/agent-card.json
- http://127.0.0.1:8003/.well-known/agent-card.json

## Project structure

```
├── agents/                  # login, billing, ticket specialists (A2A)
├── router/                  # Router agent + registry.json
├── chat_api/                # FastAPI + web UI
├── mcp_servers/jira_server/ # Jira MCP (stdio)
├── kb/                      # Support knowledge base (.md)
├── shared/                  # RAG, config, tools
├── scripts/                 # ingest_kb, start_all, check_setup
├── docs/demo.webm           # Recorded user-flow walkthrough
├── design.md                # Architecture diagrams + flows
└── README.md
```

## Tech stack (all free)

| Layer | Technology |
|-------|------------|
| Agents | Google ADK (Python) |
| Agent protocol | A2A v1.0 |
| Tools | MCP (Jira) |
| RAG | Local keyword search over KB markdown (lightweight, no GPU) |
| LLM | Gemini (free tier) |
| API | FastAPI |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `GOOGLE_API_KEY` error | Set key in `.env` |
| Router returns generic error | Ensure ports 8001–8003 are running |
| Jira 400 error | Check project key, issue type, and API token permissions |
| RAG returns empty | Run `python scripts/ingest_kb.py` |
| Gemini 429 / quota | Wait ~1 min between messages; use `gemini-2.5-flash-lite`; reduce messages per session |
| Slow first reply | Specialist agents cold-start on first request; keep all ports running |
