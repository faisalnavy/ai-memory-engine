# AI Memory Engine

**Reduce AI token usage by 90-98%** — A universal memory layer between your codebase and any AI coding assistant.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue?logo=typescript)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)
![Token Savings](https://img.shields.io/badge/Token%20Savings-90--98%25-brightgreen)

---

## What is this?

AI coding assistants (Claude, Cursor, Copilot, GPT-4, Gemini) need your entire codebase as context — costing thousands of tokens every request.

**AI Memory Engine** solves this:
- Reads and understands your project **once**
- Stores everything in a compact `.memory/` database
- On every AI query, retrieves only **relevant** files and functions
- Delivers **500-3000 tokens** instead of 50,000+

```
Project: my-flask-api  (127 files, 43,000 lines)

Without Memory Engine  →  52,000 tokens sent to AI
With Memory Engine     →  890 tokens sent to AI   (98.3% savings)
```

---

## Table of Contents

1. [Installation](#installation)
2. [Phase 2 — CLI Tool](#phase-2--cli-tool)
3. [Phase 3 — GUI App (Windows .exe)](#phase-3--gui-app)
4. [Phase 4 — VS Code Extension](#phase-4--vs-code-extension)
5. [Phase 5 — Desktop App (Electron)](#phase-5--desktop-app)
6. [Phase 6 — SaaS Platform](#phase-6--saas-platform)
7. [Using with AI Assistants](#using-with-ai-assistants)
8. [Project Structure](#project-structure)
9. [Running Tests](#running-tests)
10. [Contributing](#contributing)

---

## Installation

### Windows

**Option A — GUI App (no Python needed)**
1. Download `MemoryEngine.exe` from [Releases](https://github.com/faisalnavy/ai-memory-engine/releases)
2. Double-click and run

**Option B — From Source**
```cmd
:: Install Python 3.11+ from python.org (check "Add Python to PATH")
git clone https://github.com/faisalnavy/ai-memory-engine.git
cd ai-memory-engine
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

:: Run GUI
python -X utf8 gui/app.py

:: Or CLI
python -X utf8 cli/main.py --help

:: Install as global command
pip install -e .
memory --help
```

> Always use `python -X utf8` on Windows to avoid encoding issues.

---

### macOS

```bash
brew install python@3.11
git clone https://github.com/faisalnavy/ai-memory-engine.git
cd ai-memory-engine
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run GUI
python gui/app.py

# Or CLI
python cli/main.py --help

# Install as global command
pip install -e .
memory --help
```

> If macOS blocks the app: System Settings → Privacy & Security → Open Anyway

---

### Linux

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3.11 python3.11-venv python3-tk git -y

# Fedora
sudo dnf install python3.11 python3-tkinter git -y

# Arch
sudo pacman -S python tk git

git clone https://github.com/faisalnavy/ai-memory-engine.git
cd ai-memory-engine
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run GUI
python gui/app.py

# Or CLI
python cli/main.py --help

# Install as global command
pip install -e .
memory --help
```

---

## Phase 2 — CLI Tool

The fastest way to use the memory engine from any terminal.

### Quick Start

```bash
cd my-project
memory init .           # Step 1: initialize
memory index .          # Step 2: scan all files (run once)
memory ask "how does authentication work"    # Step 3: get AI context
memory update .         # Step 4: run after code changes
```

### All Commands

#### `memory init` — Initialize a project
```bash
memory init /path/to/project
# or from inside project:
cd my-project && memory init
```
Creates `.memory/` folder and detects language, framework, architecture.

---

#### `memory index` — Full project scan
```bash
memory index /path/to/project
```
Reads all source files, extracts functions, builds dependency graph.
Run once at the start. Use `update` for daily use.

```
Files indexed:    127
Functions stored: 843
Graph edges:    1,204
```

---

#### `memory update` — Incremental update (fast)
```bash
memory update /path/to/project
```
Only re-indexes files that changed since last scan (hash-based).
Takes seconds even on large projects.

---

#### `memory ask` — Get AI context
```bash
memory ask "how does user authentication work"  --path /path/to/project
memory ask "explain the database schema"        --path /path/to/project
memory ask "where is payment processing done"   --path /path/to/project

# Options
memory ask "question" --max-tokens 2000   # limit size (default 3000)
memory ask "question" --no-context        # show savings report only
memory ask "question" --copy              # copy context to clipboard
```

Output:
```
Original context:  ~48,000 tokens
Optimized context:   1,240 tokens
Token savings:         97.4%

## Project: my-flask-api
- Language: Python | Framework: Flask | Architecture: monolith

## Relevant Files
### routes/auth.py
Purpose: Authentication route handlers
Exports: [login, logout, register, refresh_token]

## Relevant Functions
- authenticate_user(email, password) -> User
- create_access_token(user_id) -> str
...
```

Copy this output and paste it before your question in Claude/GPT/Cursor.

---

#### `memory search` — Search files and functions
```bash
memory search "database"     --path /path/to/project
memory search "authenticate" --path /path/to/project
memory search "user model"   --path /path/to/project --limit 20
```

---

#### `memory stats` — Show statistics
```bash
memory stats /path/to/project
```
```
Files indexed:    127
Functions stored: 843
Graph edges:    1,204
Decisions:          8
Sessions:          42
Language:      Python
Framework:      Flask
```

---

#### `memory graph` — Dependency graph
```bash
memory graph /path/to/project
memory graph /path/to/project --max 50
```
Shows all file import relationships in terminal.

---

#### `memory compress` — Compress session memory
```bash
memory compress /path/to/project
memory compress /path/to/project --force
```
Compresses old sessions into a compact intelligence block.
Runs automatically after every 10 sessions.

---

#### `memory decide` — Record an architectural decision
```bash
memory decide "Use SQLite over PostgreSQL" --path /path/to/project
# Prompts: decision details, reason, tags
```
Decisions are included in every future AI context package.

---

#### `memory export` — Export memory as zip
```bash
memory export team-memory.zip --path /path/to/project
```

---

#### `memory import` — Import memory from zip
```bash
memory import team-memory.zip --path /path/to/project
```

---

### Full CLI Workflow Example

```bash
# First time setup
cd ~/my-flask-api
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

memory init .
memory index .

# Daily usage
memory ask "how does the payment system work"
memory ask "where is the user validation logic"
memory ask "explain the API rate limiting"

# After making code changes
memory update .

# Search for specific things
memory search "stripe"
memory search "webhook"

# Record important decisions
memory decide "Switched from Redis to Memcached"

# Share memory with your team
memory export team-memory.zip
```

---

## Phase 3 — GUI App

The Windows `.exe` — no Python, no terminal, just double-click.

### Download

Get `MemoryEngine.exe` from [Releases](https://github.com/faisalnavy/ai-memory-engine/releases).

### How to Use

1. **Double-click** `MemoryEngine.exe` to open
2. Click **Browse...** and select your project folder
3. Check **Initialize & Index** (checked by default)
4. Optionally check **Run test query** and type a question
5. Click **Run**
6. Watch the console panel — shows files indexed, functions stored, token savings
7. Done — `.memory/` database created inside your project

### Build it yourself

```cmd
pip install pyinstaller
python -m PyInstaller memory_engine.spec --clean --noconfirm
:: Output: dist\MemoryEngine.exe
```

---

## Phase 4 — VS Code Extension

Auto-updates memory every time you save a file.

### Install

**From source:**
```bash
cd ai-memory-engine/vscode-extension
npm install
npm run compile
# Press F5 in VS Code to run in development mode
```

### Configure

Open VS Code Settings (`Ctrl+,`) → search `Memory Engine`:

| Setting | Windows | Mac/Linux |
|---------|---------|-----------|
| `memoryEngine.pythonPath` | `python` | `python3` |
| `memoryEngine.cliPath` | full path to `cli/main.py` | full path to `cli/main.py` |
| `memoryEngine.autoUpdate` | `true` | `true` |
| `memoryEngine.maxTokens` | `3000` | `3000` |

### Sidebar Panels

Click the brain icon in the VS Code activity bar (left sidebar):

| Panel | Shows |
|-------|-------|
| Memory Explorer | Files indexed, functions stored, graph edges |
| Dependency Graph | All file import relationships |
| Token Savings | Savings from last query |
| Session History | All queries you have run |

### Commands (`Ctrl+Shift+P` → type `Memory:`)

| Command | What it does |
|---------|-------------|
| Memory: Initialize Project | Creates `.memory/` database |
| Memory: Index Project | Full scan of all source files |
| Memory: Update (Incremental) | Re-index only changed files |
| Memory: Ask — Get AI Context | Type question, get context |
| Memory: Search | Search files and functions |
| Memory: Show Stats | View memory statistics |
| Memory: Compress Sessions | Compress old sessions |
| Memory: Refresh Views | Refresh sidebar panels |

### Status Bar

```
Brain Memory           idle, ready
Brain Updating...      file just saved, re-indexing
Brain Memory OK        update complete
```

### Workflow

```
1. Open project in VS Code
2. Ctrl+Shift+P -> Memory: Initialize Project
3. Ctrl+Shift+P -> Memory: Index Project
4. Write code normally — memory auto-updates on every save
5. Ctrl+Shift+P -> Memory: Ask — Get AI Context
   -> Type your question
   -> Output panel shows context package
   -> Click "Copy Context"
   -> Paste into Claude / ChatGPT / Cursor
```

---

## Phase 5 — Desktop App

Full cross-platform desktop application (Windows, macOS, Linux).

### Prerequisites

```bash
# Node.js 18+ from nodejs.org
pip install fastapi uvicorn pydantic
```

### Run

```bash
cd ai-memory-engine/desktop-app
npm install
npm start              # development mode (React + Electron)
npm run build          # build for production
# Output: dist-electron/ (installer for your OS)
```

### 7 Pages

#### Dashboard
- Project stats (files, functions, edges, decisions, sessions)
- Live console output
- Project DNA card (language, framework, architecture)

**How to use:**
1. Click **Browse** — select project folder
2. Click **Init** — initializes database
3. Click **Index** — scans all files (watch console)
4. Click **Update** after making code changes

#### Projects
- All recently used projects
- Click any project to switch

#### Memory (Dependency Graph)
- All file import/call relationships
- Format: `source → [relationship] → target`

#### Sessions
- Full history of every query you ran
- Timestamp + query text

#### Decisions
- Form to record architectural decisions (title, details, reason)
- All decisions appear in every future AI context

#### Analytics
1. Type a question in the input bar
2. Click **Get Context**
3. See savings banner: `Original → Optimized → Savings %`
4. Click **Copy** to copy context to clipboard

---

## Phase 6 — SaaS Platform

Cloud platform for teams. Self-host with Docker or deploy to any cloud.

### Quick Start (Docker)

```bash
cd ai-memory-engine/saas-platform

# Edit environment variables
# backend/.env:
SECRET_KEY=your-32-char-random-secret
DATABASE_URL=postgresql+asyncpg://postgres:password@postgres/memory_engine
REDIS_URL=redis://redis:6379
STRIPE_SECRET_KEY=sk_live_...       # optional - for payments
AWS_ACCESS_KEY_ID=...               # optional - for cloud storage

# Start everything
docker-compose up -d

# Open the app
# http://localhost:3000        frontend
# http://localhost:8000/api/docs   API docs
```

### What starts

| Service | URL | Purpose |
|---------|-----|---------|
| Next.js frontend | http://localhost:3000 | Web app |
| FastAPI backend | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/api/docs | Swagger UI |
| PostgreSQL | localhost:5432 | Database |
| Redis | localhost:6379 | Cache |

### REST API Reference

**Auth**
```
POST /api/v1/auth/register     Create account
POST /api/v1/auth/login        Get JWT token
POST /api/v1/auth/refresh      Refresh expired token
GET  /api/v1/auth/me           Get current user profile
POST /api/v1/auth/api-keys     Create API key
```

**Projects**
```
GET    /api/v1/projects/                    List all projects
POST   /api/v1/projects/                    Create a project
GET    /api/v1/projects/{id}                Get project details
DELETE /api/v1/projects/{id}                Delete project
GET    /api/v1/projects/{id}/stats          Files, functions, sessions count
GET    /api/v1/projects/{id}/sessions       Session history
POST   /api/v1/projects/{id}/sessions       Log a query session
GET    /api/v1/projects/{id}/decisions      List decisions
POST   /api/v1/projects/{id}/decisions      Add decision
```

**Billing**
```
GET  /api/v1/billing/plans            Available plans + pricing
POST /api/v1/billing/checkout         Create Stripe checkout
POST /api/v1/billing/webhook          Stripe events (auto-upgrades plan)
GET  /api/v1/billing/usage/{org_id}   Monthly usage history
```

### Plans

| Plan | Price | Projects | Members | Features |
|------|-------|----------|---------|---------|
| Free | $0/mo | 3 | 1 | CLI + GUI, local only |
| Pro | $12/mo | 20 | 1 | API access, cloud sync |
| Team | $49/mo | 100 | 10 | Webhooks, SDK, analytics |
| Enterprise | Custom | Unlimited | Unlimited | SSO, SLA, support |

### API Usage Example (Python)

```python
import requests

BASE = "http://localhost:8000/api/v1"

# Create account
r = requests.post(f"{BASE}/auth/register", json={
    "email": "you@company.com",
    "password": "your-password",
    "full_name": "Your Name"
})
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Create a project
r = requests.post(f"{BASE}/projects/", json={
    "org_id": "your-org-id",
    "name": "My Flask API"
}, headers=headers)
project_id = r.json()["id"]

# Get stats
r = requests.get(f"{BASE}/projects/{project_id}/stats", headers=headers)
print(r.json())
# {"files": 127, "functions": 843, "tokens_saved": 234500}

# Add decision
requests.post(f"{BASE}/projects/{project_id}/decisions", json={
    "title": "Use PostgreSQL",
    "decision": "Chose PostgreSQL over SQLite for production",
    "reason": "SQLite has write concurrency limits"
}, headers=headers)
```

---

## Using with AI Assistants

### Claude (claude.ai or Claude Code)

```bash
# Get context
memory ask "how does the payment system work" --path /my-project

# Paste the output BEFORE your question in Claude chat
# Claude will have full understanding in under 3000 tokens
```

### ChatGPT / GPT-4

```bash
# Auto-copy to clipboard
memory ask "explain the database schema" --copy --path /my-project
# Paste into ChatGPT
```

### Cursor

Add to `.cursorrules`:
```
Use the project memory from .memory/project_dna.json to understand
the codebase before answering any coding question.
```

Or pipe context directly:
```bash
# Mac/Linux
memory ask "refactor auth module" --path . | pbcopy

# Windows
python -X utf8 cli/main.py ask "refactor auth module" | clip
```

### GitHub Copilot

Add at the top of your file:
```python
# Project: my-flask-api | Language: Python | Framework: Flask
# Key files: routes/auth.py, models/user.py, services/jwt.py
```

### Windsurf / Aider / Any AI

```bash
# Save context to file and include in your session
memory ask "your question" --path . > context.md
aider --read context.md your-file.py
```

---

## Project Structure

```
ai-memory-engine/
├── cli/main.py                     CLI tool (11 commands)
├── core/
│   ├── dna.py                      Project DNA detector
│   ├── file_summarizer.py          File indexer
│   ├── function_summarizer.py      Function indexer
│   ├── graph_builder.py            Dependency graph (NetworkX)
│   ├── retriever.py                6-step retrieval engine
│   ├── compressor.py               Session compression
│   ├── context_builder.py          Context assembler
│   ├── updater.py                  Incremental updater
│   ├── session_manager.py          Session tracker
│   └── decision_manager.py         Decision recorder
├── gui/app.py                      Windows/Mac/Linux GUI (tkinter)
├── parsers/base_parser.py          Python AST + regex parser
├── storage/
│   ├── db.py                       All database operations
│   └── schema.sql                  SQLite + FTS5 schema
├── models/memory_types.py          Data models
├── tests/test_engine.py            Integration tests
├── memory_engine.spec              PyInstaller spec (builds .exe)
├── vscode-extension/
│   ├── src/extension.ts            Commands + file watcher
│   ├── src/memoryProvider.ts       4 sidebar panels
│   └── src/runner.ts               Python subprocess runner
├── desktop-app/
│   ├── src/main/electron.js        Electron main process
│   ├── src/renderer/App.tsx        7-page React UI
│   └── api/server.py               Local FastAPI server
└── saas-platform/
    ├── backend/app/
    │   ├── main.py                 FastAPI app
    │   ├── api/auth.py             JWT auth + API keys
    │   ├── api/projects.py         Project CRUD
    │   ├── api/billing.py          Stripe payments
    │   ├── models/schema.py        Multi-tenant DB models
    │   └── services/auth.py        bcrypt + JWT helpers
    ├── frontend/src/app/
    │   ├── page.tsx                Landing page + pricing
    │   ├── dashboard/page.tsx      Dashboard
    │   └── login/page.tsx          Login
    └── docker-compose.yml          All services
```

---

## Running Tests

```bash
python tests/test_engine.py
```

Expected output:
```
Running memory engine tests...

OK Files indexed: 5
OK Functions stored: 7
OK Graph edges: 3
OK Context tokens: 249
OK Original tokens: 2490
OK Token savings: 90.0%
OK Incremental update detected 1 change(s)
OK FTS search found 2 file(s) for 'user'

All tests passed!
```

---

## Supported Languages

| Language | Parser | Quality |
|----------|--------|---------|
| Python | stdlib `ast` | Best — full AST analysis |
| JavaScript | Regex | Good |
| TypeScript | Regex | Good |
| Go | Regex | Good |
| Rust | Regex | Good |
| Java | Regex | Good |
| C# | Regex | Good |

---

## Contributing

1. Fork the repo
2. Create branch: `git checkout -b feature/my-feature`
3. Make changes and run tests: `python tests/test_engine.py`
4. Commit: `git commit -m "Add my feature"`
5. Push and open a Pull Request

---

## Roadmap

- [x] Core Memory Engine (SQLite + FTS5 + NetworkX)
- [x] CLI Tool (11 commands)
- [x] Windows GUI + .exe
- [x] VS Code Extension (TypeScript, auto file watcher)
- [x] Desktop App (Electron + React + FastAPI)
- [x] SaaS Platform (Next.js + FastAPI + PostgreSQL + Stripe)
- [ ] Tree-sitter deep parser for JS/TS/Go/Rust
- [ ] FAISS vector search (semantic retrieval)
- [ ] VS Code Marketplace publish
- [ ] Python + Node SDK
- [ ] GitHub Action integration

---

## License

MIT — free to use, modify, and distribute. See [LICENSE](LICENSE).

---

## Star this repo

If this saves you tokens and time, please star it on GitHub.
It helps other developers find it!

**https://github.com/faisalnavy/ai-memory-engine**
