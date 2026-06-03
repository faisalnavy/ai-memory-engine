"""
Universal AI Coding Memory Engine — Windows GUI
Tkinter-based launcher: pick a project folder, click Run, done.
"""
import sys
import os
import threading
import queue
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext

# ── Resolve project root so imports work whether run as .py or bundled .exe ──
if getattr(sys, "frozen", False):
    # Running as PyInstaller bundle
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).parent.parent

sys.path.insert(0, str(BASE_DIR))

# ── Colours & fonts ──────────────────────────────────────────────────────────
BG         = "#0f1117"
BG2        = "#1a1d27"
BG3        = "#252836"
ACCENT     = "#6c63ff"
ACCENT2    = "#a78bfa"
GREEN      = "#22c55e"
RED        = "#ef4444"
YELLOW     = "#f59e0b"
TEXT       = "#e2e8f0"
TEXT_DIM   = "#64748b"
FONT_MAIN  = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_BIG   = ("Segoe UI", 18, "bold")
FONT_MED   = ("Segoe UI", 13, "bold")
FONT_MONO  = ("Consolas", 9)


class MemoryEngineGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Memory Engine")
        self.geometry("820x680")
        self.minsize(700, 560)
        self.configure(bg=BG)
        self.resizable(True, True)

        # Message queue — worker thread → GUI
        self.msg_queue: queue.Queue = queue.Queue()
        self._running = False

        self._build_ui()
        self._poll_queue()

    # ── UI Construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Header ──
        hdr = tk.Frame(self, bg=ACCENT, pady=18)
        hdr.pack(fill="x")
        tk.Label(hdr, text="AI Memory Engine",
                 font=FONT_BIG, bg=ACCENT, fg="white").pack()
        tk.Label(hdr, text="Reduce AI token usage by 90-98% with smart project memory",
                 font=FONT_MAIN, bg=ACCENT, fg="#d4d0ff").pack()

        # ── Main card ──
        card = tk.Frame(self, bg=BG2, padx=28, pady=14)
        card.pack(fill="x", padx=20, pady=(12, 0))

        tk.Label(card, text="Project Folder",
                 font=FONT_MED, bg=BG2, fg=TEXT).grid(row=0, column=0,
                 sticky="w", columnspan=3)
        tk.Label(card, text="Select the root folder of your Python / JS / TS project",
                 font=FONT_MAIN, bg=BG2, fg=TEXT_DIM).grid(row=1, column=0,
                 sticky="w", columnspan=3, pady=(2, 10))

        # Path entry + Browse
        self.path_var = tk.StringVar()
        path_frame = tk.Frame(card, bg=BG2)
        path_frame.grid(row=2, column=0, columnspan=3, sticky="ew")
        card.columnconfigure(0, weight=1)
        path_frame.columnconfigure(0, weight=1)

        self.path_entry = tk.Entry(
            path_frame, textvariable=self.path_var,
            font=FONT_MAIN, bg=BG3, fg=TEXT,
            insertbackground=TEXT, relief="flat",
            bd=0, highlightthickness=2,
            highlightcolor=ACCENT, highlightbackground=BG3,
        )
        self.path_entry.grid(row=0, column=0, sticky="ew", ipady=8, padx=(0, 10))

        browse_btn = tk.Button(
            path_frame, text="Browse...",
            font=FONT_BOLD, bg=BG3, fg=ACCENT2,
            activebackground=BG2, activeforeground=ACCENT,
            relief="flat", bd=0, padx=16, pady=8, cursor="hand2",
            command=self._browse,
        )
        browse_btn.grid(row=0, column=1)

        # ── Options row ──
        opts = tk.Frame(card, bg=BG2)
        opts.grid(row=3, column=0, columnspan=3, sticky="w", pady=(14, 0))

        self.do_index_var = tk.BooleanVar(value=True)
        self.do_ask_var   = tk.BooleanVar(value=False)

        _chk(opts, "Initialize & Index", self.do_index_var, ACCENT2).pack(side="left", padx=(0, 20))
        _chk(opts, "Run test query after indexing", self.do_ask_var, ACCENT2).pack(side="left")

        # Test query input (shown only when do_ask is checked)
        self.query_frame = tk.Frame(card, bg=BG2)
        self.query_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(8, 0))
        tk.Label(self.query_frame, text="Test query:",
                 font=FONT_MAIN, bg=BG2, fg=TEXT_DIM).pack(side="left", padx=(0, 8))
        self.query_var = tk.StringVar(value="how does this project work")
        self.query_entry = tk.Entry(
            self.query_frame, textvariable=self.query_var,
            font=FONT_MAIN, bg=BG3, fg=TEXT,
            insertbackground=TEXT, relief="flat", bd=0,
            highlightthickness=1, highlightbackground=BG3,
        )
        self.query_entry.pack(side="left", fill="x", expand=True, ipady=6)
        self.query_frame.grid_remove()  # hidden by default

        self.do_ask_var.trace_add("write", self._toggle_query)

        # ── Run button ──
        self.run_btn = tk.Button(
            card, text="  Run  ",
            font=("Segoe UI", 12, "bold"),
            bg=ACCENT, fg="white",
            activebackground=ACCENT2, activeforeground="white",
            relief="flat", bd=0, padx=32, pady=10,
            cursor="hand2", command=self._on_run,
        )
        self.run_btn.grid(row=5, column=0, columnspan=3, pady=(20, 0))

        # ── Progress bar ──
        prog_frame = tk.Frame(self, bg=BG)
        prog_frame.pack(fill="x", padx=20, pady=(8, 0))

        self.stage_label = tk.Label(
            prog_frame, text="Ready", font=FONT_MAIN, bg=BG, fg=TEXT_DIM, anchor="w")
        self.stage_label.pack(fill="x")

        self.progress = ttk.Progressbar(prog_frame, mode="indeterminate", length=400)
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("TProgressbar", troughcolor=BG3, background=ACCENT,
                        thickness=6)
        self.progress.pack(fill="x", pady=(4, 0))

        # ── Stats row (compact) ──
        self.stats_frame = tk.Frame(self, bg=BG)
        self.stats_frame.pack(fill="x", padx=20, pady=(8, 0))
        self._stat_labels = {}
        for key, label in [("files", "Files"), ("functions", "Functions"),
                           ("edges", "Edges"), ("savings", "Savings")]:
            f = tk.Frame(self.stats_frame, bg=BG2, padx=10, pady=5)
            f.pack(side="left", expand=True, fill="x", padx=(0, 6))
            val = tk.Label(f, text="—", font=("Segoe UI", 13, "bold"),
                           bg=BG2, fg=ACCENT2)
            val.pack()
            tk.Label(f, text=label, font=("Segoe UI", 8), bg=BG2, fg=TEXT_DIM).pack()
            self._stat_labels[key] = val

        # ── Log console (larger) ──
        log_hdr = tk.Frame(self, bg=BG)
        log_hdr.pack(fill="x", padx=20, pady=(10, 2))
        tk.Label(log_hdr, text="Console Output",
                 font=FONT_BOLD, bg=BG, fg=TEXT).pack(side="left")
        tk.Button(log_hdr, text="Clear", font=FONT_MAIN,
                  bg=BG, fg=TEXT_DIM, relief="flat", bd=0,
                  cursor="hand2", command=self._clear_log).pack(side="right")

        self.log = scrolledtext.ScrolledText(
            self, font=FONT_MONO, bg=BG3, fg=TEXT,
            insertbackground=TEXT, relief="flat", bd=0,
            wrap="word", state="disabled",
        )
        self.log.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        # Tag colours for log
        self.log.tag_config("ok",      foreground=GREEN)
        self.log.tag_config("err",     foreground=RED)
        self.log.tag_config("warn",    foreground=YELLOW)
        self.log.tag_config("accent",  foreground=ACCENT2)
        self.log.tag_config("dim",     foreground=TEXT_DIM)
        self.log.tag_config("heading", foreground=ACCENT2,
                            font=("Consolas", 9, "bold"))

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _toggle_query(self, *_):
        if self.do_ask_var.get():
            self.query_frame.grid()
        else:
            self.query_frame.grid_remove()

    def _browse(self):
        folder = filedialog.askdirectory(title="Select your project folder")
        if folder:
            self.path_var.set(folder)

    def _log(self, msg: str, tag: str = ""):
        self.log.configure(state="normal")
        if tag:
            self.log.insert("end", msg + "\n", tag)
        else:
            self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def _set_stat(self, key: str, value: str):
        self.msg_queue.put(("stat", key, value))

    def _set_stage(self, text: str):
        self.msg_queue.put(("stage", text))

    # ── Queue polling (thread-safe UI updates) ───────────────────────────────

    def _poll_queue(self):
        try:
            while True:
                item = self.msg_queue.get_nowait()
                kind = item[0]
                if kind == "log":
                    self._log(item[1], item[2] if len(item) > 2 else "")
                elif kind == "stat":
                    self._stat_labels[item[1]].configure(text=item[2])
                elif kind == "stage":
                    self.stage_label.configure(text=item[1])
                elif kind == "done":
                    self._on_done(success=item[1])
        except queue.Empty:
            pass
        self.after(80, self._poll_queue)

    def _qlog(self, msg: str, tag: str = ""):
        self.msg_queue.put(("log", msg, tag))

    # ── Run logic ────────────────────────────────────────────────────────────

    def _on_run(self):
        project_path = self.path_var.get().strip()
        if not project_path:
            self._log("ERROR: Please select a project folder first.", "err")
            return
        if not Path(project_path).is_dir():
            self._log(f"ERROR: Folder not found: {project_path}", "err")
            return
        if self._running:
            return

        self._running = True
        self.run_btn.configure(state="disabled", text="Running...")
        self.progress.start(12)
        self._clear_log()

        thread = threading.Thread(
            target=self._worker,
            args=(project_path, self.do_index_var.get(),
                  self.do_ask_var.get(), self.query_var.get().strip()),
            daemon=True,
        )
        thread.start()

    def _worker(self, project_path: str, do_index: bool, do_ask: bool, query: str):
        try:
            from storage import db
            from core import (dna, file_summarizer, function_summarizer,
                              graph_builder, retriever, context_builder)

            self._qlog("=" * 60, "dim")
            self._qlog(f"  Project: {project_path}", "accent")
            self._qlog("=" * 60, "dim")

            # ── STEP 1: Init ────────────────────────────────────────────────
            self._set_stage("Step 1/3 — Initializing memory database...")
            self._qlog("\n[INIT] Creating .memory/ database...", "heading")

            memory_dir = Path(project_path) / ".memory"
            memory_dir.mkdir(parents=True, exist_ok=True)
            db.init_db(project_path)

            self._qlog("[INIT] Detecting project DNA...", "dim")
            project_dna = dna.generate_and_save(project_path)

            self._qlog(f"  Language    : {project_dna.language}", "ok")
            self._qlog(f"  Framework   : {project_dna.framework or 'not detected'}", "ok")
            self._qlog(f"  Architecture: {project_dna.architecture}", "ok")
            self._qlog(f"  Entry points: {', '.join(project_dna.entry_points) or 'none'}", "ok")
            self._qlog("[INIT] Done.", "ok")

            if not do_index:
                self.msg_queue.put(("done", True))
                return

            # ── STEP 2: Index ───────────────────────────────────────────────
            self._set_stage("Step 2/3 — Indexing files...")
            self._qlog("\n[INDEX] Scanning and indexing all source files...", "heading")

            file_count = [0]

            def on_progress(done, total, current_file):
                file_count[0] = done
                short = Path(current_file).name
                self._set_stage(f"Step 2/3 — Indexing [{done}/{total}] {short}")
                if done % 5 == 0 or done == total:
                    self._qlog(f"  [{done}/{total}] {short}", "dim")

            results = file_summarizer.summarize_directory(project_path, on_progress)

            self._set_stage("Step 2/3 — Building function index...")
            self._qlog("[INDEX] Storing function signatures...", "dim")
            fn_count = function_summarizer.summarize_all_functions(project_path, results)

            self._set_stage("Step 2/3 — Building dependency graph...")
            self._qlog("[INDEX] Building knowledge graph...", "dim")
            graph_builder.build_graph(project_path)

            stats = db.get_stats(project_path)
            self._qlog(f"\n[INDEX] Complete!", "ok")
            self._qlog(f"  Files indexed : {stats['file_memory']}", "ok")
            self._qlog(f"  Functions     : {stats['function_memory']}", "ok")
            self._qlog(f"  Graph edges   : {stats['knowledge_graph']}", "ok")

            self._set_stat("files",     str(stats["file_memory"]))
            self._set_stat("functions", str(stats["function_memory"]))
            self._set_stat("edges",     str(stats["knowledge_graph"]))

            # ── STEP 3: Test query (optional) ───────────────────────────────
            if do_ask and query:
                self._set_stage("Step 3/3 — Running test query...")
                self._qlog(f'\n[ASK] Query: "{query}"', "heading")

                pkg = retriever.retrieve(project_path, query, max_tokens=3000)
                report = context_builder.savings_report(pkg)

                self._qlog(f"  Original tokens : ~{report['original']:,}", "dim")
                self._qlog(f"  Optimized tokens: {report['optimized']:,}", "ok")
                self._qlog(f"  Token savings   : {report['savings_pct']}%", "ok")
                self._set_stat("savings", f"{report['savings_pct']}%")

                self._qlog("\n--- Context Package Preview ---", "accent")
                preview = pkg.as_markdown()[:1200]
                self._qlog(preview, "dim")
                if len(pkg.as_markdown()) > 1200:
                    self._qlog("  [... truncated — full context ready for AI ...]", "dim")
            else:
                self._set_stat("savings", "ready")

            self._set_stage("Done! Memory system is active.")
            self._qlog("\n" + "=" * 60, "dim")
            self._qlog("  MEMORY ENGINE ACTIVE — ready to use!", "ok")
            self._qlog(f"  Database: {memory_dir / 'memory.db'}", "dim")
            self._qlog("=" * 60, "dim")

            self.msg_queue.put(("done", True))

        except Exception as exc:
            import traceback
            self._qlog(f"\nERROR: {exc}", "err")
            self._qlog(traceback.format_exc(), "err")
            self.msg_queue.put(("done", False))

    def _on_done(self, success: bool):
        self._running = False
        self.progress.stop()
        self.run_btn.configure(state="normal", text="  Run  ")
        if success:
            self.stage_label.configure(text="Done! Memory system is active.", fg=GREEN)
        else:
            self.stage_label.configure(text="Failed. See console for details.", fg=RED)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _chk(parent, text, var, fg):
    return tk.Checkbutton(
        parent, text=text, variable=var,
        font=FONT_MAIN, bg=BG2, fg=fg,
        activebackground=BG2, activeforeground=fg,
        selectcolor=BG3, relief="flat", bd=0, cursor="hand2",
    )


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    app = MemoryEngineGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
