# Changelog

All versions of AI Memory Engine are documented here.
Format: `[version] — date — what changed`

---

## [v1.0.0] — 2026-06-03 — First Stable Release

### What's included

**Phase 1 — Core Memory Engine**
- 7-layer memory architecture: Project DNA, Files, Functions, Graph, Sessions, Decisions, Compression
- SQLite + FTS5 full-text search
- NetworkX dependency graph
- Hash-based incremental updates (only re-indexes changed files)
- 90-98% token savings verified in tests

**Phase 2 — CLI Tool (11 commands)**
- `memory init` — initialize project
- `memory index` — full scan
- `memory update` — incremental update
- `memory ask` — get AI context
- `memory search` — search files/functions
- `memory stats` — view statistics
- `memory graph` — dependency visualization
- `memory compress` — compress sessions
- `memory decide` — record decisions
- `memory export` — export as zip
- `memory import` — import from zip

**Phase 3 — Windows GUI (.exe)**
- Tkinter dark-theme GUI
- PyInstaller standalone .exe (55 MB)
- No Python required — double-click and run
- Progress tracking, stats tiles, console output

**Phase 4 — VS Code Extension**
- TypeScript extension with 8 commands
- 4 sidebar panels: Memory Explorer, Dependency Graph, Token Savings, Sessions
- Auto file-watcher — updates memory on every file save
- Status bar indicator (🧠 Memory / Updating... / Memory ✓)
- Installable .vsix package (27 KB)

**Phase 5 — Desktop App**
- Electron + React frontend (7 pages)
- Bundled Python FastAPI backend (api.exe — no Python needed)
- One-click launch — no terminal, no setup
- Pages: Dashboard, Projects, Memory, Sessions, Decisions, Analytics

**Phase 6 — SaaS Platform**
- Next.js 14 frontend with landing page, dashboard, login
- FastAPI multi-tenant backend
- PostgreSQL + Redis
- JWT authentication + API keys + bcrypt password hashing
- Stripe billing: Free / $12 Pro / $49 Team / Enterprise
- Docker Compose for self-hosting

### Stats
- 70+ files
- 6,700+ lines of code
- Supports: Python, JS, TS, Go, Rust, Java, C#
- Works with: Claude, Cursor, Copilot, ChatGPT, Gemini, Windsurf

---

## [v1.1.0] — Planned — Next Generation

> Changes will be tracked here when the next version is built.

Ideas for next version:
- [ ] Tree-sitter deep parser (replaces regex for JS/TS/Go/Rust)
- [ ] FAISS vector search for semantic retrieval
- [ ] VS Code Marketplace publish
- [ ] Python + Node SDK
- [ ] Slack / Teams integration
- [ ] GitHub Action for CI/CD auto-indexing
- [ ] Multi-project dashboard in GUI
- [ ] Export context directly to Claude Code / Cursor

---

## Version Numbering

| Version | Meaning |
|---------|---------|
| `v1.0.x` | Bug fixes, small improvements |
| `v1.x.0` | New features added to existing phases |
| `v2.0.0` | Major new generation (new architecture or phase) |
