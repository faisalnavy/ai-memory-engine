# 🧠 AI Memory Engine

> **Reduce AI token usage by 90–98%** — A universal memory layer between your codebase and any AI coding assistant.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)
![Token Savings](https://img.shields.io/badge/Token%20Savings-90--98%25-brightgreen)

---

## What is this?

AI coding assistants (Claude, Cursor, Copilot, etc.) need your entire codebase as context — which costs thousands of tokens every single request.

**AI Memory Engine** solves this by building a smart memory layer that:
- Reads and understands your entire project once
- Stores it in a compact SQLite database inside your project
- On every AI query, retrieves only the **relevant** files and functions
- Delivers **500–3000 tokens** instead of **50,000+**

**Result: 90–98% token savings with zero loss in accuracy.**

---

## Features

- 🗂️ **7-Layer Memory Architecture** — Project DNA, Files, Functions, Graph, Decisions, Sessions, Compressed Intelligence
- 🔍 **Full-text search** — SQLite FTS5 for instant file/function lookup
- 🕸️ **Dependency graph** — NetworkX-powered knowledge graph
- ⚡ **Incremental updates** — Only re-indexes changed files (hash-based)
- 🖥️ **Windows GUI** — One-click `.exe` launcher
- 💻 **CLI tool** — 11 commands for power users
- 🌐 **Works with any AI** — Claude, Cursor, Windsurf, Copilot, Gemini, GPT-4
- 📦 **Supports Python, JS, TS, Go, Rust, Java, C#**

---

## Quick Demo

```
Project:  my-flask-api  (127 files, 43,000 lines)

Without Memory Engine:
  Context sent to AI → 52,000 tokens  💸

With Memory Engine:
  memory ask "how does user authentication work"
  Context sent to AI → 890 tokens  ✅  (98.3% savings)
```

---

## Installation

Choose your platform:

- [🪟 Windows](#windows)
- [🍎 macOS](#macos)
- [🐧 Linux](#linux)

---

## 🪟 Windows

### Option A — GUI (Recommended, no Python needed)

1. Go to [**Releases**](../../releases) on this GitHub page
2. Download `MemoryEngine.exe`
3. Double-click to run — no installation needed

### Option B — From Source (CLI + GUI)

**Step 1 — Install Python 3.11+**

Download from [python.org](https://www.python.org/downloads/) — during install, check **"Add Python to PATH"**

Verify:
```cmd
python --version
```

**Step 2 — Clone the repository**

```cmd
git clone https://github.com/faisalnavy/ai-memory-engine.git
cd ai-memory-engine
```

**Step 3 — Create virtual environment**

```cmd
python -m venv venv
venv\Scripts\activate
```

**Step 4 — Install dependencies**

```cmd
pip install -r requirements.txt
```

**Step 5 — Run the GUI**

```cmd
python -X utf8 gui/app.py
```

**Step 6 — Or use the CLI**

```cmd
python -X utf8 cli/main.py --help
```

> **Note:** Always use `python -X utf8` on Windows to avoid encoding issues with the terminal.

**Optional — Add `memory` as a global command**

```cmd
pip install -e .
memory --help
```

---

## 🍎 macOS

**Step 1 — Install Python 3.11+**

Using Homebrew (recommended):
```bash
brew install python@3.11
```

Or download from [python.org](https://www.python.org/downloads/)

Verify:
```bash
python3 --version
```

**Step 2 — Clone the repository**

```bash
git clone https://github.com/faisalnavy/ai-memory-engine.git
cd ai-memory-engine
```

**Step 3 — Create virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Step 4 — Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 5 — Run the GUI**

```bash
python gui/app.py
```

**Step 6 — Or use the CLI**

```bash
python cli/main.py --help
```

**Optional — Add `memory` as a global command**

```bash
pip install -e .
memory --help
```

> **macOS Note:** If you see a security warning when running the GUI, go to  
> System Settings → Privacy & Security → click "Open Anyway"

---

## 🐧 Linux

**Step 1 — Install Python 3.11+ and tkinter**

Ubuntu / Debian:
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-tk git -y
```

Fedora / RHEL:
```bash
sudo dnf install python3.11 python3-tkinter git -y
```

Arch Linux:
```bash
sudo pacman -S python tk git
```

Verify:
```bash
python3 --version
```

**Step 2 — Clone the repository**

```bash
git clone https://github.com/faisalnavy/ai-memory-engine.git
cd ai-memory-engine
```

**Step 3 — Create virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Step 4 — Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 5 — Run the GUI**

```bash
python gui/app.py
```

**Step 6 — Or use the CLI**

```bash
python cli/main.py --help
```

**Optional — Add `memory` as a global command**

```bash
pip install -e .
memory --help
```

---

## Using the GUI

1. Launch `MemoryEngine.exe` (Windows) or `python gui/app.py` (Mac/Linux)
2. Click **Browse...** → select your project root folder
3. Check **Initialize & Index** (always checked by default)
4. Optionally check **Run test query** and type a question
5. Click **Run**
6. Watch the console — it will show files indexed, functions stored, and token savings
7. Done! A `.memory/` folder is created inside your project

---

## Using the CLI

After installing, run these commands from inside your project folder (or pass `--path`):

```bash
# Initialize memory for a project
memory init /path/to/your-project

# Index all files (run once, then update incrementally)
memory index /path/to/your-project

# Ask a question — get optimized AI context
memory ask "how does user authentication work" --path /path/to/your-project

# Search files and functions
memory search "database" --path /path/to/your-project

# See stats (files, functions, graph edges)
memory stats /path/to/your-project

# Update only changed files (fast!)
memory update /path/to/your-project

# Show file dependency graph
memory graph /path/to/your-project

# Compress old session memory
memory compress /path/to/your-project

# Record an architectural decision
memory decide "Use SQLite over PostgreSQL" --path /path/to/your-project

# Export memory as zip (share with team)
memory export my-project-memory.zip --path /path/to/your-project

# Import memory from zip
memory import my-project-memory.zip --path /path/to/your-project
```

---

## How to use with AI assistants

### With Claude / ChatGPT / Gemini

```bash
memory ask "your coding question" --path /path/to/project
```

Copy the output and paste it as context **before** your question in the AI chat.

### With Claude Code

```bash
# Run this in your project terminal before asking Claude Code anything
memory ask "$(cat)" --path .
# type your question, press Ctrl+D
```

### With Cursor / Windsurf / Copilot

Add this to your `.cursorrules` or system prompt file:
```
Before answering, use the memory context from .memory/project_dna.json
```

Or pipe the context directly:
```bash
memory ask "refactor the auth module" --no-context --path . | pbcopy  # Mac
memory ask "refactor the auth module" --no-context --path . | clip    # Windows
```

---

## Project Structure

```
ai-memory-engine/
├── cli/
│   └── main.py              # CLI tool — 11 commands
├── core/
│   ├── dna.py               # Project DNA detector
│   ├── file_summarizer.py   # File indexer
│   ├── function_summarizer.py  # Function indexer
│   ├── graph_builder.py     # Dependency graph (NetworkX)
│   ├── retriever.py         # 6-step retrieval engine
│   ├── compressor.py        # Session compression
│   ├── context_builder.py   # Context assembler
│   ├── updater.py           # Incremental updater
│   ├── session_manager.py   # Session tracker
│   └── decision_manager.py  # Decision recorder
├── gui/
│   └── app.py               # Windows/Mac/Linux GUI (tkinter)
├── parsers/
│   └── base_parser.py       # Python AST + generic regex parser
├── storage/
│   ├── db.py                # All database operations
│   └── schema.sql           # SQLite + FTS5 schema
├── models/
│   └── memory_types.py      # Data models
├── tests/
│   └── test_engine.py       # Integration tests
├── requirements.txt
├── setup.py
├── memory_engine.spec       # PyInstaller spec (build .exe)
└── README.md
```

---

## How it works

```
Your Project
     │
     ▼
┌─────────────────────────────────────┐
│         AI Memory Engine            │
│                                     │
│  1. Parse all source files          │
│  2. Extract functions + imports     │
│  3. Build dependency graph          │
│  4. Store in SQLite + FTS5          │
│                                     │
│  On every query:                    │
│  5. FTS5 search → relevant files    │
│  6. Graph traversal → related code  │
│  7. Assemble ≤3000 token context    │
└─────────────────────────────────────┘
     │
     ▼
AI Assistant  (90-98% fewer tokens)
```

---

## Building the .exe yourself (Windows)

```cmd
pip install pyinstaller
python -m PyInstaller memory_engine.spec --clean --noconfirm
# Output: dist\MemoryEngine.exe
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

| Language | Parser | Status |
|----------|--------|--------|
| Python | AST (stdlib) | ✅ Full |
| JavaScript | Regex | ✅ Good |
| TypeScript | Regex | ✅ Good |
| Go | Regex | ✅ Good |
| Rust | Regex | ✅ Good |
| Java | Regex | ✅ Good |
| C# | Regex | ✅ Good |

---

## Requirements

- Python 3.11 or higher
- 50 MB disk space (for the .exe) or ~10 MB (source)
- No internet connection required — fully offline

Python packages (auto-installed):
```
typer >= 0.12.0
rich >= 13.0.0
networkx >= 3.0
watchdog >= 4.0.0
```

---

## Contributing

Pull requests are welcome!

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests: `python tests/test_engine.py`
5. Commit: `git commit -m "Add my feature"`
6. Push: `git push origin feature/my-feature`
7. Open a Pull Request

---

## Roadmap

- [x] Phase 1 — Core Memory Engine
- [x] Phase 2 — CLI Tool (11 commands)
- [x] Phase 3 — Windows GUI + .exe
- [ ] Phase 4 — VS Code Extension
- [ ] Phase 5 — Desktop App (Electron + React)
- [ ] Phase 6 — SaaS Platform

---

## License

MIT — free to use, modify, and distribute.

---

## Star this repo ⭐

If this tool saves you tokens and time, please give it a star — it helps other developers find it!
